#!/usr/bin/python
""" Load the performance information already gathered into a database. """
""" We assume we care about the data directory underneath us. """

import csv, sqlite3, sys, os, glob
from club import Club

def normalize(str):
    if str:
        return ' '.join(str.split())
    else:
        return ''



os.chdir("data")  # Yes, this is sleazy

conn = sqlite3.connect("tmstats.db")
curs = conn.cursor()
clubfiles = glob.glob("clubs.*.csv")

# If the table doesn't exist yet, create it.
curs.execute("""CREATE TABLE IF NOT EXISTS clubs (
        district VARCHAR(4),
        division CHAR(1),
        area INT,
        clubnumber INT,
        clubname VARCHAR(100) COLLATE NOCASE,
        charter VARCHAR(10),  
        address VARCHAR(200) COLLATE NOCASE,
        city VARCHAR(100) COLLATE NOCASE,
        state VARCHAR(100) COLLATE NOCASE,
        zip VARCHAR(20) COLLATE NOCASE,
        country VARCHAR(100) COLLATE NOCASE,
        phone VARCHAR(40) COLLATE NOCASE,
        meetingtime VARCHAR(100) COLLATE NOCASE,
        meetingday VARCHAR(100) COLLATE NOCASE,
        clubstatus VARCHAR(100) COLLATE NOCASE,
        clubwebsite VARCHAR(100) COLLATE NOCASE,
        clubemail VARCHAR(100) COLLATE NOCASE,
        clubfacebook VARCHAR(100) COLLATE NOCASE,
        advanced BOOL,
        infodate VARCHAR(10)
        )""")

clubhist = {}
headers = None

for c in clubfiles:
    cdate = c.split('.')[1]
    print cdate
    infile = open(c, 'r')
    reader = csv.reader(infile)
    if not headers:
        headers = [p.lower().replace(' ','') for p in reader.next()]
        clubcol = headers.index('clubnumber')    
        Club.setHeaders(headers)
        dbheaders = [p for p in headers]
        dbheaders[dbheaders.index('address1')] = 'address'
        del dbheaders[dbheaders.index('address2')]   # I know there's a more Pythonic way.
        dbheaders.append('filedate')     # For now...
    else:
        reader.next()  # Throw away a line
    for row in reader:
        if len(row) < 20:
            break     # we're finished

        # Convert to unicode.  Toastmasters usually uses UTF-8 but occasionally uses Windows CP1252 on the wire.
        try:
            row = [unicode(t.strip(), "utf8") for t in row]
        except UnicodeDecodeError:
            row = [unicode(t.strip(), "CP1252") for t in row]
             
        if len(row) > 20:
            # Special case...Millbrae somehow snuck two club websites in!
            row[16] = row[16] + ',' + row[17]
            del row[17]

        row[clubcol] = Club.fixcn(row[clubcol])   # Canonicalize the club number
        club = Club(row)       # And create something we can deal with.
        if club.clubstatus.startswith('Open') or club.clubstatus.startswith('None'):
            club.clubstatus = 'Open'
        else:
            club.clubstatus = 'Restricted'

        # Clean up the address
        club.address = '\n'.join(club.address1.split('  ') + club.address2.split('  '))
        club.filedate = cdate
        
        # And put it into the database
        curs.execute('INSERT INTO CLUBS VALUES (' + ','.join('?'*len(dbheaders)) + ');', [club.__dict__[x] for x in dbheaders])

        
conn.commit()
conn.close()
    
