#!/usr/bin/python

import re, urllib, csv, xlsxwriter, codecs

resources = {'clubs': "http://reports.toastmasters.org/findaclub/csvResults.cfm?District=%(district)s",
     'current': "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=clubperformance~%(district)s",
     'historical': "http://dashboards.toastmasters.org/%(lasttmyear)s/export.aspx?type=CSV&report=clubperformance~%(district)s~~~%(lasttmyear)s"}
     
parms = {'district': "04", 'lasttmyear' : "2013-2014"}

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
            
class Geography:
    """ This class tracks information about a geographical area (city, county, or proposed division)"""
    all = {}
    @classmethod
    def find(self, name):
        nname = normalize(name)
        if nname not in self.all:
            self.all[nname] = Geography(name)
        return self.all[nname]
    
    def __init__(self, name):
        self.name = name
        self.parents = []
        self.clubcount = 0
        self.membercount = 0
        self.colors = {'R':0, 'Y':0, 'G':0}
        self.dcp = {'P':0, 'S':0, 'D':0, ' ':0}
        self.advanced = 0
        self.open = 0
        self.restricted = 0
        
    def assign(self, parent):
        if parent:
            self.parents.append(parent)
        
    def addclub(self, club):
        self.clubcount += 1
        self.membercount += int(club.activemembers)
        self.colors[club.color[0].upper()] += 1
        self.dcp[(club.dcplastyear + ' ')[0].upper()] += 1
        if club.advanced:
            self.advanced += 1
        if club.clubstatus.startswith('Open'):
            self.open += 1
        else:
            self.restricted += 1
        for p in self.parents:
            p.addclub(club)
     
    def __repr__(self):
        return '%s %d %s %s' % (self.name, self.clubcount, self.colors, self.dcp)
        
    def cleanup(self):
        # freeze the result of computations; make it easier to write the report
        self.dcpsum = self.dcp['P'] + self.dcp['S'] + self.dcp['D']
        self.nondistinguished = self.dcp[' ']
        self.red = self.colors['R']
        self.yellow = self.colors['Y']
        self.green = self.colors['G']
        

        


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
        self.citygeo = Geography.find(self.city)
        self.dcplastyear = ' '
 
            
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
            
    def addtogeo(self):
        self.citygeo.addclub(self)
        
    def cleanup(self):
        if self.clubstatus.strip() == 'Open to all':
            self.clubstatus = 'Open'
        else:
            self.clubstatus = 'Restricted'
            
    def get(self, name):
        return self.__dict__[name]
        

# Create the Geography for the whole district
d4 = Geography('d4')

class Option:
    """This holds the information about a geographical option.
       Specify the counties and cities in the North part; the others go to the South."""
    def __init__(self, name, northcounties, northcities):
        self.name = name
        self.northcounties = northcounties
        self.northcities = northcities
        self.north = Geography('North ' + name)
        self.south = Geography('South ' + name)
        for city in cities:
            county = cities[city]
            citygeo = Geography.find(city)
            cgeo = Geography.find(county + ' County')
            citygeo.assign(cgeo)
            citygeo.assign(d4)
            if county in northcounties:
                citygeo.assign(self.northgeo)
            elif city in northcities:
                citygeo.assign(self.northgeo)
            else:
                citygeo.assign(self.southgeo)
    
    def setcol(self, col):
        # Where we write our information
        self.col = col
        

# Create options for all splits:
northcounties = ['San Francisco', 'San Mateo']
northcitiestoadd = [[], ['Palo Alto', 'Stanford'], ['Mountain View'], ['Moffett Field']]
names = ['Split at County Line', 'include Palo Alto', 'include Mountain View', 'include Moffett Field']

options = []
northcities = []
for (c, n) in zip(northcitiestoadd, names):
    northcities.extend(c)
    options.append(Option(n, northcounties, northcities))
    

        

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
headers[headers.index('goalsmet')] = 'goalsmetlastyear'
headers[headers.index('clubdistinguishedstatus')] ='dcplastyear'
clubcol = headers.index('clubnumber')
only = ['goalsmetlastyear', 'dcplastyear']
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



# Finally, set the county, set the club's color based on membership, and add it to geographies:
for c in clubs.values():
    c.cleanup()  # Shorten items which are too long as received from Toastmasters
    c.setcolor()
    c.setcounty()
    c.addtogeo()



# For tonight, let's just create a CSV because we know how to do so

outfile = open('output.csv', 'wb')
w = csv.writer(outfile, delimiter=',')
fields = ['Club Number', 'Club Name', 'Status', 'Color', 'Charter Date', 'Address 1', 'Address 2', 'City', 'County', 'State', 'Zip', 'Meeting Time', 'Meeting Day', 'Club Status', 'Advanced?', 'Mem Base', 'Active Members', 'Goals Met', 'Goals Last Year', 'DCP Last Year']
members = [normalize(f) for f in fields]
w.writerow(fields)
allclubs = sorted(clubs.keys(), key=int)
for c in allclubs:
    w.writerow([clubs[c].__dict__.get(m,'') for m in members])
outfile.close()

print "ready to create excel"
# Now, let's actually create an interesting Excel file.
# The file will have several tabs:
#   Clubinfo - basic info on clubs (as from the Find A Club page)
#   Clubperf - performance data on each club, including DCP status, membership, current goals...
#   Analysis - how the districts would split under several conditions

workbook = xlsxwriter.Workbook('clubinfo.xlsx')

bold = workbook.add_format({'bold':1})
formats = {'R': workbook.add_format(), 'G': workbook.add_format(), 'Y': workbook.add_format()}
formats['R'].set_bg_color('#FF4040')
formats['Y'].set_bg_color('yellow')
formats['G'].set_bg_color('#40FF40')

worksheet = workbook.add_worksheet('Analysis')
worksheet.set_column(0, 0, 15)

# The layout of the analysis sheet is:
# Item, d4 current (extends over two vertical columns), and then a column for each option, with
#  north and south stacked.  Each time has a total AND a percentage.

doublerow_format = workbook.add_format('valign':'center')
doublerowb_format = workbook.add_format('valign': 'center', 'bold':true)
header_format = workbook.add_format('align':'center', 'bold':true)
pct_format = workbook.add_format()
pct_format.set_num_format(10)

# Row 0 is the header: item, d4 current, blank, 2-columns per option
worksheet.write(0, 1, "D4 Today", bold)
col = 2
for o in options:
    worksheet.merge_range(0, col, 0, col+1, o.name, header_format)
    o.setcol(col)
    col += 2
    
# Now, start writing information by row pairs.
def write_datum(row, col, name, membername):
    worksheet.merge_range(row, 0, row + 1, 0, name, doublerowb_format)
    worksheet.merge_range(row, 1, row + 1, 1, d4.get(membername), doublerow_format)
    worksheet.write_string(row, 2, 'North', bold)
    worksheet.write_string(row+1, 2, 'South', bold)
    for o in options:
        worksheet.write_number(row, o.col, o.north.get(membername))
        worksheet.write_number(row+1, o.col, o.south.get(membername))
        worksheet.write_number(row, o.col+1, o.north.get(membername) / float(d4.get(membername)), pct_format)
        worksheet.write_number(row+1, o.col+1, o.south.get(membername) / float(d4.get(membername)), pct_format)
    


def fillsheet(worksheet, infofields, numbers=[]):
    infomembers = [normalize(f) for f in infofields]
    nummembers = [normalize(f) for f in numbers]
    clubnamecol = infofields.index('Club Name')
    worksheet.set_column(clubnamecol, clubnamecol, 40)

    for col in xrange(len(infofields)):
        worksheet.write(0, col, infofields[col], bold)
    
    row = 1
    for c in allclubs:
        for col in xrange(len(infomembers)):
            member = infomembers[col]
            what = clubs[c].__dict__.get(member, '')
            if member in nummembers:
                if what:
                  worksheet.write_number(row, col, int(what))
            else:
                what = codecs.decode(what,'cp1252').strip()
                try:
                    if col <> clubnamecol:
                        worksheet.write_string(row, col, what)
                    else:
                        worksheet.write_string(row, col, what, formats[clubs[c].color[0]])
                except UnicodeDecodeError:
                    print 'oops'
                    print unicode(what)
                    worksheet.write_string(row, col, 'unprintable')
        row += 1

clubinfofields = ['Club Number', 'Club Name', 'Status', 'Charter Date', 'Address 1', 'Address 2', 'City', 'County', 'State', 'Zip', 'Meeting Time', 'Meeting Day', 'Club Status', 'Advanced?']
fillsheet(workbook.add_worksheet('Club Information'), clubinfofields)

clubperffields = ['Club Number', 'Club Name', 'Mem Base', 'Active Members', 'Goals Met', 'Goals Met Last Year', 'DCP Last Year']
clubperfnums = ['Mem Base', 'Active Members', 'Goals Met', 'Goals Met Last Year']
perfsheet = workbook.add_worksheet('Club Performance')
perfsheet.set_column(2, 2, 9)
perfsheet.set_column(3, 3, 13)
perfsheet.set_column(5, 5, 16)
perfsheet.set_column(6, 6, 15)
fillsheet(perfsheet, clubperffields, clubperfnums)



 
workbook.close()
    


