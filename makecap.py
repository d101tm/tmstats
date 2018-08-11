#!/usr/bin/env python3
""" Make the CAP page inclusions from the Google spreadsheet """

import tmutil, sys
import tmglobals
globals = tmglobals.tmglobals()
import xlrd
import requests
import re

def makesortkey(s):
    # Strip non-alphameric characters and return all lower-case
    return ' '.join(re.split('\W+', s.lower())).strip()

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('--capsheet', default='https://docs.google.com/spreadsheets/d/e/2PACX-1vRLTA6_-RLVQDblDybtbzFZIoiyNGfs4AGMaXi95ePEMMilfDbxaFjUNz3at2vGaG7hkjUT_HXlTyPJ/pub?output=xlsx')
    parms.add_argument('--outprefix', default='cap')
    parms.add_argument('--minvisits', default=1, type=int)
    # Add other parameters here
    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    # Get the CAP sheet
    if parms.capsheet.lower().startswith('http'):
        book = xlrd.open_workbook(file_contents=requests.get(parms.capsheet, stream=True).raw.read())
    else:
        book = xlrd.open_workbook(parms.capsheet)
        
    

    # And build the inclusion files
    # First, the ambassadors
    sheet = book.sheet_by_name('All Visits')
    colnames = sheet.row_values(0)
    asof = colnames[6]    
    ambassadors = []
    grandtotalvisits = 0
    recent101visits = 0
    for row in range(1, sheet.nrows):
        # Require first and last names
        values = sheet.row_values(row)
        if values[0] and values[1]:  # Names must be non-blank
            # This code now handles new and old visit counts
            # Convert blank counts to zero
            values[0] = values[0].strip()
            values[1] = values[1].strip()
            tvisits = 0
            for cnum in [2, 3, 4]:
                try:
                    values[cnum] = int(values[cnum])
                except ValueError:
                    values[cnum] = 0
                tvisits += values[cnum]
                grandtotalvisits += values[cnum]
            recent101visits += values[2]
            values.append(tvisits)
            ambassadors.append(values)
                
    
    with open(parms.outprefix+'ambassadors.shtml', 'w') as outfile:
        # Sort by recent visits
        ambassadors.sort(key=lambda k:(-k[2], k[1], k[0]))
        names = []
        outfile.write('<p><b>%d total visits to District 101 clubs since May 20</b>:<br />\n' % recent101visits)
        for item in ambassadors:
            if item[2] > 0:
                names.append('<span class="altname">%s %s</span> (<b>%d</b>)' % (item[0], item[1], item[2]))
        outfile.write(', '.join(names))
        outfile.write('</p>\n')            
        
        # Sort by total visits
        ambassadors.sort(key=lambda k:(-k[-1], k[1], k[0]))
        names = []
        outfile.write('<p><b>%d total visits to all clubs since July 1, 2017</b>:<br />\n' % grandtotalvisits) 
        for item in ambassadors:
            if item[-1] > 0:
                names.append('<span class="altname">%s %s</span> (<b>%d</b>)' % (item[0], item[1], item[-1]))
        outfile.write(', '.join(names))
        outfile.write('</p>\n')            
        outfile.write('<p>Information current %s.' % asof)
        
    # Now, the clubs
    sheet = book.sheet_by_name('Clubs')
    colnames = sheet.row_values(0)
    clubs = {}
    for row in range(1, sheet.nrows):
        values = sheet.row_values(row)
        values[0] = values[0].strip()
        if values[0]:  # Avoid empty rows
            try:
                values[1] = int(values[1])
            except ValueError:
                continue        # Don't include clubs with no visits
            try:
                clubs[values[1]].append(values[0])
            except KeyError:
                clubs[values[1]] = [values[0],]
                
    # Now, sort by decreasing visits
    keys = sorted(list(clubs.keys()),reverse=True)
    with open(parms.outprefix+'clubs.shtml', 'w') as outfile:
        for n in keys:
            clubs[n].sort()
            outfile.write('<p><b>%d visit%s</b>: ' % (n, 's' if n > 1 else ''))
            names = ['<span class="altname">%s</span>' % item for item in clubs[n]]
            outfile.write(', '.join(names))
            outfile.write('</p>\n')

        
    # And finally, the insights
    sheet = book.sheet_by_name('Insights')
    colnames = sheet.row_values(0)

    newinsights = []
    oldinsights = []
    for row in range(1, sheet.nrows):
        val = sheet.row_values(row)
        insight = val[1].encode('utf-8')
        if val[0]:
            newinsights.append(insight)
        else:
            oldinsights.append(insight)
            
    newinsights.sort(key=lambda k:makesortkey(k))
    oldinsights.sort(key=lambda k:makesortkey(k))
        
    with open(parms.outprefix+'insights.shtml', 'w') as outfile:
        if newinsights:
            outfile.write('<h3>Recent Insights</h3>')
            outfile.write('<ul>\n')
            for item in newinsights:
                outfile.write('<li>%s</li>\n' % item)
            outfile.write('</ul>\n')
            
        if oldinsights:
            outfile.write('''<div class="oldheaddiv" onclick="jQuery('#oldinsightopen, #oldinsightclose, #oldinsight').toggle()">''')
            outfile.write('<h3>Earlier Insights (Click to <span id="oldinsightopen">show</span><span id="oldinsightclose" style="display:none;">hide</span>)</h3></div>\n')
            outfile.write('<div id="oldinsight" style="display:none;">\n')
            outfile.write('<ul>\n')
            for item in oldinsights:
                outfile.write('<li>%s</li>\n' % item)
            outfile.write('</ul>\n')
            outfile.write('</div>\n')
