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
    

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--outfile', dest='outfile', default='markers.js')
    parms.add_argument('--newAlignment', dest='newAlignment', default=None, help='Overrides area/division data from the CLUBS table.')
    parms.add_argument('--override', dest='override', default=None, help='Overrides coordinates and info from the GEO table.')
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
    
    # Replace the latitude/longitude information from WHQ with info from the GEO table, and also create 
    #   the directory of clubs by location, and the data for each club
    clubsByLocation = {}
    curs.execute("SELECT clubnumber, latitude, longitude FROM geo")
    for (clubnumber, latitude, longitude) in curs.fetchall():
        club = clubs['%d' % clubnumber]
        club.latitude = latitude
        club.longitude = longitude
        club.coords = '(%f,%f)' % (latitude, longitude)
        club.card = makeCard(club)
        if club.coords not in clubsByLocation:
            clubsByLocation[club.coords] = []
        clubsByLocation[club.coords].append(club) 
        
    # Now, find multiple clubs at the same location
    for l in clubsByLocation.values():
        if len(l) > 1:
            print '%d clubs at %s' % (len(l), l[0].coords)
            clubinfo = []
            divs = []
            for club in l:
                print '%s%s %s' % (club.division, club.area, club.clubname)
                print '   %s' % (club.address)
                clubinfo.append('new iwTab("%s", "%s")' % (club.clubname, makeCard(club)))
                if club.division not in divs:
                    divs.append(club.division)
            clubinfo = '[%s]' % ', '.join(clubinfo)
            if len(divs) == 1:
                icon = divs[0] + 'M'
            else:
                icon = ''.join(sorted(divs))
            print icon
            outfile.write('addMarker("%d clubs", "%s",%s,%s,%s);\n' % (len(l), icon, club.latitude, club.longitude, clubinfo))
        else:
            club = l[0]
            clubinfo = '[new iwTab("%s", "%s")]' % (club.clubname, makeCard(club))
            outfile.write('addMarker("%s", "%s",%s,%s,%s);\n' % (club.clubname, (club.division + club.area).upper(), club.latitude, club.longitude, clubinfo))

    outfile.close()
   