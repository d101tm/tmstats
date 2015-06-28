#!/usr/bin/python
from simpleclub import Club
import os, sys
from tmutil import cleandate


        
def sortclubs(what):
    return sorted(what.keys(), key=lambda x:'%s%s%s' % (what[x].division, what[x].area, what[x].clubnumber.zfill(8)))

def combine(club):
    omit = ['cmp']
    keys = [k for k in club.__dict__ if k not in omit]
    keys.sort()
    for k in keys:
        if k in fieldgroups:
            (fg, fmtstr) = fieldgroups[k]

            val = [club.__dict__.get(what, '') for what in fg]

            club.__dict__[k] = fmtstr % tuple(val)
            for what in fg[1:]:
                if what in club.__dict__:
                    del club.__dict__[what] 
                if what in keys:
                    del keys[keys.index(what)]
    return keys


if __name__ == "__main__":
    import dbconn, tmparms
    
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    # Get around unicode problems
    reload(sys).setdefaultencoding('utf8')
    
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
    
    # print 'Connecting to %s:%s as %s' % (parms.dbhost, parms.dbname, parms.dbuser)
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    namestocompare = ['address', 'city', 'state', 'zip', 'country', 'meetingday', 'meetingtime', 'area', 'division', 'district']
    # Get information for clubs as of the "from" date:
    oldclubs = Club.getClubsOn(fromdate, curs, setfields=True, goodnames=namestocompare)
    newclubs = {}   # Where clubs created during the period go
    changedclubs = {}  # Where clubs changed during the period go
    
    

    
    # And compare to the the list of clubs at the end of the period
    allclubs = Club.getClubsOn(todate, curs)
    for club in allclubs.values():
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
            
    # And create results if anything has changed
    
    
    if oldclubs or newclubs or changedclubs:

                
        outfile = open('clubchanges.html', 'w')
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
            #keys = combine(club)
            
            omit = ['clubname', 'clubnumber', 'division', 'area', 'cmp', 'address', 'city', 'state', 'zip', 'country', 'meetingtime', 'meetingday']
            keys = [key for key in club.__dict__.keys() if key not in omit]
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
            keys = [key for key in club.__dict__.keys() if key not in ['cmp']]
            changedclubs[k][1].sort()
            for (item, old, new) in changedclubs[k][1]:
                if item in keys:
                    if item.startswith('meeting'):
                        item = 'meeting'
                    outfile.write("<tr><td class='item'>%s</td><td class='old'>%s</td><td class='new'>%s</td></tr>\n" % (item, old.replace('\n','<br />'), new.replace('\n', '<br />')))
            outfile.write("</tbody></table>\n")
        

