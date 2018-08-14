#!/usr/bin/env python3

# @@TODO:  Combine "export" into this program.
# @@TODO:  Create areas from Divisions.

import dbconn, tmutil, sys, os
import math
from overridepositions import overrideClubPositions
import csv
import imp


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
    except Exception as e:
        arc = 0
 
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 3956  # to get miles
    
import random
random.seed(31415926)

def allocate(total, pieces):
    """ Evenly allocate 'total' items among 'pieces' groups, assigning leftovers randomly. """
    res = pieces * [total // pieces]  # Allocate evenly
    rem = total % pieces              # What's left?
    if rem > 0:
        for k in random.sample(range(pieces), rem):
            res[k] += 1
    return res

def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print(' '.join(args), file=file)
        
def computeDistances(clubs):
    """ For a group of clubs, compute the distance of each club from their center and from each other. """
    # Now, compute bounds and center
    bounds = Bounds()
    for c in list(clubs.values()):
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
                
class Color:
    pool = {}
    
    @classmethod
    def empty(self):
        self.pool = {}
        
    @classmethod
    def touse(self):
        ret = 0
        for c in list(self.pool.values()):
            if c.togo > 0:
                ret += 1
        return ret
        
    def __init__(self, name, colors, numareas):
        count = colors[name]
        self.name = name
        self.par = count // numareas       # How many each area will get for sure
        self.togo = count % numareas       # How many need to be split
        self.sizes = numareas * [self.par] 
        self.pool[name] = self
        
class Area:
    def __init__(self, division, number, size, green, yellow, red):
        self.size = size
        self.Green = green
        self.Yellow = yellow
        self.Red = red
        self.togo = self.size - (self.Green + self.Yellow + self.Red)
        self.number = number
        self.division = division
        self.clubs = {}
        print(self)
        
    def add(self, club):
        club.newarea = '%s%d' % (self.division, self.number + 1)
        self.clubs[club.clubnumber] = club
        self.__dict__[club.color] -= 1       # Number left to assign in this color
        
    def __repr__(self):
        return'Area %d size = %d, green = %d, yellow = %d, red = %d, togo = %d' % (self.number, self.size, self.Green, self.Yellow, self.Red, self.togo)
        

        
clubs = {}

class myclub:
    
    fields = ['clubnumber', 'clubname', 'latitude', 'longitude', 'place', 'address', 'city', 'state', 'zip', 'country', 'area', 'division', 'meetingday', 'meetingtime', 'color', 'goalsmet', 'activemembers']
    
    outfields = ['clubnumber', 'clubname', 'oldarea', 'newarea', 'color', 'goalsmet', 'activemembers', 'meetingday', 'meetingtime', 'place', 'address', 'city', 'state', 'zip', 'country',  'latitude', 'longitude', ]
    
    def __init__(self, *args):
        # Assign values
        for (f, v) in zip(self.fields, args):
            self.__dict__[f] = v
        # Fix up clubnumber
        self.clubnumber = '%s' % self.clubnumber
        self.distances = []
        self.oldarea = self.division + self.area
        clubs[self.clubnumber] = self
        if self.latitude == 0.0 or self.longitude == 0.0:
            print(self.clubname, self.clubnumber, 'has no location assigned.')
            
    def out(self):
        return ['%s' % self.__dict__[f] for f in self.outfields]
        
        
### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    imp.reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
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

    # Get data from clubs
    curs.execute('SELECT MAX(lastdate) FROM CLUBS')
    lastdate = curs.fetchone()[0]
    whereclause = 'WHERE c.division IN ("A", "B", "F", "G", "J") AND c.city != "Palo Alto" AND c.lastdate = "%s"' % lastdate
    c2 = conn.cursor()
    curs.execute('SELECT g.clubnumber, g.clubname, g.latitude, g.longitude, g.place, g.address, g.city, g.state, g.zip, g.country, c.area, c.division, c.meetingday, c.meetingtime FROM geo g INNER JOIN clubs c on g.clubnumber = c.clubnumber ' + whereclause)
    for row in curs.fetchall():
        c2.execute('SELECT color, goalsmet, activemembers FROM clubperf WHERE entrytype = "L" AND clubnumber = %s', (row[0],))
        row = [cell for cell in row] + [cell for cell in c2.fetchone()]
        myclub(*row)
        
        
    # Now, get the performance metrics of interest

        
    # If there are overrides to club positioning, handle them now
    if parms.mapoverride:
        overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey)
        
    # Now, remove A1-A4 until later
    all = list(clubs.keys())
    diva = {}
    for c in all:
        if clubs[c].division == 'A' and clubs[c].area in ('1', '2', '3', '4'):
            diva[c] = clubs[c]
            del clubs[c]
    
    # And compute distances, then sort clubs by their distance from the center
    computeDistances(clubs)
    away = [c for c in sorted(clubs, reverse=True, key=lambda c:clubs[c].centraldistance)]
         

    numdivs = 5
    numareas = 5
    divs = []
    divsizes = allocate(len(clubs), numdivs)       # Allocate clubs evenly
    divnum = -1                                    # So we can increment at the top of the loop
        
    # Now, we start clustering.  
    while away:
        divnum += 1
        c = clubs[away.pop(0)]
        print(c.clubname)
        c.distances.sort(key=lambda l:l[1])
        div = {c.clubnumber:c}   # Start with THIS club
        while len(div) < divsizes[divnum] and len(c.distances) > 0:
            (cnum, dist) = c.distances.pop(0)  # Take off the first item
            if cnum in away:
                #print "club %s is %s away from %s" % (clubs[cnum].clubname, dist, c.clubname)
                if (dist > 50):
                    print("too far!")
                    break  # and we're done with this one
                div[cnum] = clubs[cnum]
                del away[away.index(cnum)]
                #print len(away), 'clubs left in away'
        divs.append(div)
        #print '%d clubs assigned to division %d; %d left to look at.' % (len(div), divnum, len(away))
    
    divletters = ['','B','G','J','F','C','A']
    
    # Now, put division A back
    divs.append(diva)
    for c in diva:
        clubs[c] = diva[c]
    numdivs += 1    
    
    # Now, do clustering for each division.  We want to evenly divide Green, Yellow, and Red clubs.
    for divnum in range(numdivs):
        thisdiv = divs[divnum]
        divname = divletters[divnum+1]
        if divname == 'A':
            print('doing A')
            numareas = 4
        else:
            numareas = 5
        # Assign distances for this division
        computeDistances(thisdiv)
        away = [c for c in sorted(thisdiv, reverse=True, key=lambda c:thisdiv[c].centraldistance)]
      
        # Get distribution of clubs by strength
        colornames = ('Green', 'Yellow', 'Red')
        colors = {}
        for color in colornames:
            colors[color] = 0
        for c in list(thisdiv.values()):
            colors[c.color] += 1
        
        # Compute area sizes as evenly as possible
        areasizes = allocate(len(thisdiv), numareas)
        
        # Compute color allocations
        Color.empty()
        green = Color('Green', colors, numareas)
        yellow = Color('Yellow', colors, numareas)
        red = Color('Red', colors, numareas)

        
        # Figure out what each area can take
        areas = []
        for i in range(numareas):
            areas.append(Area(divname, i, areasizes[i], green.par, yellow.par, red.par))
            
        # Now, work through the colors and allocate them
        
        for name in colornames:
            thiscolor = Color.pool[name]
            avail = []
            for a in areas:
                avail.extend(a.togo * [a.number])
            assignees = random.sample(avail, thiscolor.togo)
            for a in assignees:
                areas[a].__dict__[name] += 1
                areas[a].togo -= 1
                thiscolor.togo -= 1
                

        # And now, do allocations of clubs to areas.
        
        areanum = -1                     # So we can increment at the top of the loop

        
        
        print(len(away))
        
        # Now, we start clustering.  
        while away:
            areanum += 1
            area = areas[areanum]
            c = clubs[away.pop(0)]
            print(c.clubname)
            c.distances.sort(key=lambda l:l[1])
            distances = {}
            for name in colornames:
                distances[name] = [item for item in c.distances if clubs[item[0]].color == name]

            
            area.add(c)               # Add this club to the area
            for name in colornames:
                while area.__dict__[name] > 0:
                    (cnum, dist) = distances[name].pop(0)  # Take off the closest candidate
                    if cnum in away:    # Still available?
                        area.add(clubs[cnum])   # Yes, add it to the area
                        del away[away.index(cnum)]  # And remove it from the candidate list
                     
                
            print('%d clubs assigned to area %d; %d left to look at.' % (len(area.clubs), areanum, len(away)))
            
        # Now, renumber the areas from South to North.
        southmost = {}
        for i in range(len(areas)):
            area = areas[i]
            southmost[i] = min(clubs[club].latitude for club in area.clubs)
        print(southmost)
        southmost = sorted(southmost, key=southmost.__getitem__)
        print(southmost)
        for i in range(len(southmost)):
            print('Processing area %d, which becomes %d' % (southmost[i], i))
            area = areas[southmost[i]]
            area.number = i
            for club in area.clubs:
                c = clubs[club]
                print(c.clubname, 'was in', c.newarea, 'moving to %s%d' % (c.newarea[0], i+1))
                clubs[club].newarea = '%s%d' % (clubs[club].newarea[0], i+1)
                print(c.clubname, 'moved to', c.newarea)
        
        
    
    
    outfile = open('grouped.csv', 'wb')
    writer = csv.writer(outfile)
    writer.writerow(myclub.outfields)
    for i in range(len(divs)):
        divnum = i+1
        for cnum in divs[i]:
            c = clubs[cnum]
            writer.writerow(c.out())
    outfile.close()
    
