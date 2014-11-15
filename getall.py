#!/usr/bin/python

import re, urllib, csv

resources = {'clubs': "http://reports.toastmasters.org/findaclub/csvResults.cfm?District=%(district)s",
     'current': "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=clubperformance~%(district)s",
     'historical': "http://dashboards.toastmasters.org/%(tmyear)s/export.aspx?type=CSV&report=clubperformance~%(district)s~~~%(tmyear)s"}
     
parms = {'district': "04", 'tmyear' : "2013-2014"}

cities =   {'Aptos':'Santa Cruz',
            'Santa Cruz':'Santa Cruz',
            'Scotts Valley':'Santa Cruz',
            'Watsonville':'Santa Cruz',
            'Campbell':'Santa Clara',
            'Cupertino':'Santa Clara',
            'Los Gatos':'Santa Clara',
            'Milpitas':'Santa Clara',
            'Moffett Field':'Santa Clara',
            'Morgan Hill':'Santa Clara',
            'Mountain View':'Santa Clara',
            'Palo Alto':'Santa Clara',
            'San Jose':'Santa Clara',
            'Santa Clara':'Santa Clara',
            'Saratoga':'Santa Clara',
            'Stanford':'Santa Clara',
            'Sunnyvale':'Santa Clara',
            'Belmont':'San Mateo',
            'Brisbane':'San Mateo',
            'Burlingame':'San Mateo',
            'Daly City':'San Mateo',
            'Foster City':'San Mateo',
            'Menlo Park':'San Mateo',
            'Millbrae':'San Mateo',
            'Pacifica':'San Mateo',
            'Redwood City':'San Mateo',
            'Redwood Shores':'San Mateo',
            'San Bruno':'San Mateo',
            'San Carlos':'San Mateo',
            'San Mateo':'San Mateo',
            'South San Francisco':'San Mateo',
            'San Francisco':'San Francisco',
            'Carmel':'Monterey',
            'Monterey':'Monterey',
            'Salinas':'Monterey',
            'Sand City':'Monterey',
            'Seaside':'Monterey',
            'Soledad':'Monterey'}
            
            


def normalize(s):
    if s:
        return re.sub('\W\W*', '', s).strip().lower()
    else:
        return ''
        
def fixcn(s):
    try:
        return('%d' % int(s))
    except:
        return None
        
clubs = {}
class Club:
    
    @classmethod
    def setHeaders(self, headers):
        self.headers = headers
            
    def __init__(self, row):
        for i in range(len(self.headers)):
            h = self.headers[i]
            try:
                self.__dict__[h] = row[i]
            except IndexError:
                self.__dict__[h] = ''
        self.clubnumber = fixcn(self.clubnumber)
 
            
    def __repr__(self):
        return self.clubnumber + ' ' + self.clubname
        
    def addinfo(self, row, headers, only=None):
        """Add information to a club.  If 'only' is specified, only those columns are kept."""
        for i in range(len(headers)):
            h = headers[i]
            if not only or h in only:
                try:
                    self.__dict__[h] = row[i]
                except IndexError:
                    self.__dict__[h] = ''
            
    def setcolor(self):
        members = int(self.activemembers)
        if members <= 12:
            self.color = "Red"
        elif members < 20:
            self.color = "Yellow"
        else:
            self.color = "Green"
            
    def setcounty(self):
        try:
            self.county = cities[self.city.strip()]
        except KeyError:
            self.county = "Unknown"

import urllib, csv

# First, get the current information about clubs

csvfile = urllib.urlopen(resources['clubs'] % parms)
r = csv.reader(csvfile, delimiter=',')
headers = [normalize(p) for p in r.next()]
Club.setHeaders(headers)

clubcol = headers.index('clubnumber')    
for row in r:
    if len(row) > clubcol and fixcn(row[clubcol]):
        club = Club(row)
        clubs[club.clubnumber] = club
    
csvfile.close()
        
# Now, add information from the current performance data

csvfile = urllib.urlopen(resources['current'] % parms)
r = csv.reader(csvfile, delimiter=',')
headers = [normalize(p) for p in r.next()]
headers[headers.index('clubstatus')] = 'status'
clubcol = headers.index('clubnumber')
only = ['membase', 'activemembers', 'goalsmet', 'status']
for row in r:
    try:
        row[clubcol] = fixcn(row[clubcol])
        if row[clubcol]:
            try:
                clubs[row[clubcol]].addinfo(row, headers, only)
            except KeyError:
                pass
            except IndexError:
                print row
    except IndexError:
        pass
        
csvfile.close()
    
# And now, add information from historical performance data

csvfile = urllib.urlopen(resources['historical'] % parms)
r = csv.reader(csvfile, delimiter=',')
headers = [normalize(p) for p in r.next()]
headers[headers.index('goalsmet')] = 'hgoalsmet'
headers[headers.index('clubdistinguishedstatus')] ='hdcp'
clubcol = headers.index('clubnumber')
only = ['hgoalsmet', 'hdcp']
for row in r:
    try:
        row[clubcol] = fixcn(row[clubcol])
        if row[clubcol]:
            try:
                clubs[row[clubcol]].addinfo(row, headers, only)
            except KeyError:
                pass
            except IndexError:
                print row
    except IndexError:
        pass
        
csvfile.close()



# Finally, set the county and set the club's color based on membership
for c in clubs.values():
    c.setcolor()
    c.setcounty()

# For tonight, let's just create a CSV because we know how to do so

outfile = open('output.csv', 'wb')
w = csv.writer(outfile, delimiter=',')
fields = ['Club Number', 'Club Name', 'Status', 'Color', 'Charter Date', 'Address 1', 'Address 2', 'City', 'County', 'State', 'Zip', 'Meeting Time', 'Meeting Day', 'Club Status', 'Advanced?', 'Mem Base', 'Active Members', 'Goals Met', 'H Goals Met', 'HDCP']
members = [normalize(f) for f in fields]
w.writerow(fields)
for c in sorted(clubs.keys(), key=int):
    print clubs[c]
    w.writerow([clubs[c].__dict__.get(m,'') for m in members])
outfile.close()



    


