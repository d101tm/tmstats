#!/usr/bin/env python3
""" Creates the "Five for 5" report and mail it to the Program Quality Director """

import sys, csv
import tmparms, datetime
from tmutil import cleandate, UnicodeWriter, daybefore, stringify, isMonthFinal, haveDataFor, getMonthStart, getMonthEnd, dateAsWords, neaten, getClubBlock

import tmglobals
globals = tmglobals.tmglobals()


   

class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname, division, area, endnum, startnum, growth):
        self.area = area
        self.division = division
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.growth = growth



    def tablepart(self):
        return ('    <td>%s</td><td>%s</td>' % (self.area, self.clubname))

    def key(self):
        return '%s%2s%8s' % (self.division, self.area, self.clubnumber)



if __name__ == "__main__":

    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument("--basedate", dest='basedate', default='M3')
    parms.add_argument("--finaldate", dest='finaldate', default='5/15')
    parms.add_argument('--outfile', dest='outfile', default='fivefor5.html')
    parms.add_argument('--emailfile', dest='emailfile', default='fivefor5.email')
    
    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    

    # See if we have the data needed to run and build the base part of the query
    if parms.basedate.upper().startswith('M'):
        basemonth = int(parms.basedate[1:])
        if not isMonthFinal(basemonth, curs):
            sys.exit(1)
        basepart = 'monthstart = "%s" AND entrytype = "M"' % getMonthStart(basemonth, curs)
        friendlybase = 'New Members on %s' % neaten(getMonthEnd(basemonth))
        msgdate = datetime.date(globals.today.year, basemonth+1, 1)
        if basemonth == 12:
            msgdate = datetime.date(globals.today.year, 1, 1)
    else:
        basedate = cleandate(parms.basedate)
        if not haveDataFor(basedate, curs):
            sys.exit(1)
        basepart = 'asof = "%s"' % basedate
        msgdate = datetime.datetime.strptime(basedate, '%Y-%m-%d')
        friendlybase = 'New Members on %s' % neaten(msgdate)
    msgbase = dateAsWords(msgdate)

    # Figure out the end date and build that part of the query
    yesterday = cleandate('yesterday')
    if parms.finaldate.upper().startswith('M'):
        finalmonth = int(parms.finaldate[1:])
        msgdate = getMonthEnd(finalmonth)
        if isMonthFinal(finalmonth, curs):
            finalpart = 'monthstart = "%s" AND entrytype = "M"' % getMonthStart(finalmonth, curs)
            final = True
            reportdate = msgdate
        else:
            final = False
            finalpart = 'entrytype = "L"'
            reportdate = yesterday
    else:
        finaldate = cleandate(parms.finaldate)
        final = finaldate <= yesterday
        reportdate = min(finaldate,yesterday)
        finalpart = 'asof = "%s"' % reportdate
        msgdate = datetime.datetime.strptime(finaldate, '%Y-%m-%d')
    if isinstance(reportdate,str):
    	reportdate = datetime.datetime.strptime(reportdate, '%Y-%m-%d')
    prevdate = reportdate - datetime.timedelta(1)    # Need to find new qualifiers
    prevpart = 'asof = "%s"' % prevdate.date()
    friendlyend = 'New Members on %s' % neaten(reportdate)
    msgfinal = dateAsWords(msgdate)


    # OK, now find clubs with 5 or more members added
    query = 'SELECT c.clubnumber, c.clubname, c.division, c.area, c.newmembers, b.newmembers, a.newmembers FROM distperf c LEFT OUTER JOIN (SELECT clubnumber, newmembers FROM distperf WHERE %s) b ON b.clubnumber = c.clubnumber LEFT OUTER JOIN (SELECT clubnumber, newmembers FROM distperf WHERE %s) a ON a.clubnumber = c.clubnumber WHERE %s  ORDER BY c.division, c.area, c.clubnumber'
    curs.execute(query % (basepart, prevpart, finalpart))
    winners = []
    todays = []

    # Create the data for the output files.
    for (clubnumber, clubname, division, area, endnum, startnum, prevnum) in curs.fetchall():
        if not startnum:
            startnum = 0      # Handle clubs added during the period
        growth = endnum - startnum
        if not prevnum:
            prevnum = 0
        prevgrowth = prevnum - startnum

        if growth >= 5:
            winners.append(myclub(clubnumber, clubname, division, area, endnum, startnum, growth))
            if prevgrowth < 5:
                todays.append(clubname)
        
    

    # Open the output file
    clubfile = open(parms.outfile, 'w')
    if winners:
        clubfile.write(r'<b>Congratulations</b> to %s for qualifying for "Five for 5"!' % getClubBlock(winners))
    clubfile.close()

    # Open the email file
    emailfile = open(parms.emailfile, 'w')
    if todays:
        emailfile.write('<p>Clubs earning Five for 5 today:\n<ul>\n')
        for club in sorted(todays):
            emailfile.write('<li>%s</li>\n' % club)
        emailfile.write('</ul>\n')
    else:
        emailfile.write('<p>No clubs earned Five for 5 today.\n')
    emailfile.write('\n')
        
    if winners:
        emailfile.write('<p>All clubs which have earned Five for 5:\n<ul>\n')
        for club in sorted(winners, key=lambda c:c.clubname):
            emailfile.write('<li>%s</li>\n' % club.clubname)
        emailfile.write('</ul>\n')
    else:
        emailfile.write('<p>No clubs have earned Five for 5 yet.</p>\n')
    emailfile.close()
