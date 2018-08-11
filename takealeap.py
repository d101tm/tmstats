#!/usr/bin/env python3
""" Create reports for the Take a Leap promotion:

Clubs earn $40 for every DCP level they increase from the previous year.
For example, a club going from not Distinguished to Select Distinguished earns $80.
New clubs are considered "not Distinguished" for the previous year. """

import tmutil, sys, csv
import tmglobals
globals = tmglobals.tmglobals()

levels = {' ':0, 'D': 1, 'S': 2, 'P': 3}

class myclub:
    def __init__(self, dict):
        for item in dict:
            self.__dict__[item[0]] = item[1]
        self.thisyear = levels[(self.clubdistinguishedstatus+' ')[0]]
        self.lastyear = 0
        if self.activemembers < 20:
            self.needed = min(20-self.activemembers, self.membase+5-self.activemembers)
        else:
            self.needed = 0
        
 
clubs = {}

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('--tmyear', default=0, type=int, help="Toastmasters year to report on.")
    parms.add_argument('--outfile', default='takealeap.html')
    parms.add_argument('--csvfile', default='takealeap.csv')
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    if not parms.tmyear:
        parms.tmyear = globals.today.year - 1   # Use the previous TM Year during July-December
        
    # Find the latest date in the database for this and the previous TM years:
    finder = "SELECT MAX(asof) FROM clubperf WHERE monthstart >= '%d-07-01' AND monthstart <= '%d-06-01'"
    curs.execute(finder % (parms.tmyear, parms.tmyear+1))
    thisyearsdate = curs.fetchall()[0]
    
    curs.execute(finder % (parms.tmyear-1, parms.tmyear))
    lastyearsdate = curs.fetchall()[0]
               

    # Get current clubs
    curs.execute("SELECT * FROM clubperf WHERE asof = %s", (thisyearsdate,))
    # Get the column names
    columns = [item[0] for item in curs.description]
    columnsforcsv = columns[columns.index('district'):columns.index('color')]
    columnsforcsv.append('laststatus')
    columnsforcsv.append('delta')
    columnsforcsv.append('needed')
    for row in curs.fetchall():
        club = myclub(list(zip(columns, row)))
        clubs[club.clubnumber] = club
        
    # Now, update to include last year's status
    curs.execute("SELECT clubnumber, clubdistinguishedstatus FROM clubperf WHERE asof = %s", (lastyearsdate,))
    for (clubnumber, status) in curs.fetchall():
        try:
            clubs[clubnumber].laststatus = status
            clubs[clubnumber].lastyear = levels[(status+' ')[0]]
        except KeyError:
            pass
            
    # Now, compute results
    leapers = [[],[],[],[]]    # For 0-3 levels
    for club in list(clubs.values()):
        club.delta = max(0,club.thisyear - club.lastyear)
        if club.delta > 0:
            leapers[club.delta].append(club)
            
    # And create the output file
    outfile = open(parms.outfile, 'w')
    for i in range(1,4):
        if leapers[i]:
            outfile.write('<p>Congratulations to ')
            outfile.write(tmutil.getClubBlock(leapers[i]))
            outfile.write(' for earning $%d for leaping %d level%s.<p>\n' % (40*i, i, 's' if i > 1 else ''))
    outfile.close()
    
    csvfile = open(parms.csvfile, 'wb')
    csvwriter = csv.DictWriter(csvfile, fieldnames=columnsforcsv, extrasaction="ignore")
    csvwriter.writeheader()
    for club in sorted(list(clubs.values()), key=lambda c:'%s%s%.8d' % (c.division, c.area, c.clubnumber)):
        csvwriter.writerow(club.__dict__)
    csvfile.close()
    
