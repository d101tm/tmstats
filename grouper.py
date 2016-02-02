#!/usr/bin/python

# @@TODO:  Combine "export" into this program.
# @@TODO:  Create areas from Divisions.

import dbconn, tmutil, sys, os
import math
from overridepositions import overrideClubPositions
import csv


def distance_on_unit_sphere(lat1, long1, lat2, long2):
 
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
         
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
     
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    try:
        arc = math.acos( cos )
    except Exception, e:
        arc = 0
 
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 3956  # to get miles



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
    whereclause = 'WHERE c.division IN ("A", "B", "F", "G", "J") AND c.city != "Palo Alto" AND c.lastdate = "%s"' % lastdate
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
        
    # Now, remove A1-A4
    all = clubs.keys()
    for c in all:
        if clubs[c].division == 'A' and clubs[c].area in ('1', '2', '3', '4'):
            del clubs[c]
    
        
    # Now, compute bounds and center
    bounds = Bounds()
    for c in clubs.values():
        bounds.extend(c.latitude, c.longitude)
        
    bounds.clat = (bounds.north + bounds.south) / 2.0
    bounds.clong = (bounds.east + bounds.west) / 2.0
    
    for c in clubs:
        clubs[c].centraldistance = distance_on_unit_sphere(clubs[c].latitude, clubs[c].longitude,
                                bounds.clat, bounds.clong)
        for d in clubs:
            if c > d:
                dist = distance_on_unit_sphere(clubs[c].latitude, clubs[c].longitude, clubs[d].latitude, clubs[d].longitude)
                clubs[c].distances.append((d, dist))
                clubs[d].distances.append((c, dist))
                
                
     
    away = [c for c in sorted(clubs, reverse=True, key=lambda c:clubs[c].centraldistance)]
         

    
    divs = []
    divmax = math.floor(len(away) / 5)
    print divmax
    print len(away), 'clubs'
    # Now, we start clustering.  
    while away:
        c = clubs[away.pop(0)]
        print c.clubname
        c.distances.sort(key=lambda l:l[1])
        div = [c.clubnumber]   # Start with THIS club
        while len(div) < divmax and len(c.distances) > 0:
            (cnum, dist) = c.distances.pop(0)  # Take off the first item
            if cnum in away:
                #print "club %s is %s away from %s" % (clubs[cnum].clubname, dist, c.clubname)
                if (dist > 50):
                    print "too far!"
                    break  # and we're done with this one
                div.append(cnum)
                del away[away.index(cnum)]
                #print len(away), 'clubs left in away'
        divs.append(div)
        print len(div), 'clubs in div', len(divs) + 1, '. ', len(away), 'left to look at'        
    
    divletters = ['','B','G','J','F','C']
    print len(divs), 'divscreated.'
    
    outfile = open('dived.csv', 'wb')
    writer = csv.writer(outfile)
    writer.writerow(myclub.outfields)
    for i in xrange(len(divs)):
        divnum = i+1
        for cnum in divs[i]:
            c = clubs[cnum]
            c.newarea = '%s%d' % (divletters[divnum], 1)
            writer.writerow(c.out())
    outfile.close()
    
