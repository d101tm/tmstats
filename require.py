#!/usr/bin/env python3
""" Require certain conditions

    Sets the return code to 0 if all required conditions are true, else sets to 1

"""

import tmutil, sys, datetime
import tmglobals
globals = tmglobals.tmglobals()

def cleandate(s):
    return datetime.datetime.strptime(tmutil.cleandate(s, usetmyear=False), '%Y-%m-%d').date()

def datacheck(s):
    s = s.lower()
    if s.startswith('s') or s.startswith('m'):
        month = int(s[1:])
        # Compute the month to check:
        year = globals.tmyear if month >= 7 else globals.tmyear + 1
        start = "monthstart = '%d-%0.2d-01'" % (year, month)
            
        # Do we need final for the month?
        final = " AND ENTRYTYPE = 'M'" if s.startswith('m') else ''
        
        # See if we've got it
        globals.curs.execute('SELECT COUNT(*) FROM clubperf WHERE ' + start + final)
    else:
        # We have a specific date
        globals.curs.execute('SELECT COUNT(*) FROM clubperf WHERE ASOF = %s', (cleandate(s),))
    res = curs.fetchone()[0]
    if res > 0:
        return True
    else:
        return False
        
        

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    # Add other parameters here

    group = parms.add_argument_group('calendar parms')
    group.add_argument('--starting', type=str, help='First date this is true')
    group.add_argument('--ending', type=str, help='Last date this is true')
    group.add_argument('--between', type=str, nargs=2, help='First and last dates')
    group = parms.add_argument_group('database parms', 'Specify Mn if month "n" must be complete; specify Sn if month "n" must be started.')
    group.add_argument('--datafor', type=str, help='Date or Month for which data must be available.')
    group.add_argument('--nodatafor', type=str, help='Date or Month for which data must NOT be available.')
    group = parms.add_argument_group('TM Year parms')
    group.add_argument('--newtmyear', action='store_true', help='Data is available for the TM Year beginning July 1 of this calendar year')
    group.add_argument('--oldtmyear', action='store_true', help='Data is NOT available for the TM Year beginning July 1 of this calendar year')

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    today = globals.today

    if parms.starting:
        starting = cleandate(parms.starting)
        if today < starting:
            sys.exit(1)

    if parms.ending:
        ending = cleandate(parms.ending)
        if today > ending:
            sys.exit(2)

    if parms.between:
        starting = cleandate(parms.between[0])
        ending = cleandate(parms.between[1])
        if ending < starting:
            ending = ending.replace(ending.year+1)
        if today < starting or today > ending:
            sys.exit(3)
    
    if parms.datafor:
        if not datacheck(parms.datafor):
            sys.exit(4)
            
    if parms.nodatafor:
        if datacheck(parms.nodatafor):
            sys.exit(5)
        
    if parms.newtmyear:
        if globals.today.year != globals.tmyear:
            sys.exit(6)
            
    if parms.oldtmyear:
        if globals.today.year == globals.tmyear:
            sys.exit(7)
