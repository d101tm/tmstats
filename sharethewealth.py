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

print 'checking from %s to %s' % (parms.startdate, parms.enddate)
friendlyenddate = daybefore(parms.enddate)[5:].replace('-','/')
friendlystartdate = daybefore(parms.startdate)[5:].replace('-','/')

# Open both output files
divfile = open('sharethewealth.csv', 'wb')
divwriter = UnicodeWriter(divfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
clubfile = open('sharethewealthclubs.html', 'w')
clubfile.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Style-Type" content="text/css">
<title>Share The Wealth</title>
<style type="text/css">


        html {font-family: Arial, "Helvetica Neue", Helvetica, Tahoma, sans-serif;
              font-size: 75%;}
      
        table {width: 75%; font-size: 14px; border-width: 1px; border-spacing: 1px; border-collapse: collapse; border-style: solid;}
        td, th {border-color: black; border-width: 1px;  vertical-align: middle;
            padding: 2px; padding-right: 5px; padding-left: 5px; border-style: solid;}

        .name {text-align: left; font-weight: bold; width: 40%;}
        .number {text-align: right; width: 5%;}
        
        .bold {font-weight: bold;}
        .italic {font-style: italic;}
        .leader {background-color: aqua;}
        
        
        </style>
</head>
<body>
<h1>Share The Wealth Report</h1>
<p>Clubs receive $5 in District 4 Credit for every new member added May 20 - June 30.  The club or clubs in each division which adds the most new membes in the division will receive an additional $25 Credit; current leaders are highlighted in the table below.</p>
""")
divheaders = ['Division', 'New Members']
clubheaders = ['Division', 'Area', 'Club', 'Club Name', 'New Members on %s' % friendlystartdate, 'New Members on %s' % friendlyenddate, 'Members Added']
divwriter.writerow(divheaders)


# Get performance information from the database for the start date
clubs = {}
divisions = {}
curs.execute("SELECT clubnumber, clubname, newmembers FROM distperf WHERE asof=%s", (parms.startdate,))
for (clubnumber, clubname, newmembers) in curs.fetchall():
    clubs[clubnumber] = clubinfo(clubnumber, clubname)
    clubs[clubnumber].start = newmembers
    clubs[clubnumber].end = newmembers  # So any clubs which fall off end with a zero delta
    
# Write the table header for the club report
clubfile.write("""
<table>
   <thead>
     <tr>
""")
for h in clubheaders:
    style = ' style="text-align: left;"' if h=='Club Name' else ''
    clubfile.write("""
        <th%s>%s</th>
""" % (style, h))
clubfile.write("""
     </tr>
   </thead>
   <tbody>
""")
    
# Now, get information for the end data
clubsinorder = []
divmax = {}
curs.execute("SELECT clubnumber, clubname, area, division, newmembers FROM distperf WHERE asof=%s ORDER BY division, area, clubnumber", (parms.enddate,))
for (clubnumber, clubname, area, division, newmembers) in curs.fetchall():
    if clubnumber not in clubs:
        clubs[clubnumber] = clubinfo(clubnumber, clubname)
    clubsinorder.append(clubnumber)
    

    club = clubs[clubnumber]
    club.area = area
    club.division = division
    club.end = newmembers
    club.delta = club.end - club.start
    if club.delta > 0:
        if division not in divisions:
            divisions[division] = 0
            divmax[division] = 0
        if club.delta > divmax[division]:
            divmax[division] = club.delta
        divisions[division] += club.delta
        
divmax['0D'] = 999999 # Avoid special casing...
        
for clubnumber in clubsinorder:
    club = clubs[clubnumber]
    if club.delta > 0:
        clubfile.write('      <tr%s>\n' % (' class="leader"' if club.delta == divmax[club.division] else ''))
        clubfile.write('        <td class="number">%s</td>\n' % club.division)
        clubfile.write('        <td class="number">%s</td>\n' % club.area)
        clubfile.write('        <td class="number">%s</td>\n' % club.clubnumber)
        clubfile.write('        <td class="name%s">%s</td>\n' % (" bold italic" if club.delta == divmax[club.division] else "", club.clubname))
        clubfile.write('        <td class="number">%s</td>\n' % club.start)
        clubfile.write('        <td class="number">%s</td>\n' % club.end)
        clubfile.write('        <td class="number%s">%s</td>\n' % (" bold italic" if club.delta == divmax[club.division] else "", club.delta))
        clubfile.write('     </tr>\n')

                            
# Close out the club file
clubfile.write("""  </tbody>
</table>
</body>
</html>
""")

divs = sorted([d for d in divisions.keys() if not d.startswith('0')])
for d in divs:
    divwriter.writerow((d, '%d' % divisions[d]))
    
# @@HACK@@: The JA_Google Chart module chokes when the last line ends with a line end.  Let's remove it.

divfile.seek(-2, os.SEEK_END)
divfile.truncate()
        
clubfile.close()
divfile.close()
    
