#!/usr/bin/env python3
""" Clear the WordPress supercache """

import tmutil, sys, os
import tmglobals
globals = tmglobals.tmglobals()



### Insert classes and functions here.  The main program begins in the "if" statement below.

def wipe():
    try:
        os.remove('index.html')
    except OSError:
        pass
    try:
        os.remove('index.html.gz')
    except OSError:
        pass


if __name__ == "__main__":
 
    # @@TACKY@@ Move to the source directory
    os.chdir(os.path.dirname(sys.argv[0]))
    import tmparms
    
    # Establish parameters
    parms = tmparms.tmparms()
    parms.add_argument('what', nargs='*', help='pages to clear.  Specify "." to clear all pages.')
    parms.add_argument('--cachedir')
    parms.add_argument('--clearhome', action='store_true')
    parms.add_argument('--verbose', action='store_true')
    parms.add_argument('--all', action='store_true')
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    try:
        cd = parms.cachedir
    except AttributeError:
        if parms.verbose:
            sys.stderr.write('No cache directory specified.\n')
        sys.exit(1)

    if not parms.cachedir:
        if parms.verbose:
            sys.stderr.write('No cache directory specified.\n')
        sys.exit(1)
    
    try:
      os.chdir(parms.cachedir)
    except OSError:
        sys.stderr.write('Cache directory %s not found.\n' % parms.cachedir)
        sys.exit(2)

    if parms.clearhome or parms.all:
        wipe()

    if parms.all:
        for name in os.listdir('.'):
            if os.path.isdir(name) and name != 'feed':
                parms.what.append(name)
        if parms.verbose:
            sys.stderr.write('Removing\n  %s\n' % '\n  '.join(parms.what))

    for d in parms.what:
        try:
            os.chdir(d)
        except OSError:
            if parms.verbose:
                sys.stderr.write('%s not found.\n' % d)
            continue
        wipe()
        os.chdir(parms.cachedir)
        try:
            os.rmdir(d)
        except OSError:
            pass   # Something re-created it, probably


