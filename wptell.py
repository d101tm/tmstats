#!/usr/bin/env python3
""" Output shell EXPORT statements to set variables corresponding to the database in
    the WordPress configuration file """

import tmutil, sys
import tmglobals
import os.path
myglobals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    # Add other parameters here

    # Do global setup
    myglobals.setup(parms, connect=False)
    wpc  = tmutil.parseWPConfig(open(os.path.join(parms.wpdir, 'wp-config.php'), 'r'))
    def export(wpc, key):
        print(f"export {key}={wpc[key]}")
    for k in ('DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'):
        export(wpc, k)
