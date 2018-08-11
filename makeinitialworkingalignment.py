#!/usr/bin/env python3
""" Copy current club information to working alignment CSV file 

Creates a CSV with the proper headers and information based on current
clubs.  Copy that CSV into the Google Spreadsheet used by the alignment
committee to hold the working alignment.
"""

import tmutil, sys
import tmglobals
globals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    from simpleclub import Club
    
    # Establish parameters
    parms = tmparms.tmparms()
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
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
    clubs = Club.getClubsOn(curs)
    for c in sorted(list(clubs.values()),key=lambda c:c.division+c.area):
        print(('%s,"%s",%s%s' % (c.clubnumber, c.clubname, c.division, c.area)))
    
