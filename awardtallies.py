#!/usr/bin/env python3

# Create the "awards by division" and "awards by type" CSVs

import dbconn, tmutil, sys, os, datetime, tmglobals, tmparms, argparse
globals = tmglobals.tmglobals()




### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":

    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--divfile', default='awardsbydivision.csv', dest='divfile', type=argparse.FileType('w'), help="CSV file: awards by division")
    parms.add_argument('--typefile', default='awardsbytype.csv', dest='typefile', type=argparse.FileType('w'), help="CSV file: awards by type")
    parms.add_argument('--tmyear', default=None, dest='tmyear', type=int, help='TM Year (current if omitted)')
    
    # Do global setup
    globals.setup(parms)
   
    # Connect to the database        
    conn = globals.conn
    curs = globals.curs

    # We go by the calendar, not the TMyear in the database, because WHQ never stops processing awards    
    if parms.tmyear:
        tmyear = parms.tmyear
    else:
        today = datetime.datetime.today()
        if today.month <= 6:
            tmyear = today.year - 1
        else:
            tmyear = today.year


    # First, deal with awards by Division
    parms.divfile.write('Division,Awards\n')
    curs.execute("SELECT division, count(*) FROM awards WHERE tmyear = %s AND award != 'LDREXC' GROUP BY division ORDER BY division", (tmyear,))
    for l in curs.fetchall():
        parms.divfile.write('%s,%d\n' % (l[0].replace(',',';'), l[1]))
    parms.divfile.close()
     
    # And then awards by type
    parms.typefile.write('Award,Achieved\n')
    curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award = 'CC'", (tmyear,))
    parms.typefile.write('Competent Communicator,%d\n'% curs.fetchone()[0])
    curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award LIKE 'AC%%'", (tmyear,))
    parms.typefile.write('Advanced Communicator,%d\n'% curs.fetchone()[0])
    curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award = 'CL'", (tmyear,))
    parms.typefile.write('Competent Leader,%d\n'% curs.fetchone()[0])
    curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award LIKE 'AL%%'", (tmyear,))
    parms.typefile.write('Advanced Leader,%d\n'% curs.fetchone()[0])
    curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award = 'DTM'", (tmyear,))
    parms.typefile.write('Distinguished Toastmaster,%d\n'% curs.fetchone()[0])
    parms.typefile.close()    
    
    # And that's it.
