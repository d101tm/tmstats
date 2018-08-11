#!/usr/bin/env python3
""" Open House Challenge - build the HTML fragment for the Open House Challenge """

import dbconn, tmutil, sys, os
from simpleclub import Club
from datetime import datetime

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
    parms.add_argument('--infile', default='openhouseclubs.txt')
    parms.add_argument('--outfile', default='openhouseclubs.html')
    parms.add_argument('--basedate', default='12/31')
    parms.add_argument('--finaldate', default='2/15')
    parms.add_argument('--renewto', default='9/30')

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
        clubname = simplify(clubs[c].clubname)
        clubsByName[clubname] = clubs[c]
    
    # Now read the openhouse clubs and get their numbers
    eligible = {}
    with open(parms.infile, 'r') as infile:
        for l in infile.readlines():
            l = simplify(l.strip())
            if l in clubs:
                eligible[l] = clubs[l]
            elif l in clubsByName:
                eligible[clubsByName[l].clubnumber] = clubsByName[l]
            else:
                sys.stderr.write('Could not find %s in clubs\n' % (l,))
                

    
    # And build "IN" clause.  We know all the items are numbers, so we don't have to worry about SQL injection.
    eligibilityclause = ' clubnum IN (' + ','.join(list(eligible.keys())) + ') '
    
    # Now, get the count for each club of new members who have renewed for the following term
    curs.execute("SELECT clubnum, clubname, count(*) FROM roster WHERE joindate >= %s AND termenddate >= %s AND" + eligibilityclause + "GROUP BY clubnum, clubname", (basedate, renewtodate))

    for (clubnum, clubname, memdiff) in curs.fetchall():
        eligible[tmutil.stringify(clubnum)].memdiff = memdiff
        
        
    # Now, make the three lists:
    level0clubs = []   # Open House only
    level1clubs = []   # Open House, added 1 or 2 members who have renewed
    level2clubs = []   # Open House, added 3 or more members who have renewed
    
    
    
    for c in list(eligible.values()):
        if c.memdiff >= 3:
            level2clubs.append(c)
        elif c.memdiff > 0:
            level1clubs.append(c)
        else:
            level0clubs.append(c)
            

    def makecongrat(amount, winners):
        if len(winners) == 0:
            return ''
        if len(winners) == 1:
            return '<p>Congratulations to <span class="clubname">%s</span> for earning %s in District Credit.</p>\n' % (winners[0].clubname, amount)
        return '<p>Congratulations to these clubs for earning %s in District Credit: %s.</p>\n' % (amount, tmutil.getClubBlock(winners))
        
    with open(parms.outfile, 'w') as outfile:
        outfile.write(makecongrat("$25", level0clubs))
        outfile.write(makecongrat("$50", level1clubs))
        outfile.write(makecongrat("$75", level2clubs))
    
    
        
        
    
        
    
    
            
