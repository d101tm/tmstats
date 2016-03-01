#!/usr/bin/python

# @@TODO:  Combine "export" into this program.
# @@TODO:  Create areas from Divisions.

import dbconn, tmutil, sys, os
import math
from overridepositions import overrideClubPositions
import csv



def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)
        
        

        
clubs = {}

class myclub:
    
    fields = ['clubnumber', 'clubname', 'latitude', 'longitude', 'place', 'address', 'city', 'state', 'zip', 'country', 'area', 'division', 'meetingday', 'meetingtime', 'color', 'goalsmet', 'activemembers']
    
    outfields = ['clubnumber', 'clubname', 'oldarea', 'newarea', 'color', 'goalsmet', 'activemembers', 'meetingday', 'meetingtime', 'place', 'address', 'city', 'state', 'zip', 'country',  'latitude', 'longitude', ]
    
    def __init__(self, *args):
        # Assign values
        for (f, v) in zip(self.fields, args):
            self.__dict__[f] = v
        # Fix up clubnumber
        self.clubnumber = '%s' % self.clubnumber
        self.distances = []
        self.oldarea = self.division + self.area
        self.newarea = self.oldarea
        clubs[self.clubnumber] = self
        if self.latitude == 0.0 or self.longitude == 0.0:
            print self.clubname, self.clubnumber, 'has no location assigned.'
            
    def out(self):
        return ['%s' % self.__dict__[f] for f in self.outfields]
        
        
### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--mapoverride', dest='mapoverride', default=None, help='Google spreadsheet with overriding address and coordinate information')
    # Add other parameters here
    parms.parse() 
    
    # Promote information from parms.makemap if not already specified
    parms.mapoverride = parms.mappoverride if parms.mapoverride else parms.makemap.get('mapoverride',None)
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    
    from makemap import Bounds
    bounds = Bounds()

    # Get data from clubs
    curs.execute('SELECT MAX(lastdate) FROM CLUBS')
    lastdate = curs.fetchone()[0]
    whereclause = 'WHERE (c.division IN ("C", "D", "E", "H", "I") OR c.city like "%%Palo Alto%%") AND c.lastdate = "%s"' % lastdate
    c2 = conn.cursor()
    curs.execute('SELECT g.clubnumber, g.clubname, g.latitude, g.longitude, g.place, g.address, g.city, g.state, g.zip, g.country, c.area, c.division, c.meetingday, c.meetingtime FROM geo g INNER JOIN clubs c on g.clubnumber = c.clubnumber ' + whereclause)
    for row in curs.fetchall():
        c2.execute('SELECT color, goalsmet, activemembers FROM clubperf WHERE entrytype = "L" AND clubnumber = %s', (row[0],))
        row = [cell for cell in row] + [cell for cell in c2.fetchone()]
        myclub(*row)
        
        
    # Now, get the performance metrics of interest

        
    # If there are overrides to club positioning, handle them now
    if parms.mapoverride:
        overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey)

    # For D4, we need to add the info from their spreadsheet
    untouched = set(clubs.keys())
    infile = open('d4committee.csv', 'rbU')
    reader = csv.DictReader(infile)
    for row in reader:
        clubnum = row['clubnumber']
        if clubnum not in clubs:
            print '%s (%s) missing' % (row['clubname'], row['clubnumber'])
        else:
            c = clubs[clubnum]
            c.newarea = row['renameddiv'] + row['renamedarea']
            if clubnum in untouched:
                untouched.remove(clubnum)
            else:
                print clubnum, 'not in untouched'
            
    if untouched:
        print 'Clubs not in the new alignment file:'
        for c in untouched:
            club = clubs[c]
            print '  %s (%s), was in %s' % (club.clubname, club.clubnumber, club.division + club.area)
            del clubs[c]
        
    outfile = open('d4align.csv', 'wb')
    writer = csv.writer(outfile)
    writer.writerow(myclub.outfields)
    clubs = [c for c in clubs.values()]
    clubs.sort(key=lambda c:c.newarea+'%8s'%c.clubnumber)
    for c in clubs:
        writer.writerow(c.out())
    outfile.close()
    
