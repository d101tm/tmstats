#!/usr/bin/python
""" Generate the "Nothin' but Net" report based on the current club statistics. """
import csv, sys, yaml, urllib, re
from club import Club

def normalize(s):
    if s:
        return re.sub('\W\W*', '', s).strip().lower()
    else:
        return ''
    
def opener(what, parms):
    if what.startswith('http'):
        return urllib.urlopen(what % parms)
    else:
        return open(what, 'rbU')
        
clubs = {}
resources = {'clubs': "http://reports.toastmasters.org/findaclub/csvResults.cfm?District=%(district)s",
     'payments': "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=districtperformance~%(district)s~~~%(tmyear)s",
     'current': "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=clubperformance~%(district)s",
     'historical': "http://dashboards.toastmasters.org/%(lasttmyear)s/export.aspx?type=CSV&report=clubperformance~%(district)s~~~%(lasttmyear)s"}
     
outfile = open(sys.argv[1],'w')

if len(sys.argv) > 2:
    resources = yaml.load(open(sys.argv[2],'r'))['files']
    parms = {}
else:
    parms = {'district':'04'}  

# Get the clubs and assign them to divisions
csvfile = opener(resources['current'], parms)
r = csv.reader(csvfile, delimiter=',')
headers = [normalize(p) for p in r.next()]
Club.setHeaders(headers)



clubcol = headers.index('clubnumber')    
for row in r:
    try:
        row[clubcol] = Club.fixcn(row[clubcol])
        if row[clubcol]:
            club = Club(row)
            clubs[club.clubnumber] = club
    except IndexError:
        pass

    
csvfile.close()

# Now, get the April Renewal data from the district report and find any qualifiers
qualifiers = []
perffile = opener(resources['payments'], parms)
r = csv.reader(perffile, delimiter=',')
headers = [normalize(p) for p in r.next()]
clubcol = headers.index('club')
aprcol = headers.index('aprren')
only = ['aprren']

for row in r:
    try:
        row[clubcol] = Club.fixcn(row[clubcol])
    except IndexError:
        continue
    clubs[row[clubcol]].addinfo(row, headers, only)
    club = clubs[row[clubcol]]
    club.membase = float(club.membase)
    club.aprren = float(club.aprren)
    if club.membase > 0:
        club.pct = club.aprren / club.membase
        if club.pct >= 0.75:
           qualifiers.append(club)
    
# Sort the clubs by division and area:
qualifiers.sort(key=lambda c: c.division + c.area)

# And create the fragment
outfile.write("""<table style="margin-left: auto; margin-right: auto; padding: 4px;">
  <tbody>
    <tr valign="top">
      <td><strong>Area</strong></td>
      <td><strong>Club</strong></td>
      <td><strong>% of Base</strong></td>
      <td><strong>&nbsp;</strong></td>
      <td><strong>Area</strong></td>
      <td><strong>Club</strong></td>
      <td><strong>% of Base</strong></td>
  </tr>
""")
even = True
for club in qualifiers:
    if even:
        outfile.write('    <tr>')
        outfile.write('\n')
    else:
        outfile.write('      <td>&nbsp;</td>')
        outfile.write('\n')
    outfile.write('      <td>%s%s</td><td>%s</td><td>%.2f%%</td>' % (club.division, club.area, club.clubname, club.pct * 100))
    outfile.write('\n')
    if not even:
        outfile.write('    </tr>')
        outfile.write('\n')
    even = not even

if even:
    outfile.write('    </tr>\n')
outfile.write("""  </tbody>
</table>
""")

outfile.close()
