#!/usr/bin/env python
""" Check currency of all four tables for the date specified.
    If no date is specified, we want the 'clubs' table to be current for today;
      the other tables can be for today OR yesterday because they are one day behind on Toastmasters.

    Return 0 if all four tables are current.
    Return 1 if only the clubs table is outdated.
    Return 2 in any other case.
    
    Uses the 'loaded' table.
    
"""
import tmparms, os, sys, tmutil
from datetime import datetime, timedelta

import tmglobals
globals = tmglobals.tmglobals()


if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))


# Add the '--date' argument to the parser
parms = tmparms.tmparms()
today = datetime.today()
yesterday = today - timedelta(1)
today = today.strftime('%Y-%m-%d')
yesterday = yesterday.strftime('%Y-%m-%d')
parms.parser.add_argument("--date", dest='date', default=None)

# Do global setup
globals.setup(parms)
conn = globals.conn
curs = globals.curs


date = parms.date
have = {}
want = ['clubs', 'clubperf', 'distperf', 'areaperf']
for x in want:
    have[x] = False
count = 0
if date:
    date = tmutil.cleandate(date)
    # All tables have to be there for the specified date.
    curs.execute("SELECT tablename FROM loaded WHERE loadedfor='%s'"% (date))
    for x in curs.fetchall():
        have[x[0]] = True
        count += 1
else:
    curs.execute("SELECT tablename FROM loaded WHERE (loadedfor=%s OR loadedfor=%s) AND tablename IN ('clubperf', 'distperf', 'areaperf') GROUP BY tablename", (today, yesterday))
    for x in curs.fetchall():
        have[x[0]] = True
        count += 1
    curs.execute("SELECT tablename FROM loaded WHERE loadedfor=%s AND tablename = 'clubs'", (today,))
    for x in curs.fetchall():
        have[x[0]] = True
        count += 1
if count == len(want):
    sys.exit(0)   # Success!
if count == 3 and not have['clubs']:
    print 'Only clubs table is not current'
    sys.exit(1)
print 'Tables not current: %s' % ('; '.join([k for k in have if not have[k]]))
sys.exit(2)
