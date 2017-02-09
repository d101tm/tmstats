#!/usr/bin/env python
""" Open House Challenge - build the HTML fragment for the Open House Challenge """

import dbconn, tmutil, sys, os
from simpleclub import Club
from datetime import datetime

class myclub:
    def __init__(self, clubname, clubnumber):
        self.clubname = clubname
        self.clubnumber = clubnumber
        
def fixdate(d):
    # Fix a date (as text) in the appropriate TM year.  Return as string.
    dt = datetime.strptime(d, '%Y-%m-%d')
    if (dt.month > 6):
        dt = dt.replace(year=dt.year-1)
    return dt.strftime('%Y-%m-%d')
    
    

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    tmutil.gotodatadir()           # Move to the proper data directory
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--verbose', '-v', action='count')
    parms.add_argument('--infile', default='openhouseclubs.txt')
    parms.add_argument('--outfile', default='openhouseclubs.html')
    parms.add_argument('--basedate', default='12/31')
    parms.add_argument('--finaldate', default='2/15')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    
    # Figure out the full base and final dates, anchoring them in the current TM year
    basedate = fixdate(tmutil.cleandate(parms.basedate))
    finaldate = fixdate(tmutil.cleandate(parms.finaldate))
 
    # And get the clubs on the base date
    clubs = Club.getClubsOn(curs,date=basedate)
    
    # And index them by name as well as number
    clubsByName = {}
    for c in clubs.keys():
        clubname = clubs[c].clubname
        clubsByName[clubname] = clubs[c]
    
    # Now read the openhouse clubs and get their numbers
    eligible = {}
    with open(parms.infile, 'r') as infile:
        for l in infile.readlines():
            l = l.strip()
            if l in clubs:
                eligible[l] = clubs[l]
            elif l in clubsByName:
                eligible[clubsByName[l].clubnumber] = clubsByName[l]
            else:
                sys.stderr.write('Could not find %s in clubs\n' % (l,))
                

    
    # And build "IN" clause.  We know all the items are numbers, so we don't have to worry about SQL injection.
    eligibilityclause = ' IN (' + ','.join(eligible.keys()) + ') '
    
    
    # Now, get membership difference for today or the end of the contest

    curs.execute("SELECT c.clubnumber, c.clubname, c.asof, (c.activemembers - c.membase) - (p.activemembers - p.membase) AS delta FROM clubperf c INNER JOIN (SELECT activemembers, membase, clubnumber FROM clubperf WHERE asof = %s) p ON p.clubnumber = c.clubnumber WHERE asof = %s AND c.clubnumber" + eligibilityclause +  "ORDER BY LCASE(c.clubname)" , (basedate, finaldate))
    if curs.rowcount:
        final = True
    else:
        # No data returned; use today's data instead
        curs.execute("SELECT c.clubnumber, c.clubname, c.asof, (c.activemembers - c.membase) - (p.activemembers - p.membase) AS delta FROM clubperf c INNER JOIN (SELECT activemembers, membase, clubnumber FROM clubperf WHERE asof = %s)  p ON p.clubnumber = c.clubnumber WHERE entrytype = 'L' AND c.clubnumber" + eligibilityclause + "ORDER BY LCASE(c.clubname)",  (basedate, ))
        final = False
        
    
    for (clubnum, clubname, asof, delta) in curs.fetchall():
        eligible[tmutil.stringify(clubnum)].delta = delta
        
    # And check the renewal status for each eligible club, as of today
    curs.execute("SELECT c.clubnumber, c.memduesontimeapr FROM clubperf c WHERE entrytype = 'L' AND c.clubnumber" + eligibilityclause)
    for (clubnum, ontime) in curs.fetchall():
        eligible[tmutil.stringify(clubnum)].renewed = ontime
        
    # Now, make the three lists:
    level0clubs = []   # Open House only
    level1clubs = []   # Open House, renewed, added 1 or 2 members
    level2clubs = []   # Open House, renewed, added 3 or more members
    
    
    
    for c in eligible.values():
        if c.renewed and c.delta >= 3:
            level2clubs.append(c)
        elif c.renewed and c.delta > 0:
            level1clubs.append(c)
        else:
            level0clubs.append(c)
            

    def makecongrat(amount, winners):
        if len(winners) == 0:
            return ''
        if len(winners) == 1:
            return '<p>Congratulations to <span class="clubname">%s</span> for earning %s in District Credit.</p>\n' % (winners[0].clubname, amount)
        return '<p>Congratulations to these clubs for earning %s in District Credit: %s</p>\n' % (amount, tmutil.getClubBlock(winners))
        
    with open(parms.outfile, 'w') as outfile:
        outfile.write(makecongrat("$25", level0clubs))
        outfile.write(makecongrat("$50", level1clubs))
        outfile.write(makecongrat("$75", level2clubs))
    
    
        
        
    
        
    
    
            
