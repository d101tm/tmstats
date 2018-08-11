#!/usr/bin/env python3
""" Brute Force program to geocode all clubs into the GEO table """
import googlemaps
import urllib3
import logging
import dbconn, tmparms
import pprint
import os, sys
from uncodeit import myclub

import tmglobals
globals = tmglobals.tmglobals()

# Set up global environment
parms = tmparms.tmparms()
globals.setup(parms)
conn = globals.conn
curs = globals.curs

#urllib3.disable_warnings()
#logging.captureWarnings(True)
gmaps = googlemaps.Client(key=parms.googlemapsapikey)

curs.execute("SELECT clubnumber, clubname, place, address, city, state, zip, latitude, longitude FROM clubs WHERE lastdate IN (SELECT MAX(lastdate) FROM clubs) ORDER BY CLUBNUMBER;")
for (clubnumber, clubname, place, address, city, state, zip, whqlatitude, whqlongitude)  in curs.fetchall()[0:1]:
    print(clubnumber, clubname)
    print(address, city, state, zip)
    gres = gmaps.geocode("%s, %s, %s %s" % (address, city, state, zip))
    pprint.pprint(gres)
    print("=================")
    club = myclub(clubnumber, clubname, place, address, city, state, zip, whqlatitude, whqlongitude).update(gres, c)
conn.commit()

