#!/usr/bin/env python3
""" Update Google spreadsheet for anniversary open houses """


from datetime import datetime, timedelta

import gspread

import tmglobals
from tmutil import cleandate, normalize, getGoogleCredentials

globals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn

    # Get the spreadsheet
    gc = gspread.authorize(getGoogleCredentials())
    sheet = gc.open_by_url(parms.anniversaryopenhouse).sheet1
    values = sheet.get_all_values()
    labels = [normalize(c) for c in values[0]]
    deltacolumn = labels.index('newmembersadded') + 1
    eligiblethroughcol = labels.index('eligiblethrough') + 1

    qbasestr = "SELECT newmembers + addnewmembers as newcount FROM clubperf WHERE asof = %s and clubnumber = %s"

    # Get the final date in the database - we don't ask for data later than we have!
    curs.execute("SELECT MAX(asof) FROM clubperf")
    maxasof = curs.fetchone()[0]

    class Clubinfo:
        def __init__(self, labels, row):
            self.labels = labels
            for (k, v) in zip(labels, row):
                setattr(self, k, v)

        def __repr__(self):
                return ', '.join([f'{l, getattr(self, l)}' for l in labels])

    for rownum, row in enumerate(values[1:], start=2):
        club = Clubinfo(labels, row)
        clubnumber = club.clubnumber.strip()
        if not clubnumber:
            continue

        ohdate = datetime.strptime(cleandate(club.openhousedate), "%Y-%m-%d").date()
        startdate = ohdate - timedelta(1)
        enddate = ohdate

        # Need to compute the same day in the next month - if there is no same day, go to the 1st of the following
        (m, d, y) = (ohdate.month+1, ohdate.day, ohdate.year)
        if (m == 13):
            m = 1
            y += 1
        try:
            enddate = ohdate.replace(y, m, d)
        except ValueError:
            enddate = ohdate.replace(y, m+1, 1)   # We need not worry about year overflow because November has fewer days than December

        # But in case something was specified, use it.
        if club.eligiblethrough.strip():
            try:
                enddate = datetime.strptime(cleandate(club.eligiblethrough), "%Y-%m-%d").date()
            except:
                pass

        if maxasof >= startdate:
            curs.execute(qbasestr, (startdate, clubnumber))
            newstart = curs.fetchone()[0]
            curs.execute(qbasestr, (min(enddate, maxasof), clubnumber))
            newend = curs.fetchone()[0]
            delta = newend - newstart
            sheet.update_cell(rownum, deltacolumn, delta)
            sheet.update_cell(rownum, eligiblethroughcol, enddate.strftime("%-m/%-d/%y"))



