#!/usr/bin/env python3
""" Utility functions for the TMSTATS suite """
from datetime import date, timedelta, datetime
from six import StringIO
import csv, codecs
import os
import numbers
import tmglobals
globals = tmglobals.tmglobals()

def gotodatadir():
    """ Go to the 'data' directory if we're not already there """
    curdir = os.path.realpath(os.curdir)  # Get the canonical directory
    lastpart = curdir.split(os.sep)[-1]
    if lastpart.lower() != 'data':
        os.chdir('data')   # Fails if there is no data directory; that is intentional.

import math
 
def distance_on_unit_sphere(lat1, long1, lat2, long2):
 
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
         
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
     
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    try:
        arc = math.acos( cos )
    except ValueError:
        arc = 0.0
 
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 3956  # to get miles


def neaten(date):
    return date.strftime(' %m/%d').replace(' 0','').replace('/0','/').strip()

def dateAsWords(date):
    return date.strftime('%B %d').replace(' 0', ' ')

def cleandate(indate, usetmyear=True):
    if '/' in indate:
        indate = indate.split('/')
        if len(indate) == 2:
            # We need to add the year
            if usetmyear:
                if int(indate[0])>= 7:
                    indate.append('%d' % globals.tmyear)
                else:
                    indate.append('%d' % (globals.tmyear+1))
            else:
                indate.append('%d' % globals.today.year)
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

def getMonthEnd(month, year=date.today().year):
    if month == 12:
        return date(year, month, 31)
    else:
        return date(year, month+1, 1) - timedelta(days=1)


def getTMYearFromDB(curs):
    curs.execute("SELECT MAX(tmyear) FROM lastfor")
    return curs.fetchone()[0]

def getMonthStart(month, curs, tmyear=None):
    if not tmyear:
        tmyear = getTMYearFromDB(curs)
    if month <= 6:
        tmyear += 1
    return '%d-%0.2d-01' % (tmyear, month)

def isMonthFinal(month, curs, table='clubperf'):
    monthstart = getMonthStart(month, curs)
    curs.execute('SELECT COUNT(*) FROM %s WHERE monthstart = "%s" AND entrytype = "M"' % (table, monthstart))
    return 0 != curs.fetchone()[0]

def haveDataFor(date, curs, table='clubperf'):
    curs.execute('SELECT COUNT(*) FROM %s WHERE asof = "%s"' % (table, date))
    return 0 != curs.fetchone()[0]


def numToString(x):
    try:
        return '%s' % int(x)
    except ValueError:
        return ''


def stringify(value):
    """ Convert values to strings """
    # Let's normalize everything to strings/unicode strings
    if isinstance(value, (int, float, bool)):
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
        self.queue = StringIO.StringIO()
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


def overrideClubs(clubs, newAlignment, exclusive=True):
    """ Updates 'clubs' to reflect the alignment in the newAlignment spreadsheet.
        Typically used at a TM year boundary or for planning realignment.
    
        newAlignment is a "test alignment" file - a CSV with the clubs in the new
        alignment.  Non-blank columns in the file override information from the database,
        with the following exceptions:
        
            "likelytoclose" is used during planning to identify clubs in danger.
            "clubname" does NOT override what comes from Toastmasters.
            "newarea" is of the form Xn (X is the Division; n is the area).
    
        Specify exclusive=False to keep clubs not included in the spreadsheet;
        otherwise, clubs not in the spreadsheet are discarded.
    """
    
    
    pfile = open(newAlignment, 'r')
    reader = csv.DictReader(pfile)
    keepers = set()
    # Sadly, the callers of this routine have different types of key.
    # We have to be resilient against this.
    if isinstance(list(clubs.keys())[0], int):
        fixup = lambda x:int(x)
    elif isinstance(list(clubs.keys())[0], (int, float)):
        fixup = lambda x:float(x)
    else:
        fixup = lambda x:x
    for row in reader:
        clubnum = fixup(row['clubnumber'])
        try:
            club = clubs[clubnum]
        except KeyError:
            from simpleclub import Club
            club = Club(list(row.values()), fieldnames=list(row.keys()), fillall=True)
            if 'district' not in list(row.keys()):
                club.district = globals.parms.district
            clubs[clubnum] = club
        keepers.add(clubnum)
        if row['newarea'] and row['newarea'] != '0D0A':
            club.division = row['newarea'][0]
            club.area = row['newarea'][1:]
        for item in reader.fieldnames:
            if row[item].strip() and item not in ['clubnumber', 'clubname', 'newarea']:
                # Maintain the same type
                if item in club.__dict__ and isinstance(club.__dict__[item], numbers.Number):
                    if isinstance(club.__dict__[item], int):
                        club.__dict__[item] = int(row[item])
                    elif isinstance(club.__dict__[item], float):
                        club.__dict__[item] = float(row[item])
                    else:
                        club.__dict__[item] = int(row[item])
                else:
                    club.__dict__[item] = row[item]

    pfile.close()
    # Remove clubs not in the file:
    if exclusive:
        clubnumbers = list(clubs.keys())
        for c in clubnumbers:
            if c not in keepers:
                del clubs[c]
   

    return clubs

def removeSuspendedClubs(clubs, curs, date=None):
    """ Removes suspended clubs from the clubs array.
        If date=None, removes currently suspended clubs; otherwise, removes clubs which were
        suspended as of that date.
        Uses the 'distperf' table for the suspension information. """
    if date:
        curs.execute("SELECT clubnumber FROM distperf WHERE suspenddate != '' AND asof = (select min(d) FROM (SELECT %s AS d UNION ALL SELECT MAX(asof) FROM distperf) q)", (date,))
    else:
        tmyear = getTMYearFromDB(curs)
        curs.execute("SELECT distperf_id FROM lastfor WHERE tmyear = %s", (tmyear,))
        idlist = ','.join(['%d' % ans[0] for ans in curs.fetchall()])
        curs.execute("SELECT clubnumber FROM distperf WHERE id IN (" + idlist + ") AND suspenddate != ''")

    for ans in curs.fetchall():
        clubnum = numToString(ans[0])
        if clubnum in clubs:
            del clubs[clubnum]
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
    <th class="DSShidden">&nbsp;
    <th class="DSShidden">Area</th><th class="DSShidden">Club</th><th class="DSShidden">%s</th>""" % valuename)
    outfile.write("""
  </tr>
  </thead>
  <tbody>
""")

    incol1 = (1 + len(clubs)) // 2 # Number of items in the first column.
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
    <th class="DSShidden">&nbsp;
    <th class="DSShidden">Area</th><th class="DSShidden">Club</th>""")
    outfile.write("""
  </tr>
  </thead>
  <tbody>
""")

    incol1 = (1 + len(clubs)) // 2 # Number of items in the first column.
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

def getClubBlock(clubs):
    """ Returns a text string representing the clubs.  Each club's name is
        enclosed in a span of class 'clubname'. """
    res = ['<span class="clubname">%s</span>' % club.clubname for club in sorted(clubs, key=lambda club: club.clubname.lower())]
    if len(clubs) > 1:
        res[-1] = 'and ' + res[-1]
    if len(clubs) != 2:
        return ', '.join(res)
    else:
        return ' '.join(res)

def parseWPConfig(f):
    """ Parses a WordPress configuration file 
        Stolen from http://stackoverflow.com/questions/16881577/parse-php-file-variables-from-python-script """
    
    import re
    define_pattern = re.compile(r"""\bdefine\(\s*('|")(.*)\1\s*,\s*('|")(.*)\3\)\s*;""")
    assign_pattern = re.compile(r"""(^|;)\s*\$([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)\s*=\s*('|")(.*)\3\s*;""")


    php_vars = {}
    for line in f:
        for match in define_pattern.finditer(line):
            php_vars[match.group(2)]=match.group(4)
        for match in assign_pattern.finditer(line):
            php_vars[match.group(2)]=match.group(4)
    return php_vars

