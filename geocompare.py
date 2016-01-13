#!/usr/bin/env python2.7
import googlemaps
import urllib3
import logging
import dbconn, tmparms
import pprint
import dbconn, tmutil, sys, os
import json
from uncodeit import myclub

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

class Clubinfo:
    clubs = []
    clubsbylocator = {}
    def __init__(self, row):
        fields = [f.strip() for f in 'district, division, area, clubnumber, clubname, place, address, latitude, longitude, locationtype, whqlatitude, whqlongitude, whqreverse, whqreversetype, maplatitude, maplongitude, mapaddress, mapreverse, mapreversetype'.split(',')]
        for (name, value) in zip(fields, row):
            self.__dict__[name] = value
        self.whqgeodelta = distance_on_unit_sphere(self.whqlatitude, self.whqlongitude, self.latitude, self.longitude)
        self.whqmapdelta = distance_on_unit_sphere(self.whqlatitude, self.whqlongitude, self.maplatitude, self.maplongitude)
        self.geomapdelta = distance_on_unit_sphere(self.latitude, self.longitude, self.maplatitude, self.maplongitude)
        self.clubs.append(self)
        locator = 'District %s, Area %s' % (self.district, self.division + self.area)
        if locator not in self.clubsbylocator:
            self.clubsbylocator[locator] = []
        self.clubsbylocator[locator].append(self)

    def __repr__(self):
        ans = []
        ans.append("<tr>")
        ans.append("<td>%s</td>"% self.district)
        ans.append("<td>%s%s</td>"% (self.division, self.area))
        ans.append("<td>%s</td>"% self.clubnumber)
        ans.append("<td>%s</td>"% self.clubname)
        ans.append("<td>")
        ans.append("<table border=\"1\">")
        ans.append("<tr>")
        ans.append("<td width=\"50%%\">%s<br />%s<br />&nbsp;<br />%s</td>"% (self.place, self.address, self.locationtype))
        ans.append("<td width=\"50%%\">%s</td>"% (self.mapaddress))
        ans.append("</tr>")
        ans.append("<tr>")
        ans.append("<td width=\"50%%\">%s<br />&nbsp;<br />%s</td>"% (self.whqreverse, self.whqreversetype))
        ans.append("<td width=\"50%%\">%s<br />&nbsp;<br />%s</td>"% (self.mapreverse, self.mapreversetype))
        ans.append("</tr>")
        ans.append("<tr><td>WHQ to geoencoded: %.2f; WHQ to map: %.2f; map to geoencoded: %.2f"% (self.whqgeodelta, self.whqmapdelta, self.geomapdelta))
        href = []
        href.append("http://maps.googleapis.com/maps/api/staticmap?size=600x600")
        href.append("&markers=color:red%7Clabel:M%7C")
        href.append("%f,%f"% (self.maplatitude, self.maplongitude))
        href.append("&markers=color:blue%7Clabel:G%7C")
        href.append("%f,%f"% (self.latitude, self.longitude))
        if self.whqlatitude != 0.0 or self.whqlongitude != 0.0:
            href.append("&markers=color:green%7Clabel:W%7C")
            href.append("%f,%f"% (self.whqlatitude, self.whqlongitude))
        href = ''.join(href)
        ans.append('<a target="_blank"href="%s">map</a>' % href)
        ans.append('</td></tr>')
        ans.append("</table>")
        ans.append("</td>")
        ans.append("</tr>")
        return '\n'.join(ans)

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--skipload', action='store_true')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    c = conn.cursor()


    # And now, create the final comparison as a table
    outfile = open('compare.html', 'w')
    outfile.write("""<html>
  <body>
    <table>
""")
    c.execute("select clubs.district, clubs.division, clubs.area, geo.clubnumber, geo.clubname, geo.place, concat(geo.address,', ',geo.city,', ',geo.state,' ',geo.zip, ', USA'), geo.latitude, geo.longitude, locationtype, geo.whqlatitude, geo.whqlongitude, reverse, reversetype, map.lat, map.lng, map.address, mapreverse, mapreversetype from geo inner join map on map.clubnumber = geo.clubnumber inner join clubs on geo.clubnumber = clubs.clubnumber WHERE clubs.lastdate IN (SELECT MAX(lastdate) FROM clubs) order by clubs.district, clubs.division, clubs.area, geo.clubnumber")
    for (row) in c.fetchall():
        club = Clubinfo(row)
        outfile.write(repr(club))

   
    outfile.write("    </table>\n  </body>\n</html>\n")
    outfile.close()
