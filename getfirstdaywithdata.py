#!/usr/bin/env python3
""" Return the first date of the TM year with data """

import tmutil, sys
import tmglobals
globals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('year', type=int, default=0, nargs='?')
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    # Get the year start
    if not parms.year:
        yearstart = '%s-07-01' % tmutil.getTMYearFromDB(curs)
    else:
        yearstart = '%s-07-01' % parms.year
    
    # Get the first day with data
    curs.execute('SELECT MIN(loadedfor) FROM loaded WHERE monthstart >= %s', (yearstart,))
    print((curs.fetchone()[0]))
    
