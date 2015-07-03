#!/usr/bin/python
""" Build the Areas and Divisions page for the website """



import dbconn, tmparms, xlrd, csv
import os, sys, urllib2
from simpleclub import Club

class Division():
    divisions = {}
    @classmethod
    def find(self, division):
        if division == '0D':
            division = 'New'
        if division not in self.divisions:
            self.divisions[division] = Division(division)
        return self.divisions[division]

    def __init__(self, division):
        self.areas = {}
        self.name = division
        self.director = None
        
    def addarea(self, area):
        self.areas[area.name] = area
        
    def __info__(self):
        res = []
        if self.director:
            res.append(["""%s""" % self.director.info()])
        for a in sorted(self.areas):
            res.append(self.areas[a].info())
        return '\n'.join(res)
        
    def html(self):
        res = []
        res.append('<p>{tab %s|align_center|alias:%s}</p>' % (self.name.upper(), self.name))
        res.append('<table class="table1">\n  <tbody>\n')
        res.append('  <tr><th style="background-color: #f2df74;" colspan="2"><strong>Division %s</strong></th></tr>' % self.name.upper())
        if self.director:
            res.append('  %s' % self.director.html())
        else:
            res.append('<tr><td></td><td>Division Director Position is Vacant</td><tr>')
        for a in sorted(self.areas):
            res.append('  %s' % self.areas[a].html())
        res.append('  </tbody>\n</table>')
        return '\n'.join(res)

class Area():
    areas = {}
    @classmethod
    def find(self, division, area):
        name = division + area
        if name not in self.areas:
            self.areas[name] = Area(division, area)
        return self.areas[name]
        
    def __init__(self, division, area):
        self.parent = Division.find(division)
        self.clubs = []
        self.name = division + area
        self.director = None
        self.division = division
        self.area = area
        self.parent.addarea(self)
        
    def addclub(self, club):
        self.clubs.append(club)
        
    def info(self):
        res = []
        if self.director:
            res.append("""  %s""" % self.director.info())
        elif self.parent.director:
            res.append("""  *** Acting: %s """ % self.parent.director.info())
        for c in sorted(self.clubs, key=lambda x:x.clubnumber.zfill(8)):
            res.append("""    %s: %s %s""" % (c.clubnumber, c.clubname, c.getLink()))
        return '\n'.join(res)
        
    def html(self):
        if self.area == '0A':
            return ''
        res = []
        res.append('<tr><td style="background-color: #f2df74;" colspan="2"><strong>Area %s</strong></td></tr>' % self.name)
        if self.director:
            res.append(self.director.html())
        elif self.parent.director:
            res.append(self.parent.director.html(isacting=True))
        for c in sorted(self.clubs, key=lambda x:x.clubnumber.zfill(8)):
            res.append('<tr><td align="right">%s</td><td><a href="%s" target="_blank">%s</a></td></tr>' % (c.clubnumber, c.getLink(), c.clubname))
        return '\n'.join(res)
        
        
class Director():
    def __init__(self, position, first, last, email):
        part = position.split()
        if part[0] == 'Division':
            division = part[1]
            Division.find(division).director = self
        elif part[0] == 'Area':
            area = part[1][1]
            division = part[1][0]
            Area.find(division, area).director = self
        self.first = first
        self.last = last
        self.email = email
        self.position = ' '.join(part)
        
    def html(self, isacting=False):
        return """<tr>
  <td align="right"><a href="mailto:%s" target="_blank">Email</a></td>
  <td>%s%s %s %s</td>
</tr>
""" % ( self.email, '<strong>Acting: </strong>' if isacting else '',self.position, self.first, self.last)

    def info(self):
        return "%s %s %s: %s" % (self.position, self.first, self.last, self.email)
       
    


def makestring(x):
    try:
        return '%s' % int(x)
    except ValueError:
        return ''

# Make it easy to run under TextMate
if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))

    
# Get around unicode problems
reload(sys).setdefaultencoding('utf8')


parms = tmparms.tmparms(description=__doc__)
parms.add_argument('--outfile', dest='outfile', default='areasanddivisions.html')
parms.add_argument('--clubfile', dest='clubfile', default=None, help='Overrides area/division data from the CLUBS table.')
parms.parse()

# Connect to the database
conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
curs = conn.cursor()
    
# Get all clubs
clubs = Club.getClubsOn(None, curs)

if not parms.clubfile:
    sys.stderr.write('Did you forget to override the club alignment?\n')
# Override assignments as required
if parms.clubfile:
    book = xlrd.open_workbook(parms.clubfile)
    

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
        clubnum = makestring(values[clubcol])
        if clubnum in clubs:
            club = clubs[clubnum]
            was = 'District %s, Area %s%s' % (club.district, club.division, club.area)
            if values[areacol]:
                club.area = makestring(values[areacol])
            if values[divcol]:
                club.division = values[divcol]
            if values[distcol]:
                clubs.district = makestring(values[distcol])
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
            clubnum = makestring(values[clubcol])
            if clubnum in clubs:
                #print 'Suspended: %s (%s)' % (clubs[clubnum].clubname, clubs[clubnum].clubnumber)
                del clubs[clubnum]
            rownum += 1
            
# Now, assign clubs to Areas and Divisions

        
        
for c in sorted(clubs):
    club = clubs[c]
    Area.find(club.division, club.area).addclub(club)
    



# OK, now we have the club info.  Let's get the Area Director/Division Director information.
officers = urllib2.urlopen(parms.officers)
reader = csv.DictReader(officers)
for row in reader:
    if row['Title'] and row['First']:
        Director(row['Title'], row['First'], row['Last'], row['Email'])



# And now we go through the Divisions and Areas and build the output.
outfile = open(parms.outfile, 'w')
for d in sorted(Division.divisions):
    div = Division.divisions[d]
    outfile.write(div.html())
    outfile.write('\n')
    

