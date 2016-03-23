#!/usr/bin/env python
""" Make the 'Congratulations!' slide and the list of award-winners."""

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os, datetime, subprocess


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
        return '<tr><td width="48%%">%s</td><td width="48%%">%s</td></tr>' % (self.membername, self.clubname)
        
def printawards(awards, knownawards, k):
    if k in awards:
        print '<tr><td class="awardname" colspan="2">%s</td></tr>' % knownawards[k]
        for each in sorted(awards[k], key=lambda x:x.key):
            print each


def makeCongratulations(count, district, timing, parms):
    # Now, create the "Congratulations" slide
        
    cmd = ['convert']
    cmd.append(parms.baseslide)
    cmd.append('-quality')
    cmd.append('50')
    cmd.append('-font')
    cmd.append('Helvetica-Bold')
    cmd.append('-pointsize')
    cmd.append('26')
    cmd.append('-fill')
    cmd.append('black')
    line1 = 100
    left = 380
    shadow = 2
    spacing = 32
    line = line1
    texts = ["Congratulations to the %d District %s" % (count, district),
             "members who achieved one or more of their",
             "educational goals %s." % (timing,),
             "",
             "Will you be recognized next?"]
    for t in texts:
        cmd.append('-draw')
        cmd.append('"text %d,%d \'%s\'"' % (left+shadow, line+shadow, t))
        line += spacing
    line = line1 + shadow
    cmd.append('-fill')
    cmd.append('white')
    for t in texts:
        cmd.append('-draw')
        cmd.append('"text %d,%d \'%s\'"' % (left, line, t))
        line += spacing
    cmd.append(parms.prefix + '.jpg')
    
    return cmd

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
    parms.add_argument('--prefix', type=str, default='recentawards',
            help='Filename prefix for the .jpg and .html files created by this program (default: %(default)s)')
    parms.add_argument('--baseslide', type=str, default='ed-achieve-base.png',
            help='Slide to use as the base for the "Congratulations" slide')
        
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    # Close stdout and reassign it to the output file
    sys.stdout.close()
    sys.stdout = open(parms.prefix + '.shtml', 'w')
    
    clauses = []
    # Figure out the timeframe for the queries.
    today = datetime.datetime.today()

    if parms.lastmonth:
        month = today.month - 1
        year = today.year
        if month <= 0:
            month = 12
            year = year - 1
        clauses.append('MONTH(awarddate) = %d' % month)
        timestamp = 'during ' + datetime.date(year, month, 1).strftime('%B, %Y')
        
    else:
        firstdate = today - datetime.timedelta(parms.since)
        clauses.append("awarddate >= '%s'" % firstdate.strftime('%Y-%m-%d'))
        timestamp = 'since ' + firstdate.strftime('%B ') + '%d' % firstdate.day


    if not parms.include_hpl:
        clauses.append('award != "LDREXC"')
        
    curs.execute("SELECT COUNT(DISTINCT membername) FROM awards WHERE " + ' AND '.join(clauses))
    count = curs.fetchone()[0]

    curs.execute("SELECT membername, award, clubname, awarddate FROM awards WHERE " + ' AND '.join(clauses))
    for (membername, award, clubname, awarddate) in curs.fetchall():
        Award(membername, award, clubname, awarddate)
        

            
    print '<h3>Member Educationals %s</h3>' % timestamp
    print '<p>Congratulations to the following Toastmasters for reaching one or more of their educational goals %s.  Will we see YOUR name here next?</p>' % timestamp
    print '<p>Achievements not shown here can be found on the Toastmasters International'
    print '<a href="http://reports.toastmasters.org/reports/dprReports.cfm?r=3&d=%s&s=Date&sortOrder=1" target="_new">Educational Achievements Report</a>.</p>' % (parms.district)
    
    # Print the full-width version 
           
    print '<div class="moduletable hidden-phone">'
    print '<div class="custom hidden-phone">'
    print '<style scoped="scoped" type="text/css"><!-- table,th,td {border-collapse:collapse; vertical-align:top; padding:1px; padding-right: 4px; border:0.5px solid white; font-family:  Arial, sans-serif;font-size: 12px;} .awardname {background-color: #f2df74; font-size: 14pt; font-weight: bold; text-align: center; width: 100%;} td.awardname {border-left: 5px solid white; border-right: 5px solid white;}--></style>'

    print '<table>'

    for (caward, laward) in zip(commtrack, ldrtrack):
        print '  <tr>'
        print '    <td width="50%">'
        print '      <table width="100%">'
        printawards(awards, knownawards, caward)
        print '      </table>'
        print '    </td>'
        print '    <td width="50%">'
        print '      <table width="100%">'
        printawards(awards, knownawards, laward)
        print '      </table>'
        print '    </td>'
        print '  </tr>'

    print '</table>'   
    print '</div>'
    print '</div>'         
    
    # And now print the narrow version
    print '<div class="moduletable visible-phone">'
    print '<div class="custom visible-phone">'
    print '<style scoped="scoped" type="text/css"><!-- table,th,td {border-collapse:collapse; vertical-align:top; padding:1px; border:0.5px solid white; font-family: Arial, sans-serif;font-size: 12px;}  .awardname {background-color: #f2df74; font-size: 14pt; font-weight: bold; text-align: center;}--></style>'
    print '<table>'
    for k in commtrack:
        printawards(awards, knownawards, k)
    for k in ldrtrack:
        printawards(awards, knownawards, k)
    print '</table>'
    print '</div>'
    print '</div>'

        
    cmd = makeCongratulations(count, parms.district, timestamp, parms)
    subprocess.call(' '.join(cmd),shell=True)
        