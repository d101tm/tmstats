#!/usr/bin/python

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os
import urllib2, csv
import googlemaps
from uncodeit import myclub

def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--override', dest='override', default='https://docs.google.com/spreadsheets/d/1DQy6JmPkH827WXk0MxD1OdyE3BNhwdZPwoX8pQPjrr4/export?format=csv&usp=sharing', help='Google Spreadsheet with overrides coordinates and info from the GEO table.')
    
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    gmaps = googlemaps.Client(key='AIzaSyAQJ_oe8p5ldJGJEQLSHvGpJcFocCRnxYg')
    
    data = urllib2.urlopen(parms.override, 'rb')
    reader = csv.DictReader(data)
    for row in reader:
        try:
            longitude = float(row['longitude'])
            latitude = float(row['latitude'])
            # Both are specified, so we use them
        except:
            if row['address']:
                # Nope, we have to geocode
                gres = gmaps.geocode(row['address'])  # Includes city, state, zip, country if needed
                # Get info from the database
                curs.execute('SELECT clubnumber, clubname, place, address, city, state, zip, whqlatitude, whqlongitude FROM geo WHERE clubnumber = %s', (row['clubnumber'],))
                (clubnumber, clubname, place, address, city, state, zip, whqlatitude, whqlongitude) = curs.fetchone()
                if row['place']:
                    place = row['place']
                club = myclub(clubnumber, clubname, place, address, city, state, zip, whqlatitude, whqlongitude).update(gres, curs)
    conn.commit()
    