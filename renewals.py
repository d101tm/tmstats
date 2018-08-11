#!/usr/bin/env python3

""" Generate reports for renewal programs (March Madness, Stellar September) """
    
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
        self.renewals = renewals
        self.membase = membase
        if membase > 0:
            self.pct = (100.0 * renewals) / membase
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
    globals = tmglobals.tmglobals()
    

    
    # Define args and parse command line
    parms = tmparms.tmparms(description=__doc__, epilog='pct and earns must have the same number of items.\nIf names is specified, it must have the same number as well.')
    parms.add_argument('--finaldate', default='', dest='finaldate', help="Final date for qualifying.")
    parms.add_argument('--outfileprefix', default='', dest='outfileprefix', type=str, help="Output file prefix.")
    parms.add_argument('--format', default='$%d in District Credit')
    parms.add_argument('--pct', dest='pct', nargs='+', type=float, help='Threshold to qualify (in percent) for each level.', default='75.0')
    parms.add_argument('--earns', dest='earns', nargs='+', type=int, help='Amount earned for each level.', default='50')
    parms.add_argument('--program', choices=['madness', 'stellar'])
    parms.add_argument('--name', dest='name', nargs='+', type=str, help='Name for each level.  Specify \'\' if no name for a level.')
    
    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn

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

    # Conditionally resolve unspecified parameters
    if not parms.program:
        if datetime.today().month > 6:   # Fall
            parms.program = 'stellar'
        else:  # Spring
            parms.program = 'madness'

    if not parms.finaldate:
        parms.finaldate = '3/15' if parms.program == 'madness' else '9/15'

    if not parms.outfileprefix:
        parms.outfileprefix = parms.program

    finaldate = cleandate(parms.finaldate)

    
    # We want data for the earlier of "finaldate" or the most recent in the database
    mostrecent = latest.getlatest('distperf', conn)[1]
    # Anchor the final date to the proper TM year
    curs.execute("SELECT MAX(tmyear) FROM lastfor")
    tmyear = curs.fetchone()[0] 
    if finaldate[5:7] <= '06':
        finaldate = '%d%s' % (tmyear+1,finaldate[4:])
    else:
        finaldate = '%d%s' % (tmyear,finaldate[4:])
    asof = min(finaldate, mostrecent)
    asofd = datetime.strptime(asof, "%Y-%m-%d")
    if (asof == finaldate):
        asofnice = 'final'
    else:
        asofnice = 'for ' + asofd.strftime("%B") + " " + asofd.strftime("%d").lstrip('0')

    # Now, get the clubs which qualify
    # Because WHQ has been known to have bad base membership, we
    #   have to do the computation in the program instead of the database
    # Bring in any overrides here.    
    from specialbase import specials
    if parms.program == 'madness':
        rtype = 'aprrenewals'
    else:
        rtype = 'octrenewals'

    rawdata = [('clubnumber', 'clubname', rtype, 'membase', 'division', 'area', 'asof')]
    query = "SELECT c.clubnumber, c.clubname,  %s, c.membase, c.division, c.area   from clubperf c  inner join distperf d on c.clubnumber = d.clubnumber and c.asof = '%s' and d.asof = '%s' order by c.division, c.area" % (rtype, asof, asof)
    curs.execute(query)
    for c in curs.fetchall():
        c = list(c)
        if c[0] in specials:
            c[3] = specials[c[0]]
        rawdata.append(c+[asof])
        club = myclub(*c)
        for each in levels:
            if club.pct >= each.pct:
                each.winners.append(myclub(*c))
                break  # We only have to add a club to the best level it reaches

    # Write the raw data
    outfile = open(parms.outfileprefix + '.csv', 'w')
    csvwriter = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerows(rawdata)
    outfile.close()

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
    
