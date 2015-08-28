#!/usr/bin/python
""" Utility functions for the TMSTATS suite """
from datetime import date, timedelta, datetime
import csv, cStringIO, codecs
import xlrd


def cleandate(indate):
    if '/' in indate:
        indate = indate + '/' + date.today().strftime("%Y")  # Default to this year
        indate = indate.split('/')
        indate = [indate[2], indate[0], indate[1]]
    elif '-' in indate:
        indate = indate.split('-')
    elif 'today'.startswith(indate.lower()):
        return date.today().strftime('%Y-%m-%d')
    elif 'yesterday'.startswith(indate.lower()):
        return (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    try:
        return (date.today() - timedelta(int(indate))).strftime('%Y-%m-%d')
    except ValueError:
        pass
    except TypeError:
        pass
    if len(indate[0]) == 2:
        indate[0] = "20" + indate[0]
    if len(indate[1]) == 1:
        indate[1] = "0" + indate[1]
    if len(indate[2]) == 1:
        indate[2] = "0" + indate[2]
    return '-'.join(indate)
    

def numToString(x):
    try:
        return '%s' % int(x)
    except ValueError:
        return ''
    

def stringify(value):
    """ Convert values to strings """
    # Let's normalize everything to strings/unicode strings
    if isinstance(value, (int, long, float, bool)):
        value = '%s' % value
    if isinstance(value, bool):
        value = '1' if value else '0'
    elif isinstance(value, (datetime, date)):
        value = ('%s' % value)[0:10]

    return value

        
def daybefore(indate):
    """ Toastmasters data is for the day BEFORE the file was created. """
    return (datetime.strptime(cleandate(indate), '%Y-%m-%d') - timedelta(1)).strftime('%Y-%m-%d') 
    
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
            

def overrideClubs(clubs, newAlignment):
    """ Updates 'clubs' to reflect the alignment in the newAlignment spreadsheet.
        Typically used at a TM year boundary. """
    book = xlrd.open_workbook(newAlignment)
    

    # Start with the Alignment sheet
    align = book.sheet_by_name('Alignment')
    # The spreadsheet is more human-readable than computer-friendly;
    #   in particular, there are no real headings, so we go by column number.
    clubcol = 5  # ('F')
    namecol = 6
    distcol = 7
    areacol = 8
    divcol = 9
    
    # Walk down looking for a valid club number
    rownum = 0

    while rownum < align.nrows:
        values = align.row_values(rownum)
        clubnum = numToString(values[clubcol])
        if clubnum in clubs:
            club = clubs[clubnum]
            was = 'District %s, Area %s%s' % (club.district, club.division, club.area)
            if values[areacol]:
                club.area = numToString(values[areacol])
            if values[divcol]:
                club.division = values[divcol]
            if values[distcol]:
                clubs.district = numToString(values[distcol])
            now = 'District %s, Area %s%s' % (club.district, club.division, club.area)
            if (was != now):
                #print 'Change: %s (%s) from %s to %s' % (club.clubname, club.clubnumber, was, now)
                pass
        rownum += 1
        
    # Now, handle the suspended club list
    # Find the first sheet which starts with 'Suspended' 
    names = book.sheet_names()
    sheetnum = 0
    while not names[sheetnum].startswith('Suspended'):
        sheetnum += 1
        
    if sheetnum <= len(names):
        susp = book.sheet_by_index(sheetnum)
        rownum = 0
        while rownum < susp.nrows:
            values = susp.row_values(rownum)
            clubnum = numToString(values[clubcol])
            if clubnum in clubs:
                #print 'Suspended: %s (%s)' % (clubs[clubnum].clubname, clubs[clubnum].clubnumber)
                del clubs[clubnum]
            rownum += 1
            
    return clubs
    
def showclubswithvalues(clubs, valuename, outfile):
    """ Outputs clubs in a 2-column table. """
    
    outfile.write("""<table class="DSSctable">
  <thead>
  <tr>
    <th>Area</th><th>Club</th><th>%s</th>""" % valuename)
    if len(clubs) > 1:
        outfile.write("""
    <th>&nbsp;
    <th>Area</th><th>Club</th><th>%s</th>""" % valuename)
    else:
        outfile.write("""
    <th style="visibility: hidden">&nbsp;
    <th style="visibility: hidden">Area</th><th style="visibility: hidden">Club</th><th style="visibility: hidden">%s</th>""" % valuename)
    outfile.write("""
  </tr>
  </thead>
  <tbody>
""")

    incol1 = (1 + len(clubs)) / 2 # Number of items in the first column.
    left = 0  # Start with the zero'th item
    for i in range(incol1):
        club = clubs[i]
        outfile.write('  <tr>\n')
        outfile.write(club.tablepart())
        try:
            club = clubs[i+incol1]   # For the right column
        except IndexError:
            outfile.write('\n  </tr>\n')
            break
        outfile.write('\n    <td>&nbsp;</td>\n')    
        outfile.write(club.tablepart())
        outfile.write('\n  </tr>\n')
        
    outfile.write("""  </tbody>
</table>
""")

def showclubswithoutvalues(clubs, outfile):
    """ Outputs clubs in a 2-column table. """
    
    outfile.write("""<table class="DSSbtable">
  <thead>
  <tr>
    <th>Area</th><th>Club</th>""")
    if len(clubs) > 1:
        outfile.write("""
    <th>&nbsp;
    <th>Area</th><th>Club</th><th>""")
    else:
        outfile.write("""
    <th style="visibility: hidden">&nbsp;
    <th style="visibility: hidden">Area</th><th style="visibility: hidden">Club</th>""")
    outfile.write("""
  </tr>
  </thead>
  <tbody>
""")

    incol1 = (1 + len(clubs)) / 2 # Number of items in the first column.
    left = 0  # Start with the zero'th item
    for i in range(incol1):
        club = clubs[i]
        outfile.write('  <tr>\n')
        outfile.write(club.tablepart())
        try:
            club = clubs[i+incol1]   # For the right column
        except IndexError:
            outfile.write('\n  </tr>\n')
            break
        outfile.write('\n    <td>&nbsp;</td>\n')    
        outfile.write(club.tablepart())
        outfile.write('\n  </tr>\n')
        
    outfile.write("""  </tbody>
</table>
""")
