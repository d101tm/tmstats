#!/usr/bin/python
""" Create the "Club Listing By City" as an includable HTML file. """

import csv, sys, re
from club import Club

# Create the templates

header = """
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
    <style type="text/css">
    table.clubtable {width: 75%; display: none;}
    span.cityname {font-weight: bold; font-size: 150%;}
    col.c1 {width: 25%;}
    col.c2 {width: 25%;}
    col.c3 {width: 50%;}
    td.clubname {font-weight: bold; font-size: 125%;}
    td.tminfo {vertical-align: top;}
    td.meeting {vertical-align: top;}
    td.location {vertical-align: top;}
    </style>
</head>
<body>
"""

citytemplate = """
<div class="fullcity" id="%(cityid)s">
<span class="cityname" onclick='$ ( "#%(cityid)sclubs" ).toggle();'>%(cityname)s</span>
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
<td class="tminfo">%(tminfo)s<br />%(restrict)s</td>
<td class="meeting">%(meetingday)s %(meetingtime)s<br />%(contact)s</td>
<td class="location">%(location)s<br />%(city)s, %(state)s %(zip)s</td>
</tr>"""

# Helper functions


def normalize(s):
    if s:
        return re.sub('\W\W*', '', s).strip().lower()
    else:
        return ''

# Main program

if len(sys.argv) > 1:
    csvfile = open(sys.argv[1],'rbU')
else:
    csvfile = open('data/clubs.2014-12-05.csv', 'rbU')
r = csv.reader(csvfile, delimiter=',')
headers = [normalize(p) for p in r.next()]
Club.setHeaders(headers)

cities = {}
clubs = {}

clubcol = headers.index('clubnumber')    
for row in r:
    try:
        row[clubcol] = Club.fixcn(row[clubcol])
        if row[clubcol]:
            club = Club(row)
            club.city = club.city.title()
            clubs[club.clubnumber] = club
            if club.city not in cities:
                cities[club.city] = []
            cities[club.city].append(club)
    except IndexError:
        pass

    
csvfile.close()

outfile = open('data/clublist.html', 'wb')

outfile.write(header)
header = """
<html>
<head>
    <style type="text/css">
    
    </style>
</head>
<body>
"""

for city in sorted(cities.keys()):
    print city
    
    info = {}
    info['cityid']= normalize(city)
    info['cityname'] = city
    info['clubs'] = ''
    allclubinfo = []
        
    for club in cities[city]:
        data = {}
        data['clubname'] = club.clubname
        data['tminfo'] = 'Club Number %s<br />District %s<br />Division %s, Area %s<br />Charter: %s' % \
                            (club.clubnumber, club.district, club.division, club.area, club.charterdate)
        if club.clubstatus.startswith('Open'):
            data['restrict'] = 'Club is open to all'
        else:
            data['restrict'] = 'Contact club about membership requirements'
        if club.advanced:
            data['restrict'] += '<br />Advanced Club'
        data['meetingday'] = club.meetingday.replace(' ','&nbsp;')
        data['meetingtime'] = club.meetingtime.replace(' ','&nbsp;')
        data['contact'] = []
        if club.clubwebsite: 
            data['contact'].append('<a href="http://%s">Website</a>' % (club.clubwebsite))
        if club.facebook:
            data['contact'].append('<a href="http://%s">Facebook</a>' % (club.facebook))
        if club.clubemail:
            data['contact'].append('<a href="mailto:%s">Email</a>' % (club.clubemail))
        if club.phone:
            data['contact'].append('Phone: %s' % (club.phone))
        data['contact'] = '<br />'.join(data['contact'])
        # It looks like Toastmasters uses two consecutive blanks to encode a linebreak in the address info
        club.address1 = '<br />'.join(club.address1.split('  '))
        club.address2 = '<br />'.join(club.address2.split('  '))
        data['location'] = '<br />'.join([club.address1, club.address2])
        data['city'] = club.city
        data['state'] = club.state
        data['zip'] = club.zip
        allclubinfo.append(clubtemplate % data)
        
    info['clubs'] = '\n'.join(allclubinfo)
    outfile.write(citytemplate % info)
    outfile.write('\n')
    
outfile.write("""
</body>
</html>""")
outfile.close()
    