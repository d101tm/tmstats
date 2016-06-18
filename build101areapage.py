#!/usr/bin/env python
""" Build the Areas and Divisions page for the website """



import dbconn, tmparms, xlrd, csv
import os, sys, urllib2
from simpleclub import Club
from tmutil import overrideClubs, removeSuspendedClubs, gotodatadir

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
        
    def __repr__(self):
        res = []
        if self.director:
            res.append("""%s""" % self.director.__repr__())
        for a in sorted(self.areas):
            res.append(self.areas[a].__repr__())
        return '\n'.join(res)
        
    def html(self):
        res = []
        res.append('[et_pb_tab title="Division %s" tab_font_select="default" tab_font="||||" tab_line_height="2em" tab_line_height_tablet="2em" tab_line_height_phone="2em" body_font_select="default" body_font="||||" body_line_height="2em" body_line_height_tablet="2em" body_line_height_phone="2em"]' % self.name.upper())

        if self.director:
            res.append('%s' % self.director.html())
        else:
            res.append('<p>Division Director Position is Vacant</p>')
        res.append('<table class="divisiontable">')
        for a in sorted(self.areas):
            res.append('  %s' % self.areas[a].html())
        res.append('</table>')
        res.append('[/et_pb_tab]')
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
        
    def __repr__(self):
        res = []
        if self.director:
            res.append("""  %s""" % self.director.__repr__())
        elif self.parent.director:
            res.append("""  *** Acting: %s """ % self.parent.director.__repr__())
        else:
            res.append("""  Area Director Position is Vacant""")
        for c in sorted(self.clubs, key=lambda x:x.clubnumber.zfill(8)):
            res.append("""    %s: %s %s""" % (c.clubnumber, c.clubname, c.getLink()))
        return '\n'.join(res)
        
    def html(self):
        if self.area == '0A':
            return ''
        res = []
        res.append('<tr><td style="background-color: #f2df74;" colspan="2"><strong>Area %s</strong></td></tr>' % self.name)
        res.append('<tr><td>')
        if self.director:
            res.append(self.director.html())
        elif self.parent.director:
            res.append(self.parent.director.html(isacting=True))
        else:
            res.append('Area Director Position is Vacant')
        res.append('</td></tr>')
        for c in sorted(self.clubs, key=lambda x:x.clubnumber.zfill(8)):
            res.append('<tr><td align="right">%s</td><td><a href="%s" target="_blank">%s</a></td></tr>' % (c.clubnumber, c.getLink(), c.clubname))
        return '\n'.join(res)
        
        
class Director():
    def __init__(self, row):
        for f in row:
            self.__dict__[f.lower().split()[0]] = row[f]
        part = self.title.split()
        if part[0] == 'Division':
            division = part[1]
            Division.find(division).director = self
        elif part[0] == 'Area':
            area = part[1][1]
            division = part[1][0]
            Area.find(division, area).director = self
        self.position = part[0] + ' ' + part[1] + ' Director'
        self.fullname = self.first + ' ' + self.last

        
    def html(self, isacting=False):
        res = []

        if self.photo:
            res.append('<img src="/wp-content/%s"/>'% self.photo)
        res.append('<br />')
        if isacting:
            res.append('<span class="dirtitle">%s</span>' % "Acting Director")
        else:
            res.append('<span class="dirtitle">%s</span>' % self.position)
        res.append('<br />')
        res.append('<span class="dirname">%s</span>' % self.fullname)
        res.append('<br />')
        res.append('<span class="diremail"><a href="mailto:%s">%s</a></span>' % (self.email, self.email))
        res.append('<br />')

        return '\n'.join(res)

        

    def __repr__(self):
        return "%s %s %s: %s" % (self.position, self.first, self.last, self.email, self.photo)
       
    

### Main Program ###
gotodatadir()


parms = tmparms.tmparms(description=__doc__)
parms.add_argument('--outfile', dest='outfile', default='areasanddivisions.html')
parms.add_argument('--newAlignment', dest='newAlignment', default=None, help='Overrides area/division data from the CLUBS table.')
parms.add_argument('--officers', dest='officers', help='URL of the CSV export form of a Google Spreadsheet with Area/Division Directors')
parms.parse()

# Connect to the database
conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
curs = conn.cursor()
    
# Get all clubs
clubs = Club.getClubsOn(curs)

if parms.newAlignment:
    overrideClubs(clubs, parms.newAlignment)
    
# Remove suspended clubs
clubs = removeSuspendedClubs(clubs, curs)


# Now, assign clubs to Areas and Divisions

        
        
for c in sorted(clubs):
    club = clubs[c]
    Area.find(club.division, club.area).addclub(club)
    



# OK, now we have the club info.  Let's get the Area Director/Division Director information.
officers = urllib2.urlopen(parms.officers)
reader = csv.DictReader(officers)
for row in reader:
    for k in row:
        row[k] = ' '.join(row[k].split()).strip()
    if row['Title'] and row['First']:
        Director(row)
        



# And now we go through the Divisions and Areas and build the output.
outfile = open(parms.outfile, 'w')
outfile.write("""[et_pb_tabs admin_label="Tabs" use_border_color="off" border_color="#ffffff" border_style="solid" tab_font_size="24"]
""")
for d in sorted(Division.divisions):
    if d.lower() != 'new':
        div = Division.divisions[d]
        outfile.write(div.html())
        outfile.write('\n')

outfile.write("""[/et_pb_tabs]

""")
