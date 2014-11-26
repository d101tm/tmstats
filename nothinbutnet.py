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

if len(sys.argv) > 1:
    resources = yaml.load(open(sys.argv[1],'r'))['files']
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
    div = divisions[d]
    print '<table width="60%" cols="7* *">'
    print '<thead>'
    print '<tr><th colspan="2">Division %s</th></tr>' % d
    print '<tr><th>Club</td><td>Gain</th></tr>'
    print '</thead>'
    print '<tbody>'
    gains = {}
    for c in div:
        if c.gain not in gains:
            gains[c.gain] = [c]
        else:
            gains[c.gain].append(c)
    
    # Get the top 3 gains (>0, of course)
    gainlist = sorted(gains.keys(), reverse=True)
    if len(gainlist) > 3:
        gainlist = gainlist[0:3]
    for g in gainlist:
        for c in gains[g]:
            print '<tr><td>%s</td><td>%d</td></tr>' % (c.clubname, c.gain)
    print '</tbody>'
    
    

