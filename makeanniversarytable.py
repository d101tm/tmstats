#!/usr/bin/env python
""" Create the anniversary date table """

import tmutil, sys
import tmglobals
globals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms, csv
    
    # Establish parameters
    parms = tmparms.tmparms()
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    yy = globals.today.year
    mm = globals.today.month
    dd = globals.today.day

    writer = csv.writer(sys.stdout)
    writer.writerow(['Club Name', 'Club Number', 'Charter Date', 'Next Anniversary', 'Age on Next Anniversary'])
    curs.execute('SELECT MAX(lastdate) FROM clubs')
    maxdate = curs.fetchone()[0]
    curs.execute('SELECT clubname, clubnumber, charterdate FROM clubs WHERE lastdate = %s ORDER BY charterdate', (maxdate,))
    for (clubname, clubnumber, charterdate) in curs.fetchall():
        cyy = charterdate.year
        cmm = charterdate.month
        cdd = charterdate.day
        if (100*mm + dd) >= (100*cmm + cdd):
            ayy = yy + 1   # Next anniversary is next year
        else:
            ayy = yy
        age = ayy - cyy
        writer.writerow((clubname, clubnumber, charterdate, '%04d-%02d-%02d' % (ayy, cmm, cdd), age))
    
    

