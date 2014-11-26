#!/usr/bin/env python
""" This program combines info about a Toastmasters District's clubs into one easy-to-read report.  """

import csv, urllib, datetime, pickle, os, sys, webbrowser, math, time, yaml

from operator import attrgetter

dists = {
    'P': 'President\'s Distinguished = %d',
    'S': 'Select Distinguished = %d',
    'D': 'Distinguished = %d'
}

distnames = ['Distinguished', 'Select Distinguished', 'President\'s Distinguished']

clubs = {}
divisions = {}

### Utility Functions ###
            
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
        
    
    keyattrs = ['%s="%s"' % (k, kwds[k]) for k in kwds.keys()]
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


class Club:
    """ All the information about a single club """
    initinfo = ("district", "division", "area", "number", "name", "newMembers", "lateRenewals", "octRenewals", "aprRenewals", "totalRenewals", "totalCharter", "total", "dcpStatus", "eventDate")
    lostinfo = ("district", "division", "area", "number", "name")
    def __init__(self, row, lostrow=None):
        if not lostrow:
            # row comes from Toastmasters, and we hope the order is consistent
            for (name, value) in zip(self.initinfo, row):
                self.__dict__[name] = value.strip()
            self.base = None
            self.dcpitems = []
            self.goals = None
            self.dcpstat = None
        else:
            # This is a club which was not in the division report for the current month
            # Patch in data which makes sense for such a club.
            for (name, value) in zip(self.lostinfo, lostrow[:len(self.lostinfo)]):
                self.__dict__[name] = value.strip()
            for (name) in self.initinfo[len(self.lostinfo):]:
                self.__dict__[name] = '0'
            self.eventDate = 'Susp earlier'
            self.dcpStatus = ''
            self.status = ''
            self.base = 0
            self.current = 0
            self.goals = 0
            self.dcpitems = [0 for i in range(9, 22)]
            self.dcpstat = None
            self.novVisit = 0
            self.mayVisit = 0
            
        self.place = self.district + " " + self.division + " " + self.area

        self.monthly = []

        self.key = self.place + " " + self.number
        self.suspended = self.eventDate.startswith('Susp')
        self.chartered = self.eventDate.startswith('Charter')
        try:
            self.eventDate = self.eventDate.split()[-1]
        except IndexError:
            pass
        
        clubs[int(self.number)] = self
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
        return self.name + " " + self.number + " " + repr(self.monthly) + " " + repr(self.dcpitems)
        


        
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
            ret += td(self.division + self.area.lstrip('0'))
            ret += td(self.number.lstrip('0'), docclass="rightalign")
            color = colorcode(self.current)
            if self.suspended:
                color = "suspended"
            self.parentarea.addtocounter(color)
            self.parentdiv.addtocounter(color)
            if self.eventDate and len(self.eventDate) > 1:
                ret += td(self.name, color, docclass="name")
                if self.suspended:
                    ret += td("Susp %s" % self.eventDate, docclass="edate")
                else:
                    ret += td("Charter %s " % self.eventDate, docclass="edate")
            elif self.current < 8:
                ret += td(self.name, color, docclass="name")
                ret += td("Below Minimum!", docclass="belowmin")
                self.parentarea.addtocounter('below')
                self.parentdiv.addtocounter('below')
            else:
                ret += td(self.name, color, docclass="name wide", colspan="2")
            ret += td(' ', docclass="sep")
            
        ret += "\n    "
        

        
        # Membership
        if headers:
            ret += th('Membership', colspan=repr(3+len(self.monthly)), docclass='.memhead')
            row2 += th('Base', forceclass="reverse")
            months = ('Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun')
            for r in range(len(self.monthly)):
                row2 += th(months[r], forceclass="reverse")
            row2 += th('Curr', forceclass="reverse")

            row2 += th('Need', forceclass="reverse")
            ret += th(' ', docclass="sep", rowspan="2")
        else:
            ret += td(self.base, forceclass="bold")
            for r in self.monthly:
                ret += "\n        "
                ret += td(r, colorcode(r))
            ret += td(self.current, colorcode(self.current))
            need = min(20, self.base + 5) - self.current
            if (need > 0) and (not self.suspended):
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
            row2 += th('1', forceclass="reverse")
            row2 += th('2', forceclass="reverse")
            ret += th('ACs', colspan="2")
            row2 += th('3', forceclass="reverse")
            row2 += th('4', forceclass="reverse")
            ret += th('Lead', colspan="2")
            row2 += th('5', forceclass="reverse")
            row2 += th('6', forceclass="reverse")
            ret += th('Mem', colspan="2")
            row2 += th('7', forceclass="reverse")
            row2 += th('8', forceclass="reverse")
            ret += th('Trn', colspan="2")
            row2 += th('9a', forceclass="reverse")
            row2 += th('9b', forceclass="reverse")
            ret+= th('Ren|OL', colspan="2")
            row2 += th('Ren.', forceclass="reverse")
            row2 += th('OL', forceclass="reverse")
        else:
            ## CCs, ACs, Leadership, New Members
            dcpmins = (2, 2, 1, 1, 1, 1, 4, 4)
            for point in range(8):
                if self.dcpitems[point] >= dcpmins[point]:
                    color = "madeit"
                else:
                    color = ""
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
            row2 += th('1', forceclass="reverse")
            row2 += th('2', forceclass="reverse")
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
        
        

        
    

        
class Info:
    """ Information relative to a Toastmasters date """
    lasts = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    def __init__(self, m, y):


        if (m == 2) and (0 == y % 4):
            eom = (2, 29, y)
        else:
            eom = (m, self.lasts[m-1], y)
            
        self.monthend = '%d/%d/%d' % eom
        if (m == 12):
            self.nextday = [1, 1, y+1]
        else:
            self.nextday = [m+1, 1, y]
        self.lastday = self.lasts[self.nextday[0]-1]
        if (m == 1) and (0 == y % 4):
            self.lastday = 29
        
    def next(self):
        while (self.nextday[1] <= self.lastday):
            yield '%d/%d/%d' % (self.nextday[0], self.nextday[1], self.nextday[2])
            self.nextday[1] += 1
   
            
    def __iter__(self):
        return self

def makeurl(report, district, tmyearpiece="", monthend="", asof=""):
    baseurl = "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=" + report + "~" + district
    if monthend == "":
        return baseurl + "~~~" + tmyearpiece
    else:
        return baseurl + "~" + monthend + "~" + asof + "~" + tmyearpiece
        
        
district = "04"
report = "districtperformance"

if len(sys.argv) == 2:
    # Open files instead of doing our own fetches
    print sys.argv[1]
    resources = yaml.load(open(sys.argv[1],'r'))['files']
else:
    resources = {'clubs': "http://reports.toastmasters.org/findaclub/csvResults.cfm?District=%(district)s",
         'payments': "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=districtperformance~%(district)s~~~%(tmyear)s",
         'division': "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=divisionperformance~%(district)s~~~%(tmyear)s",       
         'current': "http://dashboards.toastmasters.org/export.aspx?type=CSV&report=clubperformance~%(district)s",
         'historical': "http://dashboards.toastmasters.org/%(lasttmyear)s/export.aspx?type=CSV&report=clubperformance~%(district)s~~~%(lasttmyear)s"}

parms = {'district':'04'}

def opener(what, parms):
    if what.startswith('http'):
        return urllib.urlopen(what % parms)
    else:
        return open(what, 'rbU')

# Start by figuring out what months we need info for:

today = datetime.date.today()

tmmonths = (7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6)
# If it's January-July, we care about the TM year which started the previous July 1; otherwise, it's this year.
if (today.month <= 7):
    tmyear = today.year - 1 
else:
    tmyear = today.year
    
tmyearpiece = '%d-%d' % (tmyear, tmyear+1)  # For the URLs
parms['tmyear'] = tmyearpiece
parms['lasttmyear'] = '%d-%d'% (tmyear-1, tmyear)



# Now, define the months we're going to look for

if (today.month == 7):
    months = tmmonths
else:
    months = []
    for m in tmmonths:
        months.append(m)
        if m == today.month:
            break
months = [(m, tmyear + (1 if m <= 6 else 0)) for m in months]



freshness = []
freshness.append(time.strftime("Report created %m/%d/%Y %H:%M %Z", time.localtime()))

#Start by getting current information about all clubs in the district, though all we really care about is 
#charter and suspension dates.  


s = opener(resources['payments'], parms)
    
distinfo = s.readlines()

csvreader = csv.reader(distinfo[1:-1])
for row in csvreader:
    if not (row[0].startswith('Month of')):
        c = Club(row)
        

for i in range(len(distinfo)):
    if distinfo[-i].startswith('Month of'):
        freshness.append('District Performance data: %s' % distinfo[-i].strip())
        break
        


             
s.close()        

# Now we need the information from the Area/Division report:
s = opener(resources['division'], parms)
divinfo = s.readlines()
csvreader = csv.reader(divinfo[1:-1])
for row in csvreader:
    if not (row[0].startswith('Month of')):
        c = clubs[int(row[3])]
        c.octRenewal = int(row[5])  # October renewal
        c.parentdiv.octRenewal += c.octRenewal
        c.parentarea.octRenewal += c.octRenewal
        c.aprRenewal = int(row[6])  # May renewal
        c.parentdiv.aprRenewal += c.aprRenewal
        c.parentarea.aprRenewal += c.aprRenewal
        c.novVisit = int(row[7]) # 1st series visits
        c.parentdiv.novVisit += c.novVisit
        c.parentarea.novVisit += c.novVisit
        c.mayVisit = int(row[8]) # 2nd series visits
        c.parentdiv.mayVisit += c.mayVisit
        c.parentarea.mayVisit += c.mayVisit
        c.parentarea.base = int(row[12])
        c.parentarea.paidgoals = [int(row[13]), int(row[14]), int(row[15])]
        c.parentarea.paid = int(row[16])
        c.parentarea.distgoals = [int(row[17]), int(row[18]), int(row[19])]
        c.parentarea.dist = int(row[20])
        c.parentarea.status = row[21]
        c.parentdiv.base = int(row[22])
        c.parentdiv.paidgoals = [int(row[23]), int(row[24]), int(row[25])]
        c.parentdiv.paid = int(row[26])
        c.parentdiv.distgoals = [int(row[27]), int(row[28]), int(row[29])]
        c.parentdiv.dist = int(row[30])
        c.parentdiv.status = row[31]

for i in range(len(divinfo)):
    if divinfo[-i].startswith('Month of'):
        freshness.append('Division/Area Performance data: %s' % divinfo[-i].strip())
        break

# Now we get the club performance report for every month between the start of the TM year and today.  If we are in July,
# we assume it's the previous TM year that matters.




# OK, now start getting the info.  Since TMI doesn't let us ask for info for a month without specifying a day, we begin
# by looking at the month end and continuing forward until we don't get any info.  Is this any way to run a railroad?
## TODO: At least do a binary search instead of sequential!
## Note:  This is not going to be changed to read from a file.

def getresponse(url):
    clubinfo = urllib.urlopen(url).readlines()
    if len(clubinfo) < 10:
        # We didn't get anything of value
        clubinfo = False
    return clubinfo
    
def findlastformonth(mm, yy, last=None):
    info = Info(mm, yy)
    url = makeurl('clubperformance', district, tmyearpiece, info.monthend, info.monthend)
    good = info.monthend
    clubinfo = getresponse(url)
    for asof in info.next():
        if (last) and (asof != last):
            continue
        print "getting response for ", asof
        url = makeurl('clubperformance', district, tmyearpiece, info.monthend, asof)
        newinfo = getresponse(url)
        if not newinfo:
            break
        clubinfo = newinfo
        good = asof
    return (clubinfo, asof)

for (mm, yy) in months:
    filename = 'history.%0.4d-%0.2d.pickle' % (yy, mm)
    try:
        pfile = open(filename, 'rb')
        clubinfo = pickle.load(pfile)
        asof = pickle.load(pfile)
        
        ## If we're checking on last month's data, make sure it hasn't changed
        if (mm, yy) == months[-2]:
            oldasof = asof
            (clubinfo, asof) = findlastformonth(mm, yy, last=asof)
            if (asof != oldasof):
                pfile.close()
                pfile = open(filename, 'wb')
                pickle.dump(clubinfo, pfile)
                pickle.dump(asof, pfile)
        
    except Exception, e:
        print e
        (clubinfo, asof) = findlastformonth(mm, yy)
        pfile = open(filename, 'wb')
        pickle.dump(clubinfo, pfile)
        pickle.dump(asof, pfile)
    pfile.close()
    # At this point, clubinfo has the last valid information for the month we care about
    # But all we REALLY care about is the active membership!
    if clubinfo:
        untouched = {}
        for k in clubs:
            untouched[k] = True
        csvreader = csv.reader(clubinfo[1:-1])
        for row in csvreader:
            untouched[int(row[3])] = False
            try:
                c = clubs[int(row[3])]
            except KeyError:
                ### Hmmm.  This club has vanished from the current report, but it's in an
                ###   earlier report.  Let's create it in "suspended" status without a date.
                c = Club(None, lostrow=row)
            c.monthly.append(int(row[7]))
        # And for any club without info, we need to put a blank in the monthly
        for u in untouched.keys():
            if untouched[u]:
                clubs[u].monthly.append('')
    
## Now we have to get the current info.  We want all of it.
clubinfo = opener(resources['current'], parms).readlines()
dataasof = clubinfo[-1].strip()
csvreader = csv.reader(clubinfo[1:-1])
for row in csvreader:
    row = [it.strip() for it in row]
    c = clubs[int(row[3])]
    c.status = row[4]
    c.base = int(row[6])
    c.current = int(row[7])
    c.goals = int(row[8])
    ## Continue by parsing DCP info,
    c.dcpitems = [int(row[i]) for i in range(9, 22)]
    c.dcpstat = row[22]
    c.parentarea.counters[c.dcpstat] += 1
    c.parentdiv.counters[c.dcpstat] += 1
    
for i in range(len(clubinfo)):
    if clubinfo[-i].startswith('Month of'):
        freshness.append('Club Performance data: %s' % clubinfo[-i].strip())
        break;
        
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
        outfile.write('<title>Toastmasters Statistics</title>\n')
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
        .rightalign {text-align: right;}
        .sep {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}
        .greyback {background-color: #E0E0E0; padding-left: 3px; padding-right: 3px;}
        
        .madeit {background-color: lightblue; font-weight: bold;}
        .statushead {border-right: none; }
        .status {border-right: none; padding: 1px;}
        .reverse {background-color: black; color: white;}
        .bold {font-weight: bold;}
        .italic {font-style: italic;}
        .areacell {border: none;}
        .areatable {margin-bottom: 18pt; width: 100%; page-break-inside: avoid; display: block;}
        .suspended {text-decoration: line-through; color: red;}

        .divtable {border: none; break-before: always !important; display: block; float: none; position: relative; page-break-inside: avoid; page-break-after: always !important;}

        .divtable tfoot th {border: none;}
        .footinfo {text-align: left;}
        .dob {background-color: #c0c0c0;}
        .grid {width: 2%;}

        .todol {margin-top: 0;}
        .todop {margin-bottom: 0; font-weight: bold;}
        .status {font-weight: bold; font-size: 110%;}
        
        .clubcounts {margin-top: 12pt;}
        .finale {border: none; break-after: always !important; display: block; float: none; position; relative; page-break-after: always !important; page-break-inside: avoid;}
    
        @media print { 
            body {-webkit-print-color-adjust: exact !important;}
                        td {padding: 1px !important;}}
        """)
        outfile.write('</style>\n')
        outfile.write('</head>\n')
        outfile.write('<body>\n')
    
    def writefooter(self, outfile):
        outfile.write('</body>\n')
        outfile.write('</html>\n')
    
outfiles = Outputfiles()

outfile = outfiles.add(open("stats.html", "w"))



    
    
freshness.append('Find current Educational Achievments at <a href="http://tinyurl.com/d4tmeduc">http://tinyurl.com/d4tmeduc</a>')
freshness.append('Find current Club Coach assignments at <a href="http://tinyurl.com/d4tmcoach">http://tinyurl.com/d4tmcoach</a>')

# One division at a time, please...
for d in sorted(divisions.keys()):
    divfn = "div%s.html" % d.lower()
    divfile = outfiles.add(open(divfn, "w"))
    thisdiv = divisions[d]
   
    outfiles.write('<h1 name="Div%s"><a href="%s">Division %s</a></h1>' % (d.lower(), divfn, d))
    
    
    
    outfiles.write('<table class="divtable">\n')
    outfiles.write('<tbody><tr><td class="areacell">')
    
    for a in sorted(thisdiv.areas.keys()):
        thisarea = thisdiv.areas[a]
        outfiles.write('<table class="areatable">\n')
        outfiles.write('<thead>\n')
        outfiles.write(clubs.values()[0].tr(True))  # We need to pass an instance, even though it gets ignored
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
    
    outfiles.write('<h2>Division and Area Summary</h2>')
    
    # Now, write the status and to-dos in a nice format
    
    outfiles.write('<table class="stattable">\n')
    outfiles.write('<thead><tr>')
    outfiles.write(th(' ', rowspan="2"))
    outfiles.write(th('Requirements', forceclass="reverse"))
    outfiles.write(th(' ', forceclass="sep", rowspan="2"))
    outfiles.write(th('Club Visits to Qualify', colspan="2", forceclass="reverse"))   
    outfiles.write(th(' ', forceclass="sep", rowspan="2"))
    outfiles.write(th('For Distinguished', colspan="2", forceclass="reverse"))
    outfiles.write(th(' ', forceclass="sep", rowspan="2"))
    outfiles.write(th('For Select Distinguished', colspan="2", forceclass="reverse"))
    outfiles.write(th(' ', forceclass="sep", rowspan="2"))
    outfiles.write(th('For President\'s Distinguished', colspan="2", forceclass="reverse"))

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
    outfiles.write(th('Club Totals', forceclass="reverse", colspan="14"))
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
    
    
    
    
    outfiles.write('')
        
    outfiles.write('<div class="finale"><p>' + '<br />'.join(freshness) + '</p>')
    outfiles.write('<p>Click <a href="stats.html">here</a> for full District report.</p></div>')
    outfiles.close(divfile)
 

outfiles.close(outfile)

#furl = 'file:///' + os.getcwd() + '/out.html'
#webbrowser.open(furl)
