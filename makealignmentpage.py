#!/usr/bin/env python3
""" Create the index.html page for the alignment directory on d101tm """

import os
import sys
from time import localtime, strftime

import tmglobals

myglobals = tmglobals.tmglobals()

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":

    import tmparms

    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--fordec', action='store_true')
    parms.add_argument('--outdir', type=str, default='${alignmentdir}')

    # Do global setup
    myglobals.setup(parms, sections='alignment')
    conn = myglobals.conn
    curs = myglobals.curs

    os.chdir(parms.outdir)

    class alignmentfile:
        def __init__(self, filename):
            self.filename = filename
            self.mtime = localtime(os.path.getmtime(filename))

        def makeitem(self, s):
            return f'<li><a href="{self.filename}">{s}</a></li>'


    filenames = ['detailfile', 'markerfile', 'mapfile', 'reportfile', 'summaryfile', 'colordetailfile',
                 'changesfile', 'postdecchangesfile']
    files = {n:alignmentfile(getattr(parms, n, None)) for n in filenames}
    lastupdate = strftime('%B %-d, %Y at %-I:%m %p', max([files[item].mtime for item in files]))

    details = []
    details.append(files['summaryfile'].makeitem('summary'))
    details.append(files['mapfile'].makeitem('map'))
    if not parms.fordec:
        details.append(files['detailfile'].makeitem('detailed list with club meeting times and places'))
    else:
        details.append(files['colordetailfile'].makeitem('detailed list with club meeting times and places'))
        details.append(files['reportfile'].makeitem('<i>pro forma</i> performance report'))

    sys.stdout.write(f"""<html>
    <head>
      <title>D101 Proposed Realignment as of {lastupdate}</title>
    </head>
    <body>
      <p>This page lets you see the proposed realignment as of {lastupdate}:
      <ul>
      %s
      </ul>
""" % ('\n'.join(details)))

    sys.stdout.write(open(parms.datacurrencyfile).read())

    if parms.fordec:
        sys.stdout.write("""
        <p>In addition, there is information on club changes:
        <ul>
        %s
    """ % files['changesfile'].makeitem('Club changes since July 1'))
        if (open(files['postdecchangesfile'].filename, 'r').readlines()):
            sys.stdout.write("""
        %s
    """ % files['postdecchangesfile'].makeitem('Club changes since the DEC meeting'))
        sys.stdout.write("""
        </ul>
    """)
    sys.stdout.write("""
    </body>
</html>
""")
