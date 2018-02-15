#!/usr/bin/env python2.7
""" Create alignment work file based on:

    * Information from the tmstats database
    * Limited to clubs in the latest CSV file in the 'newAlignment' Dropbox directory 
    * Information in that CSV file overrides info from tmstats 
    
    The output work file is used by other programs in the alignment process such as 'alignmap' and 'makelocationreport'
    """

import sys, os, csv
import requests
from simpleclub import Club
import dropbox
import json
from datetime import datetime
from makemap import setClubCoordinatesFromGEO
from overridepositions import overrideClubPositions
import time, calendar

import tmglobals, tmparms
globals = tmglobals.tmglobals()


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
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--outfile', default='d101align.csv')
    parms.add_argument('--mapoverride', dest='mapoverride', default=None, help='Google spreadsheet with overriding address and coordinate information')
    parms.add_argument('--workingalignment', dest='workingalignment', default=None, help='Google spreadsheet with proposed alignment')
    parms.add_argument('--trustWHQ', dest='trust', action='store_true', help='Specify this to use information from WHQ because we are in the new year')
    parms.add_argument('--includeprecharter', dest='precharter', action='store_true', help='Specify this to include "pre-charter" clubs (ones with negative club numbers in the newAlignment file)')
    
    # Do global setup
    globals.setup(parms)
    conn = globals.conn
    curs = globals.curs

    
    # Get all defined clubs from the database.
    clubs = Club.getClubsOn(curs)
    # Get coordinates
    setClubCoordinatesFromGEO(clubs, curs, removeNotInGeo=False)
    # If there are overrides to club positioning, handle them now
    if parms.mapoverride:
        overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey)
    
    # Now, add info from clubperf (and create club.oldarea for each club)
    curs.execute('SELECT clubnumber, color, goalsmet, activemembers, clubstatus FROM clubperf WHERE entrytype = "L"')
    for (clubnumber, color, goalsmet, activemembers, clubstatus) in curs.fetchall():
        c = clubs[str(clubnumber)]
        c.color = color
        c.goalsmet = goalsmet
        c.activemembers = activemembers
        c.oldarea = c.division + c.area
        c.clubstatus = clubstatus
    
    if parms.trust:
        # Remove any clubs not in the District
        # patch in newarea
        for cnum in clubs:
            c = clubs[cnum]
            if int(c.district) == parms.district:
                c.newarea = c.division + c.area
                c.likelytoclose = ''
            else:
                del clubs[cnum]
    else:
        # Override clubs using the proposed alignment spreadsheet.  Allow new clubs to be created
        ignorefields = ['clubnumber', 'clubname', 'oldarea']  # These are just decoration for this phase
        donotlog = ['newarxea']  # No need to comment on this
        overrideClubPositions(clubs, parms.workingalignment, parms.googlemapsapikey, log=True, 
        ignorefields=ignorefields, donotlog=donotlog, createnewclubs=True)
        
        # Now, remove any clubs which weren't included in the proposed alignment; also, remove precharter clubs if appropriate
        # And for any clubs without a new area specified, set it to their current area
        for cnum in clubs.keys():
            c = clubs[cnum]
            if not c.touchedby or c.touchedby not in parms.workingalignment:
                del clubs[cnum]
            elif int(cnum) < 0 and not parms.includeprecharter:
                del clubs[cnum]
            else:
                if not c.newarea:
                    c.newarea = c.oldarea

                
        

    
    # Now, create the output file, sorted by newarea (because that's what we need later on)
    outfields =  'clubnumber	clubname	oldarea	newarea	likelytoclose	color	goalsmet	activemembers	meetingday	meetingtime	place	address	city	state	zip	country	latitude	longitude'.split()
    outfile = open(parms.outfile, 'w')
    writer = csv.DictWriter(outfile, fieldnames=outfields, extrasaction='ignore')
    writer.writeheader()
    
    outclubs = sorted(clubs.values(),key=lambda club:club.newarea+club.clubnumber.rjust(8))
    # Omit suspended clubs
    for c in outclubs:
        try:
            if c.clubstatus != 'Suspended':
                writer.writerow(c.__dict__)
        except:
            writer.writerow(c.__dict__)
    outfile.close()
        
    # Finally, indicate the date of Toastmasters data
    with open('alignmentsource.txt', 'w') as outfile:
        curs.execute('SELECT MAX(asof) FROM clubperf WHERE entrytype = "L"')
        outfile.write('<p>Using Toastmasters data as of %s.</p>' % curs.fetchone()[0])
    
