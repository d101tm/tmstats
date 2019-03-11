#!/usr/bin/env python
""" Remove Google Analytics from Divi installation """

import dbconn, tmutil, sys, os
import re



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    tmutil.gotodatadir()           # Move to the proper data directory
        
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--verbose', '-v', action='count')
    parms.add_argument('--configfile', type=str, default='/dev/null')
    # Add other parameters here
    parms.parse() 
   
    
    # Parse the WP Configuration file to find the database
    config = tmutil.parseWPConfig(open(parms.configfile,'r'))
    # Connect to the database
    conn = dbconn.dbconn(config['DB_HOST'], config['DB_USER'], config['DB_PASSWORD'], config['DB_NAME'])
    curs = conn.cursor()
    prefix = config['table_prefix']
    optiontable = prefix + 'options'
    curs.execute("SELECT option_value FROM %s WHERE option_name = 'et_divi'" % optiontable)
    searchText = curs.fetchone()[0]

    pattern = re.compile(r"(</script>|^)(\s*)(<script>.*?GoogleAnalyticsObject.*?</script>)", re.I|re.M|re.S)
    m = re.search(pattern, searchText)
    # We need to keep the length of the string unchanged
    need = len(m.group(1)) + len(m.group(2)) + len(m.group(3))
    result = re.sub(pattern, ('</script>'.ljust(need)), searchText)
    if '<script>' not in result:
        sys.exit(1)
    if result != searchText:
        stmt = "UPDATE %s SET option_value=%%s WHERE option_name = 'et_divi'" % optiontable
        print(stmt)
        curs.execute(stmt, (result,))
        print(curs.rowcount, 'update')
        conn.commit()
    else:
        print("Google Analytics not found")

