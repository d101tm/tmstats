#!/usr/bin/env python3
""" Create the anniversary date table """

import tmutil, sys
import tmglobals
globals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms, csv
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('--outfile', default='anniversary.csv')
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    yy = globals.today.year
    mm = globals.today.month
    dd = globals.today.day
    if mm == 12:
        nextfirst = globals.today.replace(year=yy+1,month=1,day=1)
    else:
        nextfirst = globals.today.replace(month=mm+1,day=1)
        
    monthname = nextfirst.strftime('%B, %Y')

    writer = csv.writer(open(parms.outfile, 'w'))
    writer.writerow(['Club Name', 'Club Number', 'Charter Year', 'Charter Month', 'Charter Day', 'Age at end of ' + monthname, 'Has Anniversary in ' + monthname, 'Next Anniversary', 'Age on Next Anniversary'])
    curs.execute('SELECT MAX(lastdate) FROM clubs')
    maxdate = curs.fetchone()[0]
    curs.execute('SELECT clubname, clubnumber, charterdate FROM clubs WHERE lastdate = %s ORDER BY month(charterdate), day(charterdate)', (maxdate,))
    for (clubname, clubnumber, charterdate) in curs.fetchall():
        cyy = charterdate.year
        cmm = charterdate.month
        cdd = charterdate.day
        ayy = yy + (1 if (100*mm + dd) >= (100*cmm + cdd) else 0)
        nextannage = ayy - cyy
        nextmonage = (yy - cyy) - (1 if cmm > nextfirst.month else 0)
        writer.writerow((clubname, clubnumber, cyy, cmm, cdd,  nextmonage, 'Yes' if cmm == nextfirst.month else '', '%04d-%02d-%02d' % (ayy, cmm, cdd), nextannage))
    
    

