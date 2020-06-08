#!/usr/bin/env python3
import os
import tmglobals
import tmparms
from tmutil import getClubBlock, cleandate


class myclub:
    

    """ Just enough club info to sort the list nicely """

    def __init__(self, c):
        (self.clubnumber, self.clubname, self.delta)  = c




# Establish parameters
parms = tmparms.tmparms()
parms.parser.add_argument("--enddate", dest='enddate', type=str, default='6/30')
parms.parser.add_argument("--startdate", dest="startdate", type=str, default="M5")
parms.parser.add_argument("--outfileprefix", dest='outfileprefix', type=str, default='revup')
parms.parser.add_argument("--required", dest="required", type=int, default=3)

# Set up global environment
myglobals = tmglobals.tmglobals(parms)

conn = myglobals.conn
curs = myglobals.curs
today = myglobals.today
enddate = cleandate(parms.enddate, usetmyear=True)


qparms = []
qpart1 = "SELECT clubperf.clubnumber, clubperf.clubname, clubperf.activemembers - old.activemembers AS delta FROM clubperf INNER JOIN "
qpart2 = "(SELECT clubnumber, clubname, activemembers FROM clubperf WHERE "

if parms.startdate.startswith('M'):
    qpart2 += "entrytype = 'M' AND district = %s AND monthstart = %s"
    qparms += [parms.district, f"{today.year}-{('0'+parms.startdate[1:])[-2:]}-01"]
else:
    qpart2 += "entrytype = 'L' AND district = %s"
    qparms += [parms.district]

qpart2 += ") old ON old.clubnumber = clubperf.clubnumber WHERE "

qpart3a = " district = %s AND asof = %s "
qparmsa = qparms + [parms.district, enddate]
qpart3b = " district = %s AND entrytype = 'L'"
qparmsb = qparms + [parms.district]

qpart4 = f" HAVING delta >= {parms.required}"


# Try for final results:
curs.execute(qpart1 + qpart2 + qpart3a + qpart4, qparmsa)
if curs.rowcount:
    final = True
else:
    # Not to final date yet, so get today's results
    curs.execute(qpart1 + qpart2 + qpart3b + qpart4, qparmsb)
    final = False

winners = [myclub(c) for c in curs.fetchall()]

# Write the text block version

outfile = open(os.path.join(parms.workdir, parms.outfileprefix + '.text'), 'w')
if len(winners) > 0:
    outfile.write(f"<b>Congratulations to</b> {getClubBlock(winners)}.\n")
outfile.close()

