#!/usr/bin/env python3
""" Output 'export' statements for significant configuration items found
    in the configuration file or the database """

import tmutil, sys
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

# Date-related information
res['dbtmyear'] = globals.tmyear
today = datetime.datetime.now()
res['caltmyear'] = today.year if today.month >= 7 else today.year - 1

for (k, v) in res.items():
    print('export %s=%s' % (k, v))
