#!/usr/bin/env python

"""Populate the 'map' table based on the current map on D4TM.ORG."""

import dbconn, tmutil, sys, os, requests, re
from bs4 import BeautifulSoup


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)
    

### Insert classes and functions here.  The main program begins in the "if" statement below.

pat = r'<br>(.*?(?:meeting|Meets|am|pm|AM|PM).*?)<br>(.*)<a.*Find-a-Club/([0-9]*)'

def makeTab(club, str, lat, lng, areaIcon):
    m = re.search(pat, str)
    if m:
        clubnumber = int(m.group(3))
        address = m.group(2)
        timeinfo = m.group(1).split('<br>')[-1]
        club = club.replace('<b>','').replace('</b>','').strip()
        if len(address) > 400:
            print 'oops'
            address = address[0:399]
            print club
            print address
        curs.execute("INSERT INTO map  (clubnumber, clubname, areaicon, lat, lng, address, timeinfo) VALUES (%s, %s, %s, %s, %s, %s, %s)", (clubnumber, club, areaIcon, lat, lng, address, timeinfo))
    else:
        print "no match for", club
        print str
 

if __name__ == "__main__":
 
    import tmparms
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    
    r = requests.get('http://d4tm.org/images/map/2015-16.htm')
    if r.status_code != 200:
        sys.stderr.write('Couldn\'t get map file, status code = %d\n' % r.status_code)
        sys.exit(1)
    
    soup = BeautifulSoup(r.content)
    themap = unicode(soup.find_all('script')[-1].string).split('\n')
    
    # Now 'themap' is the Javascript that actually creates the map.
    # We're going to plow through it and build the database, instead.
    # First, clear out the map table.
    
    curs.execute("DELETE FROM map WHERE 1")
    conn.commit()
    
    linenum = 0
    for l in themap:
        if 'marker-points:' in l:
            break
        linenum += 1
    themap = themap[linenum:]
    
    # Now, we're at the start of the actual map.  We need to look for patterns....
    latlong = (0.0,0.0)
    areaicon = ''
    
    llpat = r'new\s*?g.LatLng\((.*?),(.*?)\)'
    iconpat = r'areaIcon\s*?=\s*?"(.*?)"'
    iwtabpath = r'iwTab\s*?\("(.*?)"\s*?,\s*?"(.*?)"\s*?\)\s*?;'
    
    
    for l in themap:
        m = re.search(llpat, l)
        if m:
            lat = float(m.group(1))
            lng = float(m.group(2))
        m = re.search(iconpat, l)
        if m:
            areaIcon = m.group(1)
        m = re.search(iwtabpath, l)
        if m and m.group(2).strip():
            makeTab(m.group(1), m.group(2), lat, lng, areaIcon)
            
    curs.close()
    conn.commit()
            
        
            

