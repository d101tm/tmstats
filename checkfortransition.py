#!/usr/bin/env python
""" Returns the parameters to pass to the Bash 'export' builtin to set
    or nullify a shell variable to correspond to information for a 
    specific Toastmasters year that's not the one corresponding to the
    latest information in the database.

    Uses parameters from the YML file (or from the invocation) to build
    the response.  For example, if we were looking for a 2016 value of
    newAlignment, the value would come from the 2016: newAlignment entry
    in the YML file (though a --newAlignment on the invocation would win).

    Invoke like this:
    export "$(checkfortransition.py officers)"

"""

import dbconn, tmutil, sys, os, time


if __name__ == "__main__":
 
    import tmparms
    tmutil.gotodatadir()           # Move to the proper data directory
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('varname', help='Name of the variable to set')
    parms.add_argument('--tmyear', action='store', default=None, help="Specify the TM year we are to look for; if omitted, based on the calendar date.")
    parms.add_argument('--newAlignment', dest='newAlignment', default=None, help='Overrides area/division data from the CLUBS table.')
    parms.add_argument('--officers', dest='officers', default=None, help='URL of the CSV export form of a Google Spreadsheet with Area/Division Directors')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # What year do we think we should be in?
    if parms.tmyear:
        desiredyear = int(parms.tmyear)
    else:
        (year, month) = time.localtime()[0:2]
        if month <= 6:
            desiredyear = year - 1
        else:
            desiredyear = year
    ans = '%s=' % parms.varname   # Assume we unset it
    f = parms.varname
    if desiredyear != int(tmutil.getTMYearFromDB(curs)):
        if parms.__dict__[f]:
            ans = "%s=\"--%s '%s'\"" % (f, f, parms.__dict__[f])
        elif desiredyear in parms.__dict__:
            try:
                ans = "%s=\"--%s '%s'\"" % (f, f, parms.__dict__[desiredyear][f])
            except KeyError:
                pass
    print ans

