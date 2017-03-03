#!/usr/bin/env python

""" Generate the March Madness report for the What's Trending page. """
    


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
    import dbconn, tmparms, latest, os, sys, argparse
    from datetime import datetime
    from tmutil import showclubswithvalues, cleandate, getClubBlock, gotodatadir
    
    gotodatadir()           # Move to the proper data directory
        

    # Get around unicode problems
    reload(sys).setdefaultencoding('utf8')
    
    # Define args and parse command line
    parms = tmparms.tmparms(description=__doc__)
    parms.add_argument('--finaldate', default='', dest='finaldate', help="Final date for qualifying.")
    parms.add_argument('--pct', default='75.0', dest='pct', type=float, help="Threshold to qualify (in percent)")
    parms.add_argument('--outfileprefix', default='', dest='outfileprefix', type=str, help="Output file prefix.")
    parms.add_argument('--earning', default='$50 in District Credit')
    parms.add_argument('--program', choices=['madness', 'stellar'])
    parms.parse()

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
    # print 'Connecting to %s:%s as %s' % (parms.dbhost, parms.dbname, parms.dbuser)
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
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
    # Because WHQ has fouled up the base for some clubs in 2016-17, we
    #   have to do the computation in the program instead of the database

    specials = {5042810: 36, 5404978: 25, 5474126: 44, 5477675: 29}
    clubs = []
    if parms.program == 'madness':
        rtype = 'aprrenewals'
    else:
        rtype = 'octrenewals'

    query = "SELECT c.clubnumber, c.clubname,  %s, c.membase, c.division, c.area   from clubperf c  inner join distperf d on c.clubnumber = d.clubnumber and c.asof = '%s' and d.asof = '%s' order by c.division, c.area" % (rtype, asof, asof)
    curs.execute(query)
    for c in curs.fetchall():
        c = list(c)
        if c[0] in specials:
            c[3] = specials[c[0]]
        club = myclub(*c)
        if club.pct >= parms.pct:
            clubs.append(myclub(*c))


    clubs.sort(key=lambda c: c.key())
    
    # And write the report.
    outfile = open(parms.outfileprefix + '.html', 'w')
    outfile.write('<p>This report is %s.</p>\n' % asofnice)
    showclubswithvalues(clubs, 'Renewed', outfile)
    outfile.close()

    # And write the paragraph form.
    qualifiers = getClubBlock(clubs)
    if len(clubs) == 0:
        res = ''
    else:
        res = '<p><b>Congratulations</b> to %s for earning %s!</p>' % (qualifiers, parms.earning)

    with open(parms.outfileprefix + '.text', 'w') as outfile:
        if res:
            outfile.write(res)
    
