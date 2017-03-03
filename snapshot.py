#!/usr/bin/env python
""" Creates a "DEC Snapshot" for the alignment process
    Uses "alignment.xlsx" and the latest available files in the data directory
    """

import xlsxwriter, csv, sys, os, codecs, cStringIO, re, sets
import dbconn, tmparms
from datetime import datetime
from simpleclub import Club
from tmutil import gotodatadir


def normalize(s):
    if s:
        return re.sub(r'[^a-z0-9]','',s.lower())
    else:
        return


# Set up
gotodatadir()    
reload(sys).setdefaultencoding('utf8')

# Handle parameters
parms = tmparms.tmparms()
parms.parser.add_argument("--date", dest='date', default=datetime.today().strftime('%Y-%m-%d'))
parms.add_argument('--infile', default='d101align.csv')
parms.add_argument('--outfile', default='d101migration.html')
parms.add_argument('--color', action='store_true')
parms.parse()
conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
curs = conn.cursor()

# Get club information from the database as of today
clubs = Club.getClubsOn(curs, date=parms.date)

# Now, add relevant club performance information.  If there are clubs in the 
# performance data which aren't in the master list from TMI, note it and add
# them anyway.

perffields = ['clubnumber', 'clubname', 'district', 'area', 'division', 'eligibility', 'color', 'membase', 'activemembers', 'goalsmet']

curs.execute("SELECT clubnumber, clubname, district, area, division, clubstatus as eligibility, color, membase, activemembers, goalsmet FROM clubperf WHERE entrytype = 'L' and district = %s", (parms.district,))

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

curs.execute("SELECT clubnumber, suspenddate FROM distperf WHERE entrytype = 'L' and district = %s", (parms.district,))
for (clubnum, suspenddate) in curs.fetchall():
    if clubnum in clubs:
        clubs[clubnum].addvalues(['suspended'],[suspenddate])
      
           
# And read in the alignment.  
reader = csv.DictReader(open(parms.infile, 'rbU'))
alignfields = ['newarea', 'newdivision', 'likelytoclose', 'meetingday', 'meetingtime', 'place', 'address', 'city',
        'state', 'zip']
for row in reader:
    newarea = row['newarea']
    row['newarea'] = newarea[1:]
    row['newdivision'] = newarea[0]
    try:
        club = clubs[Club.stringify(row['clubnumber'])]
    except KeyError:
        print 'Club %s (%s) is new.' % (row['clubname'], row['clubnumber'])
        continue
    alignvalues = [row[p] for p in alignfields]
    club.addvalues(alignvalues, alignfields)

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
    try:
        if c.eligibility != 'Suspended':
            newareas[new].append(c)
            if old != new:
                gonefrom[old].append(c)
            if c.newdivision not in divs:
                divs[c.newdivision] = {}
            divs[c.newdivision][new] = new
        else:
            gonefrom[old].append(c)
    except AttributeError:
        print 'no eligibility for', c.clubname

# Now, create the output file
hout = open(parms.outfile, 'w')
hout.write(""" <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Style-Type" content="text/css">
<title>District Realignment</title>
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
    if (div.strip()):
        hout.write('<h1 %s name="div%s">Division %s</h1>\n' % (h1class, div, div))
    else:
        hout.write('<h1 %s>Unassigned Clubs</h1>\n' % (h1class,))
    h1class = 'class="divh1"'  # Don't have a blank page first
    hout.write('  <table class="divtable">\n')
    hout.write('  <thead><tr>\n')
    if (div.strip()):
        hout.write('  <td class="divname" colspan="2">Division %s</td>\n' % div)
    else:
        hout.write('  <td class="divname" colspan="2">Unassigned Clubs</td>\n')
    hout.write('</tr></thead>\n')
    hout.write('    <tbody><!--begin areas-->\n')
    for a in areas:
        hout.write('  <tr><td>\n')
        hout.write('    <table class="areatable">\n')
        hout.write('      <colgroup span="2">\n')
        if a.strip():
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
