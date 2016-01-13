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
        self.whqgeodelta = distance_on_unit_sphere(self.whqlatitude, self.whqlongitude, self.latitude, self.longitude) if (self.whqlatitude != 0 and self.whqlongitude !=0) else 0
        self.whqmapdelta = distance_on_unit_sphere(self.whqlatitude, self.whqlongitude, self.maplatitude, self.maplongitude) if (self.whqlatitude != 0 and self.whqlongitude !=0) else 0
        self.geomapdelta = distance_on_unit_sphere(self.latitude, self.longitude, self.maplatitude, self.maplongitude)
        self.maxdelta = max(self.whqgeodelta, self.whqmapdelta, self.geomapdelta)
        self.clubs.append(self)
        locator = 'District %s, Area %s' % (self.district, self.division + self.area)
        if locator not in self.clubsbylocator:
            self.clubsbylocator[locator] = []
        self.clubsbylocator[locator].append(self)

    def __repr__(self):
        ans = []
        ans.append("<tr>")
        ans.append("<td>%s</td>"% self.clubnumber)
        ans.append("<td>%s</td>"% self.clubname)
        ans.append("<td>")
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
        ans.append("<img src=\"%s\">" % href)
        ans.append("<p>Meeting location in Club Central: %s<br />%s</p>\n" % (self.place, self.address)) 
        ans.append("<p>Meeting location in D4 map:%s</p>" % self.mapaddress)
        ans.append("<p>Reverse-located (%s) from Club Central: %s</p>" % (self.whqreversetype, self.whqreverse))
        ans.append("<p>Reverse-located (%s) from D4 map:%s</p>" % (self.mapreversetype, self.mapreverse))
        ans.append("<p>Coordinates in Club Central (%f, %f)</p>" % (self.whqlatitude, self.whqlongitude))
        ans.append("<p>Coordinates in D4 map (%f, %f)</p>" % (self.maplatitude, self.maplongitude))
        ans.append("<p>Coordinates relocated (%f, %f)</p>" % (self.latitude, self.longitude))
        ans.append("<p>WHQ to geoencoded: %.2f; WHQ to map: %.2f; map to geoencoded: %.2f</p>"% (self.whqgeodelta, self.whqmapdelta, self.geomapdelta))
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
    outfile.write("<html><head>\n")
    outfile.write("</head><body>\n")
    c.execute("select clubs.district, clubs.division, clubs.area, geo.clubnumber, geo.clubname, geo.place, concat(geo.address,', ',geo.city,', ',geo.state,' ',geo.zip, ', USA'), geo.latitude, geo.longitude, locationtype, geo.whqlatitude, geo.whqlongitude, reverse, reversetype, map.lat, map.lng, map.address, mapreverse, mapreversetype from geo inner join map on map.clubnumber = geo.clubnumber inner join clubs on geo.clubnumber = clubs.clubnumber WHERE clubs.lastdate IN (SELECT MAX(lastdate) FROM clubs) order by clubs.district, clubs.division, clubs.area, geo.clubnumber")
    for (row) in c.fetchall():
        club = Clubinfo(row)
    
    for l in sorted(club.clubsbylocator.keys()):
        clubs = club.clubsbylocator[l]
        outfile.write('<h3>%s</h3>\n' % l)
        clubs.sort(key=lambda k:-k.maxdelta)
        outfile.write('<table border="1">')
        for club in clubs:
            outfile.write(repr(club))
        outfile.write('</table>')
   
    outfile.write("    </table>\n  </body>\n</html>\n")
    outfile.close()
