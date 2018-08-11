#!/usr/bin/env python3
""" This program combines info about a Toastmasters District's clubs into one easy-to-read report.  """

import  datetime,  os, sys,  math, time
import dbconn, tmparms, latest, os, sys, argparse
from tmutil import stringify
import csv

from operator import attrgetter

from tmglobals import tmglobals
globals = tmglobals()

dists = {
    'P': 'President\'s Distinguished = %d',
    'S': 'Select Distinguished = %d',
    'D': 'Distinguished = %d'
}

distnames = ['Distinguished', 'Select Distinguished', 'President\'s Distinguished']

clubs = {}
divisions = {}

### Utility Functions ###

def monthtoindex(m):
    if m >= 7:
        return m - 7
    else:
        return m + 5
            
def colorcode(number):
    try:
        number = int(number)
    except:
        return ''
    if number >= 20:
        return "green"
    elif number >= 13:
        return "yellow"
    else:
        return "red"
        
def spl(n, what):
    if n == 1:
        return what
    else:
        return what+'s'
    
def normalize(str):
    if str:
        return ' '.join(str.split())
    else:
        return ''
        
def wrap(tag, what, *classes, **kwds):
    classattr = []
    for c in classes:
        if c:
            if type(c) == type('x'):
                classattr.append(normalize(c))
            else:
                for each in c:
                    classattr.append(normalize(each))
    

    # Treat docclass and forceclass attributes specially
    for f in ('docclass', 'forceclass'):
        if f in kwds:
            classattr.append(normalize(kwds[f]))
            del kwds[f]
        

        
    if classattr:
        classattr = ' class="%s"' % ' '.join(classattr)
    else:
        classattr = ''
        
    
    keyattrs = ['%s="%s"' % (k, kwds[k]) for k in list(kwds.keys())]
    if keyattrs:
        keyattrs = ' ' + ' '.join(keyattrs)
    else:
        keyattrs = ''
    return '<%s%s%s>%s</%s>' % (tag, classattr, keyattrs, what, tag)
    
        
def span(what, docclass):
    return '<span class="%s">%s</span>' % (docclass, what)
    
def div(what, docclass):
    return '<div class="%s">%s</div>' % (docclass, what)
        
def th(what, *classes, **kwds):
    if not what:
        what = '&nbsp;'
    return wrap('th', what, *classes, **kwds)

def td(what, *classes, **kwds):
    if not what:
        what = '&nbsp;'
    return wrap('td', what, *classes, **kwds)

class Outputfiles:
    """ This should be a singleton, but I'm being lazy and promise not to instantiate it twice. """
    
    def __init__(self):
        self.files = {}
        
    def add(self, file):
        self.files[file] = file
        self.writeheader(file)
        return file
        
    def close(self, file):
        self.writefooter(file)
        file.close()
        del self.files[file]
        
    def write(self, what):
        for f in self.files:
            f.write(what)
    

    def writeheader(self, outfile):    
        outfile.write('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
           ''')
        outfile.write('<html>\n')
        outfile.write('<head>\n')
        outfile.write('<meta http-equiv="Content-Style-Type" content="text/css">\n')
        if parms.title:
            outfile.write('<title>%s</title>\n' % parms.title)
        else:
            outfile.write('<title>Toastmasters Division %s Statistics</title>\n' % parms.district)
        outfile.write('<style type="text/css">\n')
        outfile.write("""

        html {font-family: Arial, "Helvetica Neue", Helvetica, Tahoma, sans-serif;
              font-size: 75%;}
      
        table {font-size: 12px; border-width: 1px; border-spacing: 0; border-collapse: collapse; border-style: solid;}
        td, th {border-color: black; border-width: 1px; border-style: solid; text-align: center; vertical-align: middle;
            padding: 2px;}

        .name {text-align: left; font-weight: bold; width: 22%;}
        .edate {border-left: none; font-weight: bold; width: 8%}
        .belowmin {border-left: none; font-weight: bold; width: 8%;}
        .number {text-align: right; width: 5%;}
        .goals {border-left: none;}
        .wide {width: 30% !important;}

        .green {background-color: lightgreen; font-weight: bold;}
        .yellow {background-color: yellow;}
        .red {background-color: red;}
        .likelytoclose {color: white;}
        .rightalign {text-align: right;}
        .sep {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}
        .greyback {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}
        
        .madeit {background-color: lightblue; font-weight: bold;}
        .statushead {border-right: none; }
        .status {border-right: none; padding: 1px;}
        .tabletop {background-color: #505050; font-weight: normal; color: white;}
        .reverse {background-color: black; color: white;}
        .bold {font-weight: bold;}
        .italic {font-style: italic;}
        .areacell {border: none;}
        .areatable {margin-bottom: 18pt; width: 100%; page-break-inside: avoid; display: block;}
        .suspended {text-decoration: line-through; color: red;}

        .divtable {border: none; break-before: always !important; display: block; float: none; position: relative; page-break-inside: avoid;}

        .divtable tfoot th {border: none;}
        .footinfo {text-align: left;}
        .dob {background-color: #c0c0c0;}
        .grid {width: 2%;}

        .todol {margin-top: 0;}
        .todop {margin-bottom: 0; font-weight: bold;}
        .status {font-weight: bold; font-size: 110%;}
        
        .clubcounts {margin-top: 12pt;}
        .finale {border: none; break-after: always !important; display: block; float: none; position: relative; page-break-after: always !important; page-break-inside: avoid;}
        
        .summary {border: none; break-before: always !important; display: block; float: none; position: relative; page-break-inside: avoid;}
    
        @media print { 
            body {-webkit-print-color-adjust: exact !important;}
            td {padding: 1px !important;}
            .areatable {font-size: 8px !important;}
            }
        """)
        outfile.write('</style>\n')
        outfile.write('</head>\n')
        outfile.write('<body>\n')
    
    def writefooter(self, outfile):
        outfile.write('</body>\n')
        outfile.write('</html>\n')
    

class Club:
    """ All the information about a single club """

    
    def __init__(self, clubnumber, clubname, area, division, district, suspenddate):
        self.name = clubname
        self.clubnumber = stringify(clubnumber)
        self.area = stringify(area)
        self.division = division
        self.district = stringify(district)
        self.suspenddate = suspenddate
        # Pre-set information in case it doesn't get filled in later (if the club only
        #    exists part of the year, for example, or if there is no charter info)
        self.charterdate = ''
        if (self.division == '0D') or (self.area == '0A'):
            # Fully unassign an unassigned club
            self.area = '0A'
            self.division = '0D'
            
    def finishSettingUp(self):
        """ Finish setting up the club for later additions.  Called AFTER any club overrides. """
        self.base = None
        self.dcpitems = []
        self.pathitems = [0, 0, 0, 0, 0, 0]
        self.goals = None
        self.dcpstat = None
        if self.suspenddate:
            self.eventDate = self.suspenddate
        else:
            self.eventDate = self.charterdate
        self.dcpStatus = ''
        self.status = ''
        self.current = 0
        self.goals = 0
        self.dcpitems = [0 for i in range(9, 22)]
        self.novVisit = 0
        self.mayVisit = 0
        self.place = self.district + ' ' + self.division + ' ' + self.area
        self.monthly = [''] * 12
        self.key = self.place + " " + self.clubnumber
        self.suspended = self.suspenddate != ''
        self.chartered = self.charterdate != ''

        if self.division not in divisions:
            divisions[self.division] = Division(self.division)
        
        if self.area not in divisions[self.division].areas:
            divisions[self.division].areas[self.area] = Area(self.division, self.area)
    
        divisions[self.division].areas[self.area].clubs.append(self)
        self.parentdiv = divisions[self.division]
        self.parentarea = self.parentdiv.areas[self.area]
        if self.suspended:
            self.parentdiv.susp += 1
            self.parentarea.susp += 1
        if self.chartered:
            self.parentdiv.charter += 1
            self.parentarea.charter += 1

            
    def __repr__(self):
        return self.name + " " + self.clubnumber + " " + repr(self.monthly) + " " + repr(self.dcpitems)
        


        
    def tr(self, headers=False):
        """ Return the table row for this club or the headers.  It's in one place for safety. """
        
        
        ret = '<tr>'
        row2 = '<tr>'
        # Place, Number, Name
        if headers:
            ret += th('Area', rowspan="2")
            ret += th('Number', docclass="number", rowspan="2")
            ret += th('Club Name', docclass="name wide", rowspan="2", colspan="2")
            ret += th(' ', docclass="sep", rowspan="2")
        else:
            if (self.division != '0D'):
                ret += td(self.division + self.area.lstrip('0'))
            else:
                ret += td('&nbsp;')
            ret += td(self.clubnumber.lstrip('0'), docclass="rightalign")
            color = colorcode(self.current)
            if self.suspended:
                color = "suspended"
            self.parentarea.addtocounter(color)
            self.parentdiv.addtocounter(color)
            namecolor = color
            try:
                if self.likelytoclose:
                    namecolor += " likelytoclose"
            except AttributeError:
                pass
                
            if self.eventDate and len(self.eventDate) > 1:
                ret += td(self.name, namecolor, docclass="name")
                if self.suspended:
                    ret += td("Susp %s" % self.eventDate, docclass="edate")
                else:
                    ret += td("Charter %s " % self.eventDate, docclass="edate")
            elif self.current < 8:
                ret += td(self.name, namecolor, docclass="name")
                ret += td("Below Minimum!", docclass="belowmin")
                self.parentarea.addtocounter('below')
                self.parentdiv.addtocounter('below')
            else:
                ret += td(self.name, namecolor, docclass="name wide", colspan="2")
            ret += td(' ', docclass="sep")
            
        ret += "\n    "
        

        
        # Membership
        if headers:
            monthcolspan = 2+len(self.monthly) 
            ret += th('Membership', colspan=repr(monthcolspan), docclass='.memhead')
            row2 += th('Base', forceclass="tabletop")
            months = ('Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun')
            for r in range(len(self.monthly)):
                row2 += th(months[r], forceclass="tabletop")
            row2 += th('Need', forceclass="tabletop")
            ret += th(' ', docclass="sep", rowspan="2")
        else:
            ret += td(self.base, forceclass="bold")
            for r in self.monthly:
                ret += "\n        "
                ret += td(r, colorcode(r))
            try:
                need = min(20, self.base + 5) - self.current
            except TypeError:
                need = 0
            if (not self.suspended) and (need > 0):
                ret += td(need, forceclass="bold")
            else:
                ret += td('')
            ret += td(' ', docclass="sep")
        ret += '\n'
        
        # Status and Goals
        if headers:
            ret += th('Goals', colspan="2", rowspan="2")
            ret += th(' ', docclass="sep", rowspan="2")
        else:
            if self.dcpStatus.strip() != '':
                useclass = "status reverse"
            else:
                useclass = "status"
            ret += td(self.dcpStatus, docclass=useclass)
            ## Goals
            ret += "\n    "
            if (self.goals) >= 9:
                useclass="bold italic dob"
            elif (self.goals) >= 7:
                useclass="bold dob"
            elif (self.goals) >= 5:
                useclass="italic dob"
            else:
                useclass=""
            ret += td(self.goals, docclass="goals " + useclass)
            ret += td(' ', docclass="sep")
        ret += "\n"

        # Specific DCP Goals
        if headers:
            ret += th('CCs', colspan="2")
            row2 += th('1', forceclass="tabletop")
            row2 += th('2', forceclass="tabletop")
            ret += th('ACs', colspan="2")
            row2 += th('3', forceclass="tabletop")
            row2 += th('4', forceclass="tabletop")
            ret += th('Lead', colspan="2")
            row2 += th('5', forceclass="tabletop")
            row2 += th('6', forceclass="tabletop")
            ret += th('Pathways', colspan="6")
            for plabel in ('L1', 'L2', '+L2', 'L3', 'L4', 'L5'):
              row2 += th(plabel, forceclass="tabletop")
            ret += th('Mem', colspan="2")
            row2 += th('7', forceclass="tabletop")
            row2 += th('8', forceclass="tabletop")
            ret += th('Trn', colspan="2")
            row2 += th('9a', forceclass="tabletop")
            row2 += th('9b', forceclass="tabletop")
            ret+= th('Ren|OL', colspan="2")
            row2 += th('Ren.', forceclass="tabletop")
            row2 += th('OL', forceclass="tabletop")
        else:
            ## CCs, ACs, Leadership
            for point in (0, 1, 2, 3, 4, 5):
                color = "madeit" if self.dcpitems[point] >= (2, 2, 1, 1, 1, 1)[point] else ""
                ret += td(self.dcpitems[point], color, "grid")
                
            ## Pathways
            for point in (0, 1, 2, 3, 4, 5):
                color = "madeit" if self.pathitems[point] >= (4, 2, 2, 2, 1, 1)[point] else ""
                ret += td(self.pathitems[point], color, "grid")
                
            
            # New Members
            for point in (6, 7):
                color = "madeit" if self.dcpitems[point] >= 4 else ""
                ret += td(self.dcpitems[point], color, "grid")

            # Training
            ret += "\n    "
            training = td(self.dcpitems[8]) + td(self.dcpitems[9])
            if (self.dcpitems[8] >= 4) and (self.dcpitems[9] >= 4):
                useclass = "madeit"
            else:
                useclass = None
            ret += td(self.dcpitems[8], docclass=useclass, forceclass="grid") + td(self.dcpitems[9], docclass=useclass, forceclass="grid")

            # Renewal + Officer List
            ret += "\n    "
            renewals = self.dcpitems[10] + self.dcpitems[11]
            if (renewals > 0) and (self.dcpitems[12] > 0):
                useclass = "madeit"
            else:
                useclass = None
            ret += td(renewals, docclass=useclass, forceclass="grid") + td(self.dcpitems[12], docclass=useclass, forceclass="grid")   
            
        # Visits
        
        if headers:
            ret += th(' ', docclass="sep", rowspan="2")
            ret += th('Visits', colspan="2")
            row2 += th('1', forceclass="tabletop")
            row2 += th('2', forceclass="tabletop")
        else:
            ret += td(' ', docclass="sep")
            ret += td(self.novVisit, "grid", "bold madeit" if self.novVisit > 0 else "")
            ret += td(self.mayVisit, "grid", "bold madeit" if self.mayVisit > 0 else "")
        ret += "\n</tr>"
        row2 += "\n</tr>"
        if headers:
            return ret + row2
        else:
            return ret
            
class Aggregate():
    """ Behavior common to a division or an area """
    
    def clubcounts(self):
        ret = []
        ret.append(td(' ', forceclass="sep"))
        ret.append(td(self.base))
        ret.append(td(self.susp))
        ret.append(td(self.counters['below']))
        ret.append(td(self.charter))
        ret.append(td(self.paid))
        ret.append(td(' ', forceclass="sep"))
        ret.append(td(self.counters['D'], forceclass="bold"))
        ret.append(td(self.counters['S'], forceclass="bold"))
        ret.append(td(self.counters['P'], forceclass="bold"))
        ret.append(td(' ', forceclass="sep"))
        ret.append(td(self.counters['green'], forceclass="green"))
        ret.append(td(self.counters['yellow'], forceclass="yellow"))
        ret.append(td(self.counters['red'], forceclass="red"))
        
        
        
        
        return '\n'.join(ret)
        
  

        
    def dcols(self):
        res = []  
        for i in range(len(self.paidgoals)):
            res.append(td(' ', forceclass="sep"))
            res.append(td("%d (%d needed)" % (self.paid, self.paidgoals[i]), "madeit" if self.paid >= self.paidgoals[i] else ""))
            res.append(td("%d (%d needed)" % (self.dist, self.distgoals[i]), "madeit" if self.dist >= self.distgoals[i] else ""))
        return ''.join(res)
        
        
    def statline(self):
        ret = []
        ret.append(td(self.id))
        ret.append(td(self.status, forceclass="madeit" if self.status else ""))
        ret.append(td(' ', forceclass="sep"))
        ret.append(self.qualcell())
        ret.append(self.dcols())

        return '\n'.join(ret)
        
    def addtocounter(self, color):
        if color in self.counters:
            self.counters[color] += 1
        
class Division(Aggregate):
    """ Information about an entire division """
    def __init__(self, div):
        self.kind = 'Division'
        self.name = div
        self.areas = {}
        self.susp = 0
        self.charter = 0
        self.counters = {'': 0, 'P': 0, 'S': 0, 'D': 0, 'green': 0, 'yellow': 0, 'red': 0, 'below': 0}
        self.octRenewal = 0
        self.aprRenewal = 0
        self.novVisit = 0
        self.mayVisit = 0
        self.isQual = False
        self.id = self.kind + ' ' + self.name

    def qualcell(self):
        self.isQual = self.status or (self.paid >= self.paidgoals[0])
        return (td('n/a')+td('n/a'))
        
class Area(Aggregate):
    """ Information about an entire area """
    def __init__(self, div, area):
        self.kind = 'Area'
        self.name = div + area.lstrip('0')
        self.clubs = []
        self.susp = 0
        self.charter = 0
        self.counters = {'': 0, 'P': 0, 'S': 0, 'D': 0, 'green': 0, 'yellow': 0, 'red': 0, 'below': 0}
        self.octRenewal = 0
        self.aprRenewal = 0
        self.novVisit = 0
        self.mayVisit = 0
        self.isQual = False
        self.id = self.kind + ' ' + self.name
        
        


        
    def qualcell(self):
        visitneed = int(math.ceil(.75 * self.base))
        res = td('%d (%d needed)' % (self.novVisit, visitneed), "madeit" if self.novVisit >= visitneed else "")
        res += td('%d (%d needed)' % (self.mayVisit, visitneed), "madeit" if self.mayVisit >= visitneed else "")
        self.isQual = (self.paid >= self.paidgoals[0]) and (self.novVisit >= visitneed) and (self.mayVisit >= visitneed)
        return res
        
        
### Main Program Starts Here ###



# Define args and parse command line
parms = tmparms.tmparms(description=__doc__)
parms.add_argument("--tmyear", default=None, action="store", dest="tmyear", help="TM Year for the report.  Default is latest year in the database; '2014' means '2014-15'.")
parms.add_argument("--testalignment", dest="testalignment", default=None, help="CSV file with alignment information to create a report with a new alignment.")
parms.add_argument('--outdir', default='.', help='Where to put the output files')
parms.add_argument("--outfile", dest="outfile", default="stats.html", help="Output file for the whole District's data")
parms.add_argument("--title", dest="title", default=None, help="Title for the HTML page.")
parms.add_argument("--makedivfiles", dest="makedivfiles", action="store_true", help="Specify to create individual HTML files for each Division")
# Do global setup
globals.setup(parms)

conn = globals.conn
curs = globals.curs
district = '%02d' % parms.district 

# Find the latest date in the system and work backwards from there to the beginning of the TM year.
today = globals.today
(latestmonth, latestdate) = latest.getlatest('clubperf', conn)
(latestyear, latestmonth) = [int(f) for f in latestmonth.split('-')[0:2]]
latestdate = datetime.datetime.strptime(latestdate, "%Y-%m-%d")
monthname = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][latestmonth - 1]
lateststamp = " from Toastmasters data for the month of " + monthname + latestdate.strftime(", current through %m/%d/%Y.")

# Let's resolve the tmyear
if parms.tmyear:
    if len(parms.tmyear) >= 4:
        tmyear = int(parms.tmyear[0:4])
    elif len(parms.tmyear) == 2:
        tmyear = 2000 + int(parms.tmyear)
    else:
        sys.stderr.write('%s is not valid for tmyear.' % parms.tmyear)
        sys.exit(1)
else:
    tmyear = latestyear



if tmyear < latestyear:
    # We assume all months are in the database.  If not, we'll find out what's missing the hard way.
    interestingmonths = list(range(1,13))
    thisyear = False
    lateststamp = " from final Toastmasters data for the year %d-%d." % (tmyear, tmyear-1999)
else:
    if latestmonth <= 6:
        # We have the previous July-December, plus months up to now.
        interestingmonths = list(range(7,13))
        interestingmonths.extend(list(range(1,latestmonth+1)))
        tmyear = latestyear - 1 
    else:
        interestingmonths = list(range(7, latestmonth+1))
        tmyear = latestyear
    thisyear = True
# Now, get the months to ask for from the database
interesting = ['%d-%02d-01' % (tmyear + (1 if n <=6 else 0), n ) for n in interestingmonths]
interesting.sort()

# And get the first and last months for queries:
firstmonth = '%d-07-01' % tmyear
lastmonth = '%d-06-01' % (tmyear + 1)

freshness = []
freshness.append(time.strftime("Report created %m/%d/%Y %H:%M %Z", time.localtime()) + lateststamp)


# Let's get basic club information for all clubs which exist or have existed for the months in
# question.  If we're getting information for this year, we also have to add 'latest' entries.

    
# Get the last entry for which we have information for every club during the year.  '
lastdistperf = {}
lastareaperf = {}
lastclubperf = {}
curs.execute("select clubnumber, distperf_id, areaperf_id, clubperf_id from lastfor where tmyear = %s", 
             (tmyear,))
for (clubnumber, distperf_id, areaperf_id, clubperf_id) in curs.fetchall():
    lastdistperf[clubnumber] = '%d' % distperf_id
    lastareaperf[clubnumber] = '%d' % areaperf_id
    lastclubperf[clubnumber] = '%d' % clubperf_id
    
alldistperf = ','.join(list(lastdistperf.values()))
allareaperf = ','.join(list(lastareaperf.values()))

# Now, get basic club information from the DISTPERF table.
curs.execute("""select clubnumber, clubname, area, division, district, suspenddate from distperf where id in (%s)""" % (alldistperf))

# And create the master dictionary of clubs from those last entries
clubs = {}
for info in curs.fetchall():
    clubnumber = info[0]
    clubs[clubnumber] = Club(*info)
    
# We need to get charter date from the clubs table because Toastmasters is not posting it consistently
#   to the performance files.
curs.execute("""select clubs.clubnumber, clubs.charterdate, clubs.clubname from clubs inner join (select clubnumber, max(lastdate) as mld from clubs group by clubnumber) a on clubs.clubnumber = a.clubnumber and clubs.lastdate = a.mld  where charterdate >= %s and charterdate <= %s """, ('%d-07-01' % tmyear, '%d-06-30' % (tmyear+1)))
for (clubnumber, charterdate, clubname) in curs.fetchall():
    try:
        clubs[clubnumber].charterdate = charterdate.strftime('%m/%d/%y')
    except KeyError:
        print('Club %s (%d) not in performance reports, ignored.' % (clubname, clubnumber))
        
    
# Test alignment processing
if parms.testalignment:
    # If any clubs get created by overrideClubs, they are of the standard
    #   simpleclub.Club type.  We need to create objects of the local Club
    #   type instead, but keep the values.  
    from simpleclub import Club as sClub
    sClub.getClubsOn(curs)   # Ensure everything is defined
    from tmutil import overrideClubs
    oldkeys = set(clubs.keys())
    clubs = overrideClubs(clubs, parms.testalignment)
    for c in list(clubs.keys()):
        if c not in oldkeys:
            nclub = clubs[c]
            # We must replace this with a club of the local type
            clubs[c] = Club(nclub.clubnumber, nclub.clubname, nclub.area, nclub.division, nclub.district, nclub.suspenddate)

    

# And now, finish setting up the structure (creating Areas and Divisions, for example)
for club in list(clubs.values()):
    club.finishSettingUp()

# Now, get information from the Area/Division performance table.  We only need the latest one.


# Now we need the information from the latest Area/Division report for each club:
curs.execute("""select clubnumber, octoberrenewals, aprilrenewals, novvisitaward, mayvisitaward, 
                areaclubbase,
                areapaidclubgoalfordist, areapaidclubgoalforselectdist, areapaidclubgoalforpresdist,
                totalpaidareaclubs,
                areadistclubgoalfordist, areadistclubgoalforselectdist, areadistclubgoalforpresdist,
                totaldistareaclubs,
                distinguishedarea,
                divisionclubbase,
                divisionpaidclubgoalfordist, divisionpaidclubgoalforselectdist, divisionpaidclubgoalforpresdist,
                totalpaiddivisionclubs,
                divisiondistclubgoalfordist, divisiondistclubgoalforselectdist, divisiondistclubgoalforpresdist,
                totaldistdivisionclubs,
                distinguisheddivision
                
                from areaperf where id in (%s)""" % allareaperf)
for (clubnumber, octoberrenewals, aprilrenewals, novvisitaward, mayvisitaward, 
                areaclubbase,
                areapaidclubgoalfordist, areapaidclubgoalforselectdist, areapaidclubgoalforpresdist,
                totalpaidareaclubs,
                areadistclubgoalfordist, areadistclubgoalforselectdist, areadistclubgoalforpresdist,
                totaldistareaclubs,
                distinguishedarea,
                divisionclubbase,
                divisionpaidclubgoalfordist, divisionpaidclubgoalforselectdist, divisionpaidclubgoalforpresdist,
                totalpaiddivisionclubs,
                divisiondistclubgoalfordist, divisiondistclubgoalforselectdist, divisiondistclubgoalforpresdist,
                totaldistdivisionclubs,
                distinguisheddivision) in curs.fetchall():
    if clubnumber in clubs:
        c = clubs[clubnumber]
        c.octRenewal = octoberrenewals  # October renewal
        c.parentdiv.octRenewal += c.octRenewal
        c.parentarea.octRenewal += c.octRenewal
        c.aprRenewal = aprilrenewals  # May renewal
        c.parentdiv.aprRenewal += c.aprRenewal
        c.parentarea.aprRenewal += c.aprRenewal
        c.novVisit = novvisitaward # 1st series visits
        c.parentdiv.novVisit += c.novVisit
        c.parentarea.novVisit += c.novVisit
        c.mayVisit = mayvisitaward # 2nd series visits
        c.parentdiv.mayVisit += c.mayVisit
        c.parentarea.mayVisit += c.mayVisit
        c.parentarea.base = areaclubbase
        c.parentarea.paidgoals = [areapaidclubgoalfordist, areapaidclubgoalforselectdist, areapaidclubgoalforpresdist ]
        c.parentarea.paid = totalpaidareaclubs
        c.parentarea.distgoals = [areadistclubgoalfordist, areadistclubgoalforselectdist, areadistclubgoalforpresdist]
        c.parentarea.dist = totaldistareaclubs
        c.parentarea.status = distinguishedarea
        c.parentdiv.base = divisionclubbase
        c.parentdiv.paidgoals = [divisionpaidclubgoalfordist, divisionpaidclubgoalforselectdist, divisionpaidclubgoalforpresdist]
        c.parentdiv.paid = totalpaiddivisionclubs
        c.parentdiv.distgoals = [divisiondistclubgoalfordist, divisiondistclubgoalforselectdist, divisiondistclubgoalforpresdist]
        c.parentdiv.dist = totaldistdivisionclubs
        c.parentdiv.status = distinguisheddivision


# Now get the monthly membership for each interesting month and put it in the right place in the club.

curs.execute("select clubnumber, activemembers, month(monthstart) from clubperf where entrytype in ('M', 'L') and monthstart >= %s and monthstart <= %s", (interesting[0], interesting[-1]))
       
for (clubnumber, activemembers, month) in curs.fetchall():
    if clubnumber in clubs:
        clubs[clubnumber].monthly[monthtoindex(month)] = activemembers
    
# Now, get the current (or end-of-year, if a past year) information for each club.

fieldnames = ['clubnumber', 'clubstatus', 'membase', 'activemembers', 'goalsmet', 'ccs', 'addccs', 'acs', 'addacs', 'claldtms', 'addclaldtms', 'newmembers', 'addnewmembers', 'offtrainedround1', 'offtrainedround2', 'memduesontimeoct', 'memduesontimeapr', 'offlistontime', 'clubdistinguishedstatus', 'level1s', 'level2s', 'addlevel2s', 'level3s', 'level4s', 'level5s']
fields = ','.join(fieldnames)
dcprange = list(range(fieldnames.index('ccs'), 1+fieldnames.index('offlistontime')))
pathrange = list(range(fieldnames.index('level1s'), 1+fieldnames.index('level5s')))
if thisyear:
    curs.execute("select %s from clubperf where entrytype = 'L'" % fields)
else:
    curs.execute("select %s from clubperf where entrytype = 'M' and monthstart = '%s' " % (fields, interesting[-1]))

fetched = {}
for row in curs.fetchall():
    if row[0] in clubs:
        c = clubs[row[0]]
        if row[0] in fetched:
            print("club %s (%s) is already here" % (c.name, c.clubnumber))
        fetched[row[0]] = True
        c.status = row[1]
        c.base = row[2]
        c.current = row[3]
        c.goals = row[4]
        ## Continue by assigning DCP info
        c.dcpitems = [row[i] for i in dcprange]
        c.pathitems = [row[i] for i in pathrange]
        c.dcpStatus = row[fieldnames.index('clubdistinguishedstatus')]
        c.parentarea.counters[c.dcpStatus] += 1
        c.parentdiv.counters[c.dcpStatus] += 1





outfiles = Outputfiles()

outfile = outfiles.add(open(os.path.join(parms.outdir, parms.outfile), "w"))
    
    

# One division at a time, please...
alldivs = sorted(divisions.keys())
for d in alldivs:
    divfn = "div%s.html" % d.lower()
    if parms.makedivfiles:
        divfile = outfiles.add(open(os.path.join(parms.outdir, parms.outfile), "w"))
    else:
        divfile = None
    thisdiv = divisions[d]
   
    if parms.makedivfiles:
        if (d != '0D'):
            outfiles.write('<h1 name="Div%s"><a href="%s">Division %s</a></h1>' % (d.lower(), divfn, d))
        else:
            outfiles.write('<h1 name="Div%s"><a href="%s">Clubs Awaiting Alignment</a></h1>' % (d.lower(), divfn))
    else:
        if (d != '0D'):
            outfiles.write('<h1 name="Div%s">Division %s</h1>' % (d.lower(), d))
        else:
            outfiles.write('<h1 name="Div%s">Clubs Awaiting Alignment</h1>' % (d.lower(),))
    
    outfiles.write('<table class="divtable">\n')
    outfiles.write('<tbody><tr><td class="areacell">')
    
    for a in sorted(thisdiv.areas.keys()):
        thisarea = thisdiv.areas[a]
        outfiles.write('<table class="areatable">\n')
        outfiles.write('<thead>\n')
        outfiles.write(list(clubs.values())[0].tr(True))  # We need to pass an instance, even though it gets ignored
        outfiles.write('</thead>\n')
        outfiles.write('<tbody>\n')
        suslist = []
        for club in sorted(thisarea.clubs, key=attrgetter('name')):
            outfiles.write(club.tr())
            outfiles.write('\n')


        outfiles.write('</tbody>\n')    
        outfiles.write('</table>\n')
    
    outfiles.write('</td></tr></tbody>\n')
    


    outfiles.write('</table>\n')
    
    if (d != '0D') and not parms.testalignment:
        outfile.write('<div class="summary">\n')
        outfiles.write('<h2>Division and Area Summary</h2>')
    
        # Now, write the status and to-dos in a nice format
    
        outfiles.write('<table class="stattable">\n')
        outfiles.write('<thead><tr>')
        outfiles.write(th(' ', rowspan="2"))
        outfiles.write(th('Requirements', forceclass="tabletop"))
        outfiles.write(th(' ', forceclass="sep", rowspan="2"))
        outfiles.write(th('Club Visits to Qualify', colspan="2", forceclass="tabletop"))   
        outfiles.write(th(' ', forceclass="sep", rowspan="2"))
        outfiles.write(th('For Distinguished', colspan="2", forceclass="tabletop"))
        outfiles.write(th(' ', forceclass="sep", rowspan="2"))
        outfiles.write(th('For Select Distinguished', colspan="2", forceclass="tabletop"))
        outfiles.write(th(' ', forceclass="sep", rowspan="2"))
        outfiles.write(th('For President\'s Distinguished', colspan="2", forceclass="tabletop"))

        outfiles.write('</tr>\n<tr>')
        outfiles.write(th('Status'))
        outfiles.write(th('Cycle 1'))
        outfiles.write(th('Cycle 2'))
        outfiles.write(th('Paid Clubs'))
        outfiles.write(th('Distinguished or Better'))
        outfiles.write(th('Paid Clubs'))
        outfiles.write(th('Distinguished or Better'))
        outfiles.write(th('Paid Clubs'))
        outfiles.write(th('Distinguished or Better'))

        outfiles.write('</tr></thead>\n')
        outfiles.write('</tr>\n')
        outfiles.write('<tbody>\n')
        outfiles.write('<tr>\n')
        outfiles.write(thisdiv.statline())
        outfiles.write('</tr>\n')





    
        for a in sorted(thisdiv.areas.keys()):
            thisarea = thisdiv.areas[a]
            outfiles.write('<tr>\n')
            outfiles.write(thisarea.statline())
            outfiles.write('</tr>\n')

        
        outfiles.write('</tbody>\n')
        outfiles.write('</table>\n')
    
        outfiles.write('<table class="clubcounts">\n')
        outfiles.write('<thead><tr>')
        outfiles.write(th(' ', rowspan="2"))
        outfiles.write(th(' ', forceclass="sep", rowspan="2"))
        outfiles.write(th('Club Totals', forceclass="tabletop", colspan="14"))
        outfiles.write('</tr>\n<tr>\n')
        outfiles.write(th('Base', forceclass="greyback"))
        outfiles.write(th('Suspended', forceclass="greyback"))
        outfiles.write(th('Below Minimum', forceclass="greyback"))
        outfiles.write(th('Chartered', forceclass="greyback"))
        outfiles.write(th('Paid', forceclass="greyback"))
        outfiles.write(th(' ', forceclass="sep", rowspan="1"))
        outfiles.write(th('Distinguished', forceclass="greyback"))
        outfiles.write(th('Select Distinguished', forceclass="greyback"))
        outfiles.write(th('President\'s Distinguished', forceclass="greyback"))
        outfiles.write(th(' ', forceclass="sep", rowspan="1"))
        outfiles.write(th('Green', forceclass="green"))
        outfiles.write(th('Yellow', forceclass="yellow"))
        outfiles.write(th('Red', forceclass="red"))
        outfiles.write('</tr></thead>\n<tbody><tr>\n')
    
        outfiles.write(td(thisdiv.id))
        outfiles.write(thisdiv.clubcounts())
        outfiles.write('</tr>')
        for a in sorted(thisdiv.areas.keys()):
            thisarea = thisdiv.areas[a]
            outfiles.write('<tr>')
            outfiles.write(td(thisarea.id))
            outfiles.write(thisarea.clubcounts())
            outfiles.write('</tr>')
        outfiles.write('</tbody></table>\n')
        outfile.write('</div>\n')
    
    
    
    
    outfiles.write('')
    if d != alldivs[-1]:
        outfiles.write('<div class="finale">\n')
    outfiles.write('<p>' + '<br />'.join(freshness) + '</p>')
    if divfile:
        divfile.write('<p>Click <a href="stats.html">here</a> for full District report.</p>\n')
    if d != alldivs[-1]:
        outfiles.write('</div>\n')
    if divfile:
        outfiles.close(divfile)
 

outfiles.close(outfile)

#furl = 'file:///' + os.getcwd() + '/out.html'
#webbrowser.open(furl)
