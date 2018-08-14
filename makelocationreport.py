#!/usr/bin/env python3
"""Create the proposed relocation report"""

import tmutil, sys, os, csv, re
from tmutil import distance_on_unit_sphere 
from makemap import Bounds
from simpleclub import Club
from datetime import datetime
import tmglobals
globals = tmglobals.tmglobals()

minimalhead = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
<title>Summary Proposed Alignment</title>
<style type="text/css">


 body {font-family: Arial; font-size: 10pt;}


.area {width: 100%; page-break-inside: avoid; display: block; clear: both;}
    .divname {font-size: 200%; font-weight: bold; text-align: center; margin-bottom: 20px;}
    .areaname {font-size: 150%; font-weight: bold; text-align: center;}

    .division {display: block; float: none; position: relative; page-break-inside: avoid; }
.notfirst {break-before: page !important; page-break-before: always !important;}
  .areatable {font-size: 10pt; border: 1px solid black; border-collapse: collapse;}
  .myrow td {vertical-align: top; padding-left: 3px; padding-right: 3px; border: 1px solid black; border-collapse: collapse}
  th {font-weight: bold; border: 1px solid black; border-collapse: collapse;}
  .ghost {background-color: #C0C0C0;}
  .myrow {border: 1px solid black; border-collapse: collapse;}
 .cnum {text-align: right; width: 10%; padding-left: 2px; padding-right: 2px;}
  .cname {text-align: left; width: 80%; font-weight: bold; padding-left: 2px;}
  .from {text-align: left; width: 5%; padding-left: 2px; padding-right: 2px;}
  .gone {font-style: italic; background-color: #E0E0E0}
  
  .area {
      width: 95%;
      margin: auto;
      padding: 10px;
  }


@media all and (min-width: 768px) {
  .areapair {clear: both; margin-top: 30px;}
  .left {
      width: 45%; float: left; }
  .right {
      width: 45%; margin-left: 50%; }
  }

@media all and (max-width: 767px) {
  .left {margin-top: 20px;}
  .right {margin-top: 20px;}
  }
@media not print {
    .divname { border-top: 2px solid black; padding-top: 10px; }
}
@media print {
    .division {border: none;}
}
  
  .clearfix:after {
    content: "";
    display: table;
    clear: both;
    
  .clearfix:before {
    content: "";
    display: table;
    clear: both;}
  }
</style>
</head>
<body>
    """



global parms
def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print(' '.join(args), file=file)

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
    if parms.map:
        ret.append('<th class="marker">ID</th>')
    ret.append('<th class="from">From</th>')
    ret.append('<th class="cnum">Number</th><th class="cname">Name</th>')
    if parms.color:
        ret.append('<th class="members">Members</th><th class="goals">Goals</th>')
    ret.append('<th class="loc">Location</th><th class="mtg">Time</th>\n')
    ret.append('</tr>\n')
    ret.append('</thead><tbody>\n')
    return ret
    
def closearea(outfile, text, locations, gonefrom):
    # This is gross and relies on knowing what "openarea" does.
    
    if len(locations) > 1:
        text[1] = text[1] % computeMaxDistance(locations)
        outfile.write(''.join(text))
    else:
        text[1] = re.sub(r'\(.*\)', '', text[1])  # Remove distance
        outfile.write(''.join(text))
    outfile.write('</tbody></table>\n')
    if gonefrom:
        outfile.write('<p>Club%s leaving area:</p>\n' % ('' if len(gonefrom) == 1 else 's'))
        outfile.write('<ul class="gonelist">\n')
        for club in sorted(gonefrom, key=lambda c: c.clubname.lower()):
            outfile.write('<li>%s' % club.clubname)
            if club.eligibility == 'Suspended':
                outfile.write(' <b>(Suspended)</b>')
            elif club.newarea and club.newdivision.strip():
                outfile.write(' (To %s%s)' % (club.newdivision, club.newarea))
            else:
                outfile.write(' (Moved out of Division 101)')
            outfile.write('</li>\n')
        outfile.write('</ul>\n')
    outfile.write('</div>\n')
    if len(locations) > 1 and parms.map:
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
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
    parms.add_argument('--infile', default='d101align.csv')
    parms.add_argument('--outfile', default='d101location.html')
    parms.add_argument('--outdir', default=None, help='Where to put the output file')
    parms.add_argument('--color', action='store_true')
    parms.add_argument('--map', action='store_true')
    parms.add_argument('--minimal', default='d101minimal.html')
    
    # Do global setup
    globals.setup(parms)
    conn = globals.conn
    curs = globals.curs
 
    
    # Your main program begins here.


    # Write the header of the output file
    outfile = open(os.path.join(parms.outdir, parms.outfile),'w')
    outfile.write("""
    <html>
    <head>
    <title>Detailed Proposed Alignment</title>
    <style type="text/css">
    
    
     body {font-family: Arial }
    
    .divname {font-size: 200%; font-weight: bold; text-align: center; margin-bottom: 20px;}

    .area {margin-bottom: 12pt; width: 100%; page-break-inside: avoid; display: block; clear: both;}

    .division {border: none; break-before: always !important; display: block; float: none; position: relative; page-break-inside: avoid; page-break-after: always !important;}
      .areatable {font-size: 10pt; border: 1px solid black; border-collapse: collapse; page-break-inside:avoid; break-inside: avoid; -webkit-column-break-inside: avoid;}
      .myrow td {vertical-align: top; padding-left: 3px; padding-right: 3px; border: 1px solid black;}
      th {font-weight: bold; border: 1px solid black; border-collaps: collapse;}
      .ghost {background-color: #C0C0C0;}
      .myrow {border: 1px solid black; border-collapse: collapse;}
      .cnum {text-align: right; width: 7%;}
      .cname {text-align: left; width: 15%; font-weight: bold;}
      .color {text-align: left; width: 5%;}
      .marker {text-align: left; width: 5%; font-weight: bold;}
      .from {text-align: center; width: 5%;}
      .red {background-color: red;}
      .yellow {background-color: yellow;}
      .green {background-color: lightgreen;}
      .goals {text-align: right; width: 5%;}
      .members {text-align: right; width: 5%;}
      .mtg {text-align: left; width: 25%;}
      .loc {text-align: left; width: 30%;}
      
      .area {
          width: 95%;
          margin: auto;
          padding: 10px;
      }
""")
    if parms.map:
        outfile.write("""
      .areainfo {
          width: 45%;
          float: left;
      }
      .areamap {
          margin-left: 50%;
      }
""")
    else:
        outfile.write("""
      .areainfo { width: 95%; float: left;}
""")
      
    outfile.write("""
      .clearfix:after {
        content: "";
        display: table;
        clear: both;
      }
    </style>
    </head>
    <body>
    """)

    # Get club information from the database as of today
    clubs = Club.getClubsOn(curs, date=datetime.today().strftime('%y-%m-%d'))

    # Now, add relevant club performance information.  If there are clubs in the 
    # performance data which aren't in the master list from TMI, note it and add
    # them anyway.

    perffields = ['clubnumber', 'clubname', 'district', 'area', 'division', 'eligibility', 'color', 'membase', 'activemembers', 'goalsmet']

    curs.execute("SELECT clubnumber, clubname, district, area, division, clubstatus as eligibility, color, membase, activemembers, goalsmet FROM clubperf WHERE entrytype = 'L' and district = %s", (parms.district,))

    for info in curs.fetchall():
        clubnum = Club.stringify(info[0])
        try:
            club = clubs[clubnum]
            club.addvalues(info, perffields)
        except KeyError:
            print('Club %s (%d) not in current CLUBS table, patching in.' % (info[1], info[0]))
            clubs[clubnum] = Club(info, perffields)
            clubs[clubnum].charterdate = ''
            
    # Now patch in suspension dates

    curs.execute("SELECT clubnumber, suspenddate FROM distperf WHERE entrytype = 'L' and district = %s", (parms.district,))
    for (clubnum, suspenddate) in curs.fetchall():
        if clubnum in clubs:
            clubs[clubnum].addvalues(['suspended'],[suspenddate])
          

    # And read in the alignment.  
    reader = csv.DictReader(open(parms.infile, 'r'))
    alignfields = ['newarea', 'newdivision', 'likelytoclose', 'meetingday', 'meetingtime', 'place', 'address', 'city',
            'state', 'zip', 'latitude', 'longitude']
    for row in reader:
        newarea = row['newarea']
        row['newarea'] = newarea[1:]
        row['newdivision'] = newarea[0]
        try:
            club = clubs[club.stringify(row['clubnumber'])]
        except KeyError:
            print('club %s (%s) is new.' % (row['clubname'], row['clubnumber']))
            clubvalues = [row['clubnumber'], row['clubname'], ' ', ' ', parms.district, 0, 0, 'Prospective', '']
            clubfields = ['clubnumber', 'clubname', 'area', 'division', 'district', 
                    'activemembers', 'goalsmet', 'eligibility', 'color']
            club = Club(clubvalues, fieldnames=clubfields)
            clubs[club.stringify(row['clubnumber'])] = club
        alignvalues = [row[p] for p in alignfields]
        club.updatevalues(alignvalues, alignfields)


        
    # Assign clubs to their new areas.  If they've changed, also assign to the area they're leaving
    gonefrom = {}
    newareas = {}
    divs = {}

    for c in list(clubs.values()):
        old = c.division + c.area
        try:
            new = c.newdivision + c.newarea
        except AttributeError:
            new = '  '
            c.newdivision = ' '
            c.newarea = ' '
        if old != new:
            c.was = '(from %s)' % old
        else:
            c.was = '&nbsp;'
        if old not in gonefrom:
            gonefrom[old] = []
        if new not in newareas:
            newareas[new] = []
        try:
            if c.eligibility != 'Suspended':
                newareas[new].append(c)
                if old != new:
                    gonefrom[old].append(c)
                if c.newdivision not in divs:
                    divs[c.newdivision] = {}
                divs[c.newdivision][new] = new
            else:
                gonefrom[old].append(c)
        except AttributeError:
            print('no eligibility for', c.clubname)


    for div in sorted(divs.keys()):
        if div.strip():
            areas = sorted(divs[div].keys())
            opendiv(outfile, div)
            for area in areas:
                locations = []
                accum = openarea(outfile, area, parms.color)
                for c in sorted(newareas[area], key=lambda x:int(x.clubnumber)):
                    marker = 'A'
                    row = c.__dict__  
                    outrow = []
                    row['closing'] = '<br />(probably closing)' if row['likelytoclose'] else ''
                    outrow.append('<tr class="myrow%s">' % (' ghost' if row['likelytoclose'] else '') )
                    if parms.map:
                        outrow.append('  <td class="marker">%s</marker>' % marker)
                    oldarea = c.division + c.area
                    newarea = c.newdivision + c.newarea
                    outrow.append('  <td class="from">%s</td>' % (oldarea if oldarea != newarea else ''))
                    outrow.append('  <td class="cnum">{clubnumber}</td><td class="cname%s">{clubname}{closing}</td>' % (' {color}' if parms.color else ''))
                    if parms.color:
                        outrow.append('  <td class="members">{activemembers}</td>\n')
                        outrow.append('  <td class="goals">{goalsmet}</td>\n')
                    outrow.append('  <td class="loc">{place}<br />{address}<br />{city}, {state} {zip}</td>')
                    outrow.append('  <td class="mtg"><b>{meetingday}</b><br />{meetingtime}</td>')
                    outrow.append('</tr>')
                    accum.append(('\n'.join(outrow)).format(**row))
                    locations.append((row['clubname'], row['latitude'], row['longitude']))
                    marker = chr(ord(marker)+1)
            
                closearea(outfile, accum, locations, gonefrom.get(area,[]))
            closediv(outfile)
    outfile.write("</body></html>\n")
    outfile.close()
    

    # And now, create the mimimal version of the report
    outfile = open(os.path.join(parms.outdir,parms.minimal), 'w')
    outfile.write(minimalhead)
    firstdiv = True
    for div in sorted(divs.keys()):
        if div.strip():
            outfile.write('<div class="clearfix division%s">\n' % ('' if firstdiv else ' notfirst'))
            firstdiv = False
            outfile.write('<p class="divname">Division %s</p>' % div)
            areas = sorted(divs[div].keys())
            # Now, we write areas out two at a time
            left = True
            for area in areas:
                if left:
                    outfile.write('<div class="areapair clearfix">\n')
                
                locations = []
                outfile.write('<div class="areadiv %s">\n' % ('left' if left else 'right'))
                outfile.write('<table class="areatable"><thead>\n')
                outfile.write('<tr><th class="areaname" colspan="3">Area %s</th></tr>' % area)
                outfile.write('<tr>\n')
                outfile.write('<th class="from">From</th>')
                outfile.write('<th class="cnum">Number</th><th class="cname">Name</th>')
                outfile.write('</tr>\n')
                outfile.write('</thead><tbody>\n')
                for c in sorted(newareas[area], key=lambda x:int(x.clubnumber)):
                    row = c.__dict__  
                    outrow = []
                    outrow.append('<tr class="myrow">')
                    oldarea = c.division + c.area
                    newarea = c.newdivision + c.newarea
                    outrow.append('  <td class="from">%s</td>' % (oldarea if oldarea != newarea else ''))
                    outrow.append('  <td class="cnum">{clubnumber}</td><td class="cname">{clubname}</td>')
                    outrow.append('</tr>')
                    outfile.write(('\n'.join(outrow)).format(**row))
                # Now, process clubs which moved away or were 
                gonelist = gonefrom.get(area,[])
                if gonelist:
                    for club in sorted(gonelist, key=lambda c:c.clubname.lower()):
                        outfile.write('<tr><td class="gone" colspan="3">%s' % club.clubname)
                        if club.eligibility == 'Suspended':
                            outfile.write(' <b>(Suspended)</b>')
                        elif club.newarea.strip() and club.newdivision.strip():
                            outfile.write(' (To %s%s)' % (club.newdivision, club.newarea))
                        else:
                            outfile.write(' (Moved out of Division 101)')
                        outfile.write('</td></tr>\n')

                outfile.write('</tbody></table>\n') 
                
                outfile.write('</div><!--areadiv-->\n')
                
                if not left:
                  outfile.write('</div><!--areapair-->\n')
                left = not left
            
            # Finished with this division    
            outfile.write('</div>\n')    
                

    outfile.write("</body></html>\n")
    outfile.close()




