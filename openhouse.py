#!/usr/bin/env python3
""" Open House Challenge - build the HTML fragment for the Open House Challenge """

import dbconn, tmutil, sys, os
from simpleclub import Club
from datetime import datetime
from gsheet import GSheet 

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
    parms.add_argument('--outfile', default='openhouseclubs.html')
    parms.add_argument('--basedate', default='9/1')
    parms.add_argument('--finaldate', default='10/31')
    parms.add_argument('--renewto', default='3/31/2019')
    parms.add_argument('--requireopenhouse', action='store_true')

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
 
    # And get the clubs on the base date
    clubs = Club.getClubsOn(curs,date=basedate)
    
    # And index them by name as well as number; set memdiff = 0 for each club.
    clubsByName = {}
    for c in list(clubs.keys()):
        clubs[c].memdiff = 0
        clubs[c].openhouse = False
        clubs[c].earnings = 0
        clubname = simplify(clubs[c].clubname)
        clubsByName[clubname] = clubs[c]
    
    sheet = GSheet(parms.openhouseclubs, parms.googlesheetsapikey)
    # Now read the openhouse clubs and get their numbers
    eligible = set()
    for row in sheet:
        cn = '%s' % row.clubnumber
        eligible.add(cn)
        clubs[cn].openhouse = True
        clubs[cn].earnings += 20           # Earn $20 for an Open House
   

    
    # And build "IN" clause.  We know all the items are numbers, so we don't have to worry about SQL injection.
    if parms.requireopenhouse:
        eligibilityclause = 'AND clubnum IN (' + ','.join(list(eligible)) + ') '
    else:
        eligibilityclause = ''
        
    onlyOH = []
    only3 = []
    only5 = []
    OHand3 = []
    OHand5 = []
    
    # Now, get the count for each club of new members who have renewed for the following term
    curs.execute("SELECT clubnum, clubname, count(*) FROM roster WHERE memberofclubsince >= %s AND memberofclubsince <= %s AND termenddate >= %s " + eligibilityclause + "GROUP BY clubnum, clubname", (basedate, finaldate, renewtodate))
    
    # And assign clubs according to the Fall 2018 Criteria
    
    for (clubnum, clubname, memdiff) in curs.fetchall():
        cn = '%s' % clubnum
        if memdiff >= 5:
            clubs[cn].earnings += 40
            if clubs[cn].openhouse:
                OHand5.append(clubs[cn])
            else:
                only5.append(clubs[cn])
        elif memdiff >= 3:
            clubs[cn].earnings += 20
            if clubs[cn].openhouse:
                OHand3.append(clubs[cn])
            else:
                only3.append(clubs[cn])
        elif clubs[cn].openhouse:
            onlyOH.append(clubs[cn])
            
        clubs['%s' % clubnum].memdiff = memdiff
        
    # This is all based on the 2018 Fall criteria.
            
   

    def makecongrat(why, amount, winners):
        if len(winners) == 0:
            return ''
        elif len(winners) == 1:
            return '<p><b>Congratulations</b> to %s for earning %s in District Credit by %s.' % (tmutil.getClubBlock(winners), amount, why)
        else:
            return '<p><b>Congratulations</b> to these clubs for earning %s in District Credit by %s: %s.</p>\n' % (amount, why, tmutil.getClubBlock(winners))
        
    with open(parms.outfile, 'w') as outfile:
        outfile.write(makecongrat("holding an Open House and adding at least 5 members", "$60", OHand5))
        outfile.write(makecongrat("holding an Open House and adding at least 3 members", "$40", OHand3))
        outfile.write(makecongrat("holding an Open House", "$20", onlyOH))
        outfile.write(makecongrat("adding at least 5 members", "$40", only5))
        outfile.write(makecongrat("adding at least 3 members", "$20", only3))
        
    
    
        
        
    
        
    
    
            
