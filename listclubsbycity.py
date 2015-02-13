#!/usr/bin/python
""" Create the "Club Listing By City" as an includable HTML file. 
    Also create the CSS/JS and actual HTML as separate pieces for Joomla. """

import csv, sys, re
from club import Club

# Create the templates


    
headinfo= {}
headinfo['style'] = """
    table.clubtable {width: 720px; display: none; border-collapse: collapse;
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

\

header = """
<html>
<head>
    <script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
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
<h3 class="cityname title pane-toggler" onclick='jQ ( "#%(cityid)sclubs" ).toggle();'>%(cityname)s</h3>
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

narrowtemplate = """
<tr>
<td class="clubname">%(clubname)s</td>
</tr>
<tr><td>%(restrict)s | Meets %(meetingday)s %(meetingtime)s</td></tr>
<tr><td class="location">%(location)s<br />%(city)s, %(state)s %(zip)s</td></tr>
<tr><td>%(stiminfo)s</td></tr>
<tr><td>%(scontact)s</td></tr>
"""


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
headfile = open('data/clublist.css', 'wb')
bodyfile = open('data/clublist.body', 'wb')

headfile.write(headinfo['style'])
outfile.write(header)


for city in sorted(cities.keys()):
    
    info = {}
    info['cityid']= normalize(city)
    info['cityname'] = city
    info['clubs'] = ''
    allclubinfo = []
    
    cities[city].sort(key=lambda x:x.clubname.lower())
    for club in cities[city]:
        data = {}
        data['clubname'] = club.clubname
        data['tminfo'] = 'Club Number %s<br />District %s<br />Division %s, Area %s<br />Charter: %s' % \
                            (club.clubnumber, club.district, club.division, club.area, club.charterdate)
        data['stminfo'] = 'Club %s | Area %s%s | Charter: %s' % \
                            (club.clubnumber, club.division, club.area, club.charterdate)
        if club.clubstatus.startswith('Open') or club.clubstatus.startswith('None'):
            data['restrict'] = 'Club is open to all'
        else:
            data['restrict'] = 'Contact club about membership requirements'
        if club.advanced:
            data['restrict'] += '; Club is an Advanced Club'
        data['meetingday'] = club.meetingday.replace(' ','&nbsp;')
        data['meetingtime'] = club.meetingtime.replace(' ','&nbsp;')
        data['contact'] = []
        if club.clubwebsite: 
            data['contact'].append('<a href="http://%s" target="_blank"> Website</a>' % (club.clubwebsite))
        if club.facebook:
            data['contact'].append('<a href="http://%s" target="_blank">Facebook</a>' % (club.facebook))
        if club.clubemail:
            data['contact'].append('<a href="mailto:%s" target="_blank">Email</a>' % (club.clubemail))
        if club.phone:
            data['contact'].append('Phone: %s' % (club.phone))
        data['lcontact'] = '<br />'.join(data['contact'])
        data['scontact'] = ' | '.join(data['contact'])
        # It looks like Toastmasters uses two consecutive blanks to encode a linebreak in the address info
        address = club.address1.split('  ') + club.address2.split('  ')
        data['location'] = '<div class="locfirst">' + \
                           address[0] + \
                           '</div>' + \
                           ('<br />'.join(address[1:]))
        data['city'] = club.city
        data['state'] = club.state
        data['zip'] = club.zip
        allclubinfo.append(clubtemplate % data)
        
    info['clubs'] = '\n'.join(allclubinfo)
    outfile.write(citytemplate % info)
    outfile.write('\n')
    bodyfile.write(citytemplate % info)
    bodyfile.write('\n')
    
outfile.write(footer);
outfile.close()
bodyfile.close()
headfile.close( )
    
