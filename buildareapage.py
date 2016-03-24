#!/usr/bin/env python
""" Build the Areas and Divisions page for the website """



import dbconn, tmparms, xlrd, csv
import os, sys, urllib2
from simpleclub import Club
from tmutil import overrideClubs, removeSuspendedClubs

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
        if self.director:
            res.append(self.director.html())
        elif self.parent.director:
            res.append(self.parent.director.html(isacting=True))
        else:
            res.append('<tr><td></td><td>Area Director Position is Vacant</td></tr>')
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
        self.position = part[0] + ' ' + part[1] + ' Director'

        
    def html(self, isacting=False):
        return """<tr>
  <td align="right"><a href="mailto:%s" target="_blank">Email</a></td>
  <td>%s%s %s %s</td>
</tr>
""" % ( self.email, '<strong>Acting: </strong>' if isacting else '',self.position, self.first, self.last)

    def __repr__(self):
        return "%s %s %s: %s" % (self.position, self.first, self.last, self.email)
       
    



# Make it easy to run under TextMate
if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))

    
# Get around unicode problems
reload(sys).setdefaultencoding('utf8')


parms = tmparms.tmparms(description=__doc__)
parms.add_argument('--outfile', dest='outfile', default='areasanddivisions.html')
parms.add_argument('--newAlignment', dest='newAlignment', default=None, help='Overrides area/division data from the CLUBS table.')
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
        Director(row['Title'], row['First'], row['Last'], row['Email'])
        



# And now we go through the Divisions and Areas and build the output.
outfile = open(parms.outfile, 'w')
for d in sorted(Division.divisions):
    if d.lower() != 'new':
        div = Division.divisions[d]
        outfile.write(div.html())
        outfile.write('\n')

