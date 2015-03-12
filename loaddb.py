#!/usr/bin/python
""" Load the performance information already gathered into a database. """
""" We assume we care about the data directory underneath us. """

import csv, sqlite3, sys, os, glob

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
        addr1 VARCHAR(100) COLLATE NOCASE,
        addr2 VARCHAR(100) COLLATE NOCASE,
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
        firstdate VARCHAR(10),
        lastdate VARCHAR(10)
        )""")

clubhist = {}

for c in clubfiles:
    cdate = c.split('.')[1]
    print cdate
    infile = open(c, 'r')
    names = infile.readline().strip().split(',')
    reader = csv.reader(infile)
    for row in reader:
        try:
            to_db = [unicode(t.strip(), "utf8") for t in row]
        except UnicodeDecodeError:
            to_db = [unicode(t.strip(), "CP1252") for t in row]
        if len(to_db) > 20:
            # Special case...Millbrae somehow snuck two club websites in!
            to_db[16] = to_db[16] + ',' + to_db[17]
            del to_db[17]

        if len(to_db) >  15:
            if 'pen' in to_db[15]:
                to_db[15] = 'Open'
            else:
                to_db[15] = 'Restricted'
            clubnum = row[3]
            if clubnum not in clubhist:
                mustupdate = True
            else:
                mustupdate =  to_db <> clubhist[clubnum][0:20]   # Don't care about firstdate

            if mustupdate:
                print len(to_db), clubnum
                to_db.append(cdate)  # Update 'firstdate' for this combination
                clubhist[clubnum] = to_db  # Save without lastdate
                to_db.append(cdate)  # Set 'lastdate'
                curs.execute('INSERT INTO CLUBS VALUES (' + ','.join('?'*len(to_db)) + ');', to_db)
            else:
                curs.execute('UPDATE CLUBS SET lastdate=? WHERE clubnumber=? and firstdate=?', (cdate, clubnum, clubhist[clubnum][20]))
        
conn.commit()
conn.close()
    
