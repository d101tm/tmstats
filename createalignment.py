#!/usr/bin/env python3
""" Create alignment work file based on:

    * Information from the tmstats database
    * Limited to clubs in the latest CSV file in the 'newAlignment' Dropbox directory 
    * Information in that CSV file overrides info from tmstats 
    
    The output work file is used by other programs in the alignment process such as 'alignmap' and 'makelocationreport'
    """

import sys, os, csv
import requests
from simpleclub import Club
import json
from datetime import datetime
from makemap import setClubCoordinatesFromGEO
from overridepositions import overrideClubPositions
import time, calendar

import tmglobals, tmparms
globals = tmglobals.tmglobals()


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print(' '.join(args), file=file)

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
    parms.add_argument('--outfile', default='d101align.csv')
    parms.add_argument('--outdir', default='.', help='Directory to put the output file in')
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
        print(('Processing general overrides from %s' % parms.mapoverride))
        overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey,log=True, createnewclubs=True)
    
    # Now, add info from clubperf (and create club.oldarea for each club)
    curs.execute('SELECT clubnumber, color, goalsmet, activemembers, clubstatus FROM clubperf WHERE entrytype = "L"')
    for (clubnumber, color, goalsmet, activemembers, clubstatus) in curs.fetchall():
        c = clubs[str(clubnumber)]
        c.color = color
        c.goalsmet = goalsmet
        c.activemembers = activemembers
        try:
            c.oldarea = c.division + c.area
        except AttributeError:
            c.oldarea = '0D0A'
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
        donotlog = ['newarea']  # No need to comment on this
        print(('Processing working alignment from %s' % parms.workingalignment))
        overrideClubPositions(clubs, parms.workingalignment, parms.googlemapsapikey, log=True, 
        ignorefields=ignorefields, donotlog=donotlog, createnewclubs=True)
        
        # Now, remove any clubs which weren't included in the proposed alignment; also, remove precharter clubs if appropriate
        # And for any clubs without a new area specified, set it to their current area
        for cnum in list(clubs.keys()):
            c = clubs[cnum]
            if not c.touchedby or c.touchedby not in parms.workingalignment:
                del clubs[cnum]
            elif int(cnum) < 0 and not parms.includeprecharter:
                del clubs[cnum]
            else:
                if not c.newarea:
                    c.newarea = c.oldarea

                
        

    
    # Now, create the output file, sorted by newarea (because that's what we need later on)
    outfields =  'clubnumber	clubname	oldarea	newarea	likelytoclose   omitfrommap	color	goalsmet	activemembers	meetingday	meetingtime	place	address	city	state	zip	country	latitude	longitude'.split()
    outfile = open(os.path.join(parms.outdir, parms.outfile), 'w')
    writer = csv.DictWriter(outfile, fieldnames=outfields, extrasaction='ignore')
    writer.writeheader()
    
    outclubs = sorted(list(clubs.values()),key=lambda club:club.newarea+club.clubnumber.rjust(8))
    # Omit suspended clubs
    for c in outclubs:
        try:
            if c.clubstatus != 'Suspended':
                writer.writerow(c.__dict__)
        except:
            print((c.__dict__))
            writer.writerow(c.__dict__)
    outfile.close()
        
    # Finally, indicate the date of Toastmasters data
    with open('alignmentsource.txt', 'w') as outfile:
        curs.execute('SELECT MAX(asof) FROM clubperf WHERE entrytype = "L"')
        outfile.write('<p>Using Toastmasters data as of %s.</p>' % curs.fetchone()[0])
    
