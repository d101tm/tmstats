#!/usr/bin/env python
import dbconn, tmparms, os, sys
from datetime import date, datetime
import argparse
from tmutil import showclubswithvalues

class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname, asof, delta, division, area):
        self.area = '%s%s' % (division, area)
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.asof = asof
        self.delta = delta
        self.stretch = (self.delta >= 7)

    def tablepart(self):
        return ('    <td>%s</td><td>%s</td><td>%d</td>' % (self.area, self.clubname, self.delta))

    def key(self):
        return (self.area, self.clubnumber)



# Make it easy to run under TextMate
if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))

reload(sys).setdefaultencoding('utf8')

# Handle parameters
parms = tmparms.tmparms()
parms.parser.add_argument("--fromend", dest='fromend', type=int, default=7)
parms.parser.add_argument("--toend", dest='toend', type=int, default=9)
parms.parser.add_argument("--outfile", dest='outfile', type=argparse.FileType('w'), default='smedley.html')

parms.parse()

conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
curs = conn.cursor()

today = datetime.now()
# If we're in the next year, make "today" last year.
if today.month < parms.fromend:
    try:
        today = today.replace(year=today.year-1)
    except ValueError:  # Today must be Leap Day!
        today = today.replace(year=today.year-1, day=28)
startmonth = '%d-%0.2d-01' % (today.year, parms.fromend)
endmonth = '%d-%0.2d-01' % (today.year, parms.toend)

outfile = parms.outfile

# If there's monthly data for the end date, use it; otherwise, use
#   today's data.

curs.execute("SELECT c.clubnumber, c.clubname, c.asof, (c.activemembers - c.membase) - (p.activemembers - p.membase) AS delta, c.division, c.area FROM clubperf c INNER JOIN (SELECT activemembers, membase, clubnumber FROM clubperf WHERE monthstart=%s AND entrytype = 'M') p ON p.clubnumber = c.clubnumber WHERE monthstart=%s AND entrytype = 'M'  HAVING delta >= 5 ORDER BY c.division, c.area" , (startmonth, endmonth))
if curs.rowcount:
    final = True
else:
    # No data returned; use today's data instead
    curs.execute("SELECT c.clubnumber, c.clubname, c.asof, (c.activemembers - c.membase) - (p.activemembers - p.membase) AS delta, c.division, c.area FROM clubperf c INNER JOIN (SELECT activemembers, membase, clubnumber FROM clubperf WHERE monthstart=%s AND entrytype = 'M')  p ON p.clubnumber = c.clubnumber WHERE entrytype = 'L'  HAVING delta >= 5 ORDER BY c.division, c.area;",  (startmonth,))
    final = False

status = "final" if final else "updated daily"

clubs = []
for c in curs.fetchall():
    clubs.append(myclub(*c))

stretchers = [c for c in clubs if c.stretch]
awards = [c for c in clubs if not c.stretch]

outfile.write("""<h3 id="smedley">Smedley Stretch and Smedley Award</h3>
<p>
Clubs adding 5 or more new, reinstated, or dual members between August 1 and September 30 receive the <q>Smedley Award</q> from Toastmasters International.  Clubs which add 7 or more new, reinstated, or dual members during that time also complete the <q>Smedley Stretch</q> and earn $50 in District Credit.  This report is %s.</p>
""" % status)

if len(stretchers) > 0:
    outfile.write("<h4>Smedley Stretchers</h4>\n")
    showclubswithvalues(stretchers, "Added", outfile)

if len(awards) > 0:
    outfile.write("<h4>Smedley Award Winners</h4>\n")
    showclubswithvalues(awards, "Added", outfile)
    

