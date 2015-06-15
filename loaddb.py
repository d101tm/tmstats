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
    
def cleandate(date):
    charterdate = date.split('/')  
    if len(charterdate[2]) == 2:
        charterdate[2] = "20" + charterdate[2]
    return '-'.join((charterdate[2],charterdate[0],charterdate[1]))
        
def doHistoricalClubs(conn):
    clubfiles = glob.glob("clubs.*.csv")
    clubhist = {}
    curs = conn.cursor()
    firsttime = True

    for c in clubfiles:
        cdate = c.split('.')[1]
        curs.execute('SELECT COUNT(*) FROM loaded WHERE tablename="clubs" AND loadedfor=%s', (cdate,))
        if curs.fetchone()[0] > 0:
            continue
        print "loading clubs for", cdate
        infile = open(c, 'rU')
        doDailyClubs(infile, conn, curs, cdate, clubhist, firsttime)
        firsttime = False
        infile.close()
    
    # Commit all changes    
    conn.commit()


def doDailyClubs(infile, conn, curs, cdate, clubhist, firsttime=False):
    """ infile is a file-like object """

    reader = csv.reader(infile)

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
        charterdate = cleandate(club.charterdate)

    
        # Clean up advanced status
        club.advanced = (club.advanced != '')
    
    
        # And put it into the database if need be
        if club.clubnumber in clubhist:
            changes = different(club, clubhist[club.clubnumber], dbheaders[:-2])
        else:
            changes = []
            if not firsttime:
                curs.execute('INSERT INTO clubchanges (clubnumber, changedate, item, old, new) VALUES (%s, %s, "New Club", "", "")', (club.clubnumber, cdate))
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
        

def doHistoricalDistrictPerformance(conn):
    perffiles = glob.glob("distperf.*.csv")
    curs = conn.cursor()

    for c in perffiles:
        cdate = c.split('.')[1]
        curs.execute('SELECT COUNT(*) FROM loaded WHERE tablename="distperf" AND loadedfor=%s', (cdate,))
        if curs.fetchone()[0] > 0:
            continue
        print "loading distperf for", cdate
        infile = open(c, 'rU')
        doDailyDistrictPerformance(infile, conn, curs, cdate)
        infile.close()

    # Commit all changes    
    conn.commit()
    
def doDailyDistrictPerformance(infile, conn, curs, cdate):
    reader = csv.reader(infile)
    hline = reader.next()
    headers = [p.lower().replace(' ','') for p in hline]
    headers = [p.replace('?','') for p in headers]
    headers = [p.replace('.','') for p in headers]
    headers = [p.replace('/','') for p in headers]
    # Do some renaming
    renames = (('club', 'clubnumber'),
               ('new', 'newmembers'),('lateren', 'laterenewals'),('octren', 'octrenewals'),
               ('aprren', 'aprrenewals'),('totalren', 'totalrenewals'),('totalchart', 'totalcharter'),
               ('distinguishedstatus', 'dist'), ('charterdatesuspenddate', 'action'))
    for (old, new) in renames:
        try:
            index = headers.index(old)
            headers[index] = new
        except:
            pass
    try:
        clubcol = headers.index('clubnumber')    
    except ValueError:
        print "'clubnumber' not in '%s'" % hline
        return
    # We're going to use the last column for the effective date of the data
    headers.append('asof')
    valstr = ','.join(['%s' for each in headers])
    headstr = ','.join(headers)
    for row in reader:
        if row[0].startswith("Month"):
            break
        action = row[-1].split()  # For later...
        row.append(cdate)
        curs.execute('INSERT IGNORE INTO distperf (' + headstr + ') VALUES (' + valstr + ')', row)
        
        
        # If this item represents a suspended club, and it's the first time we've seen this suspension,
        # add it to the clubchanges database
        if 'Susp' in action:
            clubnumber = row[clubcol]
            suspdate = cleandate(action[action.index('Susp') + 1])
            curs.execute('SELECT * FROM clubchanges WHERE clubnumber=%s and item="Suspended" and new=%s', (clubnumber, suspdate))
            if not curs.fetchone():
                # Add this suspension
                print cdate, suspdate
                curs.execute('INSERT INTO clubchanges (item, old, new, clubnumber, changedate) VALUES ("Suspended", "", %s, %s, %s)', (suspdate, clubnumber, cdate))
                
    conn.commit()
    # Now, insert the month into all of today's entries
    month = row[0].split()[-1]  # Month of Apr, for example
    curs.execute('UPDATE distperf SET month = %s WHERE asof = %s', (month, cdate))
    curs.execute('INSERT IGNORE INTO loaded (tablename, loadedfor) VALUES ("distperf", %s)', (cdate,))
    conn.commit() 

    
    

if __name__ == "__main__":

    conn = dbconn.dbconn()
    os.chdir("data")  # Yes, this is sleazy

    doHistoricalClubs(conn)
    doHistoricalDistrictPerformance(conn)

    conn.close()
    
