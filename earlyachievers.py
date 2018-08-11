#!/usr/bin/env python3
import dbconn, tmparms, os, sys
from datetime import date, datetime
from tmutil import showclubswithvalues, gotodatadir, getClubBlock, getTMYearFromDB
import argparse
import tmglobals

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




# Establish parameters
parms = tmparms.tmparms()
parms.parser.add_argument("--toend", dest='toend', type=int, default=10)
parms.parser.add_argument("--outfileprefix", dest='outfileprefix', type=str, default='earlyachievers')

# Set up global environment
globals = tmglobals.tmglobals(parms)

conn = globals.conn
curs = globals.curs
today = globals.today
endmonth = '%d-%0.2d-01' % (globals.tmyear, parms.toend)


# If there's monthly data for the end date, use it; otherwise, use
#   today's data.
curs.execute("SELECT clubnumber, clubname, asof, goalsmet, division, area FROM clubperf WHERE monthstart=%s AND entrytype = 'M'", (endmonth,))
if curs.rowcount:
    final = True
else:
    # No data returned; use today's data instead
    curs.execute("SELECT clubnumber, clubname, asof, goalsmet, division, area FROM clubperf WHERE entrytype = 'L' AND district = %s", (parms.district,))
    final = False

status = "final" if final else "updated daily"

clubs = []
for c in curs.fetchall():
    clubs.append(myclub(*c))

winners = [c for c in clubs if c.goalsmet >= 5]
almost = [c for c in clubs if c.goalsmet == 4]

# Write the HTML version
outfile = open(parms.outfileprefix + '.html', 'w')

outfile.write("""<h3 id="early">Early Achievers</h3>
<p>
Clubs achieving 5 or more Distinguished Club Program (DCP) goals by October 31 earn $100 in District Credit.  This report is %s.</p>
""" % status)

if len(winners) > 0:
    outfile.write("<h4>Early Achievers</h4>\n")
    showclubswithvalues(winners, "Goals", outfile)
    
if len(almost) > 0 and not final:
    outfile.write("<p>&nbsp;</p>")
    outfile.write("<p>These clubs have achieved 4 of the 5 DCP goals needed to join the Early Achievers.</p>")
    showclubswithvalues(almost, "Goals", outfile)

outfile.close()

# Write the text block version

outfile = open(parms.outfileprefix + '.text', 'w')
if len(winners) > 0:
    outfile.write("<b>Congratulations to our Early Achiver Club%s</b>:  " % ('s' if len(winners) > 1 else ''))
    outfile.write(getClubBlock(winners))
    outfile.write('.')
    outfile.write('\n')
outfile.close()   

