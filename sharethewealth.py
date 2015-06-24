#!/usr/bin/python
""" Creates the "Share the Wealth" report """
 
import xlsxwriter, csv, sys, os, codecs, cStringIO, re
import dbconn, tmparms
from tmutil import cleandate, UnicodeWriter, daybefore

class clubinfo:
    def __init__(self, clubnumber, clubname):
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.start = 0
        self.end = 0
        self.delta = 0

        

# Make it easy to run under TextMate
if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
reload(sys).setdefaultencoding('utf8')

# Handle parameters
enddate = min('2015-07-01', cleandate('today'))
parms = tmparms.tmparms()
parms.parser.add_argument("--startdate", dest='startdate', default='2015-05-20')
parms.parser.add_argument("--enddate", dest='enddate', default=enddate)
parms.parse()
print 'Connecting to %s:%s as %s' % (parms.dbhost, parms.dbname, parms.dbuser)
conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
curs = conn.cursor()

parms.enddate = cleandate(parms.enddate)
parms.startdate = cleandate(parms.startdate)

print 'checking from %s to %s', (parms.startdate, parms.enddate)
friendlyenddate = daybefore(parms.enddate)[5:].replace('-','/')
friendlystartdate = daybefore(parms.startdate)[5:].replace('-','/')

# Open both output files
divfile = open('sharethewealth.csv', 'wb')
divwriter = UnicodeWriter(divfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
clubfile = open('sharethewealthclubs.csv', 'wb')
clubwriter = UnicodeWriter(clubfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
divheaders = ['Division', 'New Members']
clubheaders = ['Division', 'Club', 'Club Name', 'New Members on %s' % friendlystartdate, 'New Members on %s' % friendlyenddate, 'Members Added']
divwriter.writerow(divheaders)
clubwriter.writerow(clubheaders)

# Get performance information from the database for the start date
clubs = {}
divisions = {}
curs.execute("SELECT clubnumber, clubname, newmembers FROM distperf WHERE asof=%s", (parms.startdate,))
for (clubnumber, clubname, newmembers) in curs.fetchall():
    clubs[clubnumber] = clubinfo(clubnumber, clubname)
    clubs[clubnumber].start = newmembers
    clubs[clubnumber].end = newmembers  # So any clubs which fall off end with a zero delta
    
# Now, get information for the end data
curs.execute("SELECT clubnumber, clubname, area, division, newmembers FROM distperf WHERE asof=%s ORDER BY division, area, clubnumber", (parms.enddate,))
for (clubnumber, clubname, area, division, newmembers) in curs.fetchall():
    if clubnumber not in clubs:
        clubs[clubnumber] = clubinfo(clubnumber, clubname)
    

    club = clubs[clubnumber]
    club.area = area
    club.division = division
    club.end = newmembers
    club.delta = club.end - club.start
    if club.delta > 0:
        if division not in divisions:
            divisions[division] = 0
        divisions[division] += club.delta
        clubwriter.writerow(['%s' % x for x in (club.division, club.clubnumber, club.clubname, 
                            club.start, club.end, club.delta)])

divs = sorted([d for d in divisions.keys() if not d.startswith('0')])
for d in divs:
    divwriter.writerow((d, '%d' % divisions[d]))
    
# @@HACK@@: The JA_Google Chart module chokes when the last line ends with a line end.  Let's remove it.

divfile.seek(-2, os.SEEK_END)
divfile.truncate()
        
clubfile.close()
divfile.close()
    
