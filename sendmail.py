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

print msg

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


sys.exit()


def sendbadmail(b, info):
    print 'Sending error notice to', b
    message = MIMEText(''.join(info['badtext']))
    message['Subject'] = info['badsubj']
    message['From'] = info['from']
    message['To'] = b
    if 'cc' in info:
        message['cc'] = info['cc']
    info['s'].sendmail(info['from'], [b], message.as_string())
    if 'cc' in info:
        info['s'].sendmail(info['from'], [info['cc']], message.as_string())
    if 'bcc' in info:
        info['s'].sendmail(info['from'], [info['bcc']], message.as_string())



fvote = 'Field6'
fvalidation = 'Field8'
fname = 'Field10'
femail = 'Field13'
fields = (fvote, fvalidation, fname, femail)

enext = 0
c.execute ('SELECT MAX(highwater) FROM entries;')
results = c.fetchone()
try:
  highwater = 0 + results[0] 
except TypeError:
  highwater = 0

pagesize = 100
newvoters = {}
badvoters = {}

while enext <= ecount:

    entries = json.load(opener.open(formurl + '/entries.json?pageStart=%d&pageSize=%d' % (enext, pagesize)))['Entries']
    if not entries:
	break;

    enext += pagesize

    for e in entries:
        #print e
        (vote, validation, name, email) = [e[f].strip() for f in fields]
        if int(e['EntryId']) <= highwater:
          #print 'Already processed', e['EntryId'], name, email
          continue
        c.execute('SELECT first, last, title, "Club Name" as clubname, area, division, email, vote, confirmed FROM voters WHERE validation=?', (validation,))
        results = c.fetchall()
        if results:
            for res in results:
                (first, last, title, clubname, area, division, realemail, oldvote, confirmed) = res
                if confirmed and oldvote == vote:
                    continue  # Ignore votes already registered
                dbname = '%s %s' % (first, last)
                position = ' '.join((' %s%s %s %s' % (division, area, clubname, title)).split())
                print position, dbname, 'votes', vote
                # Normalize email addresses
                realemail = realemail.lower()
                email = email.lower()
                
                if realemail <> email:
                    print 'email mismatch: db has %s, entered %s' % (realemail, email)
                if oldvote and vote <> oldvote:
                    print 'vote change from %s to %s' % (oldvote, vote)
                    confirmed = False  # Need to confirm any changes
                c.execute('UPDATE voters SET vote = ? WHERE validation=?', (vote, validation))
                if not confirmed:
                    if validation not in newvoters:
                        newvoters[validation] = {'positions': set(), 'emails': set(),
                                 'validation': validation}
                    newvoters[validation]['positions'].add(position)
                    newvoters[validation]['emails'].add(email)
                    newvoters[validation]['emails'].add(realemail)
                              
                    badvoters.pop(realemail, None)  # A good vote overrides a bad one
        else:
            print 'Fail!', name, email, validation
            badvoters[email] = email
        highwater = max(highwater, int(e['EntryId']))

conn.commit()  # Commit votes

# If there were any validation fails, send out the error
for b in badvoters:
    sendbadmail(b, info)
    print 'error for', b
    time.sleep(8)       # Make Hostgator happy

# Now, send out emails to successful voters; every time we send an email,
# commit that it's been done.
for b in newvoters:
    print '_________________________________'
    print 'success for', b
    sendgoodmail(newvoters[b], info)
    c.execute('UPDATE voters SET confirmed = 1 WHERE validation = ?', (newvoters[b]['validation'],))
    conn.commit() # Commit this one
    time.sleep(8)       # Make Hostgator happy

# Finally, update the entry number
c.execute('INSERT INTO ENTRIES (highwater) VALUES (%d);' % highwater);

conn.commit()


conn.close()