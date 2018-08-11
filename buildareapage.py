#!/usr/bin/env python3
""" Build the Areas and Divisions page for the website """



import dbconn, tmparms, xlrd, csv
import os, sys, urllib.request, urllib.error, urllib.parse
from simpleclub import Club
from tmutil import overrideClubs, removeSuspendedClubs, gotodatadir
from overridepositions import overrideClubPositions
from makemap import Bounds, setClubCoordinatesFromGEO
from gsheet import GSheet

import tmglobals
globals = tmglobals.tmglobals()

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
        res.append('[et_pb_tab title="Division %s" tab_font_select="default" tab_font="||||" tab_line_height="2em" tab_line_height_tablet="2em" tab_line_height_phone="2em" body_font_select="default" body_font="||||" body_line_height="1.3em" body_line_height_tablet="1.3em" body_line_height_phone="1.3em"]' % self.name.upper())
        res.append('<table class="divisiontable">')

        if self.director:
            res.append('%s' % self.director.html())
        else:
            res.append('<tr><td align="left" colspan="2">Division %s Director Position is Vacant</td></tr>' % self.name.upper())
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
        return '\n'.join([value.decode('utf-8', 'xmlcharrefreplace') for value in res])
        
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
            res.append('<tr><td colspan="2" align="left">Area Director Position is Vacant</td></tr>')
        for c in sorted(self.clubs, key=lambda x:x.clubnumber.zfill(8)):
            res.append('<tr><td align="right">%s</td><td><a href="%s" target="_blank">%s</a></td></tr>' % (c.clubnumber, c.getLink(), c.clubname.replace('&','&amp;')))

        return '\n'.join(res)

        
class Director():
    def __init__(self, row):
        for f in row.dict:
            self.__dict__[f.lower().split()[0]] = row.dict[f]
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
        return """<tr>
  <td align="left" colspan="2">%s%s %s %s (<a href="mailto:%s">%s</a>)</td>
</tr>
""" % ('<strong>Acting: </strong>' if isacting else '',self.position, self.first, self.last, self.email, self.email)

 
        

    def __repr__(self):
        return "%s %s %s: %s" % (self.position, self.first, self.last, self.email, self.photo)
       
    

### Main Program ###

parms = tmparms.tmparms(description=__doc__)
parms.add_argument('--outfile', dest='outfile', default='areasanddivisions.html')
parms.add_argument('--newAlignment', dest='newAlignment', default=None, help='Overrides area/division data from the CLUBS table.')
parms.add_argument('--officers', dest='officers', help='URL of a Google Spreadsheet with Area/Division Directors')
parms.add_argument('--mapdir', default=None, help='Directory to use for the area map files.')
parms.add_argument('--pindir', dest='pindir', default=None, help='Directory with pins; default uses Google pins')
parms.add_argument('--mapoverride', dest='mapoverride', default=None, help='Google spreadsheet with overriding address and coordinate information')

# Do global setup
globals.setup(parms)
conn = globals.conn
curs = globals.curs

print(parms.officers)
    
# Get all clubs
clubs = Club.getClubsOn(curs)

if parms.newAlignment:
    overrideClubs(clubs, parms.newAlignment, exclusive=False)

    
# Remove suspended clubs
clubs = removeSuspendedClubs(clubs, curs)


# Remove clubs from outside our District
for c in list(clubs.keys()):
    try:
        if int(clubs[c].district) != parms.district:
            del clubs[c]
    except ValueError:
        print((clubs[c]))
        
# Add current coordinates and remove clubs without coordinates (unless there's a new alignment)
setClubCoordinatesFromGEO(clubs, curs, removeNotInGeo=not parms.newAlignment)

# If there are overrides to club positioning, handle them now
if parms.mapoverride:
    overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey)

# Now, assign clubs to Areas and Divisions
    
        
for c in sorted(clubs):
    club = clubs[c]
    Area.find(club.division, club.area).addclub(club)
    



# OK, now we have the club info.  Let's get the Area Director/Division Director information.
for row in GSheet(parms.officers, apikey=parms.googlesheetsapikey):
    for k in row.fieldnames:
        setattr(row, k,' '.join(str(getattr(row,k))).split())
    if row.title and row.first:
        Director(row)
        



# And now we go through the Divisions and Areas and build the output.
outfile = open(parms.outfile, 'w')
outfile.write("<p><b>Click on a Division to see the clubs and Areas it contains.</b></p>")
outfile.write("""[et_pb_tabs admin_label="Tabs" use_border_color="off" border_color="#ffffff" border_style="solid" tab_font_size="18"]
""")
for d in sorted(Division.divisions):
    if d.lower() != 'new':
        div = Division.divisions[d]
        outfile.write(div.html())
        outfile.write('\n')

outfile.write("""[/et_pb_tabs]

""")

# Create map pages if mapdir was specified.
if parms.mapdir:
    for d in sorted(Division.divisions):
        if d.lower() != 'new':
            div = Division.divisions[d]
            for a in sorted(div.areas):
                with open(os.path.join(parms.mapdir, '%s.html' % a),'w') as mapfile:
                    b = Bounds()
                    mapbase="https://maps.googleapis.com/maps/api/staticmap?"
                    mapparts = []

                    clubinfo = []
                    marker = 'A'
                    for c in sorted(div.areas[a].clubs, key=lambda x:x.clubnumber.zfill(8)):
                        b.extend(float(c.latitude), float(c.longitude))
                        mapparts.append('markers=label:%s%%7C%s,%s' % (marker, c.latitude, c.longitude))
                        
                        clubinfo.append('<tr><td class="marker">%s</td>' % marker)
                        clubinfo.append('<td class="clubnum">%s</td>' % c.clubnumber)
                        clubinfo.append('<br />\n'.join(('<td><b>%s</b>' % c.clubname, c.place, c.address, '%s, %s %s' % (c.city, c.state, c.zip))))
                        clubinfo.append('<br />\n'.join(('<td>%s' % c.meetingday, c.meetingtime)))
                        clubinfo.append('</td></tr>\n')
                
                        
                        marker = chr(ord(marker)+1)
                        
                        
   
                    mapparts.append("size=640x640&scale=2")   # As large as possible, at least for now
                    mapfile.write('<html>\n')
                    mapfile.write('<head>\n')
                    mapfile.write('<style type="text/css">\n')
                    mapfile.write('.areamap {width:640px, height:640px;}\n')
                    mapfile.write('</style>\n')
                    mapfile.write('</head>\n<body>\n')
                    mapfile.write('<div class="areamap">\n')
                    mapfile.write('<img width="640px" height="640px" src="%s%s">\n' % (mapbase, '&'.join(mapparts)))
                    mapfile.write('</div>\n')
                    mapfile.write('<div class="clubinfo">\n')
                    mapfile.write('<table>\n')
                    mapfile.write('\n'.join(clubinfo))
                    mapfile.write('</table>\n</div>\n')                
                    mapfile.write('</body>\n</html>\n')
                    
  
                    
