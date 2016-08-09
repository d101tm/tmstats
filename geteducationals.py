#!/usr/bin/env python2.7

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

def makekey(membername, clubname, award, awarddate):
    return '%s+%s+%s+%s' % (membername, clubname, award, awarddate)

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
    
    # Get the existing awards (significant parts only) so we don't create duplicates.  We can't 
    #   let the datbase do it because we don't have a valid unique key - a person can earn 
    #   identical awards for the same club on the same date.
    existing = set()
    curs.execute("SELECT membername, clubnumber, award, awarddate FROM awards")
    for (membername, clubnumber, award, awarddate) in curs.fetchall():
        existing.add(makekey(membername, clubnumber, award, tmutil.stringify(awarddate)))
        
    
    # Get the data from Toastmasters
    url = "http://reports.toastmasters.org/reports/dprReports.cfm?r=3&d=%d&s=Club&sortOrder=0" % parms.district
    data = ''.join(urllib.urlopen(url).readlines())
    # Parse it
    soup = BeautifulSoup(data, 'html.parser')

    awards = []
    # We want siblings of the first table row of class "content"
    starter = soup.find('tr', class_='content')
    line = starter.find_next_sibling("tr")
    while line:
        candidate = [s.strip() for s in line.stripped_strings]
        line = line.find_next_sibling("tr")
        
        if candidate[3].startswith("P"):
            continue   # Skip pending awards
            
        # Reformat the date
        dparts = candidate[4].split('/')
        candidate[4] = dparts[2] + '-' + dparts[0] + '-' + dparts[1]
        tmyear = int(dparts[2])
        month = int(dparts[0])
        if month <= 6:
            tmyear = tmyear - 1
        candidate.append(tmyear)
        candidate.append(parms.district)
        if makekey(candidate[5], candidate[0], candidate[3], candidate[4]) not in existing:
            awards.append(candidate)
        
    # And insert awards into the database
    if awards:
        changecount = curs.executemany("INSERT INTO awards (clubnumber, division, area, award, awarddate, membername, clubname, clublocation, tmyear, district) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", awards)     
    else:
        changecount = "No"      
    inform("%s %s added" % (changecount, "awards" if changecount != 1 else "award"))
    conn.commit()
    conn.close()
