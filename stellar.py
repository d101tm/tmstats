#!/usr/bin/env python3
""" Creates Stellar September/March Madness reports from the District Tracking Google Spreadsheet"""

import tmutil, sys
import tmglobals
from gsheet import GSheet
myglobals = tmglobals.tmglobals()

    
class level:
    def __init__(self, pct, earns, name):
        self.pct = pct
        self.earns = earns
        self.name = name
        self.winners = []


class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname,  renewals, membase, division, area):
        self.area = '%s%s' % (division, area)
        self.clubnumber = clubnumber
        self.clubname = clubname
        if renewals:
            self.renewals = int(renewals)
        else:
            self.renewals = 0
        self.membase = int(membase)
        if self.membase > 0:
            self.pct = (100.0 * self.renewals) / self.membase
        else:
            self.pct = 0

    def tablepart(self):
        return ('    <td>%s</td><td>%s</td><td>%.2f%%</td>' % (self.area, self.clubname, self.pct))

    def key(self):
        return (self.area, self.clubnumber)

if __name__ == "__main__":
    import tmparms, latest, os, sys, csv
    from datetime import datetime
    from tmutil import showclubswithvalues, cleandate, getClubBlock
    import tmglobals
    myglobals = tmglobals.tmglobals()
    

    
    # Define args and parse command line
    parms = tmparms.tmparms(description=__doc__, epilog='pct and earns must have the same number of items.\nIf names is specified, it must have the same number as well.')
    parms.add_argument('--finaldate', default='', dest='finaldate', help="Final date for qualifying.")
    parms.add_argument('--outfileprefix', default='', dest='outfileprefix', type=str, help="Output file prefix - defaults to program name.")
    parms.add_argument('--format', default='$%d in District Credit')
    parms.add_argument('--pct', dest='pct', nargs='+', type=float, help='Threshold to qualify (in percent) for each level.', default='75.0')
    parms.add_argument('--earns', dest='earns', nargs='+', type=int, help='Amount earned for each level.', default='50')
    parms.add_argument('--program', choices=['madness', 'stellar'], help='Program name')
    parms.add_argument('--name', dest='name', nargs='+', type=str, help='Name for each level.  Specify \'\' if no name for a level.')
    parms.add_argument('--trackingsheet', dest='trackingsheet', default='https://docs.google.com/spreadsheets/d/1zfNpg1o5n2GVI70PAXjQXqZQ9xNxqwdYU-mKh2ChMLA/edit#gid=1938482035')
    parms.add_argument('--sheetname', dest='sheetname', default='', help='Name of the tab in the tracking spreadsheet')

    
    # Do global setup
    myglobals.setup(parms)
    curs = myglobals.curs
    conn = myglobals.conn
    
    # Do program-specific defaulting
    if not parms.outfileprefix:
        parms.outfileprefix = parms.program
    if not parms.trackingsheet:
        if parms.program == 'madness':
            parms.trackingsheet = 'March Madness-DO NOT EDIT'
        else:
            parms.trackingsheet = 'Stellar-DO NOT EDIT'
    

    # Ensure proper matching of names, pct, and earns.
    if not isinstance(parms.pct, list):
        parms.pct = ((parms.pct,))

    if not isinstance(parms.earns, list):
        parms.earns = ((parms.earns,))

    
    if len(parms.pct) != len(parms.earns):
        sys.stderr.write('The number of values for PCT and EARNS must be the same, but we got %d in PCT and %d in EARNS\n' % (len(parms.pct), len(parms.earns)))
        sys.exit(1)

    if parms.name:
        if len(parms.pct) != len(parms.name):
            sys.stderr.write('The number of values for PCT and NAME must be the same, but we got %d in PCT and %d in NAME\n' % (len(parms.pct), len(parms.name)))
            sys.exit(1)
    else:
        parms.name = len(parms.pct) * ('',)

    levels = [level(parms.pct[i], parms.earns[i], parms.name[i]) for i in range(len(parms.pct))]
    levels.sort(key=lambda l:l.pct, reverse=True)

    # Now, get the clubs which qualify
    
    for row in GSheet(parms.trackingsheet, parms.googlesheetsapikey, sheetname="March Madness-DO NOT EDIT"):
        renewalcol = row.fieldnames.index('renewed')  # Because of duplicate column headers
        row.clubnumber = row.number  # Compensate for naming changes
        try:
            int(row.clubnumber)  # Skip non-club rows
        except ValueError:
            continue
        if renewalcol > len(row.values):
            print('Ignoring short row:', '; '.join([f'{item[0]}={item[1]}' for item in zip(row.fieldnames, row.values)])) 
            continue
        curs.execute("SELECT area, division, clubname, asof FROM clubperf WHERE clubnumber = %s ORDER BY ASOF DESC LIMIT 1", (row.clubnumber,))
        try:
            (area, division, clubname, asof) = curs.fetchone() 
        except:
            print(row)
        if (clubname.strip() != row.clubname):
            print(f'Wrong club name for {row.clubnumber}: "{row.clubname}" should be "{clubname.strip()}"')
        if 'alignment' in row.fieldnames:
            alignment = division+area        
            if alignment != row.alignment:
                print(f'Wrong alignment for {row.clubname}: should be {row.alignment}, not {alignment}')
        club = myclub(row.clubnumber, clubname, row.values[renewalcol], row.base, division, area)
        for each in levels:
            if club.pct >= each.pct:
                each.winners.append(club)
                break  # We only have to add a club to the best level it reaches


    # Now, write the results for each level
    outfile = open(os.path.join(parms.workdir, parms.outfileprefix + '.html'), 'w')

    for each in levels:
        if len(each.winners) > 0:
            winners = getClubBlock(each.winners)
            res = '<p><b>Congratulations</b> to\n' + winners + '\n for renewing' + (' at least' if each.pct < 100.0 else '') + ' %d%% ' % each.pct + 'of their base membership and earning ' + (parms.format % each.earns)
            if each.name:
                res += '. Welcome to <b>' + each.name + '</b> status'
            res += '!</p>\n'
            outfile.write(res)

    outfile.close()
    
