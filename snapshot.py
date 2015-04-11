#!/usr/bin/python
""" Creates a "DEC Snapshot" for the alignment process
    Uses "alignment.xlsx" and the latest available files in the data directory
    """

import xlsxwriter, csv, sys, os, glob, codecs, cStringIO, re
from club import Club

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

os.chdir('data')    # To the data directory!

# We need the latest version of all the statistics
latest = sorted(glob.glob('clubs.*.csv'))[-1].split('.')[1]

# Start with the club listing (which should, one hopes, include everything)
# But it doesn't.  

clubs = {}

csvfile = open('clubs.' + latest + '.csv', 'rbU')
r = csv.reader(csvfile, delimiter=',')
baseheaders = [normalize(p) for p in r.next()]
Club.setHeaders(baseheaders)
clubcol = baseheaders.index('clubnumber')
allheaders = baseheaders

for row in r:
    try:
        row = [unicode(x, 'UTF8') for x in row]
    except UnicodeDecodeError:
        row = [unicode(x, 'CP1252') for x in row]

    try:
        row[clubcol] = Club.fixcn(row[clubcol])
        clubnum = row[clubcol]
        if clubnum:
            club = Club(row)
            clubs[clubnum] = club
    except IndexError:
        pass

csvfile.close()
# OK, now we have the basics.  Now, add relevant performance information

csvfile = open('clubperf.' + latest + '.csv', 'rbU')
r = csv.reader(csvfile, delimiter=',')
headers = [normalize(p) for p in r.next()]
headers[headers.index('clubstatus')] = 'eligibility'  # Avoid name collision
ourheaders = ['eligibility', 'membase', 'activemembers', 'goalsmet']
allheaders.extend(ourheaders)
clubcol = headers.index('clubnumber')
for row in r:
    try:
        row = [unicode(x, 'UTF8') for x in row]
    except UnicodeDecodeError:
        row = [unicode(x, 'CP1252') for x in row]

    try:
        row[clubcol] = Club.fixcn(row[clubcol])
        clubnum = row[clubcol]
        if clubnum:
            if clubnum not in clubs:
                # We need to patch in information about this club
                newr = []
                for item in baseheaders:
                    try:
                        newr.append(row[headers.index(item)])
                    except ValueError:
                        newr.append('')
                clubs[clubnum] = Club(newr)
                clubs[clubnum].clubnumber = clubnum  # Inconsistency, thy name is WHQ
            # Add our info
            clubs[clubnum].addinfo(row, headers, ourheaders)
    except IndexError:
        pass

csvfile.close()

# And now get the suspend date if the club is suspended...
csvfile = open('areaperf.' + latest + '.csv', 'rbU')
r = csv.reader(csvfile, delimiter=',')
headers = [normalize(p) for p in r.next()]
headers[headers.index('charterdatesuspenddate')] = 'eventdate'
ourheaders = ['eventdate']
allheaders.extend(ourheaders)
clubcol = headers.index('club')
for row in r:
    try:
        row = [unicode(x, 'UTF8') for x in row]
    except UnicodeDecodeError:
        row = [unicode(x, 'CP1252') for x in row]

    try:
        row[clubcol] = Club.fixcn(row[clubcol])
        clubnum = row[clubcol]
        if clubnum:
            try:
                clubs[clubnum].addinfo(row, headers, ourheaders)
            except KeyError:
                print 'areaperf:', clubnum, ' not in clubs'
                print row
    except IndexError:
        pass

csvfile.close()

allheaders.append('color')
# Now, some cleanup
for c in clubs.values():
    try:
        c.setcolor()
    except:
        c.color = 'Red'
    el = c.clubstatus.lower()
    if el.startswith('none') or el.startswith('open'):
        c.clubstatus = 'Open'
    else:
        c.clubstatus = 'Restricted'


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
finalheaders.extend(allheaders)

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
