#!/usr/bin/env python

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os, csv, re
from tmutil import distance_on_unit_sphere 
from makemap import Bounds

def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)

### Insert classes and functions here.  The main program begins in the "if" statement below.

def computeMaxDistance(locations):
    """locations is an array of clubname/lat/long tuples"""
    maxd = 0
    for i in range(len(locations)):
        (c1, lat1, lng1) = locations[i]
        for (c2, lat2, lng2) in locations[i+1:]:
            d = distance_on_unit_sphere(float(lat1), float(lng1), float(lat2), float(lng2))
            if (d > maxd):
                maxd = d
                maxc1 = c1
                maxc2 = c2
    return (maxd, maxc1, maxc2)
    
    
def makeareamap(area, locations):

    b = Bounds()
    mapbase="https://maps.googleapis.com/maps/api/staticmap?key=" + parms.staticmapsapikey + "&"
    mapparts = []

    clubinfo = []
    marker = 'A'
    for (clubname, latitude, longitude) in locations:
        b.extend(latitude, longitude)
        mapparts.append('markers=label:%s%%7C%s,%s' % (marker, latitude, longitude))
        marker = chr(ord(marker)+1)
    
    

 #   mapparts.append("center=%s" % (b.centercoords()))
    mapparts.append("size=640x640&scale=2")   # As large as possible, at least for now
    return '%s%s' % (mapbase, '&'.join(mapparts))

def openarea(outfile, area, color):
    ret = []
    ret.append('<div class="area clearfix">\n')
    ret.append('<h4>Area %s (%%.2f miles between %%s and %%s)</h4>\n' % area)
    ret.append('<div class="areainfo">')
    ret.append('<table class="areatable">\n')
    ret.append('<thead>\n')
    ret.append('<tr>\n')
    ret.append('<th class="marker">ID</th>')
    ret.append('<th class="cnum">Number</th><th class="cname">Name</th>')
    if color:
        ret.append('<th class="color">Color</th>')
    ret.append('<th class="members">Members</th><th class="goals">Goals</th><th class="loc">Location</th><th class="mtg">Time</th>\n')
    ret.append('</tr>\n')
    ret.append('</thead><tbody>\n')
    return ret
    
def closearea(outfile, text, locations):
    # This is gross and relies on knowing what "openarea" does.
    
    if len(locations) > 1:
        text[1] = text[1] % computeMaxDistance(locations)
        outfile.write(''.join(text))
    else:
        text[1] = re.sub(r'\(.*\)', '', text[1])  # Remove distance
        outfile.write(''.join(text))
    outfile.write('</tbody></table>\n')
    outfile.write('</div>\n')
    if len(locations) > 1:
        outfile.write('<div class="areamap">')
        outfile.write('<img src="%s" width="640px">' % makeareamap(text[1].split()[2], locations))
        outfile.write('</div>')
    outfile.write('</div>\n')
    
def opendiv(outfile, division):
    outfile.write('<div class="division"><h3>Division %s</h3>\n' % division)
    
def closediv(outfile):
    outfile.write('</div>\n')

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--infile', default='d101align.csv')
    parms.add_argument('--outfile', default='d101location.html')
    parms.add_argument('--color', action='store_true')
    parms.add_argument('--mapdir', default=None, help='Directory to use for the area map files.')
    
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    # Simple and ugly program to create location/time realignment listings
    outfile = open(parms.outfile, 'w')
    outfile.write("""
    <html>
    <head>
    <style type="text/css">
    
    
     body {font-family: Arial }
    

    .area {margin-bottom: 12pt; width: 100%; page-break-inside: avoid; display: block; clear: both;}

    .division {border: none; break-before: always !important; display: block; float: none; position: relative; page-break-inside: avoid; page-break-after: always !important;}
      .areatable {font-size: 10pt; border: 1px solid black; border-collapse: collapse;}
      .myrow td {vertical-align: top; padding-left: 3px; padding-right: 3px; border: 1px solid black;}
      th {font-weight: bold; border: 1px solid black; border-collaps: collapse;}
      .ghost {background-color: #C0C0C0;}
      .myrow {border: 1px solid black; border-collapse: collapse;}
      .cnum {text-align: right; width: 7%;}
      .cname {text-align: left; width: 15%;}
      .color {text-align: left; width: 5%;}
      .marker {text-align: left; width: 5%; font-weight: bold;}
      .red {background-color: red;}
      .yellow {background-color: yellow;}
      .green {background-color: green;}
      .goals {text-align: right; width: 5%;}
      .members {text-align: right; width: 5%;}
      .mtg {text-align: left; width: 25%;}
      .loc {text-align: left; width: 30%;}
      
      .area {
          width: 95%;
          margin: auto;
          padding: 10px;
      }
      .areainfo {
          width: 45%;
          float: left;
      }
      .areamap {
          margin-left: 50%;
      }
      
      .clearfix:after {
        content: "";
        display: table;
        clear: both;
      }
    </style>
    </head>
    <body>
    """)
    reader = csv.DictReader(open(parms.infile, 'rbU'))
    thisdiv = ''
    thisarea = ''
    locations = []
    for row in reader:
        area = row['newarea']
        div = area[0]
        if thisarea and thisarea != area:
            closearea(outfile, accum, locations)
            locations = []
        if thisdiv and thisdiv != div:
            closediv(outfile)
        if thisdiv != div:
            opendiv(outfile, div)
        if thisarea != area:
            accum = openarea(outfile, area, parms.color)
            marker = 'A'
        thisarea = area
        thisdiv = div
        outrow = []
        row['closing'] = '<br />(Probably closing)' if row['likelytoclose'] else ''
        outrow.append('<tr class="myrow%s">' % (' ghost' if row['likelytoclose'] else ''))
        outrow.append('  <td class="marker">%s</marker>' % marker)
        outrow.append('  <td class="cnum">{clubnumber}</td><td class="cname">{clubname}{closing}</td>')
        if parms.color:
            outrow.append('  <td class="color {color}">{color}</td>\n')
        outrow.append('  <td class="members">{activemembers}</td>\n')
        outrow.append('  <td class="goals">{goalsmet}</td>\n')
        outrow.append('  <td class="loc">{place}<br />{address}<br />{city}, {state} {zip}</td>')
        outrow.append('  <td class="mtg">{meetingday}<br />{meetingtime}</td>')
        outrow.append('</tr>')
        accum.append(('\n'.join(outrow)).format(**row))
        locations.append((row['clubname'], row['latitude'], row['longitude']))
        marker = chr(ord(marker)+1)
        
    closearea(outfile, accum, locations)
    closediv(outfile)
    outfile.write("</body></html>\n")
    outfile.close()
    



