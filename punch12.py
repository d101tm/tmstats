#!/usr/bin/env python3
import tmparms, os, sys
from datetime import date, datetime
from tmutil import showclubswithvalues, showclubswithoutvalues
import argparse

import tmglobals
globals = tmglobals.tmglobals()

def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print(' '.join(args), file=file)
        
class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname, net, division, area):
        self.area = '%s%s' % (division, area)
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.net = net
        self.area = '%s%s' % (division, area)

    def tablepart(self):
        return ('    <td>%s</td><td>%s</td><td>%d</td>' % (self.area, self.clubname, self.net))
        
    def novaluepart(self):
        return ('    <td>%s</td><td>%s</td>' % (self.area, self.clubname))
        

    def key(self):
        return (self.area, self.clubnumber)




### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms

    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
    parms.parser.add_argument("--fromend", dest='fromend', type=int, default=12)
    parms.parser.add_argument("--toend", dest='toend', type=int, default=2)
    parms.parser.add_argument("--outfile", dest='outfile', type=argparse.FileType('w'), default='punch.html')
    parms.parser.add_argument("--needed", dest='needed', type=int, default=5)
    parms.parser.add_argument("--renewbase", dest='renewbase', type=int, default=2)
    parms.parser.add_argument("--renewbyend", dest='renewbyend', type=int, default=3)

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    

    today = datetime.now()
    endmonth = '%d-%0.2d-01' % (today.year, parms.toend)
    startmonth = '%d-%0.2d-01' % (today.year - (1 if parms.toend < parms.fromend else 0), parms.fromend)

    outfile = parms.outfile

    # If there's monthly data for the end date, use it; otherwise, use
    #   today's data.
    
    firstpart = 'SELECT c.clubnumber, c.clubname, c.activemembers - b.activemembers AS net, c.division, c.area FROM clubperf c INNER JOIN (select clubnumber, clubname, activemembers from clubperf where entrytype = "M" and monthstart="%s") b on b.clubnumber = c.clubnumber' % startmonth
    having = ' HAVING net >= %d' % parms.needed
    curs.execute(firstpart + ' WHERE entrytype = "M" AND monthstart = %s' + having, (endmonth,))
    if curs.rowcount:
        final = True
    else:
        # No data returned; use today's data instead
        curs.execute(firstpart + " WHERE entrytype = 'L'" + having)
        final = False

    status = "final" if final else "updated daily"

    clubs = []
    for c in curs.fetchall():
        clubs.append(myclub(*c))

    winners = [c for c in clubs if c.net >= 5 and c.clubnumber != 2571179]
    punch1 = {}
    for c in winners:
        punch1[c.clubnumber] = True

    outfile.write("""<h3 id="12punch">1-2 Punch Winners</h3>
<p>Clubs which add at least 5 new members in January and February qualify for Part 1 of the District 4 "1-2 Punch Award" and receive $25 in District Credit.  This report is %s.</p>""" % status)

    if len(winners) > 0:
        outfile.write("<h4>Punch 1 Winners</h4>\n")
        showclubswithvalues(winners, "Added", outfile)
    
  
    # Now, move on to Punch 2
    
        outfile.write("""<p>&nbsp;</p><p>Clubs qualifying for Part 1 which <b>also</b> renew (by April 1st) as many members as they had at the end of February qualify for Part 2 of the District 4 "1-2 Punch Award" and receive an additional $50 in District Credit.""")  
    
    renewbase = '%d-%0.2d-01' % (today.year - (1 if parms.renewbyend < parms.renewbase else 0), parms.renewbase)
    renewbyend = '%d-%0.2d-01' % (today.year, parms.renewbyend)
    
    # See if there's data available for the renewal base yet
    curs.execute('SELECT COUNT(*) FROM distperf WHERE entrytype="M" AND monthstart=%s', (renewbase,))
    avail = curs.fetchone()[0] > 0 
    if avail:
    
    
        firstpart = 'SELECT c.clubnumber, c.clubname, c.aprrenewals, c.division, c.area FROM distperf c INNER JOIN (select clubnumber, clubname, activemembers FROM clubperf WHERE entrytype = "M" AND monthstart="%s") b ON b.clubnumber = c.clubnumber WHERE c.aprrenewals >= b.activemembers AND c.aprrenewals > 0' % renewbase
        curs.execute(firstpart + ' AND entrytype="M" AND monthstart=%s', (renewbyend,))
        if curs.rowcount:
            final = True
        else:
            # Not at the end; get today's data
            curs.execute(firstpart + ' AND entrytype="L"') 
            final = False
        status = "final" if final else "updated daily"
    
        outfile.write("  This report is %s.</p>" % status)
    
        clubs = []
        for c in curs.fetchall():
            clubs.append(myclub(*c))
        
        # Monkeypatch the output routine
        myclub.tablepart = myclub.novaluepart
            
        winners = [c for c in clubs if c.clubnumber in punch1]
        if len(winners) > 0:
            outfile.write("<h4>Punch 2 Winners</h4>\n")
            showclubswithoutvalues(winners, outfile)
            
    else:
        outfile.write('</p>')
    
    outfile.write('\n')
    outfile.close()
