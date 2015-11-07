#!/usr/bin/python
""" Make the 'Congratulations!' slide and the list of award-winners."""

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os, datetime


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)

### Insert classes and functions here.  The main program begins in the "if" statement below.

awards = {}
knownawards = {
    'CC': 'Competent Communicator',
    'ACB': 'Advanced Communicator Bronze',
    'ACS': 'Advanced Communicator Silver',
    'ACG': 'Advanced Communicator Gold',
    'CL': 'Competent Leader',
    'ALB': 'Advanced Leader Bronze',
    'ALS': 'Advanced Leader Silver',
    'DTM': 'Distinguished Toastmaster',
    'LDREXC': 'High Performance Leadership Project'
}

commtrack = ['CC', 'ACB', 'ACS', 'ACG']
ldrtrack = ['CL', 'ALB', 'ALS', 'DTM']
knowns = commtrack + ldrtrack
unknowns = set()

class Award:
    def __init__(self, membername, award, clubname, awarddate):
        self.membername = membername
        self.award = award
        self.clubname = clubname
        self.awarddate = awarddate
        self.key = self.membername + ';' + self.clubname + ';' + repr(self.awarddate)
        if award not in awards:
            awards[award] = []
        awards[award].append(self)
        if award not in knowns:
            unknowns.add(award)
            
    def __repr__(self):
        return '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (self.membername, self.clubname, self.awarddate.strftime('%m/%d/%Y'))
        


if __name__ == "__main__":
 
    import tmparms
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    group = parms.parser.add_mutually_exclusive_group()
    group.add_argument('--since', type=int, default='30',
            help='How many days to look back')
    group.add_argument('--lastmonth', action='store_true',
            help='If specified, looks at the previous month')
    parms.add_argument('--include-hpl', action='store_true',
            help='If specified, include HPL awards.  Normally, they are excluded.')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    clauses = []
    # Figure out the timeframe for the queries.
    if parms.lastmonth:
        today = datetime.datetime.today()
        month = today.month - 1
        if month <= 0:
            month = 12
        clauses.append('MONTH(awarddate) = %d' % month)
    else:
        clauses.append('DATEDIFF(CURRENT_TIMESTAMP(), awarddate) <= %d' % parms.since)
        
    if not parms.include_hpl:
        clauses.append('award != "LDREXC"')
        
    curs.execute("SELECT COUNT(DISTINCT membername) FROM awards WHERE " + ' AND '.join(clauses))
    count = curs.fetchone()[0]

    curs.execute("SELECT membername, award, clubname, awarddate FROM awards WHERE " + ' AND '.join(clauses))
    for (membername, award, clubname, awarddate) in curs.fetchall():
        Award(membername, award, clubname, awarddate)
        
    for k in commtrack:
        if k in awards:
            print knownawards[k]
            for each in sorted(awards[k], key=lambda x:x.key):
                print each
            
    for k in ldrtrack:
        if k in awards:
            print knownawards[k]
            for each in sorted(awards[k], key=lambda x:x.key):
                print each
                
            
    for k in sorted(unknowns):
        if k in awards:
            print k
            for each in sorted(awards[k], key=lambda x:x.key):
                print each
        