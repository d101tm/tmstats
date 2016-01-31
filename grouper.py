#!/usr/bin/python

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os
import math
from overridepositions import overrideClubPositions
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
    
    def __init__(self, clubname, clubnumber, latitude, longitude, place, address, city, state, zip, country, area, division):
        clubnumber = '%s' % clubnumber
        self.clubname = clubname
        self.clubnumber = clubnumber 
        self.latitude = latitude
        self.longitude = longitude
        self.place = place
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country
        self.distances = []
        self.area = area
        self.division = division
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
    parms.add_argument('--mapoverride', dest='mapoverride', default=None, help='Google spreadsheet with overriding address and coordinate information')
    # Add other parameters here
    parms.parse() 
    
    # Promote information from parms.makemap if not already specified
    parms.mapoverride = parms.mappoverride if parms.mapoverride else parms.makemap.get('mapoverride',None)
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    
    from makemap import Bounds
    bounds = Bounds()

    curs.execute('SELECT MAX(lastdate) FROM CLUBS')
    lastdate = curs.fetchone()[0]

    curs.execute('SELECT g.clubname, g.clubnumber, g.latitude, g.longitude, g.place, g.address, g.city, g.state, g.zip, g.country, c.area, c.division FROM geo g INNER JOIN clubs c on g.clubnumber = c.clubnumber WHERE c.division IN ("A", "B", "F", "G", "J") AND c.city != "Palo Alto" AND c.lastdate = %s', (lastdate,))
    for row in curs.fetchall():
        myclub(*row)

        
    # If there are overrides to club positioning, handle them now
    if parms.mapoverride:
        overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey)
        
    # Now, remove A1-A4
    all = clubs.keys()
    for c in all:
        if clubs[c].division == 'A' and clubs[c].area in ('1', '2', '3', '4'):
            del clubs[c]
    
        
    # Now, compute bounds and center
    bounds = Bounds()
    for c in clubs.values():
        bounds.extend(c.latitude, c.longitude)
        
    bounds.clat = (bounds.north + bounds.south) / 2.0
    bounds.clong = (bounds.east + bounds.west) / 2.0
    
    for c in clubs:
        clubs[c].centraldistance = distance_on_unit_sphere(clubs[c].latitude, clubs[c].longitude,
                                bounds.clat, bounds.clong)
        for d in clubs:
            if c > d:
                dist = distance_on_unit_sphere(clubs[c].latitude, clubs[c].longitude, clubs[d].latitude, clubs[d].longitude)
                clubs[c].distances.append((d, dist))
                clubs[d].distances.append((c, dist))
                
                
     
    away = [c for c in sorted(clubs, reverse=True, key=lambda c:clubs[c].centraldistance)]
         

    
    groups = []
    groupmax = math.floor(len(away) / 5)
    print groupmax
    print len(away), 'clubs'
    # Now, we start clustering.  
    while away:
        c = clubs[away.pop(0)]
        print c.clubname
        c.distances.sort(key=lambda l:l[1])
        group = [c.clubnumber]   # Start with THIS club
        while len(group) < groupmax and len(c.distances) > 0:
            (cnum, dist) = c.distances.pop(0)  # Take off the first item
            if cnum in away:
                print "club %s is %s away from %s" % (clubs[cnum].clubname, dist, c.clubname)
                if (dist > 50):
                    print "too far!"
                    break  # and we're done with this one
                group.append(cnum)
                del away[away.index(cnum)]
                print len(away), 'clubs left in away'
        groups.append(group)
        print len(group), 'clubs in group;', len(away), 'left to look at'        
    
    divletters = ['','B','G','J','F','C']
    
    outfile = open('grouped.csv', 'wb')
    writer = csv.writer(outfile)
    writer.writerow(['newdiv', 'newarea', 'clubnumber', 'clubname', 'oldarea', 'address', 'city', 'state', 'zip', 'latitude', 'longitude' ])
    for i in xrange(len(groups)):
        groupnum = i+1
        for cnum in groups[i]:
            c = clubs[cnum]
            
            writer.writerow((divletters[groupnum], 1, cnum, c.clubname, '%s%s' % (c.division, c.area), c.address, c.city, c.state, c.zip, c.latitude, c.longitude))
    outfile.close()
    
