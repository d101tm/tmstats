#!/usr/bin/python

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os
from simpleclub import Club
from tmutil import overrideClubs, removeSuspendedClubs


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)
        
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
        data['contact'].append('<a href="http://%s" target="_blank">Website</a>' % (club.clubwebsite))
    if club.facebook:
        data['contact'].append('<a href="http://%s" target="_blank">Facebook</a>' % (club.facebook))
    if club.clubemail:
        data['contact'].append('<a href="mailto:%s" target="_blank">Email</a>' % (club.clubemail))
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

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--outfile', dest='outfile', default='../../map/markers.js')
    parms.add_argument('--newAlignment', dest='newAlignment', default=None, help='Overrides area/division data from the CLUBS table.')
    parms.add_argument('--pins', dest='pins', default='../../map/pins', help='Directory with pins')
    # Add other parameters here
    parms.parse() 
    
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Get the clubs
    clubs = Club.getClubsOn(curs)
    
    # Process new alignment, if needed
    if parms.newAlignment:
        overrideClubs(clubs, parms.newAlignment)
    
    # Remove suspended clubs
    clubs = removeSuspendedClubs(clubs, curs)
    
    # Your main program begins here.
    outfile = open(parms.outfile, 'w')
    
    # Start by putting in the buildMap call, since it will vary from District to District

        
    # Replace the latitude/longitude information from WHQ with info from the GEO table, and also create 
    #   the directory of clubs by location, and the data for each club
    clubsByLocation = {}
    boundsByDivision = {}
    districtBounds = Bounds()
    curs.execute("SELECT clubnumber, latitude, longitude FROM geo")
    for (clubnumber, latitude, longitude) in curs.fetchall():
        club = clubs['%d' % clubnumber]
        club.latitude = latitude
        club.longitude = longitude
        club.coords = '(%f,%f)' % (latitude, longitude)
        club.card = makeCard(club)
        if club.coords not in clubsByLocation:
            clubsByLocation[club.coords] = []
        if club.division != '0D':
            if club.division not in boundsByDivision:
                boundsByDivision[club.division] = Bounds()
            boundsByDivision[club.division].extend(latitude, longitude)
        districtBounds.extend(latitude, longitude)
        clubsByLocation[club.coords].append(club) 
        
    # Write the actual call to build the map
    outfile.write("buildMap();\n")
    outfile.write("moveMap(%s,%s);\n" % (districtBounds.center(), districtBounds.bounds()))
    
        
    # Write the zoom code
    boundsByDivision['z'] = districtBounds
    for div in sorted(boundsByDivision.keys()):
        this = boundsByDivision[div]
        outfile.write("""
        $(".%s").click(function(){
            moveMap(%s, %s)});
        """ % (div.lower(), this.center(), this.bounds()))
        
  
        
    # Now, find multiple clubs at the same location and write out the markers
    for l in clubsByLocation.values():
        if len(l) > 1:
            inform('%d clubs at %s' % (len(l), l[0].coords))
            clubinfo = []
            divs = []
            for club in l:
                inform('%s%s %s' % (club.division, club.area, club.clubname), file=sys.stdout)
                inform('   %s' % (club.address), file=sys.stdout)
                clubinfo.append('new iwTab("%s", "%s")' % (club.clubname, makeCard(club)))
                if club.division not in divs:
                    divs.append(club.division)
            clubinfo = '[%s]' % ', '.join(clubinfo)
            if len(divs) == 1:
                icon = divs[0] + 'M'
            else:
                icon = ''.join(sorted(divs))
            inform(icon, file=sys.stdout)
            try:
                open('%s/%s.png' % (parms.pins, icon), 'r')
            except Exception, e:
                print e
                icon = 'missing'
            outfile.write('addMarker("%d clubs meet here", "%s",%s,%s,%s);\n' % (len(l), icon, club.latitude, club.longitude, clubinfo))
        else:
            club = l[0]
            clubinfo = '[new iwTab("%s", "%s")]' % (club.clubname, makeCard(club))
            outfile.write('addMarker("%s", "%s",%s,%s,%s);\n' % (club.clubname, (club.division + club.area).upper(), club.latitude, club.longitude, clubinfo))

    outfile.close()
   