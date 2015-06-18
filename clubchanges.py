#!/usr/bin/python
import os


def cleandate(indate):
    from datetime import date, timedelta
    if '/' in indate:
        indate = indate.split('/')
        indate = [indate[2], indate[0], indate[1]]
    elif '-' in indate:
        indate = indate.split('-')
    elif 'today'.startswith(indate.lower()):
        return date.today().strftime('%Y-%m-%d')
    elif 'yesterday'.startswith(indate.lower()):
        return (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    if len(indate[0]) == 2:
        indate[0] = "20" + indate[0]
    if len(indate[1]) == 1:
        indate[1] = "0" + indate[1]
    if len(indate[2]) == 1:
        indate[2] = "0" + indate[2]
    return '-'.join(indate)
    

def oldcode():
    import sys, csv, re, codecs, os
    from club import Club
    """ Inform the webmaster of any changes """


    def normalize(s):
        if s:
            return re.sub('\W\W*', '', s).strip().lower()
        else:
            return ''
        
        
    if len(sys.argv) < 3:
        (yday, today) = ['data/'+c for c in os.listdir('./data/') if 'clubs.' in c][-2:]
    else:
        today = sys.argv[1]
        yday = sys.argv[2]



    tclubs = {}
    yclubs = {}

    # Get today's clubs

    csvfile = open(today, 'rU')
    r = csv.reader(csvfile, delimiter=',')
    headers = [normalize(p) for p in r.next()]
    Club.setHeaders(headers)



    clubcol = headers.index('clubnumber')    
    for row in r:
        try:
            row[clubcol] = Club.fixcn(row[clubcol])
            if row[clubcol]:
                club = Club(row)
                tclubs[club.clubnumber] = club
        except IndexError:
            pass

    
    csvfile.close()

    # Now, get yesterday's clubs
    csvfile = open(yday, 'rU')
    r = csv.reader(csvfile, delimiter=',')

    r.next()  # Skip the headers

 
    for row in r:
        try:
            row[clubcol] = Club.fixcn(row[clubcol])
            if row[clubcol]:
                club = Club(row)
                yclubs[club.clubnumber] = club
        except IndexError:
            pass

    
    csvfile.close()

    newclubs = set(tclubs.keys()) - set(yclubs.keys())  # Clubs added
    lostclubs = set(yclubs.keys()) - set(tclubs.keys()) # Clubs deleted 
    sameclubs = set(tclubs.keys()) - newclubs - lostclubs  # Clubs to be checked for changes

    def printit(newc, oldc):
        if newc:
            print "Club: %s, club number %s" % (newc.clubname, newc.clubnumber)
            if oldc and oldc.clubname != newc.clubname:
                print "  was %s" % oldc.clubname
            print "Division %s, Area %s" % (newc.division, newc.area)
            if oldc and ((oldc.division != newc.division) or (oldc.area != newc.area)):
                print "  was Division %s, Area %s" % (oldc.division, oldc.area)
            print "Meets at %s on %s" % (newc.meetingtime, newc.meetingday)
            if oldc and (oldc.meetingtime + oldc.meetingday != newc.meetingtime + newc.meetingday):
                print "  was %s on %s" % (oldc.meetingtime, oldc.meetingday)
            newloc = codecs.decode("Location:\n  %s\n  %s\n  %s, %s  %s" % (newc.address1, newc.address2, newc.city, newc.state, newc.zip),'utf-8').strip()
            print "Location: %s" % (newloc)
            if oldc:
                oldloc = codecs.decode("Location:\n  %s\n  %s\n  %s, %s  %s" % (newc.address1, newc.address2, newc.city, newc.state, newc.zip),'utf-8').strip()
            print "Membership: %s" % (newc.clubstatus)
            if oldc and oldc.clubstatus != newc.clubstatus:
                print "  was %s" % oldc.clubstatus
            if newc.advanced:
                print "Advanced Club"
            if oldc and oldc.advanced != newc.advanced:
                print "  was %s" % ("Advanced Club" if oldc.advanced else "Normal club")
        elif oldc and not newc:
            print "Club: %s, club number %s" % (oldc.clubname, oldc.clubnumber)
            print "Division %s, Area %s" % (oldc.division, oldc.area)
    
    if len(newclubs) > 0:
        print len(newclubs), 'new clubs'

    for c in newclubs:
        printit(tclubs[c], None)
    
    print len(lostclubs), 'lost clubs'
    for c in lostclubs:
        printit(None, yclubs[c])
    
    print len(sameclubs), 'same clubs'
    for c in sorted([int(cnum) for cnum in sameclubs]):
        c = repr(c)
        if (tclubs[c].info() != yclubs[c].info()):
            print '*' * 72
            print tclubs[c].info()
            print yclubs[c].info()
            for k in yclubs[c].info().keys():
                if tclubs[c].info()[k] != yclubs[c].info()[k]:
                    print "key %s differs" % k
                    try:
                        print "today = '%s'\n  was = '%s'" % (tclubs[c].info()[k], yclubs[c].info()[k])
                    except UnicodeDecodeError:
                        pass
            try:
                printit (tclubs[c], yclubs[c])
            except UnicodeEncodeError:
                print 'code error'
        
class Club:
    """ Keep information about a club """
    @classmethod
    def setfields(self, names):
        self.fieldnames = names
        self.badnames = ['firstdate', 'lastdate']
        self.goodnames = [n for n in names if n not in self.badnames]
    
    def __init__(self, values):
        self.cmp = []
        for (name, value) in zip(self.fieldnames, values):
            self.__dict__[name] = value
            if name not in self.badnames:
                self.cmp.append(value)
     
    def __eq__(self, other):
        return self.cmp == other.cmp
         
    def __ne__(self, other):
        return self.cmp != other.cmp
        
    def delta(self, other):
        """ Return tuples of (name, self, other) for any values which have changed """
        res = []
        for name in self.goodnames:
            if self.__dict__[name] != other.__dict__[name]:
                res.append((name, self.__dict__[name], other.__dict__[name]))
        return res
        
    def __repr__(self):
        return '; '.join(['%s = "%s"' % (name, self.__dict__[name]) for name in self.goodnames])

if __name__ == "__main__":
    import dbconn, tmparms
    
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
    
    # Define args and parse command line
    parms = tmparms.tmparms()
    parms.add_argument('--fromdate', default='yesterday', dest='fromdate')
    parms.add_argument('--todate', default='today', dest='todate')
    parms.add_argument('--notify', nargs='*', default=None, dest='notify', action='append')
    parms.add_argument('--mailpw', default=None, dest='mailpw')
    parms.add_argument('--mailserver', default=None, dest='mailserver')
    parms.add_argument('--mailfrom', default=None, dest='mailfrom')
    parms.parse()
    fromdate = cleandate(parms.fromdate)
    todate = cleandate(parms.todate)
    print fromdate, todate
    
    
    print 'Connecting to %s:%s as %s' % (parms.dbhost, parms.dbname, parms.dbuser)
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
   
    # Get information for clubs as of the "from" date:
    print fromdate
    print "SELECT * FROM clubs WHERE firstdate <= %s AND lastdate >= %s" % (fromdate, fromdate)
    print curs.execute("SELECT * FROM clubs WHERE firstdate <= %s AND lastdate >= %s", (fromdate, fromdate))
    
    # Get the fieldnames before we get anything else:
    fieldnames = [f[0] for f in curs.description]
    Club.setfields(fieldnames)
    
    newclubs = {}   # Where clubs created during the period go
    changedclubs = {}  # Where clubs changed during the period go
    oldclubs = {}  # Clubs at the beginning; clubs still around at the end are removed
    
    # OK, now build the list of clubs at the beginning of the period
    for eachclub in curs.fetchall():
        club = Club(eachclub)
        oldclubs[club.clubnumber] = club
    print len(oldclubs)
    
    print todate
    # And compare to the the list of clubs at the end of the period
    print curs.execute("SELECT * FROM clubs WHERE firstdate <= %s AND lastdate >= %s", (todate, todate))    
    for eachclub in curs.fetchall():
        club = Club(eachclub) 
        if club.clubnumber not in oldclubs:
            club.info = 'New Club'
            newclubs[club.clubnumber] = club
        elif club == oldclubs[club.clubnumber]:
            # Club is unchanged; just remove it
            del oldclubs[club.clubnumber]
        else:
            # Club has changed.  Get the list of changes as a tuple (item, old, new)
            changedclubs[club.clubnumber] = (oldclubs[club.clubnumber].clubname, 
                oldclubs[club.clubnumber].delta(club))
            del oldclubs[club.clubnumber]  # And we're done with the old club
            
    # And print results
    if oldclubs:
        print "Clubs which have vanished:"
        for k in oldclubs:
            print k, oldclubs[k].clubname
            
        print "-------------------------------------------------------"
        print "New clubs:"
        for k in newclubs:
            print newclubs[k]
        
        print "-------------------------------------------------------"
        print "Changes:"
        for k in changedclubs:
            print k, changedclubs[k][0]
            for (item, old, new) in changedclubs[k][1]:
                print item, old, new
            print    


