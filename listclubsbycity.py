#!/usr/bin/env python3
""" Create the "Club Listing By City" as an includable HTML file. 
    Also create the CSS/JS and actual HTML as separate pieces for Joomla.
    And create narrow versions to be phone-friendly. """

import sys, re, os
from simpleclub import Club
import tmparms, tmglobals
from tmutil import cleandate, overrideClubs, removeSuspendedClubs
from overridepositions import overrideClubPositions
import imp

globals = tmglobals.tmglobals()

# Create the templates

headinfo= {}
headinfo['style'] = """
    table.clubtable {width: 100%; display: none; border-collapse: collapse;
       border-left-style: hidden !important;
       border-right-style: hidden !important;
    }
    .fullcity td {border: 0px solid white;}
    .fullcity tr {border: 0px solid white;}
    div.fullcity {padding-bottom: 3px;}
    h3.cityname {font-weight: bold; font-size: 150%;}
    h3.cityname:hover {background-color: #772432; color: white;}
    col.c1 {width: 22%;}
    col.c2 {width: 32%;}
    col.c3 {width: 46%;}
    td.clubname {padding-top: 6px; font-weight: bold; font-size: 125%;
          color: #772432; border-top: 1px solid #ddd;}
    td.tminfo {vertical-align: top; padding-right: 3px;
           border-right: 1px solid #ddd;}
    td.meeting {vertical-align: top; padding-right: 3px;
           padding-left: 3px;
           border-right: 1px solid #ddd;}
    td.location {vertical-align: top; padding-left: 3px;}
    div.locfirst {text-indent: -1em; padding-left: 1em;}
"""



header = """
<html>
<head>
    <script src="https://code.jquery.com/jquery-1.11.1.min.js"></script>
    <script>
        jQ = jQuery.noConflict();
    </script>    
    <style type="text/css">
    %(style)s
    </style>
</head>
</body>
""" % headinfo

footer = """
</body>
</html>
"""

citytemplate = """
<div class="fullcity" id="%(cityid)s">
<h3 class="cityname title pane-toggler" onclick='jQ ( "#%(cityid)sclubs, #%(cityid)sopen, #%(cityid)sclosed" ).toggle();'><span id="%(cityid)sopen" style="display:none;">&#x25be;</span><span id="%(cityid)sclosed">&#x25b8;</span> %(cityname)s</h3>
<table class="clubtable" id="%(cityid)sclubs">
<colgroup>
<col class="c1"><col class="c2"><col class="c3">
</colgroup>
%(clubs)s
</table>
</div>"""

clubtemplate = """
<tr>
<td class="clubname" colspan="3">%(clubname)s</td>
</tr>
<tr>
<td colspan="3">%(restrict)s</td>
</tr>
<tr>
<td class="tminfo">%(tminfo)s</td>
<td class="meeting">%(meetingday)s %(meetingtime)s<br />%(lcontact)s</td>
<td class="location">%(location)s<br />%(city)s, %(state)s %(zip)s</td>
</tr>
"""
 
narrowcitytemplate = """
<div class="fullcity" id="n%(cityid)s">
<h3 class="cityname title pane-toggler" onclick='jQ ( "#n%(cityid)sclubs, #n%(cityid)sopen, #n%(cityid)sclosed" ).toggle();'><span id="n%(cityid)sopen" style="display:none;">&#x25be;</span><span id="n%(cityid)sclosed">&#x25b8;</span>%(cityname)s</h3>
<table class="clubtable" id="n%(cityid)sclubs">
%(narrowclubs)s
</table>
</div>"""

narrowtemplate = """
<tr>
<td class="clubname">%(clubname)s</td>
</tr>
<tr><td>%(restrict)s<td></tr>
<tr><td>%(meetingday)s %(meetingtime)s</td></tr>
<tr><td class="location">%(location)s<br />%(city)s, %(state)s %(zip)s</td></tr>
<tr><td>%(stminfo)s</td></tr>
<tr><td>%(scontact)s</td></tr>
"""


# Helper functions


def normalize(s):
    if s:
        return re.sub('\W\W*', '', s).strip().lower()
    else:
        return ''

# Main program

# Make it easy to run under TextMate
if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        

# Handle parameters
parms = tmparms.tmparms()
parms.parser.add_argument("--date", dest='date', default='today')
parms.add_argument('--newAlignment', dest='newAlignment', default=None, help='Overrides area/division data from the CLUBS table.')
parms.add_argument('--mapoverride', dest='mapoverride', default=None, help='Google spreadsheet with overriding address and coordinate information')

# Do global setup
globals.setup(parms)
conn = globals.conn
curs = globals.curs

parms.date = cleandate(parms.date)

# Promote information from parms.makemap if not already specified
parms.mapoverride = parms.mapoverride if parms.mapoverride else parms.makemap.get('mapoverride',None)



# Get the club information for the specified date
clubs = Club.getClubsOn(curs, parms.date)

# And remove suspended clubs.
clubs = removeSuspendedClubs(clubs, curs)

# And override it if needed.
if parms.newAlignment:
    overrideClubs(clubs, parms.newAlignment, exclusive=False)
    

# If there are overrides to club positioning, handle them now
if parms.mapoverride:
    overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey)
    
cities = {}

for c in clubs:
    club = clubs[c]
    club.city = club.city.title()
    if club.city not in cities:
        cities[club.city] = []
    cities[club.city].append(club)


outfile = open('clublist.html', 'w')
headfile = open('clublist.css', 'w')
bodyfile = open('clublist.body', 'w')
narrowfile = open('narrowclublist.html', 'w')
narrowbodyfile = open('narrowclublist.body', 'w')

headfile.write(headinfo['style'])
outfile.write(header)
narrowfile.write(header)


for city in sorted(cities.keys()):
    
    info = {}
    info['cityid']= normalize(city)
    info['cityname'] = city
    info['clubs'] = ''
    allclubinfo = []
    allnarrowinfo = []
    
    cities[city].sort(key=lambda x:x.clubname.lower())
    for club in cities[city]:
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
        allclubinfo.append(clubtemplate % data)
        allnarrowinfo.append(narrowtemplate % data)
        
    info['clubs'] = '\n'.join(allclubinfo)
    outfile.write(citytemplate % info)
    outfile.write('\n')
    bodyfile.write(citytemplate % info)
    bodyfile.write('\n')
    info['narrowclubs'] = '\n'.join(allnarrowinfo)
    narrowfile.write(narrowcitytemplate % info)
    narrowfile.write('\n')
    narrowbodyfile.write(narrowcitytemplate % info)
    narrowbodyfile.write('\n')
    
outfile.write(footer);
narrowfile.write(footer);
outfile.close()
bodyfile.close()
narrowfile.close()
narrowbodyfile.close()
headfile.close( )
    
