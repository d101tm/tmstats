#!/usr/bin/env python3
import tmparms, os, sys
from datetime import date, datetime
from tmutil import showclubswithoutvalues, cleandate, stringify, getClubBlock
import tmglobals
globals = tmglobals.tmglobals()

class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname):
        self.clubnumber = clubnumber
        self.clubname = clubname


if __name__ == "__main__":
 

    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.parser.add_argument("--finaldate", dest='finaldate', type=str, default='4/15')
    parms.parser.add_argument('--outfile', default='presidentsclub.txt')
    parms.parser.add_argument('--earning', default='$101 in District Credit')
    parms.parser.add_argument('--requiremembership', action='store_true', help='Specify to require that clubs meet membership goals to qualify.')

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    
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
    
    if parms.requiremembership:
    
        # See if WHQ has posted any President's Distinguished Clubs; if so,
        #   use their information.  If not, calculate on our own.

        curs.execute("SELECT clubnumber, clubname FROM clubperf WHERE clubdistinguishedstatus = 'P' AND asof = %s", (targetdate,))

        for c in curs.fetchall():
            winners.append(myclub(*c))

        if not winners:
            print('No President\'s Distinguished Clubs from WHQ.', file=sys.stderr)
            # Either WHQ hasn't posted or no one qualifies.  Use our calculation.
            curs.execute("SELECT c.clubnumber, c.clubname FROM clubperf c INNER JOIN distperf d ON c.clubnumber = d.clubnumber AND c.entrytype = 'L' AND d.entrytype = 'L' AND ((d.aprrenewals > 20) OR (d.aprrenewals - c.membase) >= 5) WHERE c.goalsmet >= 9")
            for c in curs.fetchall():
                winners.append(myclub(*c))

    else:
        # We only care about clubs with at least 9 goals.
        curs.execute("SELECT clubnumber, clubname FROM clubperf WHERE goalsmet >= 9 AND asof = %s", (targetdate,))
        for c in curs.fetchall():
            winners.append(myclub(*c))

    if len(winners) > 0:
        outfile.write('<p><b>Congratulations</b> to %s for earning %s!</p>' % (getClubBlock(winners), parms.earning))
        print("%d clubs have qualified" % len(winners), file=sys.stderr)
    outfile.close()


    

