#!/usr/bin/env python2.7
""" Create alignment work file based on:

    * Information from the tmstats database
    * Limited to clubs in the latest CSV file in the 'newAlignment' Dropbox directory 
    * Information in that CSV file overrides info from tmstats 
    
    The output work file is used by other programs in the alignment process such as 'alignmap' and 'makelocationreport'
    """

import dbconn, tmutil, sys, os, csv
import requests
from simpleclub import Club
import dropbox
import json
from datetime import datetime
from makemap import setClubCoordinatesFromGEO
from overridepositions import overrideClubPositions
import time, calendar


state_file = 'alignstate.txt'
appinfo_file = 'aligntokens.txt'

def authorize():
    appinfo = open(appinfo_file,'r')
    for l in appinfo.readlines():
        (name, value) = l.split(':',1)
        name = name.strip().lower()
        value = value.strip()
        if name == 'app key':
            appkey = value
        elif name == 'app secret':
            appsecret = value
    appinfo.close()
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(appkey, appsecret)
    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print '1. Go to: ' + authorize_url
    print '2. Click "Allow" (you might have to log in first)'
    print '3. Copy the authorization code.'
    code = raw_input("Enter the authorization code here: ").strip()
    token, user_id = flow.finish(code)
    out = open(state_file, 'w')
    out.write('oauth2:%s\n' % token)
    out.close()
    return token

def getlatest(curs):
    """ Returns a list of lines from the latest alignment spreadsheet in
        the D101 Alignment directory. Also builds file with source data. """
    token = None
    try:
        tokinfo = open(state_file, 'r')
        for l in tokinfo.readlines():
            if ':' in l:
                (name, value) = l.strip().split(':')
                if name == 'oauth2':
                    token = value
                elif name == 'delta_cursor':
                    delta_cursor = value
        tokinfo.close()
    except IOError:
        pass
    if not token:
        token = authorize()

    # If we get here, we are authorized.
    client = dropbox.client.DropboxClient(token)

    # The only files we care about are in the appropriate directory in Dropbox
    path = '/D101 Alignment'

    lastfile = None
    lasttime = time.localtime(0)   # For easy comparisons
    folder_metadata = client.metadata(path)
    
    # Find the latest file
    
    for item in folder_metadata['contents']:
        filename = item['path']
        ext = os.path.splitext(filename)[1]
        if ext in ['.csv']:
            # We care about CSV files, but only the latest.
            # We assume consistency in timezone from Dropbox...
            modified = ' '.join(item['modified'].split()[1:5])
            print modified, filename
            filetime = time.strptime(modified, '%d %b %Y %H:%M:%S')
            if (filetime > lasttime):
                lastfile = filename
                lasttime = filetime
                lastext = ext
                
    # Convert the timestamp to local.  There must be an easier way!
    lasttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(calendar.timegm(lasttime)))
            
    print 'Using', lastfile, 'modified at', lasttime
    with open('alignmentsource.txt', 'w') as outfile:
        outfile.write('<p>The source for the alignment is %s, updated at %s</p>\n' % (lastfile.split('/')[-1], lasttime))
        curs.execute('SELECT MAX(asof) FROM clubperf')
        outfile.write('<p>Using Toastmasters data as of %s</p>' % curs.fetchone()[0])
    return client.get_file(lastfile).read().splitlines()


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
    parms.add_argument('--outfile', default='d101align.csv')
    parms.add_argument('--mapoverride', dest='mapoverride', default=None, help='Google spreadsheet with overriding address and coordinate information')
    parms.add_argument('--alignment', dest='alignment', default=None, help='Use this file instead of going to Dropbox.')
    # Add other parameters here
    parms.parse() 
    
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Get all defined clubs from the database.
    clubs = Club.getClubsOn(curs)
    # Get coordinates
    setClubCoordinatesFromGEO(clubs, curs, removeNotInGeo=False)
    # If there are overrides to club positioning, handle them now
    if parms.mapoverride:
        overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey)
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
    # Get the alignment CSV from Dropbox
    if not parms.alignment:
        alignment = csv.DictReader(getlatest(curs))
    else:
        alignment = csv.DictReader(open(parms.alignment).read().splitlines())
    fields = alignment.fieldnames
    ignore = ['clubnumber', 'clubname', 'newarea', 'oldarea']
    for row in alignment:
        clubnumber = row['clubnumber']
        try:
            c = clubs[clubnumber]
            c.newarea = row['newarea']
            for f in fields:
                if f in ignore:
                    continue 
                try:
                    v = row[f].strip()
                except AttributeError:
                    v = ''   # Handle missing items
                if v:
                    print 'overriding', f, 'for', c.clubname, 'from', c.__dict__[f], 'to', v
                    c.__dict__[f] = v
        except KeyError:
            # Must create a new club.  Oh, boy!
            print 'creating new club', clubnumber
            c = Club(row.values(), fieldnames=row.keys())
            print c
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
        
    
