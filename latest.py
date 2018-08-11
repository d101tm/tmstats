#!/usr/bin/env python3
""" Print the latest date and the month that goes with it, based on
    the 'loaded' table.  

"""
import tmparms, tmglobals, os, sys, tmutil, MySQLdb
globals = tmglobals.tmglobals()



def getlatest(table, conn):
    curs = conn.cursor()
    # The MySQLdb library doesn't allow interpolating the table name, so we do
    # it via normal Python.
    district = tmparms.tmparms().district
    statement = 'select t.monthstart, l.latest FROM %s t INNER JOIN (select max(loadedfor) as latest FROM loaded WHERE tablename="%s") l ON t.asof = l.latest WHERE district = "%s" GROUP BY t.monthstart, l.latest' % (table, table, district)
    try:
        curs.execute(statement)
        ans = curs.fetchone()
        if ans:
            ans = [tmutil.stringify(x) for x in ans]
        else:
            ans = ('', '')
    except (MySQLdb.Error, TypeError) as e:
        sys.stderr.write(repr(e))
        ans = ('', '')
    return ans

if __name__ == '__main__':
    parms = tmparms.tmparms()
    # Allow specifying a table.
    parms.add_argument('--table', dest='table', default='clubperf')
    
    # Do global setup
    globals.setup(parms)
    parms.parse()
    
    ans = getlatest(parms.table, globals.conn)
    print(' '.join(ans))
