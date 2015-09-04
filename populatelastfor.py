#!/usr/bin/python
""" Populate the 'lastfor' table in the database. """
import dbconn, tmutil, sys, os, datetime


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)
        

def dotable(curs, name, tmyear):
    """ Get the lastfor ids for the named table and year """
    stmt = """select ?.clubnumber, ?.id, ?.asof, ?.monthstart from ? inner join (select clubnumber, max(asof) as m from ? where entrytype in ('M', 'L') and monthstart >= %s and monthstart <= %s group by clubnumber order by monthstart desc,  m desc, clubnumber) latest on ?.clubnumber = latest.clubnumber and ?.asof = latest.m"""
    stmt = stmt.replace('?', name)  # Interpolate the table name
    curs.execute(stmt, ('%d-07-01' % tmyear, '%d-06-01' % (tmyear + 1)))
    
    res = [r for r in curs.fetchall()]
    return res

class myclub():
    def __init__(self, clubnumber):
        self.clubnumber = clubnumber
        self.clubperfid = 0
        self.areaperfid = 0
        self.distperfid = 0
        self.asof = 0
        self.monthstart = 0
    
    def adddist(self, id, asof, monthstart):
        self.distperfid = id
        self.asof = asof
        self.monthstart = monthstart
        
    def addarea(self, id, asof, monthstart):
        self.areaperfid = id
        
    def addclub(self, id, asof, monthstart):
        self.clubperfid = id
        
def doyear(y, curs):
    """ Update or insert information for year 'y' """
    clubinfo = {}
    distperf = dotable(curs, 'distperf', y)
    for (clubnumber, id, asof, monthstart) in dotable(curs, 'areaperf', y):
        clubinfo[clubnumber] = myclub(clubnumber)
        clubinfo[clubnumber].adddist(id, asof, monthstart)
    for (clubnumber, id, asof, monthstart) in dotable(curs, 'areaperf', y):
        clubinfo[clubnumber].addarea(id, asof, monthstart)
    for (clubnumber, id, asof, monthstart) in dotable(curs, 'clubperf', y):
        clubinfo[clubnumber].addclub(id, asof, monthstart)
        
    
    colnames = ['clubnumber', 'clubperf_id', 'areaperf_id', 'distperf_id', 'asof', 'monthstart', 'tmyear']
    colholders = ','.join(colnames)    
    valueholders = ','.join(len(colnames) * ['%s'])
    updateclause = ','.join([cn + '=VALUES(' + cn + ')' for cn in colnames])
    stmt = "INSERT INTO lastfor (" + colholders + ") VALUES (" + valueholders + ") ON DUPLICATE KEY UPDATE " + updateclause
    
    allclubs = [(c.clubnumber, c.clubperfid, c.areaperfid, c.distperfid, c.asof, c.monthstart, y) for c in clubinfo.values()]
    curs.executemany(stmt, allclubs)

    conn.commit()

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
    parms.add_argument('--latestonly', action='store_true')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Delete any entries in the table; we regenerate from scratch.
    curs.execute('DELETE FROM lastfor')
    
    # We assume the same years in all three performance tables.
    curs.execute("SELECT MIN(monthstart), MAX(monthstart) FROM distperf")
    (firstmonth, lastmonth) = curs.fetchone()

    firsttmyear = firstmonth.year + (1 if firstmonth.month <= 6 else 0)
    lasttmyear = lastmonth.year + (1 if lastmonth.month <= 6 else 0)
 
    # If 'latestonly' is specified, only process the last year in the database
    if parms.latestonly:
        firsttmyear = lasttmyear
 
    for y in range(firsttmyear, lasttmyear+1):
        doyear(y, curs)
    
        
        
        