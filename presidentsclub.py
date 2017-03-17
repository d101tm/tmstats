#!/usr/bin/python
import dbconn, tmparms, os, sys
from datetime import date, datetime
from tmutil import showclubswithoutvalues, cleandate, stringify, getClubBlock


class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname):
        self.clubnumber = clubnumber
        self.clubname = clubname


if __name__ == "__main__":
 
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.parser.add_argument("--finaldate", dest='finaldate', type=str, default='4/15')
    parms.parser.add_argument('--outfile', default='presidentsclub.txt')
    parms.parser.add_argument('--earning', default='$100 in District Credit')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    
    # We want data from either the final date or the latest available, whichever is earlier
    curs.execute("SELECT MAX(asof) FROM clubperf")
    latest = stringify(curs.fetchone()[0])
    parms.finaldate = cleandate(parms.finaldate)
    targetdate = min(latest, parms.finaldate)
    final = (targetdate == parms.finaldate)
    status = "final" if final else "updated daily"
    
    # Open the output file
    outfile = open(parms.outfile, 'w')

    winners = []
    
    # See if WHQ has posted any President's Distinguished Clubs; if so,
    #   use their information.  If not, calculate on our own.

    curs.execute("SELECT clubnumber, clubname FROM clubperf WHERE clubdistinguishedstatus = 'P' AND asof = %s", (targetdate,))

    for c in curs.fetchall():
        winners.append(myclub(*c))

    if not winners:
        print >> sys.stderr, 'No President\'s Distinguished Clubs from WHQ.'
        # Either WHQ hasn't posted or no one qualifies.  Use our calculation.
        curs.execute("SELECT c.clubnumber, c.clubname FROM clubperf c INNER JOIN distperf d ON c.clubnumber = d.clubnumber AND c.entrytype = 'L' AND d.entrytype = 'L' AND ((d.aprrenewals > 20) OR (d.aprrenewals - c.membase) >= 5) WHERE c.goalsmet >= 9")
        for c in curs.fetchall():
            winners.append(myclub(*c))


    if len(winners) > 0:
        outfile.write('<p><b>Congratulations</b> to %s for earning %s!</p>' % (getClubBlock(winners), parms.earning))
        print >> sys.stderr, "%d clubs have qualified" % len(winners)
    outfile.close()


    

