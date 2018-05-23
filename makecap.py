#!/usr/bin/env python
""" Make the CAP page inclusions from the Google spreadsheet """
from __future__ import print_function
import tmutil, sys
import tmglobals
globals = tmglobals.tmglobals()
import xlrd
import requests


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
    ambassadors = {}      # Key by number of visits in column C
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
            values.append(tvisits)
                    
            # And put the entry where it belongs
            try:
                ambassadors[values[2]].append(values)
            except KeyError:
                ambassadors[values[2]] = [values,]
                
    # Now, sort by decreasing number of visits
    keys = sorted(ambassadors.keys(),reverse=True)
    
    with open(parms.outprefix+'ambassadors.shtml', 'w') as outfile:
    
        if keys[0]:  # Then we have at least one member who's logged visits since May 20th
            for n in keys:
                outfile.write('<p><b>%s visit%s since May 20</b>: ' % (int(n) if n > 0 else 'No', 's' if n != 1 else '' ))
                names = []
                ambassadors[n].sort(key=lambda k:(-k[-1],k[1], k[0]))
                for item in ambassadors[n]:
                    names.append('<span class="altname">%s %s</span> (<b>%d</b>)' % (item[0], item[1], item[-1]))
                outfile.write(', '.join(names))
                outfile.write('</p>\n')            
        else:  # No visits since May 2th:
            outfile.write('<p>No visits have been made since May 20th. Visits earlier in the year:</p>\n')
            ambassadors[0].sort(key=lambda k:(-k[-1],k[1], k[0]))
            names = []
            for item in ambassadors[0]:
                names.append('<span class="altname">%s %s</span> (<b>%d</b>)' % (item[0], item[1], item[-1]))
            outfile.write(', '.join(names))
            outfile.write('</p>\n')
        outfile.write('<p>Thanks to all Club Ambassadors this year.</p>\n')
        
        
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
    keys = sorted(clubs.keys(),reverse=True)
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

    insights = []
    for row in range(1, sheet.nrows):
        val = sheet.row_values(row)
        insights.append(('<b>NEW: </b>' if val[0] else '', val[1].encode('utf-8')))
    insights.sort(key=lambda k:(-len(k[0]), k[1].lower()))
    with open(parms.outprefix+'insights.shtml', 'w') as outfile:
        outfile.write('<ul>\n')
        for row in insights:
            outfile.write('<li>%s%s</li>\n' % row)
        outfile.write('</ul>\n')
       
