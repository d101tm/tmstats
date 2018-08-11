#!/usr/bin/env python3
""" Get the latest file with specified extensions from a Dropbox directory """



import dropbox, os.path, requests, sys
from dropbox.exceptions import ApiError, AuthError
from datetime import datetime

import tmglobals
globals = tmglobals.tmglobals()

# Patch around SSL problems in outdated versions of Python (*cough* HostGator *cough*)
if sys.hexversion < 0x02070900:
    from requests.packages import urllib3
    urllib3.disable_warnings()

class Output:
    """ self.cursor:  Updated cursor from Dropbox (you can store this for delta processing)
        self.filename:  Name of the most recent file found (only the filename; path is stripped)
        self.filetime:  Time and date last modified on Dropbox server (datetime.datetime)
        self.file:  Filelike object that can be used to read the file from Dropbox as raw bytes
        self.error:  An error message if errors occur (currently only in authentication)
        self.warning:  A warning if no file is found
    """
    
    
    def __init__(self):
        self.cursor = None
        self.filename = None
        self.filetime = None
        self.file = None
        self.error = None
        self.warning = None
    
    def __repr__(self):
        return 'cursor: %s\nfilename: %s\nfiletime: %s\nerror: %s\n\n%s' % (self.cursor, self.filename, self.filetime, self.error, self.content)

def getDropboxFile(token, directory, extensions, cursor=None):
    """ token is a Dropbox access token
        directory is the path to examine (ignored if cursor is not None)
        extensions is a list of extensions to consider; empty means any extension
        cursor is the state cursor from a previous execution; if omitted, examines all files
        
        Returns an object of class Output """
    
    output = Output()
    
    if not token:
        output.error = "ERROR: No access token provided; try generating one from the app console on the web."
        return output
    
    dbx = dropbox.Dropbox(token)
    
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
    fileid = None
    had_cursor = cursor
    
    # Normalize extensions
    if extensions:
        extensions = ['.' + e.lower().replace('.','') for e in extensions]
    
    # Normalize directory
    directory = directory.strip()
    if directory and directory[0] != '/':
        directory = '/' + directory
    
    
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
                        latestfile = f.path_lower
                        fileid = f.id
                except AttributeError as e:
                    print(e)
                    pass
    
    output.cursor = cursor
    
    
    # If we found a file, set output appropriately
    if latestfile:
        output.filename = os.path.split(latestfile)[1]
        output.filetime = latesttime
        output.file = dbx.files_download(fileid)[1].raw
    else:
        output.warning = 'No %sfile found' % ('changed ' if had_cursor else '')
        if extensions:
            if len(extensions) == 1:
                s = 'with extension ' + extensions[0]
            else:
                s = 'with extension of ' + ', '.join(extensions[:-1])
                if len(extensions) > 2:
                    s += ','
                s += ' OR ' + extensions[-1]
            output.warning += ' ' + s
    
    return output


if __name__ == "__main__":
    import tmparms
    
    
    # Handle parameters
    parms = tmparms.tmparms(description=__doc__)
    parms.add_argument('--verbose', '-v', action='count', help="Increase verbosity of output", default=0)
    parms.add_argument('--directory', dest='directory', default='', help="Dropbox directory to examine")
    parms.add_argument('--extensions', dest='extensions', metavar="EXTENSION", type=str, nargs='+', action="append", help="extensions to consider")
    parms.add_argument('--outfile', dest='outfile', default='-', help="filename for output file; specify '-' for stdout; specify '+' to use the name of the file found; specify 'something.+' to keep the extension of the file but force the name to be 'something'.  File is not changed if no file is found.")
    parms.add_argument('--namefile', dest='namefile', default=None, help='filename into which to write the name of the output file.  Not changed if nothing is written.')
    parms.add_argument('--outdir', dest='outdir', default='', help="output directory for output file, especially useful if outfile is '+'")
    parms.add_argument('--dropboxtoken', dest='dropboxtoken', help="Dropbox access token")
    group = parms.add_mutually_exclusive_group()
    group.add_argument('--cursor', dest='cursor', default=None, help="Dropbox cursor")
    group.add_argument('--cfile', dest='cfile', default=None, help="Text file containing a Dropbox cursor; gets updated or created if required.")
    
    # Do global setup
    globals.setup(parms, connect=False)
    
    # Flatten extension in case it was specified many times
    if parms.extensions:
        e = []
        for element in parms.extensions:
            if isinstance(element, list):
                e.extend(element)
            else:
                e.append(element)
        
        parms.extensions = e
    
    
    if parms.cfile:
        parms.cursor = None       # If the file doesn't exist yet
        try:
            with open(parms.cfile, 'r') as f:
                parms.cursor = f.read().strip()
        except IOError:
            pass
    
    
    output = getDropboxFile(parms.dropboxtoken, parms.directory, parms.extensions, parms.cursor)
    
    if parms.cfile:
        with open(parms.cfile, 'w') as f:
            f.write(output.cursor)
    
    
    if parms.verbose >= 2:
        sys.stderr.write('cursor: %s\n' % output.cursor)
    
    if output.file:
        if parms.outfile == '-' or parms.outfile.strip() == '':
            outfile = sys.stdout.buffer
            if parms.namefile:
                with open(parms.namefile, 'w') as f:
                    f.write('')
        else:
            if parms.outdir:
                parms.outdir = os.path.expanduser(parms.outdir)
            
            if parms.outfile.endswith('.+'):
                # Construct filename, preserving the extension we found
                outfn = os.path.splitext(parms.outfile)[0] + os.path.splitext(output.filename)[1]
            elif parms.outfile == '+':
                # Preserve the filename we found
                outfn = output.filename
            else:
                # Use the name we were given
                outfn = parms.outfile
            
            outfn = os.path.join(parms.outdir, outfn)
            # Write as an absolute filename
            if parms.namefile:
                with open(parms.namefile, 'w') as f:
                    f.write(os.path.abspath(outfn))
            
            outfile = open(outfn, 'wb')  
        outfile.write(output.file.read())
        
        if parms.verbose:
            sys.stderr.write('Using %s, last modified at %s UTC\n' % (output.filename, output.filetime))
    else:
        if output.error:
            sys.stderr.write(output.error)
            sys.stderr.write('\n')
        if parms.verbose and output.warning:
            sys.stderr.write(output.warning)
            sys.stderr.write('\n')
        sys.exit(1)






