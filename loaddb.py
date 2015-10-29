#!/usr/bin/python
""" Load the performance information already gathered into a database. 
    Run from the directory containing the YML file for parms and the CSV files 
       (but in TextMate, run from the source directory).
    Return code:
       0 if changes were made to the database
       1 if no changes were made """

import csv, dbconn, sys, os, glob
from simpleclub import Club

# Global variable to see how many entries got changed.  All we really care about is zero/nonzero.
global changecount
changecount = 0

headersnotinboth = []

def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)

def normalize(str):
    if str:
        return ' '.join(str.split())
    else:
        return ''

def different(new, old, headers):
    """ Returns a list of items which have changed, each of which is a tuple of (item, old, new)."""
    res = []
    for h in headers:
        try:
            if new.__dict__[h] != old.__dict__[h]:
                #print h ,'is different for club', new.clubnumber
                #print 'old = %s, new = %s' % (old.__dict__[h], new.__dict__[h])
                res.append((h, old.__dict__[h], new.__dict__[h]))
        except KeyError:
            if h not in headersnotinboth:
                if h not in new.__dict__:
                    sys.stdout.write('%s not in new headers\n' % h)
                else:
                    sys.stdout.write('%s not in old headers\n' % h)
                headersnotinboth.append(h)
    return res
    
def cleandate(date):
    charterdate = date.split('/')  
    if len(charterdate[2]) == 2:
        charterdate[2] = "20" + charterdate[2]
    return '-'.join((charterdate[2],charterdate[0],charterdate[1]))
    
def cleanheaders(hline):
    headers = [p.lower().replace(' ','') for p in hline]
    headers = [p.replace('?','') for p in headers]
    headers = [p.replace('.','') for p in headers]
    headers = [p.replace('/','') for p in headers]
    return headers
    
def cleanitem(item):
    """ Return the item with leading zeros and spaces stripped if it's an integer; leave it alone otherwise. """
    try:
        item = '%d' % int(item)
    except ValueError:
        pass
    return item
    
        
def doHistoricalClubs(conn):
    clubfiles = glob.glob("clubs.*.csv")
    clubfiles.sort()
    curs = conn.cursor()
    firsttime = True

    for c in clubfiles:
        cdate = c.split('.')[1]
        curs.execute('SELECT COUNT(*) FROM loaded WHERE tablename="clubs" AND loadedfor=%s', (cdate,))
        if curs.fetchone()[0] > 0:
            continue
        infile = open(c, 'rU')
        doDailyClubs(infile, conn, cdate, firsttime)
        firsttime = False
        infile.close()
    
    # Commit all changes    
    conn.commit()


def doDailyClubs(infile, conn, cdate, firsttime=False):
    """ infile is a file-like object """
    global changecount
    from datetime import datetime, timedelta
    
    curs = conn.cursor()
    reader = csv.reader(infile)

    hline = reader.next()
    headers = cleanheaders(hline)

    try:
        clubcol = headers.index('clubnumber')    
    except ValueError:
        if not hline[0].startswith('{"Message"'):
            print "'clubnumber' not in '%s'" % hline
        return
        
    inform("clubs for", cdate, suppress=1)
    dbheaders = [p for p in headers]
    addrcol1 = dbheaders.index('address1')
    addrcol2 = dbheaders.index('address2')
    dbheaders[addrcol1] = 'place'
    dbheaders[addrcol2] = 'address'
    expectedheaderscount = len(dbheaders)
    dbheaders.append('firstdate')
    dbheaders.append('lastdate')     # For now...
    
    # Remove latitude and longitude for now.
    if 'latitude' in dbheaders:
        dbheaders.remove('latitude')
    if 'longitude' in dbheaders:
        dbheaders.remove('longitude')
  
    Club.setfieldnames(dbheaders)

    
    # We need to get clubs for the most recent update so we know whether to update an entry 
    #   or start a new one.
    #yesterday = datetime.strftime(datetime.strptime(cdate, '%Y-%m-%d') - timedelta(1),'%Y-%m-%d')
    clubhist = Club.getClubsOn(curs)
   
    for row in reader:
        if len(row) < expectedheaderscount:
            break     # we're finished

        # Convert to unicode.  Toastmasters usually uses UTF-8 but occasionally uses Windows CP1252 on the wire.
        try:
            row = [unicode(t.strip(), "utf8") for t in row]
        except UnicodeDecodeError:
            row = [unicode(t.strip(), "CP1252") for t in row]
         
        if len(row) > expectedheaderscount:
            print row
            # Special case...Millbrae somehow snuck two club websites in!
            row[16] = row[16] + ',' + row[17]
            del row[17]
            
        #print row[addrcol1]
        #print row[addrcol2]
        # Now, clean up the address:
        # Address line 1 is "place" information and can be multiple lines.
        # Address line 2 is the real address and should be treated as one line, with spaces normalized.
        place = '\n'.join([x.strip() for x in row[addrcol1].split('  ')]) 
        row[addrcol1] = place
        address = normalize(row[addrcol2])
        row[addrcol2] = address
        
            
        # Get the right number of items into the row by setting today as the 
        #   tentative first and last date
        row.append(cdate)
        row.append(cdate)
        
        # And create the object
        club = Club(row)



        
        # Now, clean up things coming from Toastmasters

        if club.clubstatus.startswith('Open') or club.clubstatus.startswith('None'):
            club.clubstatus = 'Open'
        else:
            club.clubstatus = 'Restricted'
        
        # Clean up the club and district numbers and the area
        club.clubnumber = cleanitem(club.clubnumber)
        club.district = cleanitem(club.district)
        club.area = cleanitem(club.area)

        
        # If a club is partially unassigned, mark it as completely unassigned.
        if (club.area == '0A') or (club.division == '0D'):
            club.area = '0A'
            club.division = '0D'

    
        # Clean up the charter date
        club.charterdate = cleandate(club.charterdate)

    
        # Clean up advanced status
        club.advanced = '1' if (club.advanced != '') else '0'
    
    
    
        # And put it into the database if need be
        if club.clubnumber in clubhist:
            changes = different(club, clubhist[club.clubnumber], dbheaders[:-2])
        else:
            changes = []
        
        if club.clubnumber not in clubhist and not firsttime:
            # This is a new (or reinstated) club; note it in the changes database.
            curs.execute('INSERT IGNORE INTO clubchanges (clubnumber, changedate, item, old, new) VALUES (%s, %s, "New Club", "", "")', (club.clubnumber, cdate))
                
        if club.clubnumber not in clubhist or changes:
            club.firstdate = club.lastdate
            # Encode newlines in the place as double-semicolons for the database
            club.place = club.place.replace('\n',';;')
            values = [club.__dict__[x] for x in dbheaders]
            
            # And then put the place back into normal form
            club.place = club.place.replace(';;','\n')
        
            thestr = 'INSERT IGNORE INTO clubs (' + ','.join(dbheaders) + ') VALUES (' + ','.join(['%s' for each in values]) + ');'
            try:
                changecount += curs.execute(thestr, values)
            except Exception, e:
                print e
            # Capture changes
            for (item, old, new) in changes:
                if (item == 'place'):
                    # Clean up the place (old and new) for the database
                    old = old.replace('\n', ';;')
                    new = new.replace('\n', ';;')
                try:
                    curs.execute('INSERT IGNORE INTO clubchanges (clubnumber, changedate, item, old, new) VALUES (%s, %s, %s, %s, %s)', (club.clubnumber, cdate, item, old, new))
                except Exception, e:
		            print e
            clubhist[club.clubnumber] = club
            if different(club, clubhist[club.clubnumber], dbheaders[:-2]):
                print 'it\'s different after being set.'
                sys.exit(3) 
        else:
            # update the lastdate
            changecount += curs.execute('UPDATE clubs SET lastdate = %s WHERE clubnumber = %s AND lastdate = %s;', (cdate, club.clubnumber, clubhist[club.clubnumber].lastdate))
    
    # If all the files were processed, today's work is done.    
    curs.execute('INSERT IGNORE INTO loaded (tablename, loadedfor) VALUES ("clubs", %s)', (cdate,))


def getasof(infile):
    """ Gets the "as of" information from a Toastmasters' report.  
        Returns a tuple: (monthstart, date) (both as characters)
        If there is no "as of" information, returns False.
        Seeks the file back to the current position.
        """
    retval = False
    filepos = infile.tell()
    for line in infile:
        if not line:
            break
        if not line.startswith("Month of"):
            continue
        (mpart, dpart) = line.split(',')
        month = 1+ ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].index(mpart.split()[-1].lower()[0:3])
        date = cleandate(dpart.split()[-1])
        asofyear = int(date[0:4])
        asofmon = int(date[5:7])
        if month == 12 and asofmon == 1:
            asofyear = asofyear - 1
        monthstart = '%04d-%02d-%02d' % (asofyear, month, 1)
        
        retval = (monthstart, date)
        break
    infile.seek(filepos)
    return retval
    
def doHistorical(conn, name):
    inform("Processing", name, suppress=2)
    perffiles = glob.glob(name + '.*.csv')
    perffiles.sort()
    curs = conn.cursor()
    for c in perffiles:
        infile = open(c, 'rU')
        (monthstart, cdate) = getasof(infile)
        # Table names can't be dynamically substituted by the MySQLdb module, so we do that ourselves.
        # We let MySQLdb substitute the date, since that comes from outside sources and needs to be sandboxed.
        curs.execute('SELECT COUNT(*) FROM loaded WHERE tablename="%s" AND loadedfor=%%s' % name, (cdate,))
        if curs.fetchone()[0] == 0:
            # Don't have data for this date; call the appropriate routine.
            if name == 'distperf':
                doDailyDistrictPerformance(infile, conn, cdate, monthstart)
            elif name == 'areaperf':
                doDailyAreaPerformance(infile, conn, cdate, monthstart)
            elif name == 'clubperf':
                doDailyClubPerformance(infile, conn, cdate, monthstart)
            else:
                sys.stderr.write("'%s' is not a valid name for historical performance requests.")
                sys.exit(1)
        infile.close()
        
    # Set 'final for month' indications for the appropriate items:
    #   For each club, set the indicator for the last entry for a month OTHER than the most recent month
    
    curs.execute("""
    UPDATE %s 
    SET    entrytype = 'M' 
    WHERE  id IN (SELECT id 
                  FROM   (SELECT id
                          FROM   %s 
                                 INNER JOIN (SELECT clubnumber, 
                                                    monthstart, 
                                                    Max(asof) maxasofformonth 
                                             FROM   %s 
                                             WHERE  monthstart != 
                                                    (SELECT Max(monthstart) 
                                                     FROM   %s) 
                                             GROUP  BY clubnumber, 
                                                       monthstart) latest 
                                         ON %s.clubnumber = latest.clubnumber 
                                            AND %s.asof = 
                                                latest.maxasofformonth
                                                AND entrytype <> 'M') 
                         updates)"""
     % (name, name, name, name, name, name))
                          
    # Now, mark the latest daily entry
    curs.execute("UPDATE %s SET entrytype = 'D' WHERE entrytype = 'L'" % name)
    curs.execute("SELECT max(asof) FROM %s" % name)
    maxasof = curs.fetchone()[0]
    curs.execute("UPDATE %s SET entrytype = 'L' WHERE entrytype = 'D' AND asof = %%s" % name, (maxasof,))
  
    conn.commit()
    
    

    
def doDailyDistrictPerformance(infile, conn, cdate, monthstart):
    global changecount
    curs = conn.cursor()
    reader = csv.reader(infile)
    hline = reader.next()
    headers = cleanheaders(hline)
    # Do some renaming
    renames = (('club', 'clubnumber'),
               ('new', 'newmembers'),('lateren', 'laterenewals'),('octren', 'octrenewals'),
               ('aprren', 'aprrenewals'),('totalren', 'totalrenewals'),('totalchart', 'totalcharter'),
               ('distinguishedstatus', 'dist'))
    for (old, new) in renames:
        try:
            index = headers.index(old)
            headers[index] = new
        except:
            pass
    # Now, replace "charterdatesuspenddate" with one field for each.
    cdsdcol = headers.index('charterdatesuspenddate')
    headers = headers[:cdsdcol] + ['charterdate','suspenddate'] + headers[cdsdcol+1:]
    try:
        clubcol = headers.index('clubnumber')    
    except ValueError:
        print "'clubnumber' not in '%s'" % hline
        return
    inform("distperf for", cdate, supress=1)
    areacol = headers.index('area')
    districtcol = headers.index('district')
    # We're going to use the last column for the effective date of the data
    headers.append('asof')
    valstr = ','.join(['%s' for each in headers])
    headstr = ','.join(headers)
    for row in reader:
        if row[0].startswith("Month"):
            break
        row.append(cdate)
        row[areacol] = cleanitem(row[areacol])
        row[clubcol] = cleanitem(row[clubcol])
        row[districtcol] = cleanitem(row[districtcol])
        
        # Break the "charterdatesuspenddate" column up
        action = row[cdsdcol].split()
        clubnumber = row[clubcol]
        try:
            charterpos = action.index('Charter')
            charterdate = action[charterpos+1]
        except ValueError:
            charterdate = ''  
        try:
            susppos = action.index('Susp')
            suspdate = action[susppos+1]
        except ValueError:
            suspdate = ''
        row = row[:cdsdcol] + [charterdate, suspdate] + row[cdsdcol+1:]
            
        
        changecount += curs.execute('INSERT IGNORE INTO distperf (' + headstr + ') VALUES (' + valstr + ')', row)
        
        
        # If this item represents a suspended club, and it's the first time we've seen this suspension,
        # add it to the clubchanges database
        if suspdate:
            curs.execute('SELECT * FROM clubchanges WHERE clubnumber=%s and item="Suspended" and new=%s', (clubnumber, suspdate))
            if not curs.fetchone():
                # Add this suspension
                curs.execute('INSERT IGNORE INTO clubchanges (item, old, new, clubnumber, changedate) VALUES ("Suspended", "", %s, %s, %s)', (suspdate, clubnumber, cdate))
                
    conn.commit()
    # Now, insert the month into all of today's entries
    curs.execute('UPDATE distperf SET monthstart = %s WHERE asof = %s', (monthstart, cdate))
    curs.execute('INSERT IGNORE INTO loaded (tablename, loadedfor, monthstart) VALUES ("distperf", %s, %s)', (cdate, monthstart))
    conn.commit() 

    

def doDailyClubPerformance(infile, conn, cdate, monthstart):
    global changecount
    curs = conn.cursor()
    reader = csv.reader(infile)
    hline = reader.next()
    headers = cleanheaders(hline)
    try:
        clubcol = headers.index('clubnumber')    
    except ValueError:
        print "'clubnumber' not in '%s'" % hline
        return
    inform("clubperf for", cdate, supress=1)
    areacol = headers.index('area')
    districtcol = headers.index('district')
    memcol = headers.index('activemembers')
    otr1col = headers.index('offtrainedround1')
    otr2col = headers.index('offtrainedround2')
    octduescol = headers.index('memduesontimeoct')
    aprduescol = headers.index('memduesontimeapr')
    offlistcol = headers.index('offlistontime')
    # We're going to use the last column for the effective date of the data
    headers.append('asof')
    headers.append('color')
    headers.append('goal9')
    headers.append('goal10')
    valstr = ','.join(['%s' for each in headers])
    headstr = ','.join(headers)
    for row in reader:
        if row[0].startswith("Month"):
            break
            
        row.append(cdate)
        row[areacol] = cleanitem(row[areacol])
        row[clubcol] = cleanitem(row[clubcol])
        row[districtcol] = cleanitem(row[districtcol])
        clubnumber = row[clubcol]        
        # Compute Colorcode
        members = int(row[memcol])
        if members <= 12:
            row.append('Red')
        elif members < 20:
            row.append('Yellow')
        else:
            row.append('Green')
            
        # Compute Goal 9 (training):
        if int(row[otr1col]) >= 4 and int(row[otr2col] >= 4):
            row.append(1)
        else:
            row.append(0)
            
        # Compute Goal 10 (paperwork):
        if ((int(row[octduescol]) > 0) or (int(row[aprduescol]) > 0)) and int(row[offlistcol]) > 0:
            row.append(1)
        else:
            row.append(0)
        
        changecount += curs.execute('INSERT IGNORE INTO clubperf (' + headstr + ') VALUES (' + valstr + ')', row)
        
        # Let's see if the club status has changed; if so, indicate that in the clubchanges table.
        curs.execute('SELECT clubstatus, asof FROM clubperf WHERE clubnumber=%s ORDER BY ASOF DESC LIMIT 2 ', (clubnumber,) )
        ans = curs.fetchall()
        if len(ans) == 2:
            if ans[0][0] != ans[1][0]:
                curs2 = conn.cursor()
                curs2.execute('INSERT IGNORE INTO clubchanges (item, old, new, clubnumber, changedate) VALUES ("Status Change", %s, %s, %s, %s)', (ans[1][0], ans[0][0], clubnumber, cdate))
        
    conn.commit()
    # Now, insert the month into all of today's entries
    curs.execute('UPDATE clubperf SET monthstart = %s WHERE asof = %s', (monthstart, cdate))
    curs.execute('INSERT IGNORE INTO loaded (tablename, loadedfor, monthstart) VALUES ("clubperf", %s, %s)', (cdate, monthstart))
    conn.commit()
    

def doDailyAreaPerformance(infile, conn, cdate, monthstart):
    global changecount
    curs = conn.cursor()
    reader = csv.reader(infile)
    hline = reader.next()
    headers = cleanheaders(hline)
    try:
        clubcol = headers.index('club')   
        headers[clubcol] = 'clubnumber' 
    except ValueError:
        print "'club' not in '%s'" % hline
        return
    inform("areaperf for", cdate, supress=1)
    areacol = headers.index('area')
    districtcol = headers.index('district')
    
    # Now, replace "charterdatesuspenddate" with one field for each.
    cdsdcol = headers.index('charterdatesuspenddate')
    headers = headers[:cdsdcol] + ['charterdate','suspenddate'] + headers[cdsdcol+1:]

    # We're going to use the last column for the effective date of the data
    headers.append('asof')
    valstr = ','.join(['%s' for each in headers])
    headstr = ','.join(headers)
    for row in reader:
        if row[0].startswith("Month"):
            break
            
        row.append(cdate)
        row[areacol] = cleanitem(row[areacol])
        row[clubcol] = cleanitem(row[clubcol])
        row[districtcol] = cleanitem(row[districtcol])
        clubnumber = row[clubcol]        
       
        # Break the "charterdatesuspenddate" column up
        action = row[cdsdcol].split()
        clubnumber = row[clubcol]
        try:
            charterpos = action.index('Charter')
            charterdate = action[charterpos+1]
        except ValueError:
            charterdate = ''  
        try:
            susppos = action.index('Susp')
            suspdate = action[susppos+1]
        except ValueError:
            suspdate = ''
        row = row[:cdsdcol] + [charterdate, suspdate] + row[cdsdcol+1:]
        
        changecount += curs.execute('INSERT IGNORE INTO areaperf (' + headstr + ') VALUES (' + valstr + ')', row)
        
       
    conn.commit()
    # Now, insert the month into all of today's entries
    curs.execute('UPDATE areaperf SET monthstart = %s WHERE asof = %s', (monthstart, cdate))
    curs.execute('INSERT IGNORE INTO loaded (tablename, loadedfor, monthstart) VALUES ("areaperf", %s, %s)', (cdate, monthstart))
    conn.commit()
 
if __name__ == "__main__":
 
    import tmparms
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.parse() 

        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
        
    inform("Processing Clubs", supress=1)
    doHistoricalClubs(conn)
    doHistorical(conn, "distperf")
    doHistorical(conn, "clubperf")
    doHistorical(conn, "areaperf")


    conn.close()
    
    if changecount == 0:
        sys.exit(1)
    
