#!/usr/bin/env python
""" Create the index.html page for the alignment directory on d101tm """

import dbconn, tmutil, sys, os
from time import localtime, strftime


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
    from tmutil import gotodatadir
    # Make it easy to run under TextMate
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    lfile = 'd101location.html'
    mfile = 'd101newmarkers.js'
    rfile = 'd101proforma.html'
    sfile = 'd101migration.html'
    # Get the last-modified dates for the alignment files.
    ltime = strftime("%Y-%m-%d %X", localtime(os.path.getmtime(lfile)))
    mtime = strftime("%Y-%m-%d %X", localtime(os.path.getmtime(mfile)))
    rtime = strftime("%Y-%m-%d %X", localtime(os.path.getmtime(rfile)))
    stime = strftime("%Y-%m-%d %X", localtime(os.path.getmtime(sfile)))
    
    sys.stdout.write("""<html>
    <head>
      <title>D101 Proposed Realignment</title>
    </head>
    <body>
      <p>This page lets you see the proposed realignment in four different ways:
      <ul>
        <li>As a <a href="d101align.htm">map</a> (updated %s)</li>
        <li>As a <a href="d101proforma.html"><i>pro forma</i> Green/Yellow/Red report</a> (updated %s)</li>
        <li>As a <a href="d101location.html">summary report</a> (updated %s)</li>
        <li>As a <a href="d101migration.html">club movement report</a> (updated %s)</li>
      </ul>
      %s
    </body>
</html>""" % (mtime, rtime, ltime, stime, open('alignmentsource.txt').read()))
    
    
    
