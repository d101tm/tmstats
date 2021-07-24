#!/usr/bin/env python3
""" Try to convert the Toastmasters training page into something tolerable """
from bs4 import BeautifulSoup
import sys, re, xlsxwriter
import tmutil, sys, os
from simpleclub import Club
from datetime import datetime
import tmglobals
myglobals = tmglobals.tmglobals()


headers = "Div,Area,Club Name,Number,Trained,Pres,VPE,VPM,VPPR,Sec,Treas,SAA"
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
        self.align = 3*['left'] + ['right'] + ['right'] + 7*['center']

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
        self.sheet.set_column('G:L', 5)
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
            
        self.sheet.write(self.row, 0, row.division, format)
        self.sheet.write(self.row, 1, row.area, format)
        self.sheet.write(self.row, 2, row.clubname, format)
        self.sheet.write(self.row, 3, row.clubnumber, format)
        self.sheet.write(self.row, 4, row.trained, format)
        self.sheet.write(self.row, 5, row.pres, format)
        self.sheet.write(self.row, 6, row.vpe, format)
        self.sheet.write(self.row, 7, row.vpm, format)
        self.sheet.write(self.row, 8, row.vppr, format)
        self.sheet.write(self.row, 9, row.sec, format)
        self.sheet.write(self.row, 10, row.treas, format)
        self.sheet.write(self.row, 11, row.saa, format)
        

        self.row += 1
    

def makediv(outfile, outbook, divname, curdiv):
    divname = divname
 #   mysheet(outbook, divname)
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

class Training:
    @staticmethod
    def getcontent(item):
        return ''.join(item.stripped_strings)

    def __init__(self, cols):
        self.division = self.getcontent(cols[0])
        self.area = self.getcontent(cols[1])
        self.clubnumber = self.getcontent(cols[2])
        self.clubname = self.getcontent(cols[3])
        self.pres = self.getcontent(cols[4])
        self.vpe = self.getcontent(cols[5])
        self.vpm = self.getcontent(cols[6])
        self.vppr = self.getcontent(cols[7])
        self.sec = self.getcontent(cols[8])
        self.treas = self.getcontent(cols[9])
        self.saa = self.getcontent(cols[10])
        self.trained = int(self.getcontent(cols[11]))

    def __lt__(self, other):
        return (self.division, self.area, int(self.clubnumber)) < (other.division, other.area, int(other.clubnumber))

    def __repr__(self):
        return f'{self.division}{self.area}  {self.clubnumber}  {self.clubname}'
    
    

if __name__ == "__main__":
 
    import tmparms
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('report', type=str, nargs='?', default='$workdir/latesttraining.html', help='Name of the training report file, default is %(default)s')
    parms.add_argument('--require9a', action='store_true', help='If true, only clubs which achieved goal 9a (4 or more officers trained during first cycle) are eligible.')
    parms.add_argument('--bonus9a', action='store_true', help='If true, clubs get a bonus reward if they trained at least 4 officers in the first cycle.')
    parms.add_argument('--reward', type=str, default='$50 in District Credit')
    parms.add_argument('--phase1name', type=str, default='Lucky 7')
    parms.add_argument('--phase2name', type=str, default='Magnificent 7')
    parms.add_argument('--bonusreward', type=str, default='$101 in District Credit')
    parms.add_argument('--lastmonth', type=str, help='Last month in this training cycle, default is "August" in June-November and "February" other times.')
    
    # Do global setup
    myglobals.setup(parms)
    curs = myglobals.curs
    conn = myglobals.conn
    os.chdir(parms.workdir)
    
    # If we're in the first cycle, ignore 9a, even if specified, unless lastmonth is explicit (to allow for historical reports)
    thismonth = datetime.today().month
    if thismonth >= 6 and thismonth <= 10 and not parms.lastmonth:
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

    # This code matches Toastmasters WHQ's site as of July, 2021.  They make FREQUENT
    #    changes to the form used for training, so this code is very volatile, and you may
    #    want to look at earlier versions of the code to see what I had to do in previous
    #    years.
    # For the format used 2018-June 2021: https://github.com/d101tm/tmstats/blob/d59a1c42604a7f934ac412cdde332d7c75894b94/training.py
    # For the format used in 2016 and 2017:  https://github.com/d101tm/tmstats/blob/0db3a0b0dd9eba3e14af6ae66dbdf7dc68bf9d69/training.py
    # For the format used in 2015: https://github.com/d101tm/tmstats/blob/8c05f299e48cd47a264931c2fd051c6c23ecf734/training.py

    # In July, 2021 the file changed again, this time including a DataTable, which we'll parse.
    # The DataTable contains a table whose body contains rows which represent the actual training data
    traininginfo = soup.select('div#club_officer_training_report_DataTable  table  tbody  tr')




    # Each row represents a club; the columns are:
    #  Division, Area, Club ID, Club Name, President, VPE, VPM, VPPR, Secretary, Treasurer, SAA, Total Trained
    # The clubs are not in a useful order, but that doesn't matter
    # Note that the datatable doesn't include status.
    results = []
    for row in traininginfo:
        cols = row.select('td')
        clubinfo = Training(cols)
        results.append(clubinfo)
       




    # Now, create the HTML result file and the matching Excel spreadsheet
    results = sorted(results)
    outfile = open('trainingreport.html', 'w')
 #   outbook = xlsxwriter.Workbook('trainingreport.xlsx')
 #   mysheet.setup(outbook)
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
    outbook = None

    for row in results:
        if row.division != curdiv:
            makediv(outfile, outbook, row.division, curdiv)
            curdiv = row.division
        outfile.write('<tr')
        classes = []
        if row.area != curarea:
            classes.append('firstarea')
            curarea = row.area
        if row.trained == 7:
            classes.append('lucky')
            if parms.require9a:
                if row.clubnum in qualified:
                    lucky.append(row)
            else:    
                lucky.append(row)
        elif row.trained >= 4:
            classes.append('dcp')
        elif row.trained == 0:
            classes.append('untrained')
        if classes:
            outfile.write(' class="%s"' % ' '.join(classes))
        outfile.write('>\n')
        outfile.write(f'<td>{row.division}</td>')
        outfile.write(f'<td>{row.area}</td>')
        outfile.write(f'<td class="clubname">{row.clubname}</td>')
        outfile.write(f'<td class="clubnum">{row.clubnumber}</td>')
        outfile.write(f'<td class="trained">{row.trained}</td>')
        outfile.write(f'<td class="tstat">{row.pres}</td>')
        outfile.write(f'<td class="tstat">{row.vpe}</td>')
        outfile.write(f'<td class="tstat">{row.vpm}</td>')
        outfile.write(f'<td class="tstat">{row.vppr}</td>')
        outfile.write(f'<td class="tstat">{row.sec}</td>')
        outfile.write(f'<td class="tstat">{row.treas}</td>')
        outfile.write(f'<td class="tstat">{row.saa}</td>')
        outfile.write('</tr>\n')


 #       sheets[curdiv].addrow(row, classes)
        
    outfile.write('</tbody>\n</table>\n</div>\n')
    outfile.write('</body></html>\n')
    outfile.close()
#    outbook.close()

    # Now, create the Lucky 7 file with a name based on today's date
    season = 'winter' if parms.lastmonth == 'February' else 'summer'
    outfilename = f'lucky7-{myglobals.today.year}-{season}.html'
    open('luckyfilename.txt', 'w').write(outfilename + '\n')
    outfile = open(outfilename, 'w')

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

    open('training-date.html', 'w').write("""<p>Training data was last updated on %s.</p>
    """ % ( datetime.today().strftime('%m/%d/%Y'),))
