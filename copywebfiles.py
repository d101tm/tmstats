#!/usr/bin/env python3
""" Copy new files from a Dropbox directory (and subdirectories) to a target folder. """

import dropbox, os.path, sys, time
from dropbox.exceptions import ApiError, AuthError
from datetime import datetime

epoch = datetime.utcfromtimestamp(0)
import tmglobals, tmparms

myglobals = tmglobals.tmglobals()
parms = tmparms.tmparms(description=__doc__)
parms.add_argument('--dropboxtoken', help='Dropbox access token')
parms.add_argument('--dropboxfolder', default='D101 Web Files', help='Dropbox folder to copy')
parms.add_argument('--outdir', default='${copydir}', help='Where to put new and updated files')
parms.add_argument('--baseurl', default='https://files.d101tm.org/', help='base URL for links')
parms.add_argument('--cursor', default=None, help='Dropbox cursor to use')
parms.add_argument('--cfile', default='${cursordir}/copywebfiles.txt', help='File containing Dropbox cursor; will be created/updated')
myglobals.setup(parms, connect=False)

if not parms.dropboxtoken:
    sys.stderr.write('ERROR: No access token provided.  Generate one from the app console on the web.')
    sys.exit(1)

# Access Dropbox; check to make sure we actually have access
dbx = dropbox.Dropbox(parms.dropboxtoken)
try:
    dbx.users_get_current_account()
except AuthError as err:
    sys.stderr.write("ERROR: Invalid access token; try re-generating an access token from the app console on the web.")
    sys.exit(2)

path = parms.dropboxfolder
if not path.startswith('/'):
    path = '/' + path
localpath = os.path.expandvars(parms.outdir)
linkpath = parms.baseurl
if not linkpath.endswith('/'):
    linkpath = linkpath + '/'

cursor = parms.cursor
if not parms.cursor and parms.cfile:
    # Try to get the cursor from the file
    try:
        with open(parms.cfile, 'r') as f:
            parms.cursor = f.read().strip()
    except IOError:
        pass  # It's OK not to have the file yet; we'll create it on output.


has_more = True

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
            
            # Copy the file
            outfile = open(outfn, 'wb')
            outfile.write(dbx.files_download(f.id)[1].raw.read())
            outfile.close()

            # Set its access and modified time to match Dropbox
            modtime = (f._client_modified_value - epoch).total_seconds()
            os.utime(outfn, (modtime, modtime))

    # Update the cursor file
    if parms.cfile:
        with open(parms.cfile, 'w') as f:
            f.write(cursor)

