#!/usr/bin/python
""" Creates a "DEC Snapshot" for the alignment process
    Uses "alignment.xlsx" and the latest available files in the data directory
    """

import xlsxwriter, csv, sys, os, codecs, cStringIO, re
import dbconn, tmparms
from datetime import datetime
from simpleclub import Club

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def normalize(s):
    if s:
        return re.sub(r'[^a-z0-9]','',s.lower())
    else:
        return


 
import tmparms
# Make it easy to run under TextMate
if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
    
reload(sys).setdefaultencoding('utf8')

# Handle parameters
parms = tmparms.tmparms()
parms.parser.add_argument("--date", dest='date', default=datetime.today().strftime('%Y-%m-%d'))
parms.parse()
#print 'Connecting to %s:%s as %s' % (parms.dbhost, parms.dbname, parms.dbuser)
conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
curs = conn.cursor()

# Get club information from the database as of the date requested (or today)
clubs = Club.getClubsOn(curs)

# Now, add relevant club performance information.  If there are clubs in the 
# performance data which aren't in the master list from TMI, note it and add
# them anyway.

perffields = ['clubnumber', 'clubname', 'district', 'area', 'division', 'eligibility', 'color', 'membase', 'activemembers', 'goalsmet']

print parms.date
curs.execute("SELECT clubnumber, clubname, district, area, division, clubstatus as eligibility, color, membase, activemembers, goalsmet FROM clubperf WHERE asof = %s", (parms.date,))

for info in curs.fetchall():
    clubnum = Club.stringify(info[0])
    try:
        club = clubs[clubnum]
        club.addvalues(info, perffields)
    except KeyError:
        print 'Club %s (%d) not in CLUBS table, patching in.' % (info[1], info[0])
        clubs[clubnum] = Club(info, perffields)
        clubs[clubnum].charterdate = ''
        
# Now patch in suspension dates

curs.execute("SELECT clubnumber, suspdate FROM distperf WHERE asof = %s", (parms.date,))
for (clubnum, suspdate) in curs.fetchall():
    if clubnum in clubs:
        clubs[clubnum].addvalues(['suspended'],[suspdate])
      
           




# Now, onward to the alignment.  All we care about is the new area and new division, if any.
csvfile = open('alignment.csv', 'rbU')
r = csv.reader(csvfile)

# This is terrible, but I'm hard-coding the layout of the file.
clubcol = 4
cdatecol = 5
newdistcol = 7
newareacol = 8
newdivcol = 9

for row in r:
    clubnum = Club.fixcn(row[clubcol])
    try:
        c = clubs[clubnum]
        nd = row[newdistcol].strip()
        if nd:
            c.newdistrict = nd
        else:
            c.newdistrict = c.district
        ndiv = row[newdivcol].strip()
        if ndiv:
            c.newdivision = ndiv
        else:
            c.newdivision = c.division
        narea = row[newareacol].strip()
        if narea:
            c.newarea = narea
        else:
            c.newarea = c.area
    except KeyError:
        pass   # Don't care about lost clubs

csvfile.close()

# We're not done...now we need to add new clubs.
csvfile = open('newclubs.csv', 'rbU')
r = csv.reader(csvfile)

# This is terrible, but I'm hard-coding the layout of the file.
clubcol = 4
cdatecol = 3
newdistcol = 6
newareacol = 7
newdivcol = 8

for row in r:
    clubnum = Club.fixcn(row[clubcol])
    try:
        c = clubs[clubnum]
        nd = row[newdistcol].strip()
        if nd:
            c.newdistrict = nd
        else:
            c.newdistrict = c.district
        ndiv = row[newdivcol].strip()
        if ndiv:
            c.newdivision = ndiv
        else:
            c.newdivision = c.division
        narea = row[newareacol].strip()
        if narea:
            c.newarea = narea
        else:
            c.newarea = c.area
        ncd = row[cdatecol].strip()
        if ncd:
            c.charterdate = ncd
    except KeyError:
        pass   # Don't care about lost clubs

csvfile.close()



# Add the new information to the file...at the front
finalheaders = ['newdistrict', 'newdivision', 'newarea']
finalheaders.extend(Club.fieldnames)

# Swap order
areacol = finalheaders.index('area')
divisioncol = finalheaders.index('division')
finalheaders[areacol] = 'division'
finalheaders[divisioncol] = 'area'


outfile = open('snapshot.csv', 'wb')
w = UnicodeWriter(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
w.writerow(finalheaders)
def getkey(x):
    key = ''
    try:
        key += x.newdistrict
    except AttributeError:
        key += ' '
    try:
        key += x.newdivision
    except AttributeError:
        key += ' '
    try:
        key += x.newarea
    except AttributeError:
        key += ' '
    try:
        key += x.clubnumber.zfill(8)
    except AttributeError:
        key += '00000000'
    return key

for c in sorted(clubs.values(), key=lambda x:getkey(x)):
    row = []
    for it in finalheaders:
        try:
            row.append(c.__dict__[it])
        except KeyError:
            row.append('')
    row = ['%s' % x for x in row]
    w.writerow(row)

outfile.close()

# Assign clubs to their new areas.  If they've changed, also assign to the area they're leaving
gonefrom = {}
newareas = {}
divs = {}

for c in clubs.values():
    old = c.division + c.area
    try:
        new = c.newdivision + c.newarea
    except AttributeError:
        new = '  '
        c.newdivision = ' '
        c.newarea = ' '
    if old != new:
        c.was = '(from %s)' % old
    else:
        c.was = '&nbsp;'
    if old not in gonefrom:
        gonefrom[old] = []
    if new not in newareas:
        newareas[new] = []
    if c.eligibility != 'Suspended':
        newareas[new].append(c)
        if old != new:
            gonefrom[old].append(c)
        if c.newdivision not in divs:
            divs[c.newdivision] = {}
        divs[c.newdivision][new] = new
    else:
        gonefrom[old].append(c)

# Now, let's create an HTML file...because I love HTML files
hout = open('snapshot.html', 'w')
hout.write(""" <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Style-Type" content="text/css">
<title>District 4 Realignment</title>
<style type="text/css">


        html {font-family: Arial, "Helvetica Neue", Helvetica, Tahoma, sans-serif;
              font-size: 75%;}
      
        table {font-size: 12px; border-width: 1px; border-spacing: 0; border-collapse: collapse; border-style: solid;}
        td, th {border-color: black; border-width: 1px;  vertical-align: middle;
            padding: 2px;}

        .name {text-align: left; font-weight: bold; width: 40%;}
        .number {text-align: right; width: 5%;}
        .goals {border-left: none;}

        .green {background-color: lightgreen; font-weight: bold;}
        .yellow {background-color: yellow;}
        .red {background-color: red;}
        .rightalign {text-align: right;}
        .sep {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}
        .greyback {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}
        
        .bold {font-weight: bold;}
        .italic {font-style: italic;}
        .areacell {border: none;}
        .areatable {margin-bottom: 18pt; width: 100%; page-break-inside: avoid;}
        .suspended {text-decoration: line-through; color: red;}

        .divh1 {page-break-before: always !important;}
        .divtable {border: none; 
                   display: block; 
                   float: none; 
                   position: relative; 
                   page-break-inside: avoid;}


        
        .newhead {width: 60%; text-align: center; background-color: aliceblue; float: left;}
        .newalign {width: 60%; float: left;}
        .gonehead {width: 35%; float: right; text-align: center; background-color: aliceblue;}
        .leaving {width: 35%; float: right;}
        .movement {width: 9%; font-weight: bold;}
        .areaname {text-align: center; font-size: 125%; font-weight: bold;}
    
        @media print { 
            body {-webkit-print-color-adjust: exact !important;}
                        td {padding: 1px !important;}}
        </style>
</head>
<body>
""")


def writeNewAlignment(hout, newareas, a):
    hout.write('        <td class="newalign">\n')
    hout.write('          <table>\n')
    # New alignment goes here
    hout.write('            <thead>\n')
    hout.write('              <tr><td>Club</td><td>Club Name</td><td>Charter</td><td class="rightalign">Base</td><td class="rightalign">Current</td><td class="rightalign">Goals</td><td>Movement</td></tr>\n')
    hout.write('            </thead>\n')
    hout.write('            <tbody>\n')
    clubcount = 0
    basecount = 0
    membercount = 0
    for c in sorted(newareas[a], key=lambda x:int(x.clubnumber)):
        hout.write('              <tr>\n')
        hout.write('                <td class="number">%s</td>\n' % c.clubnumber)
        hout.write('                <td class="%s name">%s</td>\n' % (c.color.lower(), c.clubname))
        hout.write('                <td class="charter">%s</td>\n' % (c.charterdate))
        hout.write('                <td class="rightalign">%s</td>\n' % (c.membase))
        hout.write('                <td class="rightalign">%s</td>\n' % (c.activemembers))
        hout.write('                <td class="rightalign">%s</td>\n' % (c.goalsmet))
        hout.write('                <td class="movement">%s</td>\n' % (c.was))
        hout.write('              </tr>\n')
        clubcount += 1
        basecount += int(c.membase)
        membercount += int(c.activemembers)
    hout.write('            </tbody>\n')
    hout.write('            <tfoot>\n')
    hout.write('            <tr><td colspan="7">Area totals:  %d clubs with %d members (base: %d)</td></tr>\n' % (clubcount, basecount, membercount))
    hout.write('            </tfoot>\n')
    hout.write('          </table>\n')
    hout.write('        </td><!--end newalign-->\n')
    return (clubcount, basecount, membercount)

def writeGoneFrom(hout, gonefrom, a):
    if a in gonefrom and len(gonefrom[a]) > 0:
        hout.write('        <td class="leaving">\n')
        hout.write('          <table>\n')
        hout.write('            <thead>\n')
        hout.write('              <tr><td>Club</td><td>Club Name</td><td>Disposition</td></tr>\n')
        hout.write('            </thead>\n')
        hout.write('            <tbody>\n')
        for c in sorted(gonefrom[a], key=lambda x: int(x.clubnumber)):
            hout.write('               <tr><td class="number">%s</td><td class="%s">%s</td>' % (c.clubnumber, c.color.lower(), c.clubname))
            if c.eligibility == 'Suspended':
                hout.write('<td>Suspended</td>')
            else:
                hout.write('<td>To %s%s</td>' % (c.newdivision, c.newarea))
            hout.write('</tr>\n')
        hout.write('            </tbody>\n')
        hout.write('          </table>\n')
        hout.write('        </td><!--end leaving-->\n')

h1class=""
for div in sorted(divs.keys()):
    areas = sorted(divs[div].keys())
    clubcount = 0
    basecount = 0
    membercount = 0
    hout.write('<h1 %s name="div%s">Division %s</h1>\n' % (h1class, div, div))
    h1class = 'class="divh1"'  # Don't have a blank page first
    hout.write('  <table class="divtable">\n')
    hout.write('  <thead><tr><td class="divname" colspan="2">Division %s</td></tr></thead>\n' % div)
    hout.write('    <tbody><!--begin areas-->\n')
    for a in areas:
        hout.write('  <tr><td>\n')
        hout.write('    <table class="areatable">\n')
        hout.write('      <colgroup span="2">\n')
        hout.write('      <thead>\n')
        hout.write('        <tr><td class="areaname" colspan="2">Area %s</td></tr>\n' % a)
        hout.write('        <tr><td class="newhead">New Alignment</td><td class="gonehead">Clubs Leaving Area</td></tr>\n')
        hout.write('      </thead>\n')
        hout.write('      <tbody><!-- Area %s-->\n' % a)
        hout.write('        <tr>\n')
        (cc, bc, mc) = writeNewAlignment(hout, newareas, a)
        clubcount += cc
        basecount += bc
        membercount += mc
        writeGoneFrom(hout, gonefrom, a)
        hout.write('        </tr>\n')
        hout.write('      </tbody><!-- Area %s -->\n' % a)
        hout.write('    </table><!-- Areatable -->\n')
        hout.write('  </td></tr>\n')
    hout.write('    </tbody><!--end areas-->\n')
    hout.write('    <tfoot>\n')
    hout.write('    <tr><td colspan="2">Division Total: %d clubs with %d members (base: %d)</td></tr>\n' % (clubcount, membercount, basecount))
    hout.write('<!-- End division %s table -->' % div)
    hout.write('  </table>\n')

hout.write('</body>\n</html>')
hout.close()
