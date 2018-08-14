#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Send mail congratulating award recipients. """

import dbconn, tmutil, sys, os, yaml
import tmparms, os, sys, argparse, smtplib, time
from tmutil import cleandate
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from awardinfo import Awardinfo as info

import tmglobals
globals = tmglobals.tmglobals()

from collections.abc import Iterable


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print(' '.join(args), file=file)

### Insert classes and functions here.  The main program begins in the "if" statement below.
                  
fullawardnames = info.lookup
                  
paras = ['The communication and leadership skills you have gained will be of lifelong benefit.  Our Toastmasters Educational Program is also a lifelong learning process, as communication and leadership skills must be practiced!',
         'Please email us if you have questions about the educational program.  We are here to help.  If you prefer a phone call, please send us your phone number and indicate the best time to call you.',
         'Good luck as you journey forward on the educational award path!',
         'Sincerely,',
         'Pavan Datla\nProgram Quality Director\nDistrict 101 Toastmasters']


def flatten(l):
    ### From http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, str):
            for sub in flatten(el):
                yield sub
        else:
            yield el



def fmtto72(s):
    words = s.split()
    lines = []
    l = ''
    for w in words:
        if len(l) + len(w) > 72:
            lines.append(l.rstrip())
            l = ''
        l += w + ' '
    if l:
        lines.append(l.rstrip())
    return '\n'.join(lines)
        
def sendreport(report):
    msg = MIMEMultipart('alternative')
    firstdate = report[0].awardnicedate
    lastdate = report[-1].awardnicedate
    if (firstdate == lastdate):
        subject = 'Award Congratulations for %s' % firstdate
    else:
        subject = 'Award Congratulations for %s - %s' % (firstdate, lastdate)
    msg['Subject'] = subject
    msg['From'] = parms.sender
    to = list(flatten([parms.replyto]))
    msg['To'] = ', '.join(to)
    plain = 'You need to use an HTML-capable mail client to read this note.'
    msg.attach(MIMEText(plain, 'plain'))
    html = ['<html><head>']
    html.append("""
    <style type="text/css">


            html {font-family: Arial, "Helvetica Neue", Helvetica, Tahoma, sans-serif;
                  font-size: 77%;}

            table {width: 75%; font-size: 14px; border-width: 1px; border-spacing: 1px; border-collapse: collapse; border-style: solid;}
            td, th {border-color: black; border-width: 1px;  vertical-align: middle;
                padding: 2px; padding-right: 5px; padding-left: 5px; border-style: solid;}
            </style>
    """)
    html.append('</head><body>')
    
    html.append('<p>Award congratulations:</p>')
    html.append('<table>')
    html.append('<tbody')
    for r in report:
        html.append(r.__repr__())
    html.append('</tbody>')
    html.append('</table>')
    html.append('</body></html>')
    msg.attach(MIMEText('\n'.join(html), 'html'))
    sendmail(msg, to, [], [], parms)
 
    

def sendletter(email, firstname, letterinfo, parms):
    if not email:
        print('No email for', letterinfo[0].fullname)
        return

    # Create message container (multipart/alternative)
    
    awardnicedate = letterinfo[0].awardnicedate
    msg = MIMEMultipart('alternative')
    subject = 'Congratulations on your Toastmaster Educational award%s on %s' % ('s' if len(letterinfo) > 1 else '', awardnicedate)
    
    msg['Subject'] = subject
    msg['From'] = parms.sender

    # Flatten recipient lists and insert to and cc into the message header
    to = list(flatten([email]))
    cc = list(flatten(parms.cc))
    bcc = list(flatten(parms.bcc))

    msg['To'] = ', '.join(to)
    msg['cc'] = ', '.join(cc)

    if parms.replyto:
        replyto = list(flatten([parms.replyto]))
        msg['Reply-To'] = ', '.join(replyto)


    # Now, create the plain text part.
    plain = ['Dear ' + firstname + ',', '']
    if len(letterinfo) > 1:
        plain.append(fmtto72('Congratulations on achieving %d awards on %s:' % (len(letterinfo), awardnicedate)))
        plain.append('')
        for l in letterinfo:
            plain.append('  %s (%s)' % (fullawardnames[l.award], l.award))
    else:
        l = letterinfo[0]
        plain.append(fmtto72('Congratulations on achieving the %s (%s) award on %s.' % (fullawardnames[l.award], l.award, l.awardnicedate)))
    for p in paras:
        plain.append('')
        for partial in p.split('\n'):
            plain.append(fmtto72(partial))
    msg.attach(MIMEText('\n'.join(plain), 'plain'))
    
    # Now, create the HTML part.
    html = ['<html><head></head><body>']
    html.append('<p>Dear ' + firstname + ',</p>')
    if len(letterinfo) > 1:
        html.append('<p>Congratulations on achieving %d awards on %s:</p>' % (len(letterinfo), awardnicedate))
        html.append('<ul>')
        for l in letterinfo:
            html.append('<li>%s (%s)</li>' % (fullawardnames[l.award], l.award))
        html.append('</ul>')
    else:
        l = letterinfo[0]
        html.append('<p>Congratulations on achieving the %s (%s) award on %s.</p>' % (fullawardnames[l.award], l.award, l.awardnicedate))
    for p in paras:
        html.append('<p>%s</p>' % p.replace('\n', '<br />'))
    html.append('</body></html>')
    msg.attach(MIMEText('\n'.join(html), 'html'))
    sendmail(msg, to, cc, bcc, parms)

        
 
def sendmail(msg, to, cc, bcc, parms):

    # Convert the message to string format:
    finalmsg = msg.as_string()
 
    # And send the mail.
    targets = []
    if to:
        targets.extend(to)
    if cc:
        targets.extend(cc)
    if bcc:
        targets.extend(bcc)


    # Connect to the mail server:

    mailconn = smtplib.SMTP_SSL(parms.mailserver, parms.mailport)
    mailconn.login(parms.sender, parms.mailpw)

    # and send the mail
    mailconn.sendmail(parms.sender, targets, finalmsg)

class Award:
    def __init__(self, fullname, firstname, award, awarddate, email, clubname, id):
        self.fullname = fullname
        self.firstname = firstname
        self.award = award
        self.awarddate = awarddate
        self.awardnicedate = awarddate.strftime('%B %d, %Y')
        self.email = email
        self.clubname = clubname
        self.id = id
        
    def __repr__(self):
        return '<tr><td>' + '</td><td>'.join([self.award, self.awardnicedate, self.fullname, self.email, self.clubname]) + '</td></tr>'


if __name__ == "__main__":

    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count', default=0)
    parms.parser.add_argument("--mailYML", dest='mailyml', default="awardmail.yml")
    parms.parser.add_argument("--mailserver", dest='mailserver')
    parms.parser.add_argument("--mailpw", dest='mailpw')
    parms.parser.add_argument("--mailport", dest='mailport')
    parms.parser.add_argument("--sender", dest='sender')
    parms.parser.add_argument("--reply-to", dest='replyto')
    parms.parser.add_argument("--to", dest='to', nargs='+', default=[], action='append')
    parms.parser.add_argument("--cc", dest='cc', nargs='+', default=[], action='append')
    parms.parser.add_argument("--bcc", dest='bcc', nargs='+', default=[], action='append')
    parms.add_argument('--fromdate', default='yesterday', dest='fromdate', help="First date for congrats.")
    parms.add_argument('--todate', default='yesterday', dest='todate', help="Last date for congrats")
    parms.add_argument('--dryrun', action='store_true', help="Don't send letters; do say who they'd go to.")
    
    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    
    parms.fromdate = cleandate(parms.fromdate)
    parms.todate = cleandate(parms.todate)
    
    # If there are mail-related values not yet resolved, get them from the mailYML file.
    ymlvalues = yaml.load(open(parms.mailyml, 'r'))

    for name in ['mailserver', 'mailpw', 'mailport', 'from', 'replyto']:
        if name not in parms.__dict__ or not parms.__dict__[name]:
            parms.__dict__[name] = ymlvalues[name]
    parms.sender = parms.__dict__['from']    
    

    
    report = []
    
    # Find anyone who earned one or more awards in the time period in question      

    curs.execute("SELECT awarddate, membername FROM awards WHERE awarddate >= %s AND awarddate <= %s AND acknowledged = 0 AND award != 'LDREXC' GROUP BY awarddate, membername ORDER BY awarddate, membername", (parms.fromdate, parms.todate))
    targetlist = curs.fetchall()
    
    # Now, for each person/date, get all of their info and generate the letter:
    for (awarddate, membername) in targetlist:
        curs.execute("SELECT award, clubname, clubnumber, id FROM awards WHERE awarddate = %s and membername = %s AND acknowledged = 0 AND award != 'LDREXC'", (awarddate, membername))
        awardinfo = curs.fetchall()
        theclubs = ','.join(['%d' % item[2] for item in awardinfo])
        # Get the person's information
        firstname = ''
        curs.execute("SELECT firstname, emailaddress FROM roster WHERE clubnum IN (" + theclubs + ") AND fullname = %s", (membername.replace('"', ''),))
        email = ''
        for (name, mail) in curs.fetchall():
            if email == '':
                email = mail
            firstname = name
            
        letterinfo = []
        for item in awardinfo:
            award = Award(membername, firstname if firstname else '<b>Not in roster</b>', item[0], awarddate, email if email else '<b>No email found</b>', item[1], item[3])
            report.append(award)
            letterinfo.append(award)    
            
        if not parms.dryrun:
            sendletter(email, firstname, letterinfo, parms)
            # And mark this one as acknowledged
            for l in letterinfo:
                curs.execute('UPDATE awards SET acknowledged = 1 WHERE id = %s', (l.id,))
            conn.commit()
            time.sleep(5)
        else:
            print('Would send congrats to %s at %s for:' % (membername, email))
            for award in letterinfo:
                print('   %s (%s)' % (award.award, fullawardnames[award.award]))
        
    if len(report) > 0:
        if parms.dryrun:
            dump = []
            widths = []
            for item in report:
                parts = repr(item).replace('<tr>','').replace('</tr>','').replace('</td>','').split('<td>')
                if not widths:
                    widths = [0] * len(parts)
                widths = [max(widths[i], len(parts[i])) for i in range(len(parts))]
                dump.append(parts)
            fmtstr = ' | ' + ' | '.join(['%%%ds' % w for w in widths]) +  ' | '
            for line in dump:
                print((fmtstr % tuple(line)))
        else:
            sendreport(report)
        

    
    
