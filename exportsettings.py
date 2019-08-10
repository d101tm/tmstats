#!/usr/bin/env python3
""" Output 'export' statements for significant configuration items found
    in the configuration file or the database """

import sys
import tmglobals
import tmparms
import datetime

# Do the setup
globals = tmglobals.tmglobals()
# Establish parameters
parms = tmparms.tmparms()

# Do global setup
globals.setup(parms)
curs = globals.curs
conn = globals.conn

res = {}
# Information from the configuration file:
res['workdir'] = parms.workdir
res['archivedir'] = parms.archivedir
res['pindir'] = parms.pindir
res['cursordir'] = parms.cursordir

# Where this program lives
res['SCRIPTPATH'] = sys.path[0]

# Date-related information
res['dbtmyear'] = globals.tmyear
today = datetime.datetime.now()
res['caltmyear'] = today.year if today.month >= 7 else today.year - 1
res['hour'] = today.hour
res['today'] = today.strftime('%Y-%m-%d')
res['yday'] = (today - datetime.timedelta(1)).strftime('%Y-%m-%d')

for (k, v) in res.items():
    print("export %s='%s'" % (k, v))
