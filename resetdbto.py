#!/usr/bin/python
""" Reset database to specified date """

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os, populatelastfor


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--resetto', default='yesterday', help="Date to reset the database to.")
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    resetdate = tmutil.cleandate(parms.resetto)
    print 'Resetting database to', resetdate
    
    # Do the straightforward resets
    curs.execute("DELETE FROM loaded WHERE loadedfor > %s", (resetdate,))
    curs.execute("DELETE FROM areaperf WHERE asof > %s", (resetdate, ))
    curs.execute("DELETE FROM clubperf WHERE asof > %s", (resetdate, ))
    curs.execute("DELETE FROM distperf WHERE asof > %s", (resetdate, ))
    curs.execute("DELETE FROM clubchanges WHERE changedate > %s", (resetdate,))
    
    # Take care of clubs
    # First, remove any items whose first date is after the resetdate
    curs.execute("DELETE FROM clubs WHERE firstdate > %s", (resetdate,))
    
    # And now, reset any items whose last date is after the resetdate
    curs.execute("UPDATE clubs SET lastdate = %s where lastdate > %s", (resetdate, resetdate))
    
    # Finally, rebuild lastfor
    populatelastfor.doit(curs, parms)
    
    # And declare victory
    conn.commit()
    conn.close()
    
