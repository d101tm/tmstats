#!/usr/bin/env python3
""" Creates the "Sensational Summer" report """

import sys, csv
import tmparms, datetime
from tmutil import cleandate, UnicodeWriter, daybefore, stringify, isMonthFinal, haveDataFor, getMonthStart, getMonthEnd, dateAsWords, neaten, getClubBlock

import tmglobals
globals = tmglobals.tmglobals()

def createResults(clubs):
    """ Returns a text string representing the clubs.  
        As a side effect, computes the award amount due for each club.
        Each club's name is enclosed in a span of class 'clubname'. """
    res = []
    for club in sorted(clubs, key=lambda club: club.clubname.lower()):
        htmlclass = 'clubname'
        info = []
        club.amount = club.growth * 5
        if club.growth >= 3:
            club.amount += 10
        elif club.growth >= 5:
            club.amount += 10
        info.append('%d added member%s' % (club.growth, 's' if club.growth > 1 else ''))
        
        res.append('<span class="clubname">%s</span> ($%d: %s)<br>' % (club.clubname, club.amount, '; '.join(info)))
         
    return('\n'.join(res))
   

class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname, division, area, endnum, startnum, growth, amount):
        self.area = area
        self.division = division
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.growth = growth
        self.endnum = endnum
        self.startnum = startnum
        self.amount = amount
        self.leader = False


    def tablepart(self):
        return ('    <td>%s</td><td>%s</td>' % (self.area, self.clubname))

    def key(self):
        return '%s%2s%8s' % (self.division, self.area, self.clubnumber)

def computeAmount(growth):
    amount = growth * 5
    if growth >= 3:
        amount += 10
    if growth >= 5:
        amount += 10
    return amount

if __name__ == "__main__":

    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument("--basedate", dest='basedate', default='M4')
    parms.add_argument("--finaldate", dest='finaldate', default='M6')
    parms.add_argument('--outfile', dest='outfile', default='summer.html')

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
        finalpart = 'asof = "%s"' % min(reportdate)
        msgdate = datetime.datetime.strptime(finaldate, '%Y-%m-%d')
    if isinstance(reportdate,str):
    	reportdate = datetime.datetime.strptime(reportdate, '%Y-%m-%d')
    friendlyend = 'New Members on %s' % neaten(reportdate)
    msgfinal = dateAsWords(msgdate)

    winners = {}
    wincount = 0


    # OK, now find clubs
    query = 'SELECT c.clubnumber, c.clubname, c.division, c.area, c.newmembers, b.newmembers FROM distperf c LEFT OUTER JOIN (SELECT clubnumber, newmembers FROM distperf WHERE %s) b ON b.clubnumber = c.clubnumber WHERE %s  ORDER BY c.division, c.area, c.clubnumber' % (basepart, finalpart)
    curs.execute(query)

    # Create the data for the output files.
    for (clubnumber, clubname, division, area, endnum, startnum) in curs.fetchall():
        if not startnum:
            startnum = 0      # Handle clubs added during the period
        growth = endnum - startnum
        if growth > 0:
            amount = computeAmount(growth)
            if amount not in winners:
                winners[amount] = []
            winners[amount].append(myclub(clubnumber, clubname, division, area, endnum, startnum, growth, amount))
            wincount += 1
    # Open the output file
    clubfile = open(parms.outfile, 'w')




    # Only write data if at least one club has qualified

    if len(winners) > 0:
        if wincount == 1:
            # There's only one club to congratulate
            theclub = winners[min(winners.keys())][0]
            clubfile.write("<p>Congratulations to <b>%s</b> for earning $%d for adding %d member%s.</p>\n" %
                           (theclub.clubname, theclub.amount, theclub.growth, "s" if theclub.growth > 1 else ""))
        else:
            clubfile.write("<p><b>Congratulations to these clubs for adding new members:</b></p>\n")
            for amount in sorted(winners.keys(),reverse=True):
                tranche = winners[amount]
                growth = tranche[0].growth
                clubfile.write("<p><b>Earning $%d for adding %d member%s:</b> " % (amount, growth, "s" if growth > 1 else ""))
                clubfile.write(getClubBlock(tranche))
                clubfile.write(".</p>\n")


    clubfile.close()

        
