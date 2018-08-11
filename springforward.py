#!/usr/bin/env python3
""" Creates the "Spring Forward" report """

import sys, csv
import tmparms, datetime
from tmutil import cleandate, UnicodeWriter, daybefore, stringify, isMonthFinal, haveDataFor, getMonthStart, getMonthEnd, dateAsWords, neaten

import tmglobals
globals = tmglobals.tmglobals()

def createResults(final, clubs):
    """ Returns a text string representing the clubs.  
        As a side effect, computes the award amount due for each club.
        Each club's name is enclosed in a span of class 'clubname'. """
    res = []
    for club in sorted(clubs, key=lambda club: club.clubname.lower()):
        htmlclass = 'clubname' 
        info = []
        if club.growth >= 8:
            club.amount = 10*club.growth
        elif club.growth >= 6:
            club.amount = 7*club.growth
        elif club.growth >= 3:
            club.amount = 5*club.growth
        else:
            club.amount = 0
        info.append('%d added member%s' % (club.growth, 's' if club.growth > 1 else ''))
        if club.leader:
            if final:
                club.amount += 50
                info.append('\\$50 bonus for leading Division %s' % club.division)
            else:
                info.append('currently leading Division %s' % club.division)
        
        res.append('<span class="clubname">%s</span> (\\$%d: %s)' % (club.clubname, club.amount, '; '.join(info)))
         
    return('\n'.join(res))
   

class myclub:
    """ Just enough club info to sort the list nicely """
    def __init__(self, clubnumber, clubname, division, area, endnum, startnum, growth):
        self.area = area
        self.division = division
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.growth = growth
        self.endnum = endnum
        self.startnum = startnum
        self.amount = 0
        self.leader = False


    def tablepart(self):
        return ('    <td>%s</td><td>%s</td>' % (self.area, self.clubname))

    def key(self):
        return '%s%2s%8s' % (self.division, self.area, self.clubnumber)



if __name__ == "__main__":

    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument("--basedate", dest='basedate', default='M4')
    parms.add_argument("--finaldate", dest='finaldate', default='M6')
    parms.add_argument('--outfile', dest='outfile', default='springforward.html')
    parms.add_argument('--csvfile', dest='csvfile', default='springforward.csv')
    
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


    # OK, now find clubs
    query = 'SELECT c.clubnumber, c.clubname, c.division, c.area, c.newmembers, b.newmembers FROM distperf c LEFT OUTER JOIN (SELECT clubnumber, newmembers FROM distperf WHERE %s) b ON b.clubnumber = c.clubnumber WHERE %s  ORDER BY c.division, c.area, c.clubnumber' % (basepart, finalpart)
    curs.execute(query)

    # Create the data for the output files.
    divmax = {}
    divisions = {}
    for (clubnumber, clubname, division, area, endnum, startnum) in curs.fetchall():
        if not startnum:
            startnum = 0      # Handle clubs added during the period
        growth = endnum - startnum

        if growth >= 3:
            if division not in divisions:
                divmax[division] = 0
                divisions[division] = []
            divisions[division].append(myclub(clubnumber, clubname, division, area, endnum, startnum, growth))
            if growth > divmax[division]:
                divmax[division] = growth

    # Ensure that "Division 0D" doesn't have a leading club
    try:
        divmax['0D'] += 1
    except KeyError:
        pass
        
    

    # Open the output files
    clubfile = open(parms.outfile, 'w')


    # Also make a CSV with all of the information
    columns = ['Division', 'Area', 'Club Number', 'Club Name', 'Members Added', 'Amount Earned', 'Division Leader']
    fields = ['division', 'area', 'clubnumber', 'clubname', 'growth', 'amount', 'leader']
    csvfile = open(parms.csvfile, 'wb')
    writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
    csvfile.write(','.join(columns))
    csvfile.write('\n')

    # Only write data if at least one club has qualified

    if len(divisions) > 0:

        clubfile.write(r"""
        <p>Click on a division to see the clubs which have earned awards.</p>
        """)
        
        clubfile.write("""[et_pb_tabs admin_label="Spring Forward Results" use_border_color="off" border_color="#ffffff" border_style="solid" tab_font_size="18"]
        """)
        for division in sorted(divisions.keys()):

            if division != '0D':
                # Mark the leader(s)
                for club in divisions[division]:
                    club.leader = (club.growth == divmax[division])
                    
                clubfile.write('[et_pb_tab title="Division %s" tab_font_select="default" tab_font="||||" tab_line_height="2em" tab_line_height_tablet="2em" tab_line_height_phone="2em" body_font_select="default" body_font="||||" body_line_height="1.3em" body_line_height_tablet="1.3em" body_line_height_phone="1.3em"]\n' % division)
                clubfile.write('<p>%s.</p>\n' % createResults(final, divisions[division]))
                clubfile.write('[/et_pb_tab]\n')
                
                for club in sorted(divisions[division], key=lambda c: '%.2s%.2s%0.8d' % (c.division, c.area, c.clubnumber)):
                    writer.writerow(club.__dict__)

        clubfile.write('[/et_pb_tabs]\n')

    clubfile.close()
    csvfile.close()

        
