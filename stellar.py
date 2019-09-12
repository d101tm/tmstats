#!/usr/bin/env python3
""" Temporary program to create the Stellar September winners list """

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
        self.renewals = int(renewals)
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
    from tmutil import showclubswithvalues, cleandate, getClubBlock, gotodatadir
    import tmglobals
    myglobals = tmglobals.tmglobals()
    

    
    # Define args and parse command line
    parms = tmparms.tmparms(description=__doc__, epilog='pct and earns must have the same number of items.\nIf names is specified, it must have the same number as well.')
    parms.add_argument('--finaldate', default='', dest='finaldate', help="Final date for qualifying.")
    parms.add_argument('--outfileprefix', default='stellar', dest='outfileprefix', type=str, help="Output file prefix.")
    parms.add_argument('--format', default='$%d in District Credit')
    parms.add_argument('--pct', dest='pct', nargs='+', type=float, help='Threshold to qualify (in percent) for each level.', default='75.0')
    parms.add_argument('--earns', dest='earns', nargs='+', type=int, help='Amount earned for each level.', default='50')
    parms.add_argument('--program', choices=['madness', 'stellar'])
    parms.add_argument('--name', dest='name', nargs='+', type=str, help='Name for each level.  Specify \'\' if no name for a level.')
    parms.add_argument('--sheet', dest='sheet', default='https://docs.google.com/spreadsheets/d/1zfNpg1o5n2GVI70PAXjQXqZQ9xNxqwdYU-mKh2ChMLA/edit?pli=1#gid=1558598313')
    
    # Do global setup
    myglobals.setup(parms)
    curs = myglobals.curs
    conn = myglobals.conn

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
    
    for row in GSheet(parms.sheet, parms.googlesheetsapikey, sheetname="Oct Renewals"):
        renewalcol = row.fieldnames.index('renewed')  # Because of duplicate column headers
        row.clubnumber = row.number  # Compensate for naming changes
        try:
            int(row.clubnumber)  # Skip non-club rows
        except ValueError:
            continue
        curs.execute("SELECT area, division, clubname, asof FROM clubperf WHERE clubnumber = %s ORDER BY ASOF DESC LIMIT 1", (row.clubnumber,))
        (area, division, clubname, asof) = curs.fetchone() 
        club = myclub(row.clubnumber, clubname, row.values[renewalcol], row.base, division, area)
        for each in levels:
            if club.pct >= each.pct:
                each.winners.append(club)
                break  # We only have to add a club to the best level it reaches


    # Now, write the results for each level
    outfile = open(parms.outfileprefix + '.text', 'w')

    for each in levels:
        if len(each.winners) > 0:
            winners = getClubBlock(each.winners)
            res = '<p><b>Congratulations</b> to\n' + winners + '\n for renewing' + (' at least' if each.pct < 100.0 else '') + ' %d%% ' % each.pct + 'of their base membership and earning ' + (parms.format % each.earns)
            if each.name:
                res += '. Welcome to <b>' + each.name + '</b> status'
            res += '!</p>\n'
            outfile.write(res)

    outfile.close()
    
