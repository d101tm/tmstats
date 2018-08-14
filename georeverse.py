#!/usr/bin/env python3
""" Reverse-Geocode coordinates from WHQ and from our encoding and add them to the GEO table. """
import googlemaps
import urllib3
import logging
import dbconn, tmparms
import pprint
import dbconn, tmutil, sys, os
import json
from uncodeit import myclub

import tmglobals
globals = tmglobals.tmglobals()

def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print(' '.join(args), file=file)
        
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
    arc = math.acos( cos )
 
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 3956  # to get miles


### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":

    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
    
    # Do global setup
    globals = globals.setup(parms)
    conn = globals.conn
    c = globals.curs


    # Your main program begins here.

    gmaps = googlemaps.Client(key=parms.googlemapsapikey)
    c.execute("SELECT clubnumber, clubname, latitude, longitude FROM clubs WHERE lastdate IN (SELECT MAX(lastdate) FROM clubs) ORDER BY clubnumber;")
    for (clubnumber, clubname, whqlatitude, whqlongitude) in c.fetchall():
        # Now, reverse-geocode the address and add it to the table
        print(clubnumber, clubname, whqlatitude, whqlongitude)
        try:        
            rev = gmaps.reverse_geocode((whqlatitude, whqlongitude))[0]
            fa = rev['formatted_address']
            revloctype = rev['geometry']['location_type']
            print('        ', revloctype, fa)
            c.execute('UPDATE geo SET whqreverse=%s, whqreversetype=%s WHERE clubnumber=%s',
                    (fa, revloctype, clubnumber))
        except Exception as e:
            print(e)
    conn.commit()
    
    # Do the same for the locally-geocoded data
    c.execute("SELECT clubnumber, clubname, latitude, longitude FROM geo")
    for (clubnumber, clubname, latitude, longitude) in c.fetchall():
        # Now, reverse-geocode the address and add it to the table
        print(clubnumber, clubname, latitude, longitude)
        try:        
            rev = gmaps.reverse_geocode((latitude, longitude))[0]
            fa = rev['formatted_address']
            revloctype = rev['geometry']['location_type']
            print('        ', revloctype, fa)
            c.execute('UPDATE geo SET reverse=%s, reversetype=%s WHERE clubnumber=%s',
                    (fa, revloctype, clubnumber))
        except Exception as e:
            print(e)
    conn.commit()

        
  
