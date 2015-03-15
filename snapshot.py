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

# Add the new information to the file...at the front
finalheaders = ['newdistrict', 'newdivision', 'newarea']
finalheaders.extend(allheaders)

# Swap order
areacol = finalheaders.index('area')
divisioncol = finalheaders.index('division')
finalheaders[areacol] = 'division'
finalheaders[divisioncol] = 'area'


outfile = open('alldata.csv', 'wb')
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
