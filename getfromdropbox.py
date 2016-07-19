#!/usr/bin/env python2.7
""" Get a file from Dropbox 

Input:  Dropbox Access Token
        Directory in Dropbox to examine
        Acceptable file extensions
        Dropbox cursor (optional)

Output: Updated Dropbox cursor
        Name of latest acceptable file in Dropbox (None if no changes)
        Filetime of latest acceptable file in Dropbox (None if no changes)
        Filelike object with content of latest acceptable file in Dropbox (None if no changes)

"""

import dropbox, os.path, requests
from dropbox.exceptions import ApiError, AuthError
from datetime import datetime

class Output:
    def __init__(self):
        self.cursor = None
        self.filename = None
        self.filetime = None
        self.file = None
        self.error = None
        
    def __repr__(self):
        return 'cursor: %s\nfilename: %s\nfiletime: %s\nerror: %s\n\n%s' % (self.cursor, self.filename, self.filetime, self.error, self.content)

def getDropboxFile(token, directory, extensions, cursor=None):
    """ token is a Dropbox access token
        directory is the path to examine (ignored if cursor is not None)
        extensions is a list of extensions to consider; empty means any extension
        cursor is the state cursor from a previous execution; if omitted, examines all files """
    dbx = dropbox.Dropbox(token)
    output = Output()
    
    # Make sure we have a proper token
    try:
        dbx.users_get_current_account()
    except AuthError as err:
        output.error = "ERROR: Invalid access token; try re-generating an access token from the app console on the web."
        return output
        
    # Set up to iterate through Dropbox folder
    latestfile = None
    latesttime = datetime.min
    live = True
    if extensions:
        extensions = ['.' + e.lower().replace('.','') for e in extensions]
    fileid = None
    
    while live:
        # Get information from Dropbox
        if cursor:
            result = dbx.files_list_folder_continue(cursor)
        else:
            result = dbx.files_list_folder(directory)
        
        # Set up for next iteration if need be
        live = result.has_more
        cursor = result.cursor
        
        for f in result.entries:
            path = f.path_lower
            ext = os.path.splitext(path)[1]
            if not extensions or ext in extensions:
                try:
                    if f.server_modified > latesttime:
                        latesttime = f.server_modified
                        latestfile = f.path_display
                        fileid = f.id
                except AttributeError:
                    pass
        
    output.cursor = cursor
    output.filename = latestfile
    output.filetime = latesttime
    
    # If we found a file, get it
    if output.filename:
        output.file = dbx.files_download(fileid)[1].raw
        
    return output
    
    
if __name__ == "__main__":
    import tmutil, tmparms, sys
    tmutil.gotodatadir()
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--verbose', '-v', action='count')
    parms.add_argument('--directory', dest='directory', default='')
    parms.add_argument('--extensions', dest='extensions', type=str, nargs='+')
    parms.add_argument('--outfile', dest='outfile', default='-')
    parms.add_argument('--outdir', dest='outdir', default='')
    parms.add_argument('--token', dest='token')
    # Add other parameters here
    parms.parse() 
    
    


    output = getDropboxFile(parms.token, parms.directory, parms.extensions)

    if parms.outfile == '-':
        outfile = sys.stdout
    else:
        if parms.outdir:
            parms.outdir = os.path.expanduser(parms.outdir)
            print parms.outdir
        outfn = os.path.join(parms.outdir, output.filename[1:] if parms.outfile == '+' else parms.outfile)
        print outfn
        outfile = open(outfn, 'w')
    outfile.write(output.file.read())
    

            
        
        
        

