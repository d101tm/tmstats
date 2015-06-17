#!/usr/bin/python
""" Check currency of all four tables.  If no date specified on the command line's --date argument, use today.

    Return 0 if all four tables are current.
    Return 1 if only the clubs table is outdated.
    Return 2 in any other case.
    
    Uses the 'loaded' table.
    
"""
import tmparms, dbconn, argparse, os, sys
from datetime import datetime


if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))


# Add the '--date' argument to the parser
parms = tmparms.tmparms()
today = datetime.today()
parms.parser.add_argument("--date", nargs=1, dest='date', default=[datetime.today().strftime('%Y-%m-%d')])
parms.parse()
conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
curs = conn.cursor()
date = parms.args.date[0]
print "SELECT tablename FROM loaded WHERE loadedfor='%s'"% (date)

curs.execute("SELECT tablename FROM loaded WHERE loadedfor='%s'"% (date))
have = {}
want = ['clubs', 'clubperf', 'distperf', 'areaperf']
for x in want:
    have[x] = False
count = 0
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
