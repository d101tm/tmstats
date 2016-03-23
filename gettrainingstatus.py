#!/usr/bin/env python2.7
""" If there's a new HTML file in the Webmaster's training directory,
    get it (if more than one, only get the latest).
    Otherwise, exit with a status of 1. """

import dropbox
import os.path
from datetime import datetime
import sys
from tmutil import gotodatadir


# temphackfix

from dropbox.rest import urllib3
urllib3.disable_warnings()

state_file = 'trainingstate.txt'
appinfo_file = 'trainingtokens.txt'

gotodatadir()  # Ensure we are in the data directory


def authorize():
    appinfo = open(appinfo_file,'r')
    for l in appinfo.readlines():
        (name, value) = l.split(':',1)
        name = name.strip().lower()
        value = value.strip()
        if name == 'app key':
            appkey = value
        elif name == 'app secret':
            appsecret = value
    appinfo.close()
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(appkey, appsecret)
    # Have the user sign in and authorize this token
    authorize_url = flow.start()
    print '1. Go to: ' + authorize_url
    print '2. Click "Allow" (you might have to log in first)'
    print '3. Copy the authorization code.'
    code = raw_input("Enter the authorization code here: ").strip()
    token, user_id = flow.finish(code)
    out = open(state_file, 'w')
    out.write('oauth2:%s\n' % token)
    out.close()
    return token


token = None
delta_cursor = None
try:
    tokinfo = open(state_file, 'r')
    for l in tokinfo.readlines():
        (name, value) = l.strip().split(':')
        if name == 'oauth2':
            token = value
        elif name == 'delta_cursor':
            delta_cursor = value
    tokinfo.close()
except IOError:
    pass
if not token:
    token = authorize()

# If we get here, we are authorized.
client = dropbox.client.DropboxClient(token)

# The only files we care about are in the training directory in Dropbox
path = '/training'

has_more = True
lastfile = None
lasttime = datetime.min   # For easy comparisons

while has_more:
    delta = client.delta(delta_cursor, path)   # See if anything has happened

    # No matter what, we want to write the cursor out to the state file

    tokinfo = open(state_file, 'w')
    tokinfo.write('oauth2:%s\ndelta_cursor:%s\n' % (token, delta['cursor']))
    tokinfo.close()

    # Be ready for 'has_more', unlikely though it is:
    has_more = delta['has_more']
    delta_cursor = delta['cursor']

    # All we care about is changes to .html or .htm files.  
    for (filename, fileinfo) in delta['entries']:
        if fileinfo:
            print filename
        ext = os.path.splitext(filename)[1]
        if fileinfo and ext in ['.htm', '.html']:
            # We care about HTML files, but only ones which exist.
            # We only want to keep the very latest HTML file.
            # We assume consistency in timezone from Dropbox...
            fileinfo['modified'] = ' '.join(fileinfo['modified'].split()[1:5])
            filetime = datetime.strptime(fileinfo['modified'], "%d %b %Y %H:%M:%S")
            if (filetime > lasttime):
                lastfile = filename
                lasttime = filetime


# OK, if any HTML files were updated, we have the name of the latest in 
# 'lastfile'.  Go get it.

if lastfile:
    outfile = open('latesttraining.html', 'wb')
    with client.get_file(lastfile) as f:
        outfile.write(f.read())
    outfile.close()
    with open('trainingfileinfo.txt', 'wb') as outfile:
        outfile.write('%s\n' % (lastfile))
    sys.exit(0)

# If we get here, nothing has happened.  Exit RC=1
sys.exit(1)

