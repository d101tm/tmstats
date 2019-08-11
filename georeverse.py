#!/usr/bin/env python3
""" Reverse-Geocode coordinates from WHQ and from our encoding and add them to the GEO table. """
import sys

import googlemaps

import tmglobals
import tmparms

myglobals = tmglobals.tmglobals()


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print(' '.join(args), file=file)
        


### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":

    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
    
    # Do global setup
    myglobals = myglobals.setup(parms)
    conn = myglobals.conn
    c = myglobals.curs


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

        
  
