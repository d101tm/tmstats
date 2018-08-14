#!/usr/bin/env python3
""" Try to convert the Toastmasters training page into something tolerable """
from bs4 import BeautifulSoup
import sys, re, xlsxwriter
import tmutil, sys, os
from simpleclub import Club
from datetime import datetime
import tmglobals
globals = tmglobals.tmglobals()


headers = "Div,Area,Club Name,Number,Status,Trained,Pres,VPE,VPM,VPPR,Sec,Treas,SAA"
sheets = {}
colors = {}
colors['lucky'] = '#ADD8E6'
colors['dcp'] = '#90EE90'
colors['untrained'] = '#FF8E8E'



### Insert classes and functions here.  The main program begins in the "if" statement below.





class mysheet:
    @classmethod
    def setup(self, outbook):
        # Create the format objects we're going to need
        self.align = 3*['left'] + ['right'] + ['left'] + ['right'] + 7*['center']

        self.formats = {}
        self.formats[''] = [outbook.add_format({'border':1, 'align': self.align[i]}) for i in range(len(self.align))]
        self.formats['lucky'] = [outbook.add_format({'border':1, 'align': self.align[i], 'bg_color': colors['lucky']}) for i in range(len(self.align))]
        self.formats['dcp'] = [outbook.add_format({'border':1, 'align': self.align[i], 'bg_color': colors['dcp']}) for i in range(len(self.align))]
        self.formats['untrained'] = [outbook.add_format({'border':1, 'align': self.align[i], 'bg_color': colors['untrained']}) for i in range(len(self.align))]
        self.formats['bold'] = [outbook.add_format({'border':1, 'align': self.align[i], 'bold': True}) for i in range(len(self.align))]

    def __init__(self, outbook, divname):
        self.sheet = outbook.add_worksheet('Division ' + divname)
        elements = headers.split(',')
        for i in range(len(elements)):
            self.sheet.write(0, i, elements[i], self.formats['bold'][i])
        self.sheet.set_column('A:A', 3)
        self.sheet.set_column('B:B', 4)
        self.sheet.set_column('C:C', 45)
        self.sheet.set_column('D:D', 8)
        self.sheet.set_column('G:M', 5)
        self.row = 1
        sheets[divname] = self
        
    def addrow(self, row, classes):
        if 'lucky' in classes:
            format = self.formats['lucky']
        elif 'dcp' in classes:
            format = self.formats['dcp']
        elif 'untrained' in classes:
            format = self.formats['untrained']
        else:
            format = self.formats['']
        for i in range(len(row)):
            self.sheet.write(self.row, i, row[i], format[i])
        self.row += 1
    

def makediv(outfile, outbook, divname, curdiv):
    divname = divname
    mysheet(outbook, divname)
    if curdiv:
        outfile.write('</tbody>\n')
        outfile.write('</table>\n')
        outfile.write('</div>\n')
        outfile.write('<div class="page-break"></div>\n')
    outfile.write('<div id="training-div-%s" class="trainingdiv">\n' % divname)
    outfile.write('<table>')
    outfile.write('<colgroup>' +
              '<col span="1" style="width: 5%;">' + # /Division
              '<col span="1" style="width: 5%;">' + # /Area
              '<col span="1" style="width: 35%; ">' + # /Club Name
              '<col span="1" style="width: 9%;">' + # /Club Number
              '<col span="1" style="width: 6%;">' + # /Status
              '<col span="1" style="width: 5%;">' + # / Trained
              '<col span="1" style="width: 5%;">' + # / President
              '<col span="1" style="width: 5%;">' + # / VPE
              '<col span="1" style="width: 5%;">' + # / VPM
              '<col span="1" style="width: 5%;">' + # / VPPR
              '<col span="1" style="width: 5%;">' + # / Secretary
              '<col span="1" style="width: 5%;">' + # / Treasurer
              '<col span="1" style="width: 5%;">' + # / SAA
              '</colgroup>\n')
    outfile.write('<thead style="font-weight:bold";><tr><td>')
    outfile.write('</td><td>'.join(headers.split(',')))
    outfile.write('</td></tr></thead>\n')
    outfile.write('<tbody>')

if __name__ == "__main__":
 
    import tmparms
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('report', type=str, nargs='?', default='latesttraining.html', help='Name of the training report file, default is %(default)s')
    parms.add_argument('--require9a', action='store_true', help='If true, only clubs which achieved goal 9a (4 or more officers trained during first cycle) are eligible.')
    parms.add_argument('--bonus9a', action='store_true', help='If true, clubs get a bonus reward if they trained at least 4 officers in the first cycle.')
    parms.add_argument('--reward', type=str, default='$50 in District Credit')
    parms.add_argument('--phase1name', type=str, default='Lucky 7')
    parms.add_argument('--phase2name', type=str, default='Magnificent 7')
    parms.add_argument('--bonusreward', type=str, default='$101 in District Credit and joining the Magnificent 7')
    parms.add_argument('--lastmonth', type=str, help='Last month in this training cycle, default is "August" in June-November and "February" other times.')
    
    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    # If we're in the first cycle, ignore 9a, even if specified
    thismonth = datetime.today().month
    if thismonth >= 6 and thismonth <= 10:
        parms.bonus9a = False
        parms.require9a = False
    
    # Your main program begins here.
    clubs = Club.getClubsOn(curs)
    
    if parms.require9a or parms.bonus9a:
        # Find the clubs which qualified in round 1
        curs.execute("SELECT clubnumber FROM clubperf INNER JOIN (SELECT MAX(asof) AS m FROM clubperf) ao ON ao.m = clubperf.asof WHERE offtrainedround1 >= 4")
        qualified = set()
        for l in curs.fetchall():
            qualified.add('%d' % l[0])
            
    if not parms.lastmonth:
        if thismonth >= 6 and thismonth <= 11:
            parms.lastmonth = "August"
        else:
            parms.lastmonth = "February"

    if parms.lastmonth == "August":
        parms.period = "June-August"
    else:
        parms.period = "December-February"
            

    finder = re.compile(r'.*AREA *([0-9A]*) *DIVISION *(0?[A-Za-z] *)')
    results = []

    # The input file might be in UTF-8 or Windows encoding.  Let's tolerate both
    try:
        report = open(parms.report, 'r').read()
    except UnicodeDecodeError:
        report = open(parms.report, 'r', encoding='iso8859-1').read()
    
 
    soup = BeautifulSoup(report,features="html.parser")

    # This code matches Toastmasters WHQ's site as of January 11, 2018.  They make FREQUENT
    #    changes to the form used for training, so this code is very volatile, and you may
    #    want to look at earlier versions of the code to see what I had to do in previous
    #    years.  
    # For the format used in 2016 and 2017:  https://github.com/d101tm/tmstats/blob/0db3a0b0dd9eba3e14af6ae66dbdf7dc68bf9d69/training.py
    # For the format used in 2015: https://github.com/d101tm/tmstats/blob/8c05f299e48cd47a264931c2fd051c6c23ecf734/training.py

    # For 2018, the code has one <div class="division"> tag for each Division in the District.
    # The actual data lives in a table for each area inside those divs.
    # Each club is in one row of the table, which is laid out as follows:
    # Sequence, Club Name, Status, Club Number, Pres, VPE, VPM, VPPR, Sec, Treas, SAA, Total
    # Each officer's status is represented by an <input> element of type 'checkbox'.
    #   The item has the 'checked' attribute if the officer has been trained.

    # Find all the divisions and loop through them
    divisions = soup.select('div[class="division"]')

    for thediv in divisions:
        # Find all the areas and loop through them
        areatables = thediv.find_all('table')
        for table in areatables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if not cells:
                    continue   # Must be a header row
                clubname = ''.join(cells[1].stripped_strings)
                clubstatus = ''.join(cells[2].stripped_strings)
                clubnumber = ''.join(cells[3].stripped_strings)
                # Omit suspended clubs
                if clubstatus.startswith('S'):
                    continue
                club = clubs[clubnumber]
                res = [club.division, club.area, clubname, clubnumber, clubstatus]
                offlist = []
                trained = 0
                for o in row.find_all('input', type='checkbox'):
                    if 'checked' in o.attrs:
                        trained += 1
                        offlist.append('X')
                    else:
                        offlist.append(' ')
                res.append(trained)
                res.extend(offlist)
                results.append(res)                


    # Now, create the HTML result file and the matching Excel spreadsheet
    results.sort(key=lambda x:(x[0], x[1], x[3]))
    outfile = open('trainingreport.html', 'w')
    outbook = xlsxwriter.Workbook('trainingreport.xlsx')
    mysheet.setup(outbook)
    outfile.write("""<html><head><title>Training Status</title>
            <style type="text/css">
            body {font-family: "Myriad-Pro", Arial, sans serif}
            tr, td, th {border-collapse: collapse; border-width: 1px; border-color: black; border-style: solid;}
            table {margin-bottom: 24px; border-collapse: collapse; border-width: 1px; border-color: black; border-style: solid;}
            .firstarea {margin-top: 12px; border-width-top: 2px;}
            .lucky {background-color: lightblue}
            .dcp {background-color: lightgreen}
            .untrained {background-color: #FF8E8E}
            .trainingtable {border-color: black; border-spacing: 0;}
            .trainingtable thead {font-weight: bold;}
            .page-break {page-break-before: always !important; break-before: always !important; display: block; float: none; position: relative;}
            .clubnum {text-align: right; padding-right: 2px}
            .clubname {font-weight: bold;}
            .trained {text-align: right; padding-right: 2px}
            .tstat {text-align: center;}
            @media print { body {-webkit-print-color-adjust: exact !important;}}
           </style></head>""")
    outfile.write("<body>")
    curdiv = ''
    curarea = ''

    lucky = []

    for row in results:
        if row[0] != curdiv:
            makediv(outfile, outbook, row[0], curdiv)
            curdiv = row[0]
        outfile.write('<tr')
        classes = []
        if row[1] != curarea:
            classes.append('firstarea')
            curarea = row[1]
        if row[5] == 7:
            classes.append('lucky')
            if parms.require9a:
                if row[3] in qualified:
                    lucky.append(row)
            else:    
                lucky.append(row)
        elif row[5] >= 4:
            classes.append('dcp')
        elif row[5] == 0:
            classes.append('untrained')
        if classes:
            outfile.write(' class="%s"' % ' '.join(classes))
        outfile.write('>\n')
        for partnum in range(len(row)):
            outfile.write('<td')
            if partnum == 2:
                outfile.write(' class="clubname"')
            elif partnum == 3:
                outfile.write(' class="clubnum"')
            elif partnum == 5:
                outfile.write(' class="trained"')
            elif partnum > 5:
                outfile.write(' class="tstat"')
            outfile.write('>%s</td>\n' % row[partnum])
        outfile.write('</tr>\n')
        sheets[curdiv].addrow(row, classes)
        
    outfile.write('</tbody>\n</table>\n</div>\n')
    outfile.write('</body></html>\n')
    outfile.close()
    outbook.close()

    # Now, create the Lucky 7 file

    outfile = open('lucky7.html', 'w')

    bonus = []
    if lucky:
        # Do we need to split up clubs?
        if parms.bonus9a:
            onlylucky = []
            for club in lucky:
                if club[3] in qualified:
                    bonus.append(club)
                else:
                    onlylucky.append(club)
            lucky = onlylucky

    # Set up to use getClubBlock
    class localclub:
        def __init__(self, club):
            self.clubname = club[2]

    if parms.bonus9a and parms.lastmonth == 'February':
     
        #outfile.write('<p>Clubs which have all 7 Officers attend <a href="/training">Club Officer Training</a> during the December-February training period and which trained at least 4 Officers during June-August earn <b>%s</b> and join the <b>%s</b>.</p>\n' % (parms.bonusreward, parms.phase2name))
        if bonus:
            luckyclubs = [localclub(club) for club in bonus]
            outfile.write('<p><b>Congratulations</b> to ')
            outfile.write(tmutil.getClubBlock(luckyclubs))
            outfile.write(' for earning %s and joining the %s.</p>\n' % (parms.bonusreward, parms.phase2name))

        #outfile.write('<p>Clubs which have all 7 Officers attend <a href="/training">Club Officer Training</a> during the December-February training period but trained fewer than 4 Officers during June-August earn <b>%s</b>.</p>\n' % parms.reward)

    elif parms.require9a and parms.lastmonth == 'February':
        outfile.write('<p>Clubs which have all 7 Officers attend <a href="/training">Club Officer Training</a> during the December-February training period and which trained at least 4 Officers during June-August earn <b>%s</b>.</p>\n' % parms.reward)

    else:
        outfile.write('<p>Join the <b>%s</b> and earn <b>%s</b> by having all seven Club Officers attend <a href="/training">Club Officer Training</a> in the %s period.</p>\n' % (parms.phase1name, parms.reward, parms.period))
 


    if lucky:
        luckyclubs = [localclub(club) for club in lucky]
        outfile.write('<p><b>Congratulations</b> to ')
        outfile.write(tmutil.getClubBlock(luckyclubs))
        outfile.write(' for earning %s and joining the %s.</p>\n' % (parms.reward, parms.phase1name))

    if (lucky or bonus):
        outfile.write("""<p>Training data was last updated on %s.</p>
    """ % ( datetime.today().strftime('%m/%d/%Y'),))
