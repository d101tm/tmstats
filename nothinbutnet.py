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
cssoutfile = open(sys.argv[2],'w')
cssoutfile.write("""
    table.nbntable { width: 60%; margin-bottom: 1.5em; border: 1px solid black; border-collapse: collapse; background-color: #004165; color: white;}
    table.nbntable td {border-width: 0px;}
    table.nbntable tr {border-width: 0px;}
    table.nbntable th {border-width: 0px;}
    tr.nbngold {background-color: #FFDE4A; color: black;}
    tr.nbnsilver {background-color: #EEEEEE; color: black;}
    tr.nbnbronze {background-color: #FFC25E; color: black;}
    .nbnclubname {text-align: left;}
    .nbngain {text-align:right;} 
    .nbnhead .nbndiv {width: 40%; background-color: #004165; color: white; text-align:center; font-size: 125%;}
    .nbnhead {background-color: #004165; color: white; }
    .nbnhead .nbnclubname {background-color: #004165; color: white; width: 30%}
    .nbnhead .nbngain {background-color: #004165; color: white; width: 30%}
""")
cssoutfile.close()

if len(sys.argv) > 3:
    resources = yaml.load(open(sys.argv[3],'r'))['files']
    parms = {}
else:
    parms = {'district':'04'}  

# First, get the current information about clubs and assign them to divisions
divisions = {}

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
            club.city = ''
            club.gain = int(club.activemembers) - int(club.membase)
            clubs[club.clubnumber] = club
            if club.division not in divisions:
                divisions[club.division] = []
            divisions[club.division].append(club)
    except IndexError:
        pass

    
csvfile.close()

# Now, proceed by division....
for d in sorted(divisions.keys()):
    if d.strip() == '0D':
        continue
    div = divisions[d]
    outfile.write('<table class="nbntable">\n')
    outfile.write('<thead>\n')
    outfile.write('<tr class="nbnhead"><th class="nbnclubname">Club</th><th class="nbndiv">Division %s</th><th class="nbngain">Gain</th></tr>\n' % (d))
    outfile.write('</thead>\n')
    outfile.write('<tbody>\n')
    gains = {}
    classes = ['nbngold', 'nbnsilver', 'nbnbronze']
    for c in div:
        if c.gain > 0:
            if c.gain not in gains:
                gains[c.gain] = [c]
            else:
                gains[c.gain].append(c)
    
    # Get the top 3 gains
    gainlist = sorted(gains.keys(), reverse=True)
    if len(gainlist) > 3:
        gainlist = gainlist[0:3]
    for gnum in xrange(len(gainlist)):
        g = gainlist[gnum]
        for i in xrange(len(gains[g])):
            c = gains[g][i]
            outfile.write('<tr class="%s"><td class="nbnclubname" colspan="2">%s</td><td class="nbngain">%d</td></tr>\n' % (classes[gnum], c.clubname, c.gain))
    outfile.write('</tbody>\n')
    outfile.write('</table>\n')

outfile.close()
