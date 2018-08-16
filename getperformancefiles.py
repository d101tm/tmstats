#!/usr/bin/env python3
""" Get performance information from Toastmasters and write them to files.

    Unless invoked with --startdate, only gets the latest available information,
    including club information (unles --skip-clubs is specified).

    If invoked with --startdate, gets information and writes files for that date 
    (and, if --enddate is specified, for all available dates through --enddate).
    Does not get club information because it's not available for past dates.

"""

import tmparms, os, sys
from tmutil import cleandate
from datetime import datetime, timedelta, date
import requests

import tmglobals
globals = tmglobals.tmglobals()
    
# Map filenames to report names from Toastmasters
reportnames = {'clubperf':'clubperformance',
               'areaperf':'divisionperformance',
               'distperf':'districtperformance'}
        
def getmonthend(m, y):
    lasts = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    if (m == 2) and (0 == y % 4):
        eom = (2, 29, y)
    else:
        eom = (m, lasts[m-1], y)
        
    return '%d/%d/%d' % eom
    

def makeurl(report, district, tmyearpiece="", monthend="", asof=""):
    url = "http://dashboards.toastmasters.org/"
    if tmyearpiece:
        url += tmyearpiece 
    url += "/export.aspx?type=CSV&report=" + reportnames[report] + "~" + district
    try:
        asof = asof.strftime('%m/%d/%Y')
    except AttributeError:
        pass
    return url + "~" + monthend + "~" + asof + "~" + tmyearpiece

        
def getresponse(url):
    clubinfo = requests.get(url).text.replace('\r','').split('\n')
    if len(clubinfo) < 10:
        # We didn't get anything of value
        print("Nothing fetched for", url)
        clubinfo = False
    elif clubinfo[0][0] in ['{', '<']:
        # This isn't a naked CSV
        print("Not a CSV at", url)
        clubinfo = False
    return clubinfo
        
        
def getreportfromWHQ(report, district, tmyearpiece, month, thedate):
    url = makeurl(report, district, tmyearpiece, getmonthend(month[0],month[1]), datetime.strftime(thedate, '%m/%d/%Y'))
    resp = getresponse(url)
    if not resp:
        print("No valid response received")
    return resp
    
def gettmyearfordate(d):
    if d.month >= 7:
        tmyearpiece = "%d-%d" % (d.year, d.year+1)
    else:
        tmyearpiece = "%d-%d" % (d.year-1, d.year)
    return tmyearpiece
        
        
def writereportfile(data, report, reportdate, monthend, tmyearpiece):
    if data:
        with open(makefilename(report, reportdate), 'w') as f:
            f.write('\n'.join(data))
            print('Wrote %s for %s (month: %s, year: %s)' % (report, reportdate, monthend, tmyearpiece))
    else:
        print('No data for %s for %s (month %s, year: %s)' % (report, reportdate, monthend, tmyearpiece))

def makefilename(reportname, thedate):
    return '%s.%s.csv' % (reportname, thedate.strftime('%Y-%m-%d'))
    

def getreport(report, district, monthend, tmyearpiece, asof=""):
    """ Returns (data, reportdate, reportmonthend) tuple from report """
    reportdate = None
    reportmonthend = None
    url = makeurl(report, district, monthend=monthend, tmyearpiece=tmyearpiece, asof=asof)
    data = getresponse(url)

    if data:
        while not data[-1].strip():
            data = data[:-1]
        dateline = data[-1].replace(',','')
        reportdate = datetime.strptime(cleandate(dateline.split()[-1]), '%Y-%m-%d').date()  # "Month of Jun, as of 07/02/2015" => '2015-07-02'

        # Figure out the last day of the month for which the report applies
        reportmonth = datetime.strptime(dateline.split()[2], "%b").month  # Extract the month of the report
        
        if reportmonth == reportdate.month:
            reportmonthend = getmonthend(reportmonth, reportdate.year) 
        else:
            reportmonthend = getmonthend(reportmonth, reportdate.year if reportmonth != 12 else reportdate.year-1)
            
    return (data, reportdate, reportmonthend)
    
def doreportsfor(district, asof):
    """ Get and write files for the specified date (if available) """
    # Try for the month in question
    tmyearpiece = gettmyearfordate(asof)
    monthend = getmonthend(asof.month, asof.year)
    (data, reportdate, reportmonthend) = getreport('clubperf', district, monthend=monthend, tmyearpiece=tmyearpiece, asof=asof)
    if not data:
        # Need to try the previous month
        if asof.month == 1:
            monthend = getmonthend(12, asof.year - 1)
        else:
            monthend = getmonthend(asof.month -1, asof.year)
        (data, reportdate, reportmonthend) = getreport('clubperf', district, monthend=monthend, tmyearpiece=tmyearpiece, asof=asof)
        
        if not data:
            # Need to try for June data from the previous TM year (can't be any farther back)
            monthend = getmonthend(6, asof.year)
            tmyearpiece = gettmyearfordate(date(asof.year, 6, 30))
            (data, reportdate, reportmonthend) = getreport('clubperf', district, monthend=monthend, tmyearpiece=tmyearpiece, asof=asof)
            
    if not data:
        print("Data not available for ", asof.strftime("%Y-%m-%d"))
    else:
        writereportfile(data, 'clubperf', reportdate, monthend, tmyearpiece)
        # and now do the other two reports
        (data, reportdate, monthend) = getreport('areaperf', district, monthend, tmyearpiece, asof)
        writereportfile(data, 'areaperf', reportdate, monthend, tmyearpiece)
        (data, reportdate, monthend) = getreport('distperf', district, monthend, tmyearpiece, asof)
        writereportfile(data, 'distperf', reportdate, monthend, tmyearpiece)
    
    
def dolatest(district):
    """ Get and write files for the latest available from WHQ """
    monthend = ''
    tmyearpiece = ''
    # Note:  We can't fetch areaperf first because we need to give WHQ a valid 'monthend' to get
    #        back club suspend/charter dates in that report.  
    for report in ('clubperf', 'areaperf', 'distperf'):
            (data, reportdate, monthend) = getreport(report, district, monthend, tmyearpiece)
            if monthend and not tmyearpiece:
                repmonth = datetime.strptime(monthend, "%m/%d/%Y")
                tmyearpiece = gettmyearfordate(repmonth)
            writereportfile(data, report, reportdate, monthend, tmyearpiece)


if __name__ == "__main__":            
    parms = tmparms.tmparms(description=__doc__)
    parms.add_argument('--district', type=int)
    parms.add_argument('--startdate', default=None)
    parms.add_argument('--enddate', default=None)
    parms.add_argument('--skipclubs', action='store_true',
     help='Do not get latest club information.')
    
    globals.setup(parms, connect=False)

    district = "%0.2d" % parms.district

   
    if not parms.startdate:
        # Get today's data
        print("Getting the latest performance info")
        dolatest(district)
        
        
        # And get and write current club data unless told not to
        # WHQ doesn't supply date information, but it's always as of yesterday
        if not parms.skipclubs:
            url = "https://www.toastmasters.org/api/sitecore/FindAClub/DownloadCsv?district=%s&advanced=1&latitude=0&longitude=0" % district
            clubdata = getresponse(url)
            if clubdata:
                with open(makefilename('clubs', date.today() - timedelta(1)), 'w') as f:
                            f.write(''.join(clubdata).replace('\r',''))
                print("Fetched clubs")
            else:
                print('No data received from %s' % url)

    else:
        # We are getting historical data
        startdate = datetime.strptime(cleandate(parms.startdate), '%Y-%m-%d').date()
        if parms.enddate:
            enddate = datetime.strptime(cleandate(parms.enddate), '%Y-%m-%d').date()
        else:
            enddate = startdate
     
        d = startdate
        while d <= enddate:
            
            doreportsfor(district, d)
            d += timedelta(1)
    
