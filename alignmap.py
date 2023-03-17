#!/usr/bin/env python3
""" Build map for tentative alignment """

import dbconn, tmutil, sys, os
from simpleclub import Club
from tmutil import overrideClubs, removeSuspendedClubs
from overridepositions import overrideClubPositions
from makemap import makemap, setClubCoordinatesFromGEO
from tmglobals import tmglobals
from datetime import datetime
myglobals = tmglobals()

def getMapSkeleton(tmyear, district):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
    
    <meta charset="utf-8" />
    
    <title>Map of Proposed {tmyear}-{1+tmyear} District {district} Alignment</title>
    
    <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key=AIzaSyD-9pjELs27IRAzeKOlS2GYg95m-zzvuZI">
    </script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
    <style type="text/css">
     div.wrapper {{
        margin: 0px;
        display: none;
      }}
     
    span.activeTab, span.passiveTab, span.hoverTab {{
     -moz-border-radius-topleft: 0px;
     -moz-border-radius-topright: 0px;
     -webkit-border-top-left-radius: 0px;
     -webkit-border-top-right-radius: 0px;
     border-top-left-radius: 0px;
     border-top-right-radius: 0px;
    }}
    
     span.activeTab {{
        margin-right:-5px;
        padding-left:7px;
        padding-right:7px;
        font-weight:bold;
        font-size:16px;
        border:1px solid #AAA;
        color:#5D5CA0;
        background-color:#FFF;
        border-bottom:2px solid #FFF;
     }}
    
    *span.activeTab {{
        /* IE border top fix */
        zoom:1;
        /* IE border bottom fix */
        position:relative;
        bottom:-1px;
    }}
    
     span.passiveTab {{
        margin-right:-5px;
        padding-left:8px;
        padding-right:8px;
        border:1px solid #AAA;
        font-size:12px;
        cursor:default;
        background-color:#E9E9E9;
        color:#006;
        border-bottom:2px solid #E9E9E9;
    }}
    
     span.hoverTab {{
        margin-right:-5px;
        padding-left:7px;
        padding-right:7px;
        font-size:14px;
        border:none;
        border-bottom:2px solid #DCDCDC;
        cursor:pointer;
        background-color:#DCDCDC;
        color:#5676EA;
    }}
     div.cardContent {{
        padding: 1px 1px 1px 0px;
        border-top:1px solid #CACACA;
        overflow:auto;
        display:none;
        overflow:auto; 
    }}
     div.minimap {{
        border: solid 1px gray; 
        border-width: 1px 2p 3px 4px;
        padding: 3px;
        font-size: 1.0em;
        overflow:auto; 
      }}
     
    #map {{width:98%; height:700px; border: 2px solid silver;}}
    
    </style>
    
    </head>
    <body>
    
    <div id="mapinfo">
    <div id="map"></div>
    </div>
    
    <script type="text/javascript" src="mapcode.js"></script>
    <script type="text/javascript" src="setcolors.js"></script>
    <script type-"text/javascript" src="d101newmarkers.js"></script>
    <script type-"text/javascript" src="d101borders.js"></script>
    
    </body>
    </html>
    '''

def inform(*args, **kwargs):
    """ Print information to 'file', depending on the verbosity level.
        'level' is the minimum verbosity level at which this message will be printed. """
    level = kwargs.get('level', 0)
    file = kwargs.get('file', sys.stderr)

    if parms.verbosity >= level:
        print(' '.join(args), file=file)

if __name__ == "__main__":

    import tmparms

    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
    parms.add_argument('--verbose', '-v', action='count', default=0)
    parms.add_argument('--outfile', dest='outfile', default=None)
    parms.add_argument('--outdir', default='${WORKDIR}', help='Where to put the output files')
    parms.add_argument('--divfile', dest='divfile', default=None)
    parms.add_argument('--pindir', dest='pindir', default=None, help='Directory with pins; default uses Google pins')
    parms.add_argument('--mapoverride', dest='mapoverride', default=None, help='Google spreadsheet with overriding address and coordinate information')
    parms.add_argument('--testalign', dest='testalign', default=None)
    parms.add_argument('--district', dest='district')
    parms.add_argument('--makedivisions', dest='makedivisions', action='store_true')
    parms.add_argument('--nomakedivisions', dest='nomakedivisions', action='store_true')
    parms.add_argument('--showdetails', dest='showdetails', action='store_true')

    # Do global setup 
    myglobals.setup(parms, sections=['alignment'])
    conn = myglobals.conn
    curs = myglobals.curs

    # Compute verbosity level.  Default is zero.
    parms.verbosity = parms.verbose - parms.quiet

    # Make choices for unspecified options depending on the District
    if parms.district == '4':
        if parms.makedivisions or parms.nomakedivisions:
            parms.makedivisions = parms.makedivisions
    elif parms.district == '101':
        if parms.makedivisions or parms.nomakedivisions:
            parms.makedivisions = not parms.nomakedivisions
    if not parms.outfile:
        parms.outfile = 'd%snewmarkers.js' % parms.district
    if not parms.divfile:
        parms.divfile = 'd%sborders.js' % parms.district



    # Promote information from parms.makemap if not already specified
    parms.mapoverride = parms.mapoverride if parms.mapoverride else parms.makemap.get('mapoverride',None)
    parms.pindir = parms.pindir if parms.pindir else parms.makemap.get('pindir',None)


    # Get the clubs
    clubs = Club.getClubsOn(curs)

    # Remove suspended clubs unless there's a test alignment
    if not parms.testalign:
        clubs = removeSuspendedClubs(clubs, curs)
    
    # Get coordinates
    setClubCoordinatesFromGEO(clubs, curs, removeNotInGeo=False)

    # If there are overrides to club positioning, handle them now
    # This will also add secret clubs if they exist
    if parms.mapoverride:
        overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey, createnewclubs=True)
    

    # Process new grouping
    if parms.testalign:
        clubs = overrideClubs(clubs, parms.testalign)

    # Delete clubs at (0.0, 0.0)
    for cnum in clubs:
        c = clubs[cnum]
        if c.latitude == 0.0 and c.longitude == 0.0:
            print('Deleting', c)
            del clubs[cnum]

    # Create the skeleton map
    with open(os.path.join(parms.outdir, parms.mapfile), 'w') as skeleton:
        skeleton.write(getMapSkeleton(myglobals.tmyear, parms.district))

    # Make the club entries for the map
    outfile = open(os.path.join(parms.outdir, parms.outfile), 'w')
    makemap(outfile, clubs, parms, bequiet=True, timestamp=f'Created at {datetime.now().strftime("%B %-d, %Y at %-H:%M %p")}')
    outfile.close()

    if parms.makedivisions:
        outfile = open(os.path.join(parms.outdir, parms.divfile), 'w')        
        import pytess
        from shapely.ops import cascaded_union
        from shapely.geometry import Polygon

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
        from d101boundary import d101
        d101 = Polygon(d101)

        sites = {}         # (lat,lng) ==> Division
        for c in list(clubs.values()):
            if c.onlineonly:
                continue  # Ignore online-only clubs
            point = (c.latitude, c.longitude)
            if point in sites:
                if c.division != sites[point]:
                    sites[point] += c.division
            else:
                sites[point] = c.division

        points = [loc for loc in list(sites.keys()) if len(sites[loc]) == 1]

        # Gross hack to put Gilroy in Division A
        Gilroy = (37.005782, -121.568275)
        sites[Gilroy] = 'A'
        points.append(Gilroy)

        # And another gross hack for Rancho San Antonio
        RanchoSanAntonio = (37.321972, -122.096326)
        sites[RanchoSanAntonio] = 'B'
        points.append(RanchoSanAntonio)
        
        voronoipolys = pytess.voronoi(points, buffer_percent=200)


        # Compute the union of polygons for each division and write it to the file
        polygons = {}
        for (point, poly) in voronoipolys:
            if point in sites:
                div = sites[point]
                if div not in polygons:
                    polygons[div] = []
                polygons[div].append(Polygon(poly))

        def dopoly(outfile, outline, div, num=0):
            if num > 0:
                varname = '%s%d' % (div, num)
            else:
                varname = div
            outfile.write("""
            var div%s = [
            """ % varname)
            outfile.write(',\n'.join(['new g.LatLng(%s, %s)' % p for p in outline.exterior.coords]))
            outfile.write("""];
            DrawHull(div%s, fillcolors["%s"]);
            """ % (varname,d))

        for d in polygons:
            outline = polygons[d][0]
            for p in polygons[d][1:]:
                outline = outline.union(p.buffer(0))
            outline = outline.intersection(d101)

            if outline.geom_type == 'Polygon':
                dopoly(outfile, outline, d)
            else:
                 print(('Division %s has %d pieces' % (d, len(outline.geoms))))
                 num = 0
                 for poly in outline.geoms:
                     num += 1
                     dopoly(outfile, poly, d, num)

        # Finally, draw the D101 boundary

        outfile.write("""


        function DrawBoundary(hullPoints) {
             polyline = new google.maps.Polygon({
              map: map,
              paths:hullPoints,
              fillColor:'#FFFFC0',
              strokeWidth:2,
              fillOpacity:0.2,
              strokeColor:'#000000',
              strokeOpacity:0.7
             })
             };

        var d101 = [
        """)
        outfile.write(',\n'.join(['new g.LatLng(%s, %s)' % p for p in d101.exterior.coords]))
        outfile.write("""];
        DrawBoundary(d101);
        """)

        outfile.close()
