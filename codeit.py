#!/usr/bin/env python2.7
import googlemaps
import urllib3
import logging
import dbconn, tmparms
import pprint
import os, sys
from uncodeit import myclub

reload(sys).setdefaultencoding('utf8')
# Make it easy to run under TextMate
if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
    sys.stdout.close()
    open('codeit.txt', 'w')        


#urllib3.disable_warnings()
#logging.captureWarnings(True)
gmaps = googlemaps.Client(key='AIzaSyAQJ_oe8p5ldJGJEQLSHvGpJcFocCRnxYg')
parms = tmparms.tmparms()
parms.parse()
conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
c = conn.cursor()
c.execute("SELECT clubnumber, clubname, place, address, city, state, zip, latitude, longitude FROM clubs WHERE lastdate IN (SELECT MAX(lastdate) FROM clubs) ORDER BY CLUBNUMBER;")
for (clubnumber, clubname, place, address, city, state, zip, whqlatitude, whqlongitude)  in c.fetchall():
    print clubnumber, clubname
    print address, city, state, zip
    gres = gmaps.geocode("%s, %s, %s %s" % (address, city, state, zip))
    pprint.pprint(gres)
    print "================="
    club = myclub(clubnumber, clubname, place, address, city, state, zip, whqlatitude, whqlongitude).update(gres, c)
conn.commit()

