#!/usr/bin/env python3
""" Copy current club information to working alignment CSV file 

Creates a CSV with the proper headers and information based on current
clubs.

You must copy that CSV into the Google Spreadsheet used by the alignment
committee to hold the working alignment.
"""

import tmglobals
import tmparms
from simpleclub import Club
from overridepositions import overrideClubPositions

# Establish parameters
parms = tmparms.tmparms()
# Add other parameters here

# Do global setup
myglobals = tmglobals.tmglobals()
myglobals.setup(parms)
curs = myglobals.curs
conn = myglobals.conn

headers = [
        "clubnumber",
        "clubname",
        "oldarea",
        "newarea",
        "likelytoclose",
        "color",
        "goalsmet",
        "activemembers",
        "meetingday",
        "meetingtime",
        "place",
        "address",
        "city",
        "state",
        "zip",
        "country",
        "latitude",
        "longitude"
        ]

print(','.join(headers))
# Get current club information from the clubperf file - that will include hidden and suspended clubs.
curs.execute('SELECT clubnumber, clubname, division, area FROM clubperf WHERE entrytype = "L"')
clubs = []
for club in curs.fetchall():
    clubs.append((club[0], club[1], club[2]+club[3]))

# Sort by area
clubs.sort(key=lambda club:club[2])

# And print
for club in clubs:
    print(f'{club[0]},"{club[1]}",{club[2]}')


