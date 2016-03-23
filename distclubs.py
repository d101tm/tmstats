#!/usr/bin/env python
""" Generate the "Distinguished Clubs" report based on the current club statistics. """

import csv, sys, yaml, urllib, re, os.path
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

        
def writeheader(outfile):    
	outfile.write('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
	   ''')
	outfile.write('<html>\n')
	outfile.write('<head>\n')
	outfile.write('<meta http-equiv="Content-Style-Type" content="text/css">\n')
	outfile.write('<title>Distinguished Club Report</title>\n')
	outfile.write('<style type="text/css">\n')
	outfile.write("""

	html {font-family: Arial, "Helvetica Neue", Helvetica, Tahoma, sans-serif;
	      font-size: 75%;}

	table {font-size: 12px; border-width: 1px; border-spacing: 0; border-collapse: collapse; border-style: solid;}
	td, th {border-color: black; border-width: 1px; border-style: solid; text-align: center; vertical-align: middle;
	    padding: 2px;}

	.name {text-align: left; font-weight: bold; width: 22%;}
        .division {text-align: left; font-weight: bold; width: 5%;}
        .area {text-align: left; font-weight: bold; width: 5%;}
	.edate {border-left: none; font-weight: bold; width: 8%}
	.belowmin {border-left: none; font-weight: bold; width: 8%;}
	.number {text-align: right; width: 5%;}
	.goals {border-left: none;}
	.wide {width: 30% !important;}

	.green {background-color: lightgreen; font-weight: bold;}
	.yellow {background-color: yellow;}
	.red {background-color: red;}
	.rightalign {text-align: right;}
	.sep {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}
	.greyback {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}

	.madeit {background-color: lightblue; font-weight: bold;}
	.statushead {border-right: none; }
	.status {border-right: none; padding: 1px;}
	.reverse {background-color: black; color: white;}
	.bold {font-weight: bold;}
	.italic {font-style: italic;}
	.areacell {border: none;}
	.areatable {margin-bottom: 18pt; width: 100%; page-break-inside: avoid; display: block;}
	.suspended {text-decoration: line-through; color: red;}

	.divtable {border: none; break-before: always !important; display: block; float: none; position: relative; page-break-inside: avoid; page-break-after: always !important;}

	.divtable tfoot th {border: none;}
	.footinfo {text-align: left;}
	.dob {background-color: #c0c0c0;}
	.grid {width: 2%;}

	.todol {margin-top: 0;}
	.todop {margin-bottom: 0; font-weight: bold;}
	.status {font-weight: bold; font-size: 110%;}

	.clubcounts {margin-top: 12pt;}
	.finale {border: none; break-after: always !important; display: block; float: none; position; relative; page-break-after: always !important; page-break-inside: avoid;}

	@media print { 
	    body {-webkit-print-color-adjust: exact !important;}
			td {padding: 1px !important;}}
	""")
        outfile.write('</style>\n')
        outfile.write('</head>\n')
        outfile.write('<body>\n')

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

# Now, get the club performance report and find the distinguished or better clubs

pclubs = []
sclubs = []
dclubs = []
perffile = opener(resources['current'], parms)
r = csv.reader(perffile, delimiter=',')
headers = [normalize(p) for p in r.next()]
clubcol = headers.index('clubnumber')
aprcol = headers.index('clubdistinguishedstatus')
only = ['clubdistinguishedstatus']

for row in r:
    try:
        row[clubcol] = Club.fixcn(row[clubcol])
    except IndexError:
        continue
    clubs[row[clubcol]].addinfo(row, headers, only)
    club = clubs[row[clubcol]]
    if club.clubdistinguishedstatus == 'D':
        dclubs.append(club)
    elif club.clubdistinguishedstatus == 'S':
        sclubs.append(club)
    elif club.clubdistinguishedstatus == 'P':
        pclubs.append(club)
    clubs[row[clubcol]] = club    
    


# Sort the clubs by division and area:
pclubs.sort(key=lambda c: c.division + c.area)
sclubs.sort(key=lambda c: c.division + c.area)
dclubs.sort(key=lambda c: c.division + c.area)

winners = [pclubs, sclubs, dclubs]
names = ['President\'s Distinguished Clubs', 'Select Distinguished Clubs',
         'Distinguished Clubs']

for (qualifiers, level) in zip(winners, names):
    outfile.write('<h4 id="%sclubs">%s for 2014-15</h4>\n' % (level[0],level))

    # And create the fragment
    outfile.write("""<table style="margin-left: auto; margin-right: auto; padding: 4px;">
      <tbody>
        <tr valign="top">
          <td><strong>Area</strong></td>
          <td><strong>Club</strong></td>
          <td><strong>&nbsp;</strong></td>
          <td><strong>Area</strong></td>
          <td><strong>Club</strong></td>
      </tr>
    """)
# But now we want to go down, not across...
    incol1 = (1 + len(qualifiers)) / 2# Number of items in the first column.  
    left = 0  # Start with the zero'th item
    for i in range(incol1):
		club = qualifiers[i]
		outfile.write('<tr>\n')
		outfile.write('  <td>%s%s</td><td>%s</td>\n' % (club.division, club.area, club.clubname))
		outfile.write('  <td>&nbsp;</td>\n')
		try:
			club = qualifiers[i+incol1]   # For the right column
		except IndexError:
			outfile.write('<td>&nbsp;</td><td>&nbsp;</td>\n')    # Close up the row neatly
			outfile.write('</tr>\n')
			break
		outfile.write('  <td>%s%s</td><td>%s</td>\n' % (club.division, club.area, club.clubname))
		outfile.write('</tr>\n')
		
    outfile.write("""  </tbody>
    </table>
    """)

outfile.close()

