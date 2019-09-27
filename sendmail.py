#!/usr/bin/env python3
""" Send an email contained in a file. """
import tmparms, os, sys, argparse, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

import tmglobals
myglobals = tmglobals.tmglobals()

from collections.abc import Iterable
def flatten(l):
    ### From http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, str):
            for sub in flatten(el):
                yield sub
        else:
            yield el


# Handle parameters
parms = tmparms.tmparms(description=__doc__, includedbparms=False)
parms.parser.add_argument("--htmlfile", dest='htmlfile')
parms.parser.add_argument("--textfile", dest='textfile')
parms.parser.add_argument("--mailserver", dest='mailserver')
parms.parser.add_argument("--mailpw", dest='mailpw')
parms.parser.add_argument("--mailport", dest='mailport')
parms.parser.add_argument("--from", dest='from')
parms.parser.add_argument("--to", dest='to', nargs='+', default=[], action='append')
parms.parser.add_argument("--cc", dest='cc', nargs='+', default=[], action='append')
parms.parser.add_argument("--bcc", dest='bcc', nargs='+', default=[], action='append')
parms.parser.add_argument("--subject", dest='subject', default='Mail from the District Webmaster')
parms.parser.add_argument("--section", dest='section', help='INI file section to use in addition to [common]')

myglobals.setup(parms, connect=False)
if parms.section:
    # Need to reparse to pick up proper defaults from the named section
    myglobals.setup(parms, connect=False, sections=parms.section)


parms.sender = parms.__dict__['from']  # Get around reserved word


# Create message container (multipart/alternative)

msg = MIMEMultipart('alternative')
msg['Subject'] = parms.subject
msg['From'] = parms.sender
msg['Date'] = formatdate(localtime=True)

# Flatten recipient lists and insert to and cc into the message header
parms.to = list(flatten(parms.to))
parms.cc = list(flatten(parms.cc))
parms.bcc = list(flatten(parms.bcc))
msg['To'] = ', '.join(parms.to)
msg['cc'] = ', '.join(parms.cc)




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
    targets.extend(parms.to)
if parms.cc:
    targets.extend(parms.cc)
if parms.bcc:
    targets.extend(parms.bcc)

# Connect to the mail server:
mailconn = smtplib.SMTP_SSL(parms.mailserver, parms.mailport)
mailconn.login(parms.sender, parms.mailpw)

# and send the mail
mailconn.sendmail(parms.sender, targets, finalmsg)


