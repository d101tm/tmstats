#!/usr/bin/python
""" Load the performance information already gathered into a database. """
""" We assume we care about the data directory underneath us. """

import csv, dbconn, sys, os, glob
from club import Club

def normalize(str):
    if str:
        return ' '.join(str.split())
    else:
        return ''

def different(new, old, headers):
    """ Returns a list of items which have changed, each of which is a tuple of (item, old, new)."""
    res = []
    for h in headers:
        if new.__dict__[h] != old.__dict__[h]:
            print h ,'is different for club', new.clubnumber
            print 'old = %s, new = %s' % (old.__dict__[h], new.__dict__[h])
            res.append((h, old.__dict__[h], new.__dict__[h]))
    return res

def doHistoricalClubs(conn):
    clubfiles = glob.glob("clubs.*.csv")
    clubhist = {}
    headers = None
    curs = conn.cursor()

    for c in clubfiles:
        cdate = c.split('.')[1]
        curs.execute('SELECT COUNT(*) FROM loaded WHERE tablename="clubs" AND loadedfor=%s', (cdate,))
        if curs.fetchone()[0] > 0:
            continue
        print "loading clubs for", cdate
        infile = open(c, 'rU')
        doDailyClubs(infile, conn, curs, headers, cdate, clubhist)
        infile.close()
    
    # Commit all changes    
    conn.commit()


def doDailyClubs(infile, conn, curs, headers, cdate, clubhist):
    """ infile is a file-like object """

    reader = csv.reader(infile)
    if not headers:
        hline = reader.next()
        headers = [p.lower().replace(' ','') for p in hline]
        headers = [p.replace('?','') for p in headers]
        try:
            clubcol = headers.index('clubnumber')    
        except ValueError:
            print "'clubnumber' not in '%s'" % hline
            return
        Club.setHeaders(headers)
        dbheaders = [p for p in headers]
        dbheaders[dbheaders.index('address1')] = 'address'
        del dbheaders[dbheaders.index('address2')]   # I know there's a more Pythonic way.
        dbheaders.append('firstdate')
        dbheaders.append('lastdate')     # For now...
    
    
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
        
        # Clean up the club and district numbers
        club.clubnumber = int(club.clubnumber)
        club.district = int(club.district )

        # Clean up the address
        club.address = ';'.join([x.strip() for x in club.address1.split('  ') + club.address2.split('  ')])
        club.address = ';'.join([x.strip() for x in club.address.split(',')])
        club.address = ', '.join(club.address.split(';'))
    
        club.lastdate = cdate
    
        # Clean up the charter date

        charterdate = club.charterdate.split('/')  
        club.charterdate = '-'.join((charterdate[2],charterdate[0],charterdate[1]))
    
        # Clean up advanced status
        club.advanced = (club.advanced != '')
    
    
        # And put it into the database if need be
        if club.clubnumber in clubhist:
            changes = different(club, clubhist[club.clubnumber], dbheaders[:-2])
        else:
            changes = []
        if club.clubnumber not in clubhist or changes:
            club.firstdate = club.lastdate
            values = [club.__dict__[x] for x in dbheaders]
        
            thestr = 'INSERT INTO CLUBS (' + ','.join(dbheaders) + ') VALUES (' + ','.join(['%s' for each in values]) + ');'
            try:
                curs.execute(thestr, values)
            except:
                print "Duplicate entry for", club
            # Capture changes
            for (item, old, new) in changes:
                try:
                    curs.execute('INSERT INTO clubchanges (clubnumber, changedate, item, old, new) VALUES (%s, %s, %s, %s, %s)', (club.clubnumber, cdate, item, old, new))
                except Exception, e:
                    print e
            clubhist[club.clubnumber] = club
            if different(club, clubhist[club.clubnumber], dbheaders[:-2]):
                print 'it\'s different after being set.'
                sys.exit(3) 
        else:
            # update the lastdate
            curs.execute('UPDATE CLUBS SET lastdate = %s WHERE clubnumber = %s AND firstdate = %s;', (cdate, club.clubnumber, clubhist[club.clubnumber].firstdate))
    
    # If all the files were processed, today's work is done.    
    curs.execute('INSERT INTO loaded (tablename, loadedfor) VALUES ("clubs", %s)', (cdate,))
        



if __name__ == "__main__":

    conn = dbconn.dbconn()
    os.chdir("data")  # Yes, this is sleazy

    doHistoricalClubs(conn)

    curs = conn.cursor()
    curs.execute('SELECT COUNT(*) FROM CLUBS')
    print curs.fetchall()
    conn.commit()
    print 'Commit done'
    curs.execute('SELECT COUNT(*) FROM CLUBS')
    print curs.fetchall()
    conn.close()
    
