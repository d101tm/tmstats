#!/usr/bin/env python3

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os
from simpleclub import Club
from tmutil import overrideClubs, removeSuspendedClubs
from overridepositions import overrideClubPositions
import tmglobals
globals = tmglobals.tmglobals()


def inform(*args, **kwargs):
    """ Print information to 'file', depending on the verbosity level.
        'level' is the minimum verbosity level at which this message will be printed. """
    level = kwargs.get('level', 0)
    file = kwargs.get('file', sys.stderr)
    verbosity = kwargs.get('verbosity', 0)

    if verbosity >= level:
        print(' '.join(args), file=file)

def makeCard(club):
    cardtemplate = """
    <table>
    <tr><td>%(restrict)s<td></tr>
    <tr><td>%(meetingday)s %(meetingtime)s</td></tr>
    <tr><td class="location">%(location)s<br />%(city)s, %(state)s %(zip)s</td></tr>
    <tr><td>%(scontact)s</td></tr>
    <tr><td>%(stminfo)s</td></tr>
    </table>
    """
    data = {}
    data['clubname'] = club.clubname
    data['tminfo'] = 'Club %s<br />Area %s%s<br />Charter: %s' % \
                        (club.clubnumber, club.division, club.area, club.charterdate)
    data['stminfo'] = 'Club %s | Area %s%s | Charter: %s' % \
                        (club.clubnumber, club.division, club.area, club.charterdate)
    if club.clubstatus.startswith('Open') or club.clubstatus.startswith('None'):
        data['restrict'] = 'Club is open to all'
    else:
        data['restrict'] = 'Contact club about membership requirements'
    if club.advanced == '1':
        data['restrict'] += '; Club is an Advanced Club'
    data['meetingday'] = club.meetingday.replace(' ','&nbsp;')
    data['meetingtime'] = club.meetingtime.replace(' ','&nbsp;')
    data['contact'] = []
    if club.clubwebsite:
        data['contact'].append('<a href="%s" target="_blank">Website</a>' % (club.clubwebsite))
    if club.facebook:
        data['contact'].append('<a href="%s" target="_blank">Facebook</a>' % (club.facebook))
    if club.clubemail:
        data['contact'].append('<a href="%s" target="_blank">Email</a>' % (club.clubemail))
    if club.phone:
        data['contact'].append('Phone: %s' % (club.phone))
    data['lcontact'] = '<br />'.join(data['contact'])
    data['scontact'] = ' | '.join(data['contact'])
    address = club.place.split('\n')
    address.append(club.address)
    data['location'] = '<div class="locfirst">' + \
                       address[0] + \
                       '</div>' + \
                       ('<br />'.join(address[1:]))
    data['city'] = club.city
    data['state'] = club.state
    data['zip'] = club.zip
    return (cardtemplate % data).replace('"','\\"').replace("\n","\\n")



class Bounds:

    def __init__(self):
        self.north = None
        self.south = None
        self.east = None
        self.west = None

    def extend(self, latitude, longitude):
        if self.north is None:
            self.north = latitude
            self.south = latitude
        else:
            self.north = max(self.north, latitude)
            self.south = min(self.south, latitude)
        if self.east is None:
            self.east = longitude
            self.west = longitude
        else:
            self.east = max(self.east, longitude)
            self.west = min(self.west, longitude)

    def center(self):
        return '{lat:%f, lng:%f}' % ((self.north + self.south) / 2.0, (self.east + self.west) / 2.0)

    def northeast(self, latpadding, longpadding):
        return '{lat:%f, lng:%f}' % (self.north + latpadding, self.east + longpadding)

    def southwest(self, latpadding, longpadding):
        return '{lat:%f, lng:%f}' % (self.south - longpadding, self.west - latpadding)

    def bounds(self, latpadding=0.005, longpadding=0.001):
        return 'new g.LatLngBounds(%s, %s)' % (self.southwest(latpadding, longpadding), self.northeast(latpadding, longpadding))

def setClubCoordinatesFromGEO(clubs, curs, removeNotInGeo=True):
    # Also removes any clubs NOT in GEO table unless told otherwise
    geoclubs = {}
    curs.execute("SELECT clubnumber, latitude, longitude FROM geo")
    for (clubnumber, latitude, longitude) in curs.fetchall():
        clubnumber = '%d' % clubnumber
        geoclubs[clubnumber] = True
        if clubnumber in clubs:
            club = clubs[clubnumber]
            club.latitude = latitude
            club.longitude = longitude
    if removeNotInGeo:
        allclubs = list(clubs.keys())
        for c in allclubs:
            if c not in geoclubs:
                del clubs[c]


def makemap(outfile, clubs, parms):
    #   Create the directory of clubs by location, and the card data for each club
    clubsByLocation = {}
    boundsByDivision = {}
    districtBounds = Bounds()
    for c in sorted(clubs.keys()):
        club = clubs[c]
        club.latitude = float(club.latitude)
        club.longitude = float(club.longitude)  # In case the values in the database are funky
        if club.latitude == 0.0 or club.longitude == 0.0:
            print('no position for', club.clubnumber, club.clubname)
        club.coords = '(%f,%f)' % (club.latitude, club.longitude)
        club.card = makeCard(club)
        if club.coords not in clubsByLocation:
            clubsByLocation[club.coords] = []
        if club.division != '0D':
            if club.division not in boundsByDivision:
                boundsByDivision[club.division] = Bounds()
            boundsByDivision[club.division].extend(club.latitude, club.longitude)
        districtBounds.extend(club.latitude, club.longitude)
        clubsByLocation[club.coords].append(club)


    oneline = len(boundsByDivision) < 6   # @@TODO@@  Effectively, a surrogate for "Divsion 4"


    # Write the actual call to build the map
    outfile.write("buildMap();\n")
    outfile.write("function ZoomToDistrict() {")

    if oneline:
        outfile.write("""
        moveMap({
    lat: 37.470120,
    lng: -122.304236
}, new g.LatLngBounds({
    lat: 37.396502,
    lng: -122.509855
}, {
    lat: 37.807738,
    lng: -122.102617
}));
""")
    else:
        outfile.write("  moveMap(%s,%s);\n" % (districtBounds.center(), districtBounds.bounds()))
    outfile.write('}\n')
    outfile.write('ZoomToDistrict();')

    # Insert the "zoom" controls
    outfile.write("""zoomdiv = $('<div id="zoom"></div>').insertAfter('#map');\n""")
    structure = []
    structure.append('<span id="nav-head">Click to Select</span>')
    structure.append('<span class="divdistrict">District %s</span>' % parms.district)

    for div in sorted(boundsByDivision.keys()):
        structure.append('<span class="div%s">Division %s</span>' % (div, div))

    outfile.write("$('%s').appendTo('#zoom');\n" % '\\\n'.join(structure))


    def outputprops(props, left, top):
        out = []
        for k, v in props.items():
            out.append("'%s':'%s'" % (k, v))
        out.append("'left':'%dpx'" % left)
        out.append("'top':'%dpx'" % top)
        out.append("'position':'absolute'")
        return '{%s}' % ','.join(out)



    # Position and style the "zoom" controls

    if oneline:
        cellwidth = 65
        celltotal = 75
        cellheight = 40
        celltotalheight = 44
        initwidth = 60
        selectwidth = 55
    else:
        cellwidth = 65
        celltotal = 75
        cellheight = 20
        celltotalheight = 24
        initwidth = 60
        selectwidth = 55
    standardprops = {'width':'%dpx' % cellwidth,'padding':'2px','border-style':'solid','border-width':'1px','border-color':'#555','vertical-align':'top'}
    outfile.write("$('#zoom').css({'top':'3px', 'font-family':'Arial', 'font-size':'10pt', 'position':'relative', 'height':'47px'});\n")
    outfile.write("$('#nav-head').css({'width':'%dpx','text-align':'center','vertical-align':'middle','height':'%dpx','display':'inline-block'});\n" % (selectwidth, cellheight if oneline else (2*cellheight)))
    aaaprops = standardprops.copy()
    aaaprops['display'] = 'inline-block'
    aaaprops['height'] = '%dpx' % (cellheight * 2)
    aaaprops['vertical-align'] = 'center'
    outfile.write("$('.divdistrict').css(%s);\n" % outputprops(aaaprops, initwidth, 0))
    left = initwidth + celltotal
    top = 0
    i = 1

    # The positioning depends very much on the width of the map, so we have to write dynamic code.
    half = (1 + len(boundsByDivision)) // 2

    # If there are fewer than 6 divisions, try to stay on one line.
    if oneline:
        maxwidth = left + (len(boundsByDivision) * celltotal)
    else:
        maxwidth = left + (half * celltotal)

    outfile.write("if ($('#map').width() >= %d) {\n" % maxwidth)
    # Normal case, if there's enough room
    for div in sorted(boundsByDivision.keys()):
        outfile.write("$('.div%s').css(%s);\n" % (div, outputprops(standardprops, left, top)))
        outfile.write("$('.div%s').css('background-color', fillcolors['%s']);\n" % (div, div))
        thehtml = 'Division %s' % div
        outfile.write("$('.div%s').html('%s');\n" % (div, thehtml))
        if i == half and not oneline:
            left = initwidth + celltotal
            top = celltotalheight
        else:
            left += celltotal
        i += 1
    outfile.write("} else {\n")
    # if there isn't enough room, cram it together
    left = initwidth + celltotal
    smalltotal = 25
    top = 0
    standardprops['width'] = '15px'
    standardprops['text-align'] = 'center'
    i = 1
    for div in sorted(boundsByDivision.keys()):
        outfile.write("$('.div%s').css(%s);\n" % (div, outputprops(standardprops, left, top)))
        outfile.write("$('.div%s').css('background-color', fillcolors['%s']);\n" % (div, div))
        outfile.write("$('.div%s').html(' %s ');\n" % (div, div))
        if i == half:
            left = initwidth + celltotal
            top = celltotalheight
        else:
            left += smalltotal
        i += 1
    outfile.write("}\n")

    outfile.write("$('.divdistrict').click(ZoomToDistrict);")

    # Write the zoom code
    for div in sorted(boundsByDivision.keys()):
        this = boundsByDivision[div]
        outfile.write("""
        $(".div%s").click(function(){
            moveMap(%s, %s)});
        """ % (div, this.center(), this.bounds()))

    # Figure out if we show details
    try:
        showdetails = parms.showdetails
    except AttributeError:
        showdetails = False

    # Now, write out the markers (combining multiple clubs at the same location)
    for l in list(clubsByLocation.values()):
        # Omit clubs that shouldn't be on the map
        newl = []
        for club in l:
            try:
                if club.omitfrommap:
                    inform('Omitting %s from map' % club.clubname, level=1, file=sys.stdout, verbosity=parms.verbosity)
                else:
                    newl.append(club)
            except AttributeError:
                newl.append(club)
        l = newl
        if not l:
            continue       # No clubs left at this location
            
        if len(l) > 1:
            inform('%d clubs at %s' % (len(l), l[0].coords), level=1, file=sys.stdout, verbosity=parms.verbosity)
            clubinfo = []
            divs = []
            for club in l:
                inform('%s%s %s' % (club.division, club.area, club.clubname), file=sys.stdout, level=2, verbosity=parms.verbosity)
                inform('   %s' % (club.address), file=sys.stdout, level=2, verbosity=parms.verbosity)
                clubinfo.append('new iwTab("%s", "%s")' % (club.clubname, makeCard(club)))
                if club.division not in divs:
                    divs.append(club.division)
            clubinfo = '[%s]' % ', '.join(clubinfo)
            if len(divs) == 1:
                icon = divs[0] + 'M'
            else:
                icon = ''.join(sorted(divs))
            inform(icon, file=sys.stdout, level=2, verbosity=parms.verbosity)
            if parms.pindir:
                try:
                    open('%s/%s.png' % (parms.pindir, icon), 'r')
                except Exception as e:
                    print(e)
                    icon = 'missing'
                    for club in l:
                        inform('%s%s %s' % (club.division, club.area, club.clubname), file=sys.stdout, level=0, verbosity=parms.verbosity)
                        inform('   %s' % (club.address), file=sys.stdout, level=0, verbosity=parms.verbosity)
            else:
                icon = ''
            markertext = []
            for c in l:
                if showdetails:
                    markertext.append('%s (%s, %s%s)' % (c.clubname, c.color, c.division, c.area))
                else:
                    markertext.append(c.clubname)
            markertext = '\\n'.join(markertext)
            outfile.write('addMarker("%s", "%s",%s,%s,%s);\n' % (markertext, icon, club.latitude, club.longitude, clubinfo))
        else:
            club = l[0]
            if parms.pindir:
                icon = (club.division + club.area).upper()
                try:
                    open('%s/%s.png' % (parms.pindir, icon), 'r')
                except Exception as e:
                    print(e)
                    icon = 'missing'
            else:
                icon = ''
            clubinfo = '[new iwTab("%s", "%s")]' % (club.clubname, makeCard(club))
            if showdetails:
                outfile.write('addMarker("%s (%s)", "%s",%s,%s,%s);\n' % (club.clubname, club.color, icon, club.latitude, club.longitude, clubinfo))
            else:
                outfile.write('addMarker("%s", "%s",%s,%s,%s);\n' % (club.clubname, icon, club.latitude, club.longitude, clubinfo))


if __name__ == "__main__":

    import tmparms

    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
    parms.add_argument('--verbose', '-v', action='count', default=0)
    parms.add_argument('--outfile', dest='outfile', default='markers.js')
    parms.add_argument('--newAlignment', dest='newAlignment', default=None, help='Overrides area/division data from the CLUBS table.')
    parms.add_argument('--pindir', dest='pindir', default=None, help='Directory with pins; default uses Google pins')
    parms.add_argument('--mapoverride', dest='mapoverride', default=None, help='Google spreadsheet with overriding address and coordinate information')
    # Add other parameters here
    # Do global setup
    globals.setup(parms)
    conn = globals.conn
    curs = globals.curs

    # Compute verbosity level.  Default is zero.
    parms.verbosity = parms.verbose - parms.quiet


    # Promote information from parms.makemap if not already specified
    parms.mapoverride = parms.mapoverride if parms.mapoverride else parms.makemap.get('mapoverride',None)
    parms.pindir = parms.pindir if parms.pindir else parms.makemap.get('pindir',None)


    # Get the clubs
    clubs = Club.getClubsOn(curs)

    # Remove suspended clubs
    clubs = removeSuspendedClubs(clubs, curs)


    # Add current coordinates and remove clubs without coordinates unless there's a new alignment file to deal with
    setClubCoordinatesFromGEO(clubs, curs, removeNotInGeo=not parms.newAlignment)

    # Process new alignment, if needed
    if parms.newAlignment:
        overrideClubs(clubs, parms.newAlignment, exclusive=False)
        
    # If there are overrides to club positioning, handle them now
    if parms.mapoverride:
        overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey)


    outfile = open(parms.outfile, 'w')

    makemap(outfile, clubs, parms)

    outfile.close()
