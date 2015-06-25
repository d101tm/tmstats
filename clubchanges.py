#!/usr/bin/python
from simpleclub import Club
import os, sys
from tmutil import cleandate




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
    
   
    # Get information for clubs as of the "from" date:
    oldclubs = Club.getClubsOn(fromdate, curs, setfields=True)
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
            
    # And create results
    outfile = open('clubchanges.html', 'w')
    
    
    if oldclubs or newclubs or changedclubs:
        outfile.write("<html>\n")
        outfile.write("""<head>
        <style type="text/css">


                html {font-family: Arial, "Helvetica Neue", Helvetica, Tahoma, sans-serif;
                      font-size: 75%;}
      
                table {width: 75%; font-size: 14px; border-width: 1px; border-spacing: 1px; border-collapse: collapse; border-style: solid;}
                td, th {border-color: black; border-width: 1px;  vertical-align: middle;
                    padding: 2px; padding-right: 5px; padding-left: 5px; border-style: solid;}

                .name {text-align: left; font-weight: bold; width: 40%;}
                .number {text-align: right; width: 5%;}
        
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
        for k in oldclubs:
            club = oldclubs[k]
            outfile.write("<tr><td>")
            outfile.write("</td><td>".join((club.division, club.area, club.clubnumber, club.clubname)))
            outfile.write("</td></tr>\n")
        outfile.write("</tbody></table>\n")
         
    if newclubs: 
        outfile.write("<h3>New clubs</h3>\n")
        for k in newclubs:
            club = newclubs[k]
            outfile.write("<h4>%s (%s), Area %s%s</h4>\n" % (club.clubname, club.clubnumber, club.division, club.area))
            outfile.write("<table><thead>\n<tr>")
            outfile.write("<th>Item</th><th>Value</th></tr></thead>\n")
            outfile.write("<tbody>\n")
            omit = ['clubname', 'clubnumber', 'division', 'area', 'cmp']
            for item in club.__dict__:
                if item not in omit and club.__dict__[item]:
                    outfile.write("<tr><td>%s</td><td>%s</td></tr>\n" % (item, club.__dict__[item].replace('\n', '<br />')))
            outfile.write("</tbody></table>\n")
              

        
    if changedclubs:
        outfile.write("<h3>Changed clubs</h3>\n")
        for k in changedclubs:
            club = allclubs[k]
            outfile.write("<h4>%s (%s), Area %s%s</h4>\n" % (club.clubname, club.clubnumber, club.division, club.area))
            outfile.write("<table><thead>\n<tr>")
            outfile.write("<th>Item</th><th>Old</th><th>New</th></tr></thead>\n")
            outfile.write("<tbody>\n")
            for (item, old, new) in changedclubs[k][1]:
                outfile.write("<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (item, old.replace('\n','<br />'), new.replace('\n', '<br />')))
            outfile.write("</tbody></table>\n")
        

