#!/usr/bin/env python3
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
    print('1. Go to: ' + authorize_url)
    print('2. Click "Allow" (you might have to log in first)')
    print('3. Copy the authorization code.')
    code = input("Enter the authorization code here: ").strip()
    token, user_id = flow.finish(code)
    out = open(state_file, 'w')
    out.write('oauth2:%s\n' % token)
    out.close()
    return token


token = None
cursor = None
try:
    tokinfo = open(state_file, 'r')
    for l in tokinfo.readlines():
        if ':' in l:
            (name, value) = l.strip().split(':')
            if name == 'oauth2':
                token = value
            elif name in ['delta_cursor', 'cursor']:
                cursor = value
    tokinfo.close()
except IOError:
    pass
if not token:
    token = authorize()

# If we get here, we are authorized.
dbx = dropbox.Dropbox(token)

# The only files we care about are in the Web Files directory in Dropbox
path = '/D101 Web Files'
localpath = os.path.expanduser('~/files/')
linkpath = 'http://files.d101tm.org/'

has_more = True
lastfile = None
lasttime = datetime.min   # For easy comparisons

while has_more:
    if cursor:
        result = dbx.files_list_folder_continue(cursor)
    else:
        result = dbx.files_list_folder(path, recursive=True, include_deleted=False)
        

    # Set up for next iteration if need be
    has_more = result.has_more
    cursor = result.cursor




    # All we care about is changes to specific filetypes.  We recurse if needed.  We don't process deletions. 
    okexts = ['.xls', '.xlsx', '.doc', '.docx', '.ppt', '.pptx', '.pdf']
    for f in result.entries:
        if type(f) == dropbox.files.DeletedMetadata:
            continue  # Skip deleted files
        filename = f.path_lower
        # Normalize filename
        normalizedfilename = filename.lower().replace(' ','-')
        ext = os.path.splitext(filename)[1].lower()
        if ext in okexts:
            localfn = normalizedfilename[1+len(path):]
            outfn = os.path.join(localpath,localfn)
            outpath = os.path.split(outfn)[0]
            print('copying', filename, 'to', outfn)
            print('find it at %s%s' % (linkpath, localfn))
            if not os.path.isdir(outpath):
                print('creating', outpath)
                os.makedirs(outpath)
            
                
            outfile = open(outfn, 'wb')
            outfile.write(dbx.files_download(f.id)[1].raw.read())
            outfile.close()

    # Finally, update the state file

    tokinfo = open(state_file, 'w')
    tokinfo.write('oauth2:%s\ncursor:%s\n' % (token, cursor))
    tokinfo.close()
