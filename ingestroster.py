#!/usr/bin/env python
""" Ingest the roster into the database.  Completely replaces the
    roster table every time. """

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.
from __future__ import print_function

import dbconn, tmutil, sys, os, xlrd, re, csv, codecs
from datetime import datetime

import tmglobals
globals = tmglobals.tmglobals()


### Insert classes and functions here.  The main program begins in the "if" statement below.


def normalizefieldnames(fields):
    # ('#' -> 'num', ' ID' -> 'num', lowercase, no spaces or special chars)
    # ('Membership Begin' -> 'termbegindate', 'Membership End' -> 'termenddate')
    # ('middle' -> 'middlename')
    fieldnames = []
    for f in fields:
        f = f.lower().strip().replace('#', 'num')
        f = f.replace(' id', 'num')
        f = f.replace('membership begin', 'termbegindate')
        f = f.replace('membership end', 'termenddate')
        f = f.replace('original join date', 'joindate')
        if f == 'middle':
            f = 'middlename'
        f = re.sub(r'[^a-zA-z0-9]+','',f)
        fieldnames.append(f)
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
 

    
    # Handle parameters
    import tmparms
    parms = tmparms.tmparms()
    parms.add_argument('roster', type=str, nargs=1, help='Name of the roster file')
    
    # Do global setup
    globals.setup(parms)
    conn = globals.conn
    curs = globals.curs
    
    parms.roster = parms.roster[0]

    
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
        
        # The file might be in UTF-8 or Latin-1 - the only way to find out is to
        #    read the whole thing as UTF-8 and see
        
        encoding = 'utf-8'
        tester = UTF8Recoder(csvfile, encoding=encoding)
        try:
            while tester.next():
                pass
        except StopIteration:
            pass
        except UnicodeDecodeError:
            encoding = 'latin-1'
            
        print('Roster encoding seems to be %s' % encoding)
        csvfile.seek(0)  # Back to the beginning of the file
        reader = UnicodeReader(csvfile, encoding=encoding)

        # Skip any prefatory lines in the file until we get to one
        #   with 'District', 'Division', and 'Area' in it.  That will
        #   be the line defining the fieldnames
        for fieldline in reader:
            fieldnames = normalizefieldnames(fieldline)
            if 'district' in fieldnames and \
               'division' in fieldnames and \
               'area' in fieldnames:
                break
        # Now, we can proceed
        fieldnames.append('fullname')
        ifirstname = fieldnames.index('firstname')
        imiddle = fieldnames.index('middlename')
        ilastname = fieldnames.index('lastname')
        datecols = [cname for cname in fieldnames if cname.endswith('date')]
        idates = [fieldnames.index(cname) for cname in datecols]
        ijoin = fieldnames.index('joindate')
        itermbegin = fieldnames.index('termbegindate')
        
        format = '%Y-%m-%d'
        # And get the values
        for row in reader:
            # Convert dates
            # Watch out for missing join date - use term start if so
            if not row[ijoin].strip():
                row[ijoin] = row[itermbegin]
            for col in idates:
                try:
                    row[col] = datetime.strptime(row[col], format)
                except ValueError as e:
                    format = '%m/%d/%Y'
                    try:
                        row[col] = datetime.strptime(row[col], format)
                    except Exception as e:
                        print(e)
                        print(row[col])
                        print(row)
                        sys.exit(1)
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
        elif f.endswith('date'):
            declare.append(f + ' DATE')
        else:
            declare.append(f + ' VARCHAR(100)')
        

    create = 'CREATE TABLE roster \n(%s,\n INDEX (clubnum, fullname))' % ',\n'.join(declare)
    
    # And create the table (dropping an old one if it exists)
    curs.execute('DROP TABLE IF EXISTS roster')
    curs.execute(create)
    
    # And now, populate the table
    valuepart = ','.join(['%s']*len(fieldnames))
    
    print(curs.executemany('INSERT INTO roster VALUES (' + valuepart + ')', values), 'members found.')
    conn.commit()
