#!/usr/bin/env python3
""" Insert description of this program here """

import tmutil, sys
import tmglobals
globals = tmglobals.tmglobals()
import csv, xlsxwriter



### Insert classes and functions here.  The main program begins in the "if" statement below.
divisions = {}
fontname = 'Myriad Pro'

class myclub(object):    
    
    def __init__(self, info, dec):
        keepers = ['clubnumber', 'clubname', 'oldarea', 'newarea']
        for f in keepers:
           self.__dict__[f] = info[f]

        if self.clubnumber in dec:
            self.decarea = dec[self.clubnumber]
        else:
            self.decarea = 'New'
            
        self.clubnumber = int(self.clubnumber)
        self.division = self.newarea[0]
        if self.division not in divisions:
            divisions[self.division] = {}
        thisdiv = divisions[self.division]
        if self.newarea not in thisdiv:
            thisdiv[self.newarea] = []
        thisarea = thisdiv[self.newarea]
        thisarea.append(self)
            
        
        

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    # Add other parameters here
    parms.add_argument('--infile', default='d101align.csv')
    parms.add_argument('--decfile', default='d101decalign.csv')
    parms.add_argument('--outtemplate', default='d101bm-div%s.xlsx')

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn

    # Start by getting alignment from the DEC file
    reader = csv.DictReader(open(parms.decfile, 'r'))
    dec = {}
    for row in reader:
        dec[row['clubnumber']] = row['newarea']
    
    # The only information we need is in the alignment file
    reader = csv.DictReader(open(parms.infile, 'r'))
    for row in reader:
        myclub(row, dec)

    
        
    # Process each division in turn
    divnames = sorted(divisions.keys())
    
    for div in divnames:
        thisdiv = divisions[div]
        book = xlsxwriter.Workbook(parms.outtemplate % div)
        
        # Create formats
        divformat = book.add_format({'bold': True, 'font_name': fontname, 'font_size': 18, 'align': 'center'})
        areaformat = book.add_format({'bold': True, 'font_name': fontname, 'font_size': 14, 'align': 'center'})
        nameformat = book.add_format({'bold': True, 'font_name': fontname})
        numformat = book.add_format({'align': 'right', 'font_name': fontname})
        bold = book.add_format({'bold':True, 'font_name': fontname})
        boldright = book.add_format({'bold': True, 'align':'right', 'font_name': fontname})
        changedformat = book.add_format({'italic': True, 'bold': True, 'font_name': fontname, 'bg_color': '#E0E0E0'})
        
        sheet = book.add_worksheet()
        sheet.set_column(0, 0, 15)
        sheet.set_column(1, 1, 50)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.merge_range(0, 0, 0, 3, 'Division %s' % div, divformat)  
        sheet.write(1, 0, 'Club Number', boldright)
        sheet.write(1, 1, 'Club Name', bold)
        sheet.write(1, 2, 'Current Alignment', bold)
        sheet.write(1, 3, 'Proposed Alignment', bold)
        rownum = 2
        # Process each area in turn
        areanames = sorted(thisdiv.keys())
        for area in areanames:
            thisarea = thisdiv[area]
            thisarea.sort(key=lambda c:c.clubnumber)
            sheet.merge_range(rownum, 0, rownum, 3, 'Area %s' % area, areaformat)
            rownum += 1
            for club in thisarea:
                sheet.write(rownum, 0, club.clubnumber, numformat)
                if club.newarea != club.decarea:
                    print(club.clubname, 'moved to', club.newarea, '- was', club.decarea)
                    sheet.write(rownum, 1, club.clubname, changedformat)
                else:
                    sheet.write(rownum, 1, club.clubname, nameformat)
                sheet.write(rownum, 2, club.oldarea)
                sheet.write(rownum, 3, club.newarea)
                rownum += 1
        
        # That's it
        book.close()
    
    
