#!/usr/bin/python

# Get Educational Awards

import dbconn, tmutil, sys, os, urllib
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

if __name__ == "__main__":
 
    import tmparms
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--district', type=int)
    parms.parse()

    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Get the data from Toastmasters
    url = "http://reports.toastmasters.org/reports/dprReports.cfm?r=3&d=%d&s=Club&sortOrder=0" % parms.district
    data = ''.join(urllib.urlopen(url).readlines())
    # Parse it
    soup = BeautifulSoup(data)

    awards = []
    # We want siblings of the first table row of class "content"
    starter = soup.find('tr', class_='content')
    line = starter.find_next_sibling("tr")
    while line:
        awards.append([s.strip() for s in line.stripped_strings])
        # Reformat the date
        dparts = awards[-1][4].split('/')
        awards[-1][4] = dparts[2] + '-' + dparts[0] + '-' + dparts[1]
        tmyear = int(dparts[2])
        month = int(dparts[0])
        if month <= 6:
            tmyear = tmyear - 1
        awards[-1].append(tmyear)
        line = line.find_next_sibling("tr")
    # And insert awards into the database
    changecount = curs.executemany("INSERT IGNORE INTO awards (clubnumber, division, area, award, awarddate, membername, clubname, clublocation, tmyear) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", awards)           
    inform("%d %s added" % (changecount, "awards" if changecount != 1 else "award"))
    conn.commit()
    conn.close()