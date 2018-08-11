#!/usr/bin/env python3
""" MakeGuides - Create the Pathways Guides list based on the
    Excel spreadsheet """


import tmutil, sys
import tmglobals
import xlrd, re, codecs
globals = tmglobals.tmglobals()

class Guide:
    guides = {}
    def __init__(self, first, last, email):
        self.first = first.strip()
        self.last = last.strip()
        self.email = email.strip()
        self.guides[normalize('%s %s' % (first, last))] = self
        
    def ref(self):
        return '<a href="mailto:%s">%s %s</a>' % (self.email, self.first, self.last)

def normalize(s):
    s = s.strip().lower().replace('#','num')
    s = re.sub(r'[^a-zA-z0-9]+','',s)  
    return s

def normalizefieldnames(fields):
    # ('#' -> 'num', lowercase, no spaces or special chars)
    return [normalize(f) for f in fields]

def getfieldcols(colnames, fieldnames):
    res = []
    for f in fieldnames:
        res.append(colnames.index(f))
    return res

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('source', type=str)
    parms.add_argument('--outfile', dest='outfile', default='guides.html')
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn

    outfile = codecs.open(parms.outfile, 'w', 'utf-8', errors='ignore')
    outfile.write('<table id="guides">\n')
    outfile.write('  <thead>\n')
    outfile.write('    <tr>\n')
    outfile.write('    <th>Area</th>\n')
    outfile.write('    <th>Club Number</th>\n')
    outfile.write('    <th>Club Name</th>\n')
    outfile.write('    <th>Pathways Guide</th>\n')
    outfile.write('  </thead>\n')
    outfile.write('  <tbody>\n')


    # Open the spreadsheet
    book = xlrd.open_workbook(filename=parms.source)
    
    # Get the guides
    sheet = book.sheet_by_name('GuidesContact')
    colnames = normalizefieldnames(sheet.row_values(0))
    (firstcol, lastcol, emailcol) = getfieldcols(colnames, ('first', 'last', 'email'))
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        if len(row) >= 3 and row[2].strip():
            Guide(row[firstcol], row[lastcol], row[emailcol])

    # OK, now we need the club information
    sheet = book.sheet_by_name('PathwaysAssignments')
    colnames = normalizefieldnames(sheet.row_values(0))
    (divcol, areacol, numcol, namecol, guidecol) = getfieldcols(colnames,
            ('division', 'area', 'clubnumber', 'clubname', 'pathwaysguide'))

    # Write a row for every club
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        parts = ['<tr>\n']
        parts.append('  <td>%s%d</td>\n' % (row[divcol], row[areacol]))
        parts.append('  <td>%d</td>\n' % (row[numcol]))
        parts.append('  <td>%s</td>\n' % (row[namecol]))
        parts.append('  <td>%s</td>\n' % (Guide.guides[normalize(row[guidecol])].ref()))
        parts.append('</tr>\n')
        outfile.write(''.join(parts))

    # Finish the table
    outfile.write('  </tbody>\n')
    outfile.write('</table>\n')
    outfile.close()
    
