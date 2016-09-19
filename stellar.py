#!/usr/bin/env python

""" Generate the Stellar September list and table """
    


class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname,  octrenewals, membase, division, area):
        self.area = '%s%s' % (division, area)
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.octrenewals = octrenewals
        self.membase = membase
        if membase > 0:
            self.pct = (100.0 * octrenewals) / membase
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
    parms.add_argument('--finaldate', default='9/15', dest='finaldate', help="Final date for qualifying.")
    parms.add_argument('--pct', default='75.0', dest='pct', type=float, help="Threshold to qualify (in percent)")
    parms.add_argument('--outfileprefix', default='stellar', dest='outfileprefix', type=str, help="Output file prefix.")
    parms.parse()
    finaldate = cleandate(parms.finaldate)
    # print 'Connecting to %s:%s as %s' % (parms.dbhost, parms.dbname, parms.dbuser)
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # We want data for the earlier of "finaldate" or the most recent in the database
    mostrecent = latest.getlatest('distperf', conn)[1]
    # Anchor the final date to the proper TM year
    curs.execute("SELECT MAX(tmyear) FROM lastfor")
    tmyear = curs.fetchone()[0]
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
    curs.execute("SELECT c.clubnumber, c.clubname,  d.octrenewals, c.membase, c.division, c.area   from clubperf c  inner join distperf d on c.clubnumber = d.clubnumber and c.asof = %s and d.asof = %s order by c.division, c.area;", (asof, asof))
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
        res = '<b>Congratulations to our Stellar Club%s:</b> %s.\n' % ('s' if len(clubs) > 1 else '', qualifiers)

    with open(parms.outfileprefix + '.text', 'w') as outfile:
        if res:
            outfile.write(res)
    
    
    
