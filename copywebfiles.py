#!/usr/bin/env python2.7
""" Copy new files from a Dropbox directory (and subdirectories) to a target folder. """

import dropbox
import os.path
from datetime import datetime
import sys
from tmutil import gotodatadir


state_file = 'copystate.txt'
appinfo_file = 'copytokens.txt'

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
        if ':' in l:
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

# The only files we care about are in the roster directory in Dropbox
path = '/D101 Web Files'
localpath = os.path.expanduser('~/files/')


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

    # All we care about is changes to specific filetypes.  We recurse if needed.  We don't process deletions. 
    okexts = ['.xls', '.xlsx', '.doc', '.docx', '.ppt', '.pptx', '.pdf']
    for (filename, fileinfo) in delta['entries']:
        if fileinfo:
            print filename
        # Normalize filename
        normalizedfilename = filename.lower().replace(' ','-')
        ext = os.path.splitext(filename)[1].lower()
        if fileinfo and ext in okexts:
            localfn = normalizedfilename[1+len(path):]
            outfn = os.path.join(localpath,localfn)
            outpath = os.path.split(outfn)[0]
            print 'copying', filename, 'to', outfn
            if not os.path.isdir(outpath):
                print 'creating', outpath
                os.makedirs(outpath)
            
                
            outfile = open(outfn, 'wb')
            with client.get_file(filename) as f:
                outfile.write(f.read())
            outfile.close()


