#!/usr/bin/python
import dbconn, tmparms, os, sys
from datetime import date, datetime
from tmutil import showclubswithoutvalues, cleandate, stringify


class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname, asof, goalsmet, division, area):
        self.area = '%s%s' % (division, area)
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.asof = asof
        self.goalsmet = goalsmet

    def tablepart(self):
        return ('    <td>%s</td><td>%s</td><td>%d</td>' % (self.area, self.clubname, self.goalsmet))

    def key(self):
        return (self.area, self.clubnumber)

if __name__ == "__main__":
 
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.parser.add_argument("--finaldate", dest='finaldate', type=str, default='4/15')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    
    # We want data from either the final date or the latest available, whichever is earlier
    curs.execute("SELECT MAX(asof) FROM clubperf")
    latest = stringify(curs.fetchone()[0])
    targetdate = min(latest, cleandate(parms.finaldate))
    final = (targetdate == parms.finaldate)
    
    # Open the output file
    outfile = sys.stdout
    
    # Get the qualifying clubs
    
    curs.execute("SELECT clubnumber, clubname, asof, goalsmet, division, area FROM clubperf where goalsmet >= 9 and asof = %s and memduesontimeapr >= 1 and (activemembers >= 20 or activemembers - membase >= 5)", (targetdate,))

    status = "final" if final else "updated daily"

    winners = []
    for c in curs.fetchall():
        winners.append(myclub(*c))


    outfile.write("""<h3 id="early">President's Club</h3>
    <p>
    Clubs achieving President's Distinguished status by April 15 join the President's Club.  This report is %s.</p>
    """ % status)

    if len(winners) > 0:
        showclubswithoutvalues(winners, outfile)
        print >> sys.stderr, "%d clubs have qualified" % len(winners)


    

