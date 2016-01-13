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

def subtable(place, address, locationtype, reverse, reversetype):
    res = ['<table>']
    res.append('<tr class="loctype"><td>%s</td></tr>' % locationtype)
    res.append('<tr class="place"><td>%s<br />' % place.replace(';;','<br />'))
    res.append('%s</td></tr>' % address)
    res.append('<tr class="loctype"><td>%s</td></tr>' % reversetype)
    res.append('<tr class="address"><td>%s</td></tr>' % reverse)
    res.append('</table>')
    return '\n'.join(res)

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
    for (district, division, area, clubnumber, clubname, place, address, latitude, longitude, locationtype, whqlatitude, whqlongitude, whqreverse, whqreversetype, maplatitude, maplongitude, mapaddress, mapreverse, mapreversetype) in c.fetchall():
        whqgeodelta = distance_on_unit_sphere(whqlatitude, whqlongitude, latitude, longitude)
        whqmapdelta = distance_on_unit_sphere(whqlatitude, whqlongitude, maplatitude, maplongitude)
        geomapdelta = distance_on_unit_sphere(latitude, longitude, maplatitude, maplongitude)
        outfile.write("      <tr>\n")
        outfile.write("        <td>%s</td>\n" % district)
        outfile.write("        <td>%s%s</td>\n" % (division, area))
        outfile.write("        <td>%s</td>\n" % clubnumber)
        outfile.write("        <td>%s</td>\n" % clubname)
        outfile.write("<td>")
        outfile.write("<table>\n")
        outfile.write("<tr>\n")
        outfile.write("<td width=\"50%%\">%s<br />%s<br />&nbsp;<br />%s</td>" % (place, address, locationtype))
        outfile.write("<td width=\"50%%\">%s</td>" % (mapaddress))
        outfile.write("</tr>\n")
        outfile.write("<tr>\n")
        outfile.write("<td width=\"50%%\">%s<br />&nbsp;<br />%s</td>" % (whqreverse, whqreversetype))
        outfile.write("<td width=\"50%%\">%s<br />&nbsp;<br />%s</td>" % (mapreverse, mapreversetype))
        outfile.write("</tr>\n")
        outfile.write("<tr><td>WHQ to geoencoded: %.2f; WHQ to map: %.2f; map to geoencoded: %.2f\n" % (whqgeodelta, whqmapdelta, geomapdelta))
        href = []
        href.append("http://maps.googleapis.com/maps/api/staticmap?size=600x600")
        href.append("&markers=color:red%7Clabel:M%7C")
        href.append("%f,%f" % (maplatitude, maplongitude))
        href.append("&markers=color:blue%7Clabel:G%7C")
        href.append("%f,%f" % (latitude, longitude))
        if whqlatitude != 0.0 or whqlongitude != 0.0:
            href.append("&markers=color:green%7Clabel:W%7C")
            href.append("%f,%f" % (whqlatitude, whqlongitude))
        href = ''.join(href)
        outfile.write('<a target="_blank" href="%s">map</a>' % href)
        outfile.write('</td></tr>')
        outfile.write("</table>\n")
        outfile.write("</td>\n")
        outfile.write("      </tr>\n")
    outfile.write("    </table>\n  </body>\n</html>\n")
    outfile.close()
