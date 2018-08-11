#!/usr/bin/env python3
""" Find club changes. 

    Create an HTML file with changes in club information between two dates, based on Toastmasters' Find-a-Club data.
    There are up to three sections in the report:
    
        * Clubs which are no longer in the list from Toastmasters
        * Clubs which have been added to the list (with detailed infomation about each club)
        * Clubs whose information has been changed (by default, only the area, division, place, address, and meeting information is checked or displayed.)

    Exit 0 if no changes; 1 if there are changes.
    
"""
from simpleclub import Club
import os, sys
from tmutil import cleandate, removeSuspendedClubs, stringify
import datetime, argparse
import tmglobals, tmparms
globals = tmglobals.tmglobals()


        
def sortclubs(what):
    return sorted(list(what.keys()), key=lambda x:'%s%s%s' % (what[x].division, what[x].area, what[x].clubnumber.zfill(8)))



if __name__ == "__main__":

    
    # Define args and parse command line
    parms = tmparms.tmparms(description=__doc__)
    parms.add_argument('--fromdate', default='', dest='fromdate', help="Base date for club status (or status this many days ago, if an integer).  Default is second-most recent date in the CLUBS table.")
    parms.add_argument('--todate', default='', dest='todate', help="Show changes through this date.  Default is most recent date in the CLUBS table")
    parms.add_argument('--runon', default=None, dest='runon', nargs='+', 
                        help='Day of the week (Mon, Tue...) on which to run.  Runs daily if omitted.')
    parms.add_argument('--outfile', default='-', dest='outfile', type=argparse.FileType('w'), help="Output file.")
    parms.add_argument('--short', action='store_true', help="Print short output instead of creating HTML")
    
    # Do global setup
    globals.setup(parms)
    conn = globals.conn
    curs = globals.curs

    # Let's see if we're supposed to run today.
    if parms.runon:
        weekday = datetime.datetime.today().strftime('%A')
        run = [True for w in parms.runon if weekday.startswith(w)]  # Note:  T means Tuesday OR Thursday; S is Saturday OR Sunday
        if not run:
            #sys.stderr.write('Not running because today is %s but --runon=%s was specified\n' % (weekday, ' '.join(parms.runon)))
            sys.exit(0)  # Not running is a normal exit.
    
    # OK, we are running.  Figure out the dates to use.
    if parms.todate:
        cleanedtodate = cleandate(parms.todate, usetmyear=False)
        # Go forward to the first date with data on or after the date specified
        curs.execute("SELECT MIN(loadedfor) FROM loaded where tablename = 'clubs' AND loadedfor >= %s", (cleanedtodate,))
        todate = stringify(curs.fetchone()[0])
        if todate is None:
            todate = cleanedtodate
    else:
        # We want the last date in the database
        curs.execute("SELECT MAX(loadedfor) FROM loaded WHERE tablename = 'clubs'")
        todate = stringify(curs.fetchone()[0])

    if parms.fromdate:
        fromdate = cleandate(parms.fromdate,usetmyear=False)
        # Go backwards to the last date with data on or before the date specified 
        curs.execute("SELECT MAX(loadedfor) FROM loaded where tablename = 'clubs' AND loadedfor <= %s", (fromdate,))
        fromdate = stringify(curs.fetchone()[0])
    else:
        # We want the most recent date with data before the todate
        curs.execute("SELECT MAX(loadedfor) FROM loaded WHERE tablename = 'clubs' AND loadedfor < %s", ((todate,)))
        fromdate = stringify(curs.fetchone()[0])
    
  
    namestocompare = ['place', 'address', 'city', 'state', 'zip', 'country', 'meetingday', 'meetingtime', 'area', 'division', 'district']
    # Get information for clubs as of the "from" date:
    oldclubs = Club.getClubsOn(curs, date=fromdate, goodnames=namestocompare)
    oldclubs = removeSuspendedClubs(oldclubs, curs, date=fromdate)
    newclubs = {}   # Where clubs created during the period go
    changedclubs = {}  # Where clubs changed during the period go

    
    # And compare to the the list of clubs at the end of the period
    allclubs = Club.getClubsOn(curs, date=todate)
    allclubs = removeSuspendedClubs(allclubs, curs, date=todate)
    
    for club in list(allclubs.values()):
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
            ct = changedclubs[club.clubnumber]
            del oldclubs[club.clubnumber]  # And we're done with the old club
            
    # And create results if anything has changed
    
    rc = 1 if oldclubs or newclubs or changedclubs else 0  
    if rc == 1:
        
        outfile = parms.outfile

        if parms.short:
            outfile.write("Club Changes from %s to %s\n\n" % (fromdate, todate))
            if newclubs:
                outfile.write('New Clubs\n')
                for c in list(newclubs.values()):
                    outfile.write('  %s (%s)\n' % (c.clubname, c.clubnumber))
                outfile.write('=' * 72)
                outfile.write('\n')

            if oldclubs:
                outfile.write('Removed Clubs\n')
                for c in list(oldclubs.values()):
                    outfile.write('  %s (%s)\n' % (c.clubname, c.clubnumber))
                outfile.write('=' * 72)
                outfile.write('\n')
                    

                
            if changedclubs:
                outfile.write('Changed Clubs\n')
                for c in list(changedclubs.values()):
                    outfile.write('  %s\n' % c[0])
                    for each in c[1]:
                        outfile.write('    %s\n' % each[0])
                        outfile.write('      Old: %s\n' % each[1].replace('\n', ';;'))
                        outfile.write('      New: %s\n' % each[2].replace('\n', ';;'))
                    outfile.write('\n')
                
        else:
                
            outfile.write("<html>\n")
            outfile.write("""<head>
            <style type="text/css">


                    html {font-family: Arial, "Helvetica Neue", Helvetica, Tahoma, sans-serif;
                          font-size: 77%;}
      
                    table {width: 75%; font-size: 14px; border-width: 1px; border-spacing: 1px; border-collapse: collapse; border-style: solid;}
                    td, th {border-color: black; border-width: 1px;  vertical-align: middle;
                        padding: 2px; padding-right: 5px; padding-left: 5px; border-style: solid;}
                    
                    .item {width: 10%;}
                    .old {width: 40%;}
                    .new {width: 40%;}

                    .name {text-align: left; font-weight: bold; width: 40%;}
                    .number {text-align: right; width: 7%;}
        
                    .bold {font-weight: bold;}
                    .italic {font-style: italic;}
                    .leader {background-color: aqua;}
        
        
                    </style>
            </head>""")
            outfile.write("<body>\n")
            outfile.write("<h2>Club changes from %s to %s</h2>\n" % (fromdate, todate))

    
            if oldclubs:
                outfile.write("<h3>Clubs removed from the listing</h3>\n")
                outfile.write("<table><thead><tr><th>")
                outfile.write("</th><th>".join(('Division', 'Area', 'Club Number', 'Club Name')))
                outfile.write("</th></tr></thead>\n")
                outfile.write("<tbody>")
                for k in sortclubs(oldclubs):
                    club = oldclubs[k]
                    outfile.write("<tr><td>")
                    outfile.write("</td><td>".join((club.division, club.area, club.clubnumber, club.clubname)))
                    outfile.write("</td></tr>\n")
                outfile.write("</tbody></table>\n")
         
            if newclubs: 
                outfile.write("<h3>New clubs</h3>\n")
                for k in sortclubs(newclubs):
                    club = newclubs[k]
                    outfile.write("<h4>%s (%s), Area %s%s</h4>\n" % (club.clubname, club.clubnumber, club.division, club.area))
                    outfile.write("<table><thead>\n<tr>")
                    outfile.write("<th class='item'>Item</th><th>Value</th></tr></thead>\n")
                    outfile.write("<tbody>\n")
                    outfile.write("<tr><td>Link</td><td><a href='%s'>%s</a></td></tr>" % (club.getLink(), club.getLink()))
            
                    omit = ['clubname', 'clubnumber', 'division', 'area', 'cmp', 'place', 'address', 'city', 'state', 'zip', 'country', 'meetingtime', 'meetingday']
                    keys = [key for key in list(club.__dict__.keys()) if key not in omit]
                    outfile.write("<tr><td class='item'>%s</td><td>%s</td></tr>\n" % ('place', club.place))
                    outfile.write("<tr><td class='item'>%s</td><td>%s</td></tr>\n" % ('address', club.makeaddress()))
                    outfile.write("<tr><td class='item'>%s</td><td>%s</td></tr>\n" % ('meeting', club.makemeeting()))
            
                    for item in sorted(keys):
                        if club.__dict__[item]:
                            outfile.write("<tr><td class='item'>%s</td><td>%s</td></tr>\n" % (item, club.__dict__[item].replace('\n', '<br />')))
                    outfile.write("</tbody></table>\n")
              

        
            if changedclubs:
                outfile.write("<h3>Changed clubs</h3>\n")
                interestingclubs = {}
                for club in changedclubs:
                    interestingclubs[club] = allclubs[club]
                for k in sortclubs(interestingclubs):
                    club = interestingclubs[k]
                    outfile.write("<h4>%s (%s), Area %s%s</h4>\n" % (club.clubname, club.clubnumber, club.division, club.area))
                    outfile.write("<table><thead>\n<tr>")
                    outfile.write("<th class='item'>Item</th><th class='old'>Old</th><th class='new'>New</th></tr></thead>\n")
                    outfile.write("<tbody>\n")
                    outfile.write("<tr><td>Link</td><td colspan='2'><a href='%s'>%s</a></td></tr>" % (club.getLink(), club.getLink()))
                    keys = [key for key in list(club.__dict__.keys()) if key not in ['cmp']]
                    changedclubs[k][1].sort()
                    for (item, old, new) in changedclubs[k][1]:
                        if item in keys:
                            if item.startswith('meeting'):
                                item = 'meeting'
                            if item == 'place':
                                old = old.replace(';;', '<br />')
                                new = new.replace(';;', '<br />')
                            outfile.write("<tr><td class='item'>%s</td><td class='old'>%s</td><td class='new'>%s</td></tr>\n" % (item, old.replace('\n','<br />'), new.replace('\n', '<br />')))
                    outfile.write("</tbody></table>\n")
        
sys.exit(rc)
