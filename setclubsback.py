#!/usr/bin/env python3
""" Single-use program to set the 'clubs' table and .CSV files back by one day """

import tmutil, sys, os
import tmglobals
globals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    import zipfile
    import datetime
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('zipfiles', nargs='*', help='ZIP files in which to rename club.*.csv files')
    parms.add_argument('--updatedatabase', dest='database', action='store_true' )
    # Add other arguments here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    if len(parms.zipfiles) == 0 and not parms.database:
        parms.parser.print_help()
        sys.exit(1)
        
    if parms.database:
        # We have to delete and re-create the primary key to be able to do the update easily
        curs.execute("START TRANSACTION")
        curs.execute("ALTER TABLE loaded DROP PRIMARY KEY")
        curs.execute("UPDATE loaded SET loadedfor = SUBDATE(loadedfor, 1) WHERE tablename = 'clubs'")
        curs.execute("ALTER TABLE loaded ADD PRIMARY KEY (tablename, loadedfor)")
        
        # And now we have to fix all the dates in the CLUBS table
        # Again, we have a key to delete and re-create
        curs.execute("ALTER TABLE clubs DROP KEY clubnumber")
        curs.execute("UPDATE clubs SET firstdate = SUBDATE(firstdate, 1), lastdate = SUBDATE(lastdate, 1)")
        curs.execute("ALTER TABLE clubs ADD KEY clubnumber (clubnumber, firstdate)")
        
        curs.execute("COMMIT")
        
    if parms.zipfiles:
        for f in parms.zipfiles:
            newname = f+'.new'
            bakname = f+'.bak'
            inzip = zipfile.ZipFile(f, 'r')
            outzip = zipfile.ZipFile(newname,'w',zipfile.ZIP_DEFLATED)
            items = inzip.infolist()
            for item in items:
                newitem = item
                names = item.filename.split('.')
                if names[0] == 'clubs' and names[-1] == 'csv':
                    # Change to yesterday
                    names[1] = (datetime.datetime.strptime(names[1], '%Y-%m-%d') - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                    newitem.filename = '.'.join(names)
                outzip.writestr(newitem,inzip.read(item))
            inzip.close()
            outzip.close()
            os.rename(f, bakname)
            os.rename(newname, f)
        
