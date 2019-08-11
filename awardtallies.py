#!/usr/bin/env python3

# Create the "awards by division" and "awards by type" CSVs

import dbconn, tmutil, sys, os, datetime, tmglobals, tmparms, argparse
myglobals = tmglobals.tmglobals()




### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":

    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--divfile', default='${WORKDIR}/awardsbydivision.csv', dest='divfile', type=str, help="CSV file: awards by division")
    parms.add_argument('--typefile', default='${WORKDIR}/awardsbytype.csv', dest='typefile', type=str, help="CSV file: awards by type")
    parms.add_argument('--tmyear', default=None, dest='tmyear', type=int, help='TM Year (current if omitted)')
    
    # Do global setup
    myglobals.setup(parms)
   
    # Connect to the database        
    conn = myglobals.conn
    curs = myglobals.curs

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
    with open(parms.divfile, 'w') as outfile:
        outfile.write('Division,Awards\n')
        curs.execute("SELECT division, count(*) FROM awards WHERE tmyear = %s AND award != 'LDREXC' GROUP BY division ORDER BY division", (tmyear,))
        for l in curs.fetchall():
            outfile.write('%s,%d\n' % (l[0].replace(',',';'), l[1]))
     
    # And then awards by type
    with open(parms.typefile, 'w') as outfile:
        outfile.write('Award,Achieved\n')
        curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award = 'CC'", (tmyear,))
        outfile.write('Competent Communicator,%d\n'% curs.fetchone()[0])
        curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award LIKE 'AC%%'", (tmyear,))
        outfile.write('Advanced Communicator,%d\n'% curs.fetchone()[0])
        curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award = 'CL'", (tmyear,))
        outfile.write('Competent Leader,%d\n'% curs.fetchone()[0])
        curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award LIKE 'AL%%'", (tmyear,))
        outfile.write('Advanced Leader,%d\n'% curs.fetchone()[0])
        curs.execute("SELECT COUNT(*) FROM awards WHERE tmyear = %s AND award = 'DTM'", (tmyear,))
        outfile.write('Distinguished Toastmaster,%d\n'% curs.fetchone()[0])

    # And that's it.
