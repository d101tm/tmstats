#!/usr/bin/python
""" Send an email contained in a file. """
import tmparms, os, sys, argparse, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Make it easy to run under TextMate
if 'TM_DIRECTORY' in os.environ:
    os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
reload(sys).setdefaultencoding('utf8')

# Handle parameters
parms = tmparms.tmparms()
parms.parser = argparse.ArgumentParser(description="Process parameters for sendmail.py")   # We want the useful functions, but not the default parms
parms.parser.add_argument('YMLfile', help="YML file with information such as mail user, mail server...", default="tmmail.yml", nargs='?')
parms.parser.add_argument("--htmlfile", dest='htmlfile')
parms.parser.add_argument("--textfile", dest='textfile')
parms.parser.add_argument("--mailserver", dest='mailserver')
parms.parser.add_argument("--mailpw", dest='mailpw')
parms.parser.add_argument("--mailport", dest='mailport')
parms.parser.add_argument("--from", dest='from')
parms.parser.add_argument("--to", dest='to', nargs='+', default='')
parms.parser.add_argument("--cc", dest='cc', nargs='+', default='')
parms.parser.add_argument("--bcc", dest='bcc', nargs='+', default='')
parms.parser.add_argument("--subject", dest='subject', default='Mail from the District Webmaster')
parms.parse()

parms.sender = parms.__dict__['from']  # Get around reserved word


# Create message container (multipart/alternative)

msg = MIMEMultipart('alternative')
msg['Subject'] = parms.subject
msg['From'] = parms.sender


# Resolve items which are repeatable by converting the list to comma-separated items
if not isinstance(parms.to, basestring):
    parms.to = ', '.join(parms.to)
msg['To'] = parms.to
if not isinstance(parms.cc, basestring):
    parms.cc = ', '.join(parms.cc)
msg['cc'] = parms.cc
if not isinstance(parms.bcc, basestring):
    parms.bcc = ', '.join(parms.cc)
    


# Now, create the parts.
if parms.textfile:
    part1 = MIMEText(open(parms.textfile, 'r').read(), 'plain')
    msg.attach(part1)
else:
    msg.attach(MIMEText('This is a multipart message with no plain-text part', 'plain'))
    
if parms.htmlfile:
    part2 = MIMEText(open(parms.htmlfile, 'r').read(), 'html')
    msg.attach(part2)
    

# Convert the message to string format:
finalmsg = msg.as_string()


# And send the mail.
targets = []
if parms.to:
    targets.append(parms.to)
if parms.cc:
    targets.append(parms.cc)
if parms.bcc:
    targets.append(parms.bcc)
allto = ', '.join(targets)


# Connect to the mail server:
mailconn = smtplib.SMTP(parms.mailserver, parms.mailport)
mailconn.login(parms.sender, parms.mailpw)

# and send the mail
mailconn.sendmail(parms.sender, allto, finalmsg)


