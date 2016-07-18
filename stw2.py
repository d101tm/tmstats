#!/usr/bin/env python
""" Creates the "Share the Wealth 2.0" report """

import xlsxwriter, csv, sys, os, codecs, cStringIO, re
import dbconn, tmparms, datetime
from tmutil import cleandate, UnicodeWriter, daybefore, stringify, isMonthFinal, haveDataFor, getMonthStart, getMonthEnd, dateAsWords, neaten


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


    def tablepart(self):
        return ('    <td>%s</td><td>%s</td>' % (self.area, self.clubname))

    def key(self):
        return '%s%2s%8s' % (self.division, self.area, self.clubnumber)



if __name__ == "__main__":
    from tmutil import gotodatadir
    gotodatadir()
    reload(sys).setdefaultencoding('utf8')

    # Handle parameters
    parms = tmparms.tmparms()
    parms.parser.add_argument("--basedate", dest='basedate', default='M5')
    parms.parser.add_argument("--finaldate", dest='finaldate', default='M6')
    parms.parse()
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()

    # See if we have the data needed to run and build the base part of the query
    if parms.basedate.upper().startswith('M'):
        basemonth = int(parms.basedate[1:])
        if not isMonthFinal(basemonth, curs):
            sys.exit(1)
        basepart = 'monthstart = "%s" AND entrytype = "M"' % getMonthStart(basemonth, curs)
        msgdate = getMonthEnd(basemonth)
        friendlybase = 'New Members on %s' % neaten(msgdate)
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
    friendlyend = 'New Members %son %s' % ('reported ' if not final else '',  neaten(reportdate))
    msgfinal = dateAsWords(msgdate)


    # OK, now find clubs with 1 or more members added
    query = 'SELECT c.clubnumber, c.clubname, c.division, c.area, c.newmembers, b.newmembers FROM distperf c LEFT OUTER JOIN (SELECT clubnumber, newmembers FROM distperf WHERE %s) b ON b.clubnumber = c.clubnumber WHERE %s  ORDER BY c.division, c.area, c.clubnumber' % (basepart, finalpart)
    curs.execute(query)

    # Create the data for the output files.
    clubs = {}
    divisions = {}
    divmax = {}
    for (clubnumber, clubname, division, area, endnum, startnum) in curs.fetchall():
        if not startnum:
            startnum = 0      # Handle clubs added during the period
        growth = endnum - startnum

        if growth > 0:
            clubs[clubnumber] = myclub(clubnumber, clubname, division, area, endnum, startnum, growth)
            if division not in divisions:
                divisions[division] = 0
                divmax[division] = 0
            divisions[division] += growth
            if growth > divmax[division]:
                divmax[division] = growth

    # Ensure that "Division 0D" doesn't have a leading club
    try:
        divmax['0D'] += 1
    except KeyError:
        pass

    # Open both output files
    divfile = open('stw2.csv', 'wb')
    divwriter = UnicodeWriter(divfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    clubfile = open('stw2.html', 'w')
    clubfile.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
    <meta http-equiv="Content-Style-Type" content="text/css">
    <title>Share The Wealth 2.0</title>
    <style type="text/css">


            html {font-family: Arial, "Helvetica Neue", Helvetica, Tahoma, sans-serif;
                  font-size: 75%;}

            table {width: 75%; font-size: 14px; border-width: 1px; border-spacing: 1px; border-collapse: collapse; border-style: solid;}
            td, th {border-color: black; border-width: 1px;  vertical-align: middle;
                padding: 2px; padding-right: 5px; padding-left: 5px; border-style: solid;}

            .name {text-align: left; font-weight: bold; width: 40%;}
            .number {text-align: right; width: 5%;}

            .bold {font-weight: bold;}
            .italic {font-style: italic;}
            .leader {background-color: aqua;}


            </style>
    </head>
    <body>
    """)
    clubfile.write("""
    <h1>Share The Wealth Report</h1>
    <p>Clubs receive Toastmasters Gift Certificates worth $5 for each of the first 3 members added in June; $10 for each of the next three, and $15 for every new member from 7 onward.  These statistics are %s.</p>
    <p>The club or clubs in each division which adds the most new members in that division will receive an additional $25 in Gift Certificates; current leaders are highlighted in the table below.</p>
    """ % ('final' if final else 'updated daily'))
    divheaders = ['Division', 'New Members']
    clubheaders = ['Division', 'Area', 'Club', 'Club Name', friendlybase, friendlyend, 'Members Added']
    divwriter.writerow(divheaders)




    # Write the table header for the club report
    clubfile.write("""
    <table>
       <thead>
         <tr>
    """)
    for h in clubheaders:
        style = ' style="text-align: left;"' if h=='Club Name' else ''
        clubfile.write("""
            <th%s>%s</th>
    """ % (style, h))
    clubfile.write("""
         </tr>
       </thead>
       <tbody>
    """)


    for club in sorted(clubs.values(), key=lambda c:c.key()):
        clubfile.write('      <tr%s>\n' % (' class="leader"' if club.growth == divmax[club.division] else ''))
        clubfile.write('        <td class="number">%s</td>\n' % club.division)
        clubfile.write('        <td class="number">%s</td>\n' % club.area)
        clubfile.write('        <td class="number">%s</td>\n' % club.clubnumber)
        clubfile.write('        <td class="name%s">%s</td>\n' % (" bold italic" if club.growth == divmax[club.division] else "", club.clubname))
        clubfile.write('        <td class="number">%s</td>\n' % club.startnum)
        clubfile.write('        <td class="number">%s</td>\n' % club.endnum)
        clubfile.write('        <td class="number%s">%s</td>\n' % (" bold italic" if club.growth == divmax[club.division] else "", club.growth))
        clubfile.write('     </tr>\n')


    # Close out the club file
    clubfile.write("""  </tbody>
    </table>
    </body>
    </html>
    """)

    divs = sorted([d for d in divisions.keys() if not d.startswith('0')])
    for d in divs:
        divwriter.writerow((d, '%d' % divisions[d]))

    # @@HACK@@: The JA_Google Chart module chokes when the last line ends with a line end.  Let's remove it.

    divfile.seek(-2, os.SEEK_END)
    divfile.truncate()

    clubfile.close()
    divfile.close()
