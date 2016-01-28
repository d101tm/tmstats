#!/usr/bin/python

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os
import math
import csv

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
    except Exception, e:
        print e
        print '(%f, %f), (%f, %f), %f' % (lat1, long1, lat2, long2, cos)
        arc = 0
 
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 3956  # to get miles



def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)
        
clubs = {}

class myclub:
    
    def __init__(self, clubname, clubnumber, latitude, longitude):
        self.clubname = clubname
        self.clubnumber = clubnumber
        self.latitude = latitude
        self.longitude = longitude
        self.distances = {}
        clubs[clubnumber] = self
        if latitude == 0.0 or longitude == 0.0:
            print clubname
        
        
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
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    c2 = conn.cursor()
    # Your main program begins here.
    
    info = []
    
    outfile = open('realign.csv', 'wb')
    writer = csv.writer(outfile)

    curs.execute('SELECT MAX(lastdate) FROM CLUBS')
    lastdate = curs.fetchone()[0]

    print curs.execute('SELECT g.clubnumber, g.clubname, c.division, c.area,c.address, c.city,c.state,c.zip,  c.meetingday, c.meetingtime FROM geo g LEFT OUTER JOIN (SELECT clubnumber, latitude, longitude, division, area, address, city, state, zip, meetingday, meetingtime from clubs where lastdate = %s) c on g.clubnumber = c.clubnumber  WHERE c.division IN ("A", "B", "F", "G", "J") AND c.city != "Palo Alto"', (lastdate,))
    
    writer.writerow(['clubnumber', 'clubname', 'division', 'area', 'address', 'city', 'state', 'zip', 'meetingday', 'meetingtime', 'color', 'goals', 'activemembers'])
    for row in curs.fetchall():
        c2.execute('SELECT color, goalsmet, activemembers FROM clubperf WHERE entrytype = "L" AND clubnumber = %s', (row[0],))
        row = [cell for cell in row] + [cell for cell in c2.fetchone()]
        info.append(row)
        
        
    info.sort(key=lambda l:('%s%s %s' % (l[2], l[3], l[1].zfill(8))))
    for row in info:
        writer.writerow(row)
            
    sys.exit()
    for (clubname, clubnumber, latitude, longitude) in curs.fetchall():
        myclub(clubname, clubnumber, latitude, longitude)
        bounds.extend(latitude, longitude)
    
    for c in clubs:
        for d in clubs:
            if c > d:
                dist = distance_on_unit_sphere(clubs[c].latitude, clubs[c].longitude, clubs[d].latitude, clubs[d].longitude)
                clubs[c].distances[d] = dist
                clubs[d].distances[c] = dist
                
    
    
