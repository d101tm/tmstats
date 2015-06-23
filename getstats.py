#!/usr/bin/env python
""" This program gets all available monthly statistics from Toastmasters 
    for the current Toastmasters year.  Use it to catch up when starting
    to track district statistics. """

import urllib, datetime 

        
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



# Now we get the performance report for the months we need.
# Since TMI doesn't let us ask for info for a month without specifying a day, we begin
# by looking at the month end and continuing forward until we don't get any info.  


def getresponse(url):
    print url
    clubinfo = urllib.urlopen(url).readlines()
    if len(clubinfo) < 10:
        # We didn't get anything of value
        clubinfo = False
    return clubinfo
    
def cleandate(indate):
    from datetime import date, timedelta
    if '/' in indate:
        indate = indate.split('/')
        indate = [indate[2], indate[0], indate[1]]
    elif '-' in indate:
        indate = indate.split('-')
    elif 'today'.startswith(indate.lower()):
        return date.today().strftime('%Y-%m-%d')
    elif 'yesterday'.startswith(indate.lower()):
        return (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    if len(indate[0]) == 2:
        indate[0] = "20" + indate[0]
    if len(indate[1]) == 1:
        indate[1] = "0" + indate[1]
    if len(indate[2]) == 1:
        indate[2] = "0" + indate[2]
    return '-'.join(indate)
    
    
def findlastformonth(mm, yy, report, last=None):
    info = Info(mm, yy)
    url = makeurl(report, district, tmyearpiece, info.monthend, info.monthend)
    good = info.monthend
    clubinfo = getresponse(url)
    for asof in info.next():
        if (last) and (asof != last):
            continue
        print "getting response for ", asof
        url = makeurl(report, district, tmyearpiece, info.monthend, asof)
        newinfo = getresponse(url)
        if not newinfo:
            break
        clubinfo = newinfo
        good = asof
    return (clubinfo, asof)
    
    
def doareport(report, filename):    
    for (mm, yy) in months:
        (clubinfo, asof) = findlastformonth(mm, yy, report)
        # At this point, clubinfo has the last valid information for the month we care about
        # But all we REALLY care about is the active membership!
        if clubinfo: 
            open('%s.%s.csv' % (filename, cleandate(asof)),'w').write(''.join(clubinfo).replace('\r','')) 

doareport('clubperformance', 'clubperf')
doareport('divisionperformance', 'areaperf')
doareport('districtperformance', 'distperf')
    

        
