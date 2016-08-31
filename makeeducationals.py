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
        return '<tr class="awardline"><td class="awardmember">%s</td><td class="awardclub">%s</td></tr>' % (self.membername, self.clubname)

def printawards(awards, knownawards, k):
    if k in awards:
        print '[et_pb_tab title="%s" tab_font_select="default" tab_font="||||" tab_line_height="2em" tab_line_height_tablet="2em" tab_line_height_phone="2em" body_font_select="default" body_font="||||" body_line_height="2em" body_line_height_tablet="2em" body_line_height_phone="2em"]' % knownawards[k]
        print '<table>'
        print '<tr><td class="awardname" colspan="2">%s</td></tr>' % knownawards[k]
        for each in sorted(awards[k], key=lambda x:x.key):
            print each
        print '</table>'
        print '[/et_pb_tab]'


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
    group.add_argument('--since', type=str, default='30',
            help='How long ago or first date to look for awards.')
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
        firstdate = datetime.datetime.strptime(tmutil.cleandate(parms.since), '%Y-%m-%d')
        clauses.append("awarddate >= '%s'" % firstdate.strftime('%Y-%m-%d'))
        timestamp = 'since ' + firstdate.strftime('%B ') + '%d' % firstdate.day


    if not parms.include_hpl:
        clauses.append('award != "LDREXC"')

    if parms.district:
        clauses.append('district = %s' % parms.district)

    curs.execute("SELECT COUNT(DISTINCT membername) FROM awards WHERE " + ' AND '.join(clauses))
    count = curs.fetchone()[0]

    curs.execute("SELECT membername, award, clubname, awarddate FROM awards WHERE " + ' AND '.join(clauses))
    for (membername, award, clubname, awarddate) in curs.fetchall():
        Award(membername, award, clubname, awarddate)



    print '<h3>Member Educationals %s</h3>' % timestamp
    print '<p>Congratulations to the following Toastmasters for reaching one or more of their educational goals %s.  Will we see YOUR name here next?</p>' % timestamp
    print '<p>Achievements not shown here can be found on the Toastmasters International <a href="http://reports.toastmasters.org/reports/dprReports.cfm?r=3&d=%s&s=Date&sortOrder=1" target="_new">Educational Achievements Report</a>.</p>' % (parms.district)

    # And now print the awards themselves.

    print '<div class="awardstable">'
    print '[et_pb_tabs admin_label="awards" use_border_color="off" border_color="#ffffff" border_style="solid" tab_font_size="18"]'
    for k in commtrack:
        printawards(awards, knownawards, k)
    for k in ldrtrack:
        printawards(awards, knownawards, k)
    print '[/et_pb_tabs]'
    print '</div>'


    cmd = makeCongratulations(count, parms.district, timestamp, parms)
    subprocess.call(' '.join(cmd),shell=True)
