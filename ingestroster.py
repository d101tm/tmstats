#!/usr/bin/python
""" Ingest the roster into the database.  Completely replaces the
    roster table every time. """

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os, xlrd, re


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)

### Insert classes and functions here.  The main program begins in the "if" statement below.

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('roster', type=str, nargs='?', default='latestroster.xlsx', help='Name of the roster file, default is %(default)s')
    parms.add_argument('--quiet', '-q', action='count')
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Open the Excel file
    book = xlrd.open_workbook(parms.roster)
    sheet = book.sheet_by_index(0)

    # Get the field names ('#' -> 'num', lowercase, no spaces or special chars)
    fields = sheet.row_values(0)
    fieldnames = [f.strip().lower().replace('#','num') for f in fields]
    fieldnames = [re.sub(r'[^a-zA-z0-9]+','',f) for f in fieldnames]
    
    # Now, convert the field names into a SQL table declaration.  
    declare = []
    for f in fieldnames:
        if f.endswith('num'):
            declare.append(f + ' INT')
        else:
            declare.append(f + ' VARCHAR(100)')

    create = 'CREATE TABLE roster \n(%s,\n INDEX (clubnum, membernum))' % ',\n'.join(declare)
    
    # And create the table (dropping an old one if it exists)
    curs.execute('DROP TABLE IF EXISTS roster')
    curs.execute(create)
    
    # And now, populate the table
    values = []
    for row in xrange(1, sheet.nrows):
        values.append(sheet.row_values(row))
    valuepart = ','.join(['%s']*len(fieldnames))
    print curs.executemany('INSERT INTO roster VALUES (' + valuepart + ')', values), 'members found.'
    curs.execute('ALTER TABLE roster ADD COLUMN fullname VARCHAR(100)')
    print ('UPDATE roster SET fullname = REPLACE(CONCAT(lastname, ", ", firstname, " ", middle), \'"\', "")')
    curs.execute('UPDATE roster SET fullname = REPLACE(CONCAT(lastname, ", ", firstname, " ", middle), \'"\', "")')
    conn.commit()
