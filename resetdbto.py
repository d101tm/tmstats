#!/usr/bin/env python3
""" Reset database to specified date """

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os, populatelastfor
import tmglobals
globals = tmglobals.tmglobals()


### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--clubsonly', action='store_true')
    parms.add_argument('resetto', default='yesterday', help="Date to reset the database to.")
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    # Your main program begins here.
    resetdate = tmutil.cleandate(parms.resetto)
    print('Resetting %sdatabase to %s' % ('CLUBS and CLUBCHANGES tables in ' if parms.clubsonly else '', resetdate))
    
    # Reset LOADED; reset the performance tables (if called for)
    # NOTE:  Does NOT reset the entrytype in the performance tables to match the latest for each club.
    if parms.clubsonly:
        curs.execute("DELETE FROM loaded WHERE loadedfor > %s AND tablename = 'clubs'", (resetdate,))
    else:
        curs.execute("DELETE FROM loaded WHERE loadedfor > %s", (resetdate,))
        curs.execute("DELETE FROM loaded WHERE loadedfor > %s AND tablename LIKE '%%perf'", (resetdate,))
        perftables = ("areaperf", "distperf", "clubperf")
        for t in perftables:
            curs.execute("DELETE FROM " + t + " WHERE asof > %s", (resetdate,))
    
    # Reset the club changes table
    curs.execute("DELETE FROM clubchanges WHERE changedate > %s", (resetdate,))
    
    # Take care of clubs
    # First, remove any items whose first date is after the resetdate
    curs.execute("DELETE FROM clubs WHERE firstdate > %s", (resetdate,))
    
    # And now, reset any items whose last date is after the resetdate
    curs.execute("UPDATE clubs SET lastdate = %s where lastdate > %s", (resetdate, resetdate))
    
    # Finally, rebuild lastfor
    populatelastfor.doit(curs, parms)
    
    # And declare victory
    conn.commit()
    conn.close()
    
