#!/usr/bin/env python2.7
""" Create alignment work file based on:

    * Information from the tmstats database
    * Limited to clubs in the 'newAlignment' Google spreadsheet
    * Information in the 'newAlignment' spreadsheet overrides info from tmstats 
    
    The output work file is used by other programs in the alignment process such as 'alignmap' and 'makelocationreport'
    """

import dbconn, tmutil, sys, os, csv
import requests
from simpleclub import Club

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
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--newAlignment', default='https://docs.google.com/spreadsheets/d/1K0LMRNvzB38hz-tVSRyOUhT-e8y-bgsNrLzhQnp6UaA/pub?gid=872194435&single=true&output=csv')
    parms.add_argument('--outfile', default='d101align.csv')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Get all defined clubs from the database.
    clubs = Club.getClubsOn(curs)
    ourclubs = {}
    
    # Now, add info from clubperf (and create club.oldarea for each club)
    curs.execute('SELECT clubnumber, color, goalsmet, activemembers FROM clubperf WHERE entrytype = "L"')
    for (clubnumber, color, goalsmet, activemembers) in curs.fetchall():
        c = clubs[str(clubnumber)]
        c.color = color
        c.goalsmet = goalsmet
        c.activemembers = activemembers
        c.oldarea = c.division + c.area
    
    
    # Remove any clubs NOT in the newAlignment; patch in newarea and likelytoclose; override anything else specified.
    # Get the alignment CSV from Google Sheets
    alignment = csv.DictReader(requests.get(parms.newAlignment).text.split('\r\n'))
    fields = alignment.fieldnames
    overridestart = fields.index('likelytoclose') + 1
    for row in alignment:
        clubnumber = row['clubnumber']
        c = clubs[clubnumber]
        c.newarea = row['newarea']
        c.likelytoclose = row['likelytoclose']
        for f in fields[overridestart:]:
            v = row[f]
            if v:
                print 'overriding', f, 'for', c.clubname, 'with', v
                c.__dict__[f] = v
        ourclubs[clubnumber] = c

    # Now, create the output file, sorted by newarea (because that's what we need later on)
    outfields =  'clubnumber	clubname	oldarea	newarea	likelytoclose	color	goalsmet	activemembers	meetingday	meetingtime	place	address	city	state	zip	country	latitude	longitude'.split()
    outfile = open(parms.outfile, 'w')
    writer = csv.DictWriter(outfile, fieldnames=outfields, extrasaction='ignore')
    writer.writeheader()
    outclubs = sorted(ourclubs.values(),key=lambda club:club.newarea+club.clubnumber.rjust(8))
    for c in outclubs:
        writer.writerow(c.__dict__)
    outfile.close()
        
    
