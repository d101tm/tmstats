#!/usr/bin/env python

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os
from simpleclub import Club
from tmutil import overrideClubs, removeSuspendedClubs
from overridepositions import overrideClubPositions
from makemap import makemap, setClubCoordinatesFromGEO
from geometry import convexHull
import pytess
from shapely.ops import cascaded_union
from shapely.geometry import Polygon
from d101 import d101

def inform(*args, **kwargs):
    """ Print information to 'file', depending on the verbosity level. 
        'level' is the minimum verbosity level at which this message will be printed. """
    level = kwargs.get('level', 0)
    file = kwargs.get('file', sys.stderr)
    
    if parms.verbosity >= level:
        print >> file, ' '.join(args)

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
    parms.add_argument('--verbose', '-v', action='count', default=0)
    parms.add_argument('--outfile', dest='outfile', default='newmarkers.js')
    parms.add_argument('--newAlignment', dest='newAlignment', default=None, help='Overrides area/division data from the CLUBS table.')
    parms.add_argument('--pindir', dest='pindir', default=None, help='Directory with pins; default uses Google pins')
    parms.add_argument('--mapoverride', dest='mapoverride', default=None, help='Google spreadsheet with overriding address and coordinate information')
    parms.add_argument('--testalign', dest='testalign', default='grouped.csv')
    parms.add_argument('--district', dest='district')
    # Add other parameters here
    parms.parse() 
    
    # Compute verbosity level.  Default is zero.
    parms.verbosity = parms.verbose - parms.quiet

    
    # Promote information from parms.makemap if not already specified
    parms.mapoverride = parms.mappoverride if parms.mapoverride else parms.makemap.get('mapoverride',None)
    parms.pindir = parms.pindir if parms.pindir else parms.makemap.get('pindir',None)
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Get the clubs
    clubs = Club.getClubsOn(curs)
    
    # Remove suspended clubs
    clubs = removeSuspendedClubs(clubs, curs)
    
    # Get coordinates
    setClubCoordinatesFromGEO(clubs, curs)
    
    # If there are overrides to club positioning, handle them now
    if parms.mapoverride:
        overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey)
        
    
    # Process new grouping
    if parms.testalign:
        import csv
        infile = open(parms.testalign, 'rbU')
        reader = csv.reader(infile)
        newclubs = {}
        newdivs = {}
        clubsbypos = {}
        line = reader.next()  # Skip header
        for line in reader:
            newdiv = line[3][0]
            newarea = line[3][1:]
            clubnum = line[0]
            newclubs[clubnum] = (newdiv, newarea)
            c = clubs[clubnum]
            c.division = newdiv
            c.area = newarea
            if newdiv not in newdivs:
                newdivs[newdiv] = []
            latitude = float(c.latitude)
            longitude = float(c.longitude)
            coords = (latitude, longitude)
            clubsbypos[coords] = c
            newdivs[newdiv].append(coords)
        for c in clubs.keys():
            if c not in newclubs:
                del clubs[c]    

    


    outfile = open(parms.outfile, 'w')
    
    makemap(outfile, clubs, parms)
    
    outfile.write("""
    
    
    function DrawHull(hullPoints, color) {
         polyline = new google.maps.Polygon({
          map: map,
          paths:hullPoints, 
          fillColor:color,
          strokeWidth:2, 
          fillOpacity:0.5, 
          strokeColor:color,
          strokeOpacity:0.7
         })
         };
    """)
    
    # Now, compute the new divisions.
    d101 = Polygon(d101)
    
    sites = {}         # (lat,lng) ==> Division
    for c in clubs.values():
        point = (c.latitude, c.longitude)
        if point in sites:
            if c.division != sites[point]:
                sites[point] += c.division
        else:
            sites[point] = c.division
            
    points = [loc for loc in sites.keys() if len(sites[loc]) == 1]
    voronoipolys = pytess.voronoi(points, buffer_percent=200)
           

    # Compute the union of polygons for each division and write it to the file
    polygons = {}
    for (point, poly) in voronoipolys:
        if point in sites:
            div = sites[point]
            if div not in polygons:
                polygons[div] = []
            polygons[div].append(Polygon(poly))
            
    for d in polygons:
        outline = polygons[d][0]
        for p in polygons[d][1:]:
            outline = outline.union(p)
        outline = outline.intersection(d101)
        outfile.write("""
        var div%s = [
        """ % d)
        if outline.type == 'Polygon':
            outfile.write(',\n'.join(['new g.LatLng(%s, %s)' % p for p in outline.exterior.coords]))
        else:
             for poly in outline.geoms:
                 res = []
                 res.append(',\n'.join(['new g.LatLng(%s, %s)' % p for p in poly.exterior.coords]))
             outfile.write(',\n'.join(res))
        outfile.write("""];
        DrawHull(div%s, fillcolors["%s"]);
        """ % (d,d))
        
       
    
    

    outfile.close()
   