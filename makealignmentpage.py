#!/usr/bin/env python3
""" Create the index.html page for the alignment directory on d101tm """

import dbconn, tmutil, sys, os
from time import localtime, strftime
import tmglobals
globals = tmglobals.tmglobals()


### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--fordec', action='store_true')
    
    # Do global setup
    globals.setup(parms)
    conn = globals.conn
    curs = globals.curs

    
    lfile = 'alignment/d101location.html'
    mfile = 'alignment/d101newmarkers.js'
    rfile = 'alignment/d101proforma.html'
    sfile = 'alignment/d101minimal.html'
    postdecfile = 'alignment/changessincedecmeeting.html'

    # Get the last-modified dates for the alignment files.
    ltime = strftime("%Y-%m-%d %X", localtime(os.path.getmtime(lfile)))
    mtime = strftime("%Y-%m-%d %X", localtime(os.path.getmtime(mfile)))
    rtime = strftime("%Y-%m-%d %X", localtime(os.path.getmtime(rfile)))
    stime = strftime("%Y-%m-%d %X", localtime(os.path.getmtime(sfile)))

    details = []
    details.append('<li><a href="d101minimal.html">summary</a> (updated %s)</li>' % stime)
    details.append('<li><a href="d101align.htm">map</a> (updated %s)</li>' % mtime)
    details.append('<li><a href="d101location.html">detailed list with club meeting times and places</a> (updated %s)</li>' % ltime)

    if parms.fordec:
        details.append('<li><a href="d101proforma.html"><i>pro forma</i>performance report<a> (updated %s)</li>' % rtime)


    sys.stdout.write("""<html>
    <head>
      <title>D101 Proposed Realignment</title>
    </head>
    <body>
      <p>This page lets you see the proposed realignment as follows:
      <ul>
      %s
      </ul>
""" % ('\n'.join(details)))
    sys.stdout.write(open('alignmentsource.txt').read())


    if parms.fordec:
        sys.stdout.write("""
        <p>In addition, there is information on club changes:
        <ul>
        <li><a href="changesthisyear.html">All changes this Toastmasters Year</a>
    """)
        if (open(postdecfile, 'r').readlines()):
            sys.stdout.write("""
        <li><a href="changessincedecmeeting.html">Changes since the DEC meeting</a> 
    """)
        sys.stdout.write("""
        </ul>
    """)
    sys.stdout.write("""
    </body>
</html>
""")
    
    
    
