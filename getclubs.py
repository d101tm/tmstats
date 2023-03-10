#!/usr/bin/env python3
""" Get club list from WHQ. """

import sys
import tmglobals
import json
import requests
import csv
from datetime import datetime
from tmutil import gotoworkdir
import os

myglobals = tmglobals.tmglobals()

### Insert classes and functions here.  The main program begins in the "if" statement below.

def writeClubData(district, outfile):

    def getit(c, fields):
        # 'fields' is a space-separated list of fields to be fetched in turn.
        # So to get c['Classification']['District']['Name'], call get(c'Classification District Name')
        # Returns an empty string if the object isn't there
        input = c
        for f in fields.split():
            if input:
                input = input.get(f, '')
        return input if input else ''


    # Get the JSON file from WHQ
    clubinfo = json.loads(requests.get(f'https://www.toastmasters.org/api/sitecore/FindAClub/Search?q=&district={district:>02}&advanced=1&latitude=1&longitude=1').text)


    fieldnames = (
        "District",
        "Area",
        "Division",
        "Club Number",
        "Club Name",
        "Charter Date",
        "Location",
        "Address",
        "City",
        "State",
        "Zip",
        "Country",
        "Phone",
        "Meeting Time",
        "Meeting Day",
        "Club Status",
        "Club Website",
        "Club Email",
        "Facebook",
        "Twitter",
        "Longitude",
        "Latitude",
        "Advanced?",
        "Allows Online Attendance?",
        "Prospective Club?"
    )

    out = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
    out.writerow(fieldnames)

    # Now, for every club, create a row with the necessary information
    for c in clubinfo['Clubs']:
        row = []
        # District
        row.append(getit(c, 'Classification District Name'))
        # Area
        row.append(getit(c, 'Classification Area Name'))
        # Division
        row.append(getit(c, 'Classification Division Name'))
        # Club Number
        row.append(getit(c, 'Identification Id Value'))
        # Club Name
        row.append(getit(c, 'Identification Id Name'))
        # Charter Date
        cd = getit(c, 'CharterDate')
        if cd:
            cd = int(cd.replace('/','').replace('Date','').replace('(','').replace(')','')) / 1000
            cd = datetime.utcfromtimestamp(cd)  # This works because we're west of Greenwich
            row.append(cd.strftime('%m/%d/%Y'))
        else:
            row.append('')
        # Location
        row.append(getit(c, 'Location'))
        # Address
        row.append(getit(c, 'Address Street'))
        # City
        row.append(getit(c, 'Address City'))
        # State
        row.append(getit(c, 'Address PrimaryRegionDescription'))
        # Zip
        row.append(getit(c, 'Address PostalCode'))
        # Country
        row.append(getit(c, 'CountryName'))
        # Phone
        phone = getit(c, 'Phone')
        # Toastmasters was having some problems with the phone field when I was writing this.
        phone = phone.replace('+undefined','').replace('undefined','')
        row.append(phone)
        # Meeting Time
        row.append(getit(c, 'MeetingTime'))
        # Meeting Day
        row.append(getit(c, 'MeetingDay'))
        # Club Status
        row.append('Restricted' if getit(c, 'Restriction') else 'Open')
        # Club Website
        row.append(getit(c, 'Website'))
        # Club Email
        row.append(getit(c, 'Email'))
        # Facebook
        row.append(getit(c, 'FacebookLink'))
        # Twitter
        row.append(getit(c, 'TwitterLink'))
        # Longitude
        row.append(getit(c, 'Address Coordinates Longitude'))
        # Latitude
        row.append(getit(c, 'Address Coordinates Latitude'))
        # Advanced?
        row.append('Yes' if getit(c, 'Note') else '')
        # Allows Online Attendance?
        row.append('Yes' if getit(c, 'AllowsVirtualAttendance') else '')
        # Prospective Club?
        row.append('Yes' if getit(c, 'IsProspective') else '')
        out.writerow(row)

if __name__ == "__main__":
    import tmparms

    # Establish parameters
    parms = tmparms.tmparms()
    # Add other parameters here
    parms.add_argument('--district', type=int)
    parms.add_argument('outfile', type=str, nargs='?', help='Defaults to clubs.csv in the work directory.')


    # Do global setup
    myglobals.setup(parms)
    curs = myglobals.curs
    conn = myglobals.conn

    if not parms.outfile:
        gotoworkdir()
        parms.outfile = os.path.join(parms.workdir, 'clubs.csv')


    # And do the job
    writeClubData(parms.district, open(parms.outfile, 'w'))


