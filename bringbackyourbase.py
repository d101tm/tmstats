#!/usr/bin/env python3
import os
import tmglobals
import tmparms
from tmutil import getClubBlock, cleandate


class myclub:
    """ Just enough club info to sort the list nicely """

    def __init__(self, *c):
        (self.clubnumber, self.clubname, self.asof, self.membase, self.activemembers)  = c



    def tablepart(self):
        return ('    <td>%s</td><td>%s</td><td>%d</td>' % (self.area, self.clubname, self.goalsmet))

    def key(self):
        return (self.area, self.clubnumber)


# Establish parameters
parms = tmparms.tmparms()
parms.parser.add_argument("--enddate", dest='enddate', type=str, default='6/30')
parms.parser.add_argument("--outfileprefix", dest='outfileprefix', type=str, default='bringbackyourbase')
parms.parser.add_argument("--award", dest='award', type=str, default='$50 in Toastmasters International Gift Certificates')

# Set up global environment
myglobals = tmglobals.tmglobals(parms)

conn = myglobals.conn
curs = myglobals.curs
today = myglobals.today
enddate = cleandate(parms.enddate, usetmyear=True)

# If there's data for the end date, use it; otherwise, use
#   today's data.
qpart = "SELECT clubnumber, clubname, asof, membase, activemembers FROM clubperf WHERE "

curs.execute(
    qpart + "asof = %s",
    (enddate,))
if curs.rowcount:
    final = True
else:
    # No data returned; use today's data instead
    curs.execute(
        qpart + "entrytype = 'L' AND district = %s",
        (parms.district,))
    final = False

status = "final" if final else "updated daily"

clubs = []
for c in curs.fetchall():
    clubs.append(myclub(*c))

winners = [c for c in clubs if c.activemembers >= c.membase]


# Write the text block version

outfile = open(os.path.join(parms.workdir, parms.outfileprefix + '.text'), 'w')
if len(winners) > 0:
    outfile.write("<b>Congratulations to</b> ")
    outfile.write(getClubBlock(winners))
    outfile.write(f'for earning {parms.award}.')
    outfile.write('\n')
outfile.close()

