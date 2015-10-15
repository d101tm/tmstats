#!/usr/bin/python

# Create the "largest club" and "most new members" CSVs

import dbconn, tmutil, sys, os


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
 
    import tmparms, argparse
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--netfile', default='netadd.csv', dest='netfile', type=argparse.FileType('w'), help="CSV file: net new members")
    parms.add_argument('--bigfile', default='bigclubs.csv', dest='bigfile', type=argparse.FileType('w'), help="CSV file: active members")
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Main program begins here.

    # First, deal with net adds
    # Get the top ten (with ties)
    parms.netfile.write('Club Name,Members Added\n')
    curs.execute("select clubname, activemembers - membase as net from clubperf where entrytype = 'L'  having net > 0 and net >= (select min(net) from (select activemembers - membase as net from clubperf where entrytype = 'L' order by net desc limit 10) m) order by net desc, clubname")
    for l in curs.fetchall():
        parms.netfile.write('%s, %d\n' % (l[0].replace(',',';'), l[1]))
    parms.netfile.close()
     
    # And now, the biggest clubs
    parms.bigfile.write('Club Name,Active Members\n')
    curs.execute("select clubname, activemembers from clubperf where entrytype = 'L' having activemembers >= (select min(activemembers) from (select activemembers from clubperf where entrytype = 'L' order by activemembers desc limit 10) m) order by activemembers desc, clubname")
    for l in curs.fetchall():
        parms.bigfile.write('%s, %d\n' % (l[0].replace(',',';'), l[1]))
    parms.bigfile.close()    
    
    # And that's it.
