#!/usr/bin/env python3
""" Ingest the roster into the database.  Completely replaces the
    roster table every time. """

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.


import dbconn, tmutil, sys, os, xlrd, re, csv, codecs
from datetime import datetime, date

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
        for row in range(1, sheet.nrows):
            values.append(sheet.row_values(row))
            # And add the fullname
            values[-1].append(('%s, %s %s' % (row[ilastname],row[ifirstname],row[imiddle])).strip())
            
    
    elif filetype in ['.csv']:
        # We have to be able to handle files in UTF-8 or Latin-1, so we
        #    try to read the whole thing as UTF-8 and if it fails, use
        #    Latin-1.  *sigh*
        
        encoding = 'utf-8'
        csvfile = open(parms.roster, 'r', encoding=encoding)
        try:
            line = next(csvfile)
            while line:
               line = next(csvfile)
        except StopIteration:
            pass
        except UnicodeDecodeError as e:
            # Close and reopen in latin-1
            csvfile.close()
            encoding = 'latin-1'
            csvfile = open(parms.roster, 'r', encoding=encoding)
            
        print('Roster encoding seems to be %s' % encoding)
        csvfile.seek(0)  # Back to the beginning of the file
        reader = csv.reader(csvfile)

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
                if row[col]:      # Ignore blank ones
                    try:
                        row[col] = datetime.strptime(row[col], format)
                    except ValueError as e:
                        format = '%m/%d/%y'
                        print('Trying ', format)
                        try:
                            row[col] = datetime.strptime(row[col], format)
                        except ValueError as e:
                            format = '%m/%d/%Y'
                            print('Trying ', format)
                            try:
                                row[col] = datetime.strptime(row[col], format)
                            except Exception as e:
                                print(e)
                                print(row[col])
                                print(row)
                                sys.exit(1)
                else:
                    # If no date, patch in today.
                    row[col] = date.today()
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
