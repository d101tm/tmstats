#!/usr/bin/env python
""" Ingest the roster into the database.  Completely replaces the
    roster table every time. """

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os, xlrd, re, csv, codecs


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)

### Insert classes and functions here.  The main program begins in the "if" statement below.


def normalizefieldnames(fields):
    # ('#' -> 'num', lowercase, no spaces or special chars)
    fieldnames = [f.strip().lower().replace('#','num') for f in fields]
    fieldnames = [re.sub(r'[^a-zA-z0-9]+','',f) for f in fieldnames]
    return fieldnames
    
        
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

if __name__ == "__main__":
 
    import tmparms
    from tmutil import gotodatadir
    gotodatadir()
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('roster', type=str, nargs=1, help='Name of the roster file')
    parms.add_argument('--quiet', '-q', action='count')
    # Add other parameters here
    parms.parse() 
    
    parms.roster = parms.roster[0]
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    filetype = os.path.splitext(parms.roster)[1].lower()
    values = []
    
    if filetype in ['.xls', '.xlsx']:
        # Open the Excel file
        book = xlrd.open_workbook(parms.roster)
        sheet = book.sheet_by_index(0)

        # Get the field names and normalize them; find the name columns
        fieldnames = normalizefieldnames(sheet.row_values(0))
        fieldnames.append('fullname')
        ifirstname = fieldnames.index('firstname')
        imiddle = fieldnames.index('middle')
        ilastname = fieldnames.index('lastname')
    
        # And get the values
        for row in xrange(1, sheet.nrows):
            values.append(sheet.row_values(row))
            # And add the fullname
            values[-1].append(('%s, %s %s' % (row[ilastname],row[ifirstname],row[imiddle])).strip())
            
    
    elif filetype in ['.csv']:
        csvfile = open(parms.roster, 'rbU')
        reader = UnicodeReader(csvfile, encoding='Latin-1')

        # Get the field names and normalize them; find the name columns
        fieldnames = normalizefieldnames(reader.next())
        fieldnames.append('fullname')
        ifirstname = fieldnames.index('firstname')
        imiddle = fieldnames.index('middle')
        ilastname = fieldnames.index('lastname')
        
        
        # And get the values
        for row in reader:
            values.append(row)
            # And add the fullname
            values[-1].append(('%s, %s %s' % (row[ilastname],row[ifirstname],row[imiddle])).strip())
        csvfile.close()
    
    # Now, convert the field names into a SQL table declaration.  
    # add "fullname" at the end
    declare = []
    for f in fieldnames:
        if f.endswith('num'):
            declare.append(f + ' INT')
        else:
            declare.append(f + ' VARCHAR(100)')
        

    create = 'CREATE TABLE roster \n(%s,\n INDEX (clubnum, fullname))' % ',\n'.join(declare)
    
    # And create the table (dropping an old one if it exists)
    curs.execute('DROP TABLE IF EXISTS roster')
    curs.execute(create)
    
    # And now, populate the table
    valuepart = ','.join(['%s']*len(fieldnames))
    
    print curs.executemany('INSERT INTO roster VALUES (' + valuepart + ')', values), 'members found.'
    conn.commit()
