#!/usr/bin/python
import sys, csv, re, codecs
from club import Club
""" Inform the webmaster of any changes """


def normalize(s):
    if s:
        return re.sub('\W\W*', '', s).strip().lower()
    else:
        return ''
        
        
if len(sys.argv) < 3:
    today = 'data/clubs.2014-11-24.csv'
    yday = 'data/clubs.2014-11-23.csv'
else:
    today = sys.argv[1]
    yday = sys.argv[2]

print 'today', today
print 'yesterday', yday

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
        newloc = "Location:\n  %s\n  %s\n  %s, %s  %s" % (newc.address1, newc.address2, newc.city, newc.state, newc.zip)
        print codecs.decode(newloc,'cp1252').strip()
        if oldc:
            oldloc = "Location:\n  %s\n  %s\n  %s, %s  %s" % (newc.address1, newc.address2, newc.city, newc.state, newc.zip)
            if oldloc != newloc:
                print "was %s" % codecs.decode(oldloc,'cp1252').strip()
        print "Membership: %s" % (newc.clubstatus)
        if oldc and oldc.clubstatus != newc.clubstatus:
            print "  was %s" % oldc.clubstatus
        if newc.advanced:
            print "Advanced Club"
        if oldc and oldc.advanced != newc.advanced:
            print "  was %s" % ("Advanced Club" if oldc.advanced else "Normal club")
    elif oldc and not newc:
        print "Club: %s, club number %s" % (oldc.clubname, oldc.clubnumber)
        print "Division s, Area %s" % (oldc.division, oldc.area)
    
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
        printit (tclubs[c], yclubs[c])
        
        

