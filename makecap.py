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
    parms.add_argument('--minvisits', default=2, type=int)
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
    sheet = book.sheet_by_name('Ambassadors')
    colnames = sheet.row_values(0)
    ambassadors = []
    for row in range(1, sheet.nrows):
        ambassadors.append(tuple(sheet.row_values(row)))
    ambassadors.sort(key=lambda k:(-k[2],k[1],k[0]))
    with open(parms.outprefix+'ambassadors.shtml', 'w') as outfile:
        outfile.write('<table class="caprec">\n')
        outfile.write('<thead>\n')
        outfile.write('<tr><td><b>Ambassador</b><td>%s</td><td></td></tr>\n' % colnames[2])
        outfile.write('</thead>\n<tbody>\n')
        for row in ambassadors:
            outfile.write('<tr><td>%s %s</td><td>%d</td><td>%s</td></tr>\n' % row)
        outfile.write('</tbody>\n</table>\n')
        
    # Now, the clubs
    sheet = book.sheet_by_name('Clubs')
    colnames = sheet.row_values(0)
    clubs = []
    for row in range(1, sheet.nrows):
        clubs.append(tuple(sheet.row_values(row)))
    clubs.sort(key=lambda k:(-k[1], k[0]))
    with open(parms.outprefix+'clubs.shtml', 'w') as outfile:
        outfile.write('<table class="caprec">\n')
        outfile.write('<thead>\n')
        outfile.write('<tr><td><b>%s</b><td>%s</td></tr>\n' % tuple(colnames))
        outfile.write('</thead>\n<tbody>\n')
        for row in clubs:
            outfile.write('<tr><td>%s</td><td>%d</td></tr>\n' % row)
        outfile.write('</tbody>\n</table>\n')
        
    # And finally, the insights
    sheet = book.sheet_by_name('Insights')
    colnames = sheet.row_values(0)

    
    with open(parms.outprefix+'insights.shtml', 'w') as outfile:
        outfile.write('<ul>\n')
        for row in range(1, sheet.nrows):
            val = sheet.row_values(row)
            outfile.write('<li>%s%s</li>\n' % ('<b>NEW:  <b>' if val[0] else '', val[1].encode('utf-8')))
        outfile.write('</ul>\n')
       