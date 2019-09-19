#!/usr/bin/env python3
""" Update Google spreadsheet for anniversary open houses and build recognition inclusions """


from datetime import datetime, timedelta
import gspread
import tmglobals
from tmutil import cleandate, normalize, getGoogleCredentials, getClubBlock

myglobals = tmglobals.tmglobals()


class Clubinfo:
    def __init__(self, labels, row):
        self.labels = labels
        for (k, v) in zip(labels, row):
            setattr(self, k, v)

    def __repr__(self):
        return ', '.join([f'{l, getattr(self, l)}' for l in labels])

class Winner:
    def __init__(self, clubname):
        self.clubname = clubname


if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('--outfile', default='${workdir}/amazing.txt')
    parms.add_argument('--prize1', default='an Amazing Gift Basket ($45 value)')
    parms.add_argument('--prize2', default='an even more Amazing Gift Basket ($70 value)')
    parms.add_argument('--needed', default=3)

    # Do global setup
    myglobals.setup(parms)
    curs = myglobals.curs
    conn = myglobals.conn

    winners = [[],[]]  # List of clubnames for each level.

    # Get the spreadsheet
    gc = gspread.authorize(getGoogleCredentials())
    sheet = gc.open_by_url(parms.anniversaryopenhouse).sheet1
    values = sheet.get_all_values()
    labels = [normalize(c) for c in values[0]]
    deltacolumn = labels.index('newmembersadded') + 1
    eligiblethroughcol = labels.index('eligiblethrough') + 1


    # Get the final date in the database - we don't ask for data later than we have!
    curs.execute("SELECT MAX(asof) FROM clubperf")
    maxasof = curs.fetchone()[0]



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

        qbasestr = "SELECT newmembers + addnewmembers as newcount, clubname FROM clubperf WHERE asof = %s and clubnumber = %s"

        if maxasof >= startdate:
            curs.execute(qbasestr, (startdate, clubnumber))
            newstart = curs.fetchone()[0]
            curs.execute(qbasestr, (min(enddate, maxasof), clubnumber))
            (newend, clubname) = curs.fetchone()
            delta = newend - newstart
            sheet.update_cell(rownum, deltacolumn, delta)
            sheet.update_cell(rownum, eligiblethroughcol, enddate.strftime("%-m/%-d/%y"))
            # Add the club to the proper winners list
            winners[1 if delta >= parms.needed else 0].append(Winner(clubname))

    # Now, write out the congratulatory text if there are any winners.
    outfile = open(parms.outfile, 'w')
    if len(winners[0]):
        outfile.write(f'<p><b>Congratulations</b> to {getClubBlock(winners[0])}\nfor earning {parms.prize1}\n')
        outfile.write('by holding an Open House during the month of their club anniversary!</p>\n')
    if len(winners[1]):
        outfile.write(f'<p><b>Congratulations</b> to {getClubBlock(winners[1])}\nfor earning {parms.prize2}\n')
        outfile.write('by holding an Open House during the month of their club anniversary <b>and</b>\n')
        outfile.write(f'adding at least {parms.needed} members within a month of their Open House!</p>\n')
    outfile.close()

