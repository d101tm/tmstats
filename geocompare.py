#!/usr/bin/env python2.7
import googlemaps
import urllib3
import logging
import dbconn, tmparms
import pprint
import dbconn, tmutil, sys, os
import json
import csv
from uncodeit import myclub

import tmglobals
globals = tmglobals.tmglobals()

style = """
.deltatable {
        margin:0px;padding:0px;
        width:100%;
        border:1px solid #000000;
}.deltatable table{
    border-collapse: collapse;
        border-spacing: 0;
        width:100%;
        height:100%;
        margin:0px;padding:0px;
}.deltatable tr:last-child td:last-child {
        -moz-border-radius-bottomright:0px;
        -webkit-border-bottom-right-radius:0px;
        border-bottom-right-radius:0px;
}
.deltatable table tr:first-child td:first-child {
        -moz-border-radius-topleft:0px;
        -webkit-border-top-left-radius:0px;
        border-top-left-radius:0px;
}
.deltatable table tr:first-child td:last-child {
        -moz-border-radius-topright:0px;
        -webkit-border-top-right-radius:0px;
        border-top-right-radius:0px;
}.deltatable tr:last-child td:first-child{
        -moz-border-radius-bottomleft:0px;
        -webkit-border-bottom-left-radius:0px;
        border-bottom-left-radius:0px;
}.deltatable tr:hover td{
        background-color:#ffffff;
                

}
.deltatable td{
        vertical-align:top;
        
        background-color:#ffffff;

        border:1px solid #000000;
        border-width:0px 1px 1px 0px;
        text-align:left;
        padding:3px;
        font-size:14px;
        font-family:Arial;
        font-weight:normal;
        color:#000000;
}.deltatable tr:last-child td{
        border-width:0px 1px 0px 0px;
}.deltatable tr td:last-child{
        border-width:0px 0px 1px 0px;
}.deltatable tr:last-child td:last-child{
        border-width:0px 0px 0px 0px;
}
.deltatable tr:first-child td{
                background:-o-linear-gradient(bottom, #cccccc 5%, #cccccc 100%);        background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #cccccc), color-stop(1, #cccccc) );
        background:-moz-linear-gradient( center top, #cccccc 5%, #cccccc 100% );


        background-color:#cccccc;
        border:0px solid #000000;
        text-align:center;
        border-width:0px 0px 1px 1px;
        font-size:14px;
        font-family:Arial;
        font-weight:bold;
        color:#000000;
}

.h1 {text-align: center;}

.clubid {
    font-size: 180%;
    text-align: center;}

.bigtable {
padding-bottom: 18px;
border:0px solid #ffffff;}


"""

def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)
        
import math
 
def distance_on_unit_sphere(lat1, long1, lat2, long2):
 
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
         
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
     
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    try:
        arc = math.acos( cos )
    except ValueError:
        arc = 1.0
 
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 3956  # to get miles


### Insert classes and functions here.  The main program begins in the "if" statement below.

repl = (('Wy', 'Way'),
        ('St', 'Street'),
        ('Ave', 'Avenue'),
        ('Dr', 'Drive'),
        ('Fl', 'Floor'),
        ('Pl', 'Place'),
        ('Rd', 'Road'),
        ('Bldg', 'Building'),
        ('Blvd', 'Boulevard'),
        ('Pkwy', 'Parkway'),
        ('Ct', 'Court'),
        ('Cir', 'Circle'),
        ('Ctr', 'Center'),
        ('Suite', ''),
        ('Ste', ''),
        ('Apt', ''),
        ('N', 'North'),
        ('S', 'South'),
        ('E', 'East'),
        ('W', 'West'))
        
repdict = {}
for a,b in repl:
    a = a.lower()
    b = b.lower()
    repdict[a] = b
    repdict[b] = b
    

def cleanaddr(what):
    """ Try to clean up address formats """
    words = what.lower().replace('#','').replace('-','').replace('.','').split()
    cleaned = []
    for w in words:
        if w in repdict:
            cleaned.append(repdict[w])
        else:
            cleaned.append(w)
    return ' '.join(cleaned)
        


class Clubinfo:
    clubs = []
    clubsbylocator = {}
    def __init__(self, row):
        fields = [f.strip() for f in 'district, division, area, clubnumber, clubname, place, address, latitude, longitude, reverse, reversetype, locationtype, whqlatitude, whqlongitude, whqreverse, whqreversetype, formatted'.split(',')]
        for (name, value) in zip(fields, row):
            self.__dict__[name] = value
        self.whqgeodelta = distance_on_unit_sphere(self.whqlatitude, self.whqlongitude, self.latitude, self.longitude) if (self.whqlatitude != 0 and self.whqlongitude !=0) else 0
        astart = cleanaddr(self.address.split(',')[0])
        fstart = cleanaddr(self.formatted.split(',')[0])
        rstart = cleanaddr(self.reverse.split(',')[0])
        self.examineinput = astart != fstart
        self.examineoutput = fstart != rstart
        self.clubs.append(self)
        locator = 'District %s, Area %s' % (self.district, self.division + self.area)
        if locator not in self.clubsbylocator:
            self.clubsbylocator[locator] = []
        self.clubsbylocator[locator].append(self)

    def __repr__(self):
        ans = []

        ans.append("<h2 class=\"clubid\">%s (<b>%s</b>)</h4>"% (self.clubnumber, self.clubname))
        ans.append("<table class=\"clubtable\">")
        ans.append("<tbody>")
        ans.append("<tr>")
        ans.append("<td style=\"vertical-align: top\">")
        ans.append("<table border=\"1\">")
        ans.append("<tbody>")
        ans.append("<tr>")
        ans.append("<td>Meeting Place in Club Central</td>")
        ans.append("<td>%s</td>" % (self.place))
        ans.append("</tr><tr>")
        ans.append("<td>Meeting Address in Club Central</td>")
        ans.append("<td>%s</td>" % (self.address)) 
        ans.append("</tr><tr>")
        if (self.examineinput):
            ans.append("<td>Address as interpreted by Google</td>")
            ans.append("<td>%s</td>" % (self.formatted))
            ans.append("</tr><tr>")
        ans.append("<td>Map Pin (D) on d4tm.org</td>")
        ans.append("<td>%s<br />(%s)" % (self.reverse, self.reversetype))
        ans.append("<td>&nbsp;</td>")
        ans.append("</tr><tr>")
        ans.append("<td>Map Pin (T) on toastmasters.org</td>")
        ans.append("<td>%s<br />(%s)" % (self.whqreverse, self.whqreversetype))
        ans.append("</tr><tr>")
        ans.append("<td>Distance (miles) between map pins</td>")
        ans.append("<td>%s</td>" % ('%.2f' % self.whqgeodelta if self.whqlatitude != 0 and self.whqlongitude != 0 else 'N/A'))
        ans.append("</tr><tr>")
        ans.append("<td>Coordinates on Club Central</td>")
        ans.append("<td>(%f, %f)</td>" % (self.whqlatitude, self.whqlongitude))
        ans.append("</tr><tr>")
        ans.append("<td>Coordinates on D4TM.ORG</td>")
        ans.append("<td>(%f, %f)</td>" % (self.latitude, self.longitude))
        ans.append("</tr>")
        if club.clubnumber in addrchanges:
            ans.append('<tr><td>Address last changed</td><td>%s</td></tr>' % addrchanges[club.clubnumber])
        if club.clubnumber in coordchanges:
            ans.append('<tr><td>Coordinates last updated</td><td>%s</td></tr>' % coordchanges[club.clubnumber])
        
        ans.append("</tbody>")
        ans.append("</table>")
        ans.append("</td>")
        ans.append("<td>")
        href = []
        href.append("http://maps.googleapis.com/maps/api/staticmap?size=400x400&key=AIzaSyAMfs7vnmebebI4j00oTz8kqH3hw7b9s_8") 
        href.append("&markers=color:blue%7Clabel:D%7C")
        href.append("%f,%f"% (self.latitude, self.longitude))
        if self.whqlatitude != 0.0 or self.whqlongitude != 0.0:
            href.append("&markers=color:green%7Clabel:T%7C")
            href.append("%f,%f"% (self.whqlatitude, self.whqlongitude))
        href = ''.join(href)
        ans.append("<img src=\"%s\">" % href)
        ans.append("</td>")
        ans.append("</tr>")
        ans.append("</table>")
        return '\n'.join(ans)

if __name__ == "__main__":
 

    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--skipload', action='store_true')
    
    # Do global setup
    globals.setup(parms)
    conn = globals.conn
    c = globals.curs
    



    # And now, create the final comparison as a table

    c.execute("select clubs.district, clubs.division, clubs.area, geo.clubnumber, geo.clubname, geo.place, concat(geo.address,', ',geo.city,', ',geo.state,' ',geo.zip, ', USA'), geo.latitude, geo.longitude, geo.reverse, geo.reversetype, geo.locationtype, geo.whqlatitude, geo.whqlongitude, geo.whqreverse, geo.whqreversetype, geo.formatted from geo inner join map on map.clubnumber = geo.clubnumber inner join clubs on geo.clubnumber = clubs.clubnumber WHERE clubs.lastdate IN (SELECT MAX(lastdate) FROM clubs) order by clubs.district, clubs.division, clubs.area, geo.clubnumber")
    for (row) in c.fetchall():
        club = Clubinfo(row)
        
    # Get changes to address or coordinates at Club Central
    addrchanges = {}
    coordchanges = {}
    c.execute("select item, changedate, clubnumber, old from clubchanges where item in ('latitude', 'longitude', 'address', 'city', 'state', 'zip') and not (item in ('latitude', 'longitude') and old = 0)  order by changedate")
    for (item, changedate, clubnumber, old) in c.fetchall():
        if item in ('latitude', 'longitude'):
            coordchanges[clubnumber] = changedate
        else:
            addrchanges[clubnumber] = changedate
            
    # And now, create pretty web pages and a spreadsheet
    
    csvfile = open('compare.csv', 'wb')
    writer = csv.writer(csvfile)
    sheetfields = ['district', 'division', 'area', 'clubnumber', 'clubname', 'place', 'examineinput',
                    'examineoutput', 'address', 'formatted', 'whqreverse', 'reverse']
    writer.writerow(sheetfields)
    
    
    for l in sorted(club.clubsbylocator.keys()):
        clubs = club.clubsbylocator[l]
        outfile = open('compare%s.html' % (clubs[0].division + clubs[0].area), 'w')
        outfile.write("<html><head>\n")
        outfile.write("<style type=\"text/css\">")
        outfile.write(style)
        outfile.write("</style>")
        outfile.write("</head><body>\n")
        outfile.write('<h1>%s</h1>\n' % l)
        clubs.sort(key=lambda k:-k.whqgeodelta)

        for club in clubs:
            outfile.write(repr(club))
            writer.writerow([club.__dict__[k] for k in sheetfields])
           
        outfile.write("</body>\n</html>\n")
        outfile.close()
    csvfile.close()
