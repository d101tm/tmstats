#!/usr/bin/env python
""" Insert description of this program here """

import dbconn, tmutil, sys, os



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    tmutil.gotodatadir()           # Move to the proper data directory
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--verbose', '-v', action='count')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
