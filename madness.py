#!/usr/bin/python

""" Generate the March Madness report for the What's Trending page. """
    


class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname,  pct, division, area):
        self.area = '%s%s' % (division, area)
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.pct = pct 

    def tablepart(self):
        return ('    <td>%s</td><td>%s</td><td>%.2f%%</td>' % (self.area, self.clubname, self.pct))

    def key(self):
        return (self.area, self.clubnumber)

if __name__ == "__main__":
    import dbconn, tmparms, latest, os, sys, argparse
    from datetime import datetime
    from tmutil import showclubswithvalues, cleandate
    
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    # Get around unicode problems
    reload(sys).setdefaultencoding('utf8')
    
    # Define args and parse command line
    parms = tmparms.tmparms(description=__doc__)
    parms.add_argument('--finaldate', default='3/15', dest='finaldate', help="Final date for qualifying.")
    parms.add_argument('--outfile', default='madness.html', dest='outfile', type=argparse.FileType('w'), help="Output file.")
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
    finaldate = '%d%s' % (tmyear+1,finaldate[4:])
    asof = min(finaldate, mostrecent)
    asofd = datetime.strptime(asof, "%Y-%m-%d")
    if (asof == finaldate):
        asofnice = 'final'
    else:
        asofnice = 'for ' + asofd.strftime("%B") + " " + asofd.strftime("%d").lstrip('0')

    curs.execute("SELECT MAX(loadedfor) FROM loaded WHERE tablename = 'clubs'")
    clubdate = curs.fetchone()[0].strftime("%Y-%m-%d") 
    clubdate = min(finaldate, clubdate)
    
    # Now, get the clubs which qualify
    # We compute using the base as of the first July data we have
    curs.execute("SELECT MIN(asof) FROM clubperf WHERE monthstart = '%d-07-01'" % tmyear)
    firstdate = curs.fetchone()[0]


    clubs = []
    curs.execute("SELECT d.clubnumber, d.clubname,  100.0 * (d.aprrenewals / c.membase) as pct, d.division, d.area   from clubperf c  inner join distperf d on c.clubnumber = d.clubnumber and c.asof = %s and d.asof = %s having pct >= 75", (firstdate, asof))
    for c in curs.fetchall():
        clubs.append(myclub(*c))

    # Now, add clubs which chartered this year.  We use their charter membership as their base.
    query = "SELECT d.clubnumber, d.clubname, 100.0 * (d.aprrenewals / d.totalcharter) AS pct, d.division, d.area FROM  (SELECT clubnumber, charterdate FROM clubs WHERE charterdate >= '%s' AND firstdate <= '%s' AND lastdate >= '%s') c INNER JOIN distperf d ON c.clubnumber = d.clubnumber AND d.asof = '%s' HAVING pct >= 75"% (firstdate, clubdate, clubdate, asof)
    curs.execute(query)

    for c in curs.fetchall():
        clubs.append(myclub(*c))


    clubs.sort(key=lambda c: c.key())
    
    # And write the report.
        
    parms.outfile.write('<h3 id="madness">March Madness</h3>\n')
    parms.outfile.write('<p>Clubs renewing at least 75% of their base membership by March 15 receive $50 in District Credit.\n')
    parms.outfile.write('This report is %s.</p>\n' % asofnice)
    showclubswithvalues(clubs, 'Renewed', parms.outfile)
    
    
