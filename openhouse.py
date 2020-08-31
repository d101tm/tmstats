#!/usr/bin/env python3
""" Open House Challenge - build the HTML fragment for the Open House Challenge 
    Using the newest version of the Toastmasters District Roster, with the previous
    term's memberships shown as 'UNPAID'.
"""

import dbconn, tmutil, sys, os
from simpleclub import Club
from datetime import datetime
from gsheet import GSheet 
from overridepositions import overrideClubPositions

import tmglobals
globals = tmglobals.tmglobals()


    
def simplify(name):
    # Simplify club name by lowercasing, removing spaces, "Toastmasters", and "Club"
    name = name.lower()
    name = name.replace('toastmasters','')
    name = name.replace('club','')
    name = name.replace(' ','')
    return name

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--verbose', '-v', action='count')
    parms.add_argument('--openhouseclubs', default='', help="")
    parms.add_argument('--outfile', default='${workdir}/openhouseclubs.html')
    parms.add_argument('--basedate', default='8/1')
    parms.add_argument('--finaldate', default='10/31')
    parms.add_argument('--renewto', default='3/31/2020')
    parms.add_argument('--requireopenhouse', action='store_true')
    parms.add_argument('--sheetname', default='2019 Summer')

    #Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    
    # Figure out the full base and final dates, anchoring them in the current TM year
    basedate = tmutil.cleandate(parms.basedate)
    finaldate = tmutil.cleandate(parms.finaldate)
    # Also figure out the term end date we need, anchored to the calendar year
    renewtodate = tmutil.cleandate(parms.renewto, usetmyear=False)
     
    # Get all clubs for this year; we'll sort out suspended clubs later if need be
    clubs = Club.getClubsOn(curs)
    overrideClubPositions(clubs, parms.mapoverride, parms.googlemapsapikey, createnewclubs=True)
    
    # And index them by name as well as number; set memdiff = 0 for each club.
    clubsByName = {}
    for c in list(clubs.keys()):
        clubs[c].memdiff = 0
        clubs[c].openhouse = False
        clubs[c].earnings = 0
        clubname = simplify(clubs[c].clubname)
        clubsByName[clubname] = clubs[c]
    
    # Build the result arrays
    only3 = []
    only5 = []
    OHand3 = []
    OHand5 = []
    onlyOH = []

    sheet = GSheet(parms.openhouseclubs, parms.googlesheetsapikey, sheetname=parms.sheetname)
    # Now read the openhouse clubs and get their numbers
    
    hadOH = set()
    for row in sheet:
        cn = '%s' % row.clubnumber
        hadOH.add(cn)
        clubs[cn].openhouse = True
        clubs[cn].earnings += 15           # Earn $15 for an Open House

    
    # And build "IN" clause.  We know all the items are numbers, so we don't have to worry about SQL injection.
    if parms.requireopenhouse:
        eligibilityclause = 'AND clubnum IN (' + ','.join(list(hadOH)) + ') '
    else:
        eligibilityclause = ''
        
    # Build the query:
    query = """SELECT roster.clubnum, COUNT(*) FROM roster 
              INNER JOIN (SELECT clubnum, membernum FROM roster WHERE clubjoindate >= %s AND clubjoindate <= %s AND paidstatus = 'PAID') n 
              ON roster.clubnum = n.clubnum AND roster.membernum = n.membernum 
              WHERE termenddate >= %s """ + eligibilityclause + " AND paidstatus = 'PAID' GROUP BY roster.clubnum"
    # And get the results:

    curs.execute(query, (basedate, finaldate, renewtodate))
    
    # And assign clubs according to the Fall 2018 Criteria
    
    for (clubnum, memdiff) in curs.fetchall():
        cn = '%s' % clubnum
        try:
            clubs[cn].memdiff = memdiff
        except KeyError:
            print(f'Club number {cn} not found in Clubs table; memdiff = {memdiff}')
            continue
        if memdiff >= 5:
            clubs[cn].earnings += 50  # Includes the earnings for 3 
            if clubs[cn].openhouse:
                OHand5.append(clubs[cn])
                hadOH.remove(cn)
            else:
                only5.append(clubs[cn])
        elif memdiff >= 3:
            clubs[cn].earnings += 20
            if clubs[cn].openhouse:
                OHand3.append(clubs[cn])
                hadOH.remove(cn)
            else:
                only3.append(clubs[cn])
        
    # Now, 'hadOH' is reduced to clubs which had an Open House but didn't add enough members
    onlyOH = [clubs[cn] for cn in hadOH]

    def makecongrat(why, winners):
        if len(winners) == 0:
            return ''
        amount = winners[0].earnings

        if len(winners) == 1:
            return '<p><b>Congratulations</b> to %s for earning $%s in District Credit by %s.' % (tmutil.getClubBlock(winners), amount, why)
        else:
            return '<p><b>Congratulations</b> to these clubs for earning $%s in District Credit by %s: %s.</p>\n' % (amount, why, tmutil.getClubBlock(winners))
        
    with open(parms.outfile, 'w') as outfile:
        outfile.write(makecongrat("holding an Open House and adding at least 5 members", OHand5))
        outfile.write(makecongrat("holding an Open House and adding at least 3 members", OHand3))
        outfile.write(makecongrat("holding an Open House", onlyOH))
        outfile.write(makecongrat("adding at least 5 members", only5))
        outfile.write(makecongrat("adding at least 3 members", only3))
        
    
    
        
        
    
        
    
    
            
