#!/usr/bin/env python3
"""Fix up awards in the database to use new IDs from WHQ

In particular, remove any awards with the new short pathids,
then update all awards with the old long pathids to use the 
new short pathid.  """



import tmutil, sys
import tmglobals
globals = tmglobals.tmglobals()

def doit(it):
    curs = globals.curs
    curs.execute(it)
    if curs.rowcount:
        print(it)
        print(curs.rowcount, 'row%s affected' %( 's' if curs.rowcount > 1 else ''))

oldtonew = {'DYNLEA': 'DL',
            'EFFCOA': 'EC',
            'INNPLA': 'IP',
            'LEADEV': 'LD',
            'MOTSTR': 'MS',
            'PERINF': 'PI',
            'PREMAS': 'PM',
            'STRREL': 'SR',
            'TEACOL': 'TC',
            'VISCOM': 'VC'}


### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn

    # If there are no old awards in the database, exit.  
    gotsome = False
    for id in oldtonew:
        it = 'SELECT COUNT(*) FROM awards WHERE award LIKE "%s%%"' % id
        curs.execute(it)
        if curs.fetchone()[0] > 0:
            gotsome = True
            break

    if not gotsome:
        print('No old awards in database; exiting.')
        sys.exit(1)

        
    # Now, update old to new:
    for id in oldtonew:
        for i in range(1,6):
            # Delete new awards which weren't acknowledged
            doit('DELETE FROM awards WHERE award = "%s%d and acknowledged = 0"' % (oldtonew[id], i))
            doit('UPDATE awards SET award="%s" WHERE award="%s"' % ('%s%d' % (oldtonew[id], i), '%sL%d' % (id, i)))

            doit('UPDATE awards SET award="%s" WHERE award="%s"' % ('%s%d' % (oldtonew[id], i), '%s%d' % (id, i)))

            
    conn.commit()
        
    
    
