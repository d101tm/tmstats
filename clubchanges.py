#!/usr/bin/python
from simpleclub import Club
import os


def cleandate(indate):
    from datetime import date, timedelta
    if '/' in indate:
        indate = indate.split('/')
        indate = [indate[2], indate[0], indate[1]]
    elif '-' in indate:
        indate = indate.split('-')
    elif 'today'.startswith(indate.lower()):
        return date.today().strftime('%Y-%m-%d')
    elif 'yesterday'.startswith(indate.lower()):
        return (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    if len(indate[0]) == 2:
        indate[0] = "20" + indate[0]
    if len(indate[1]) == 1:
        indate[1] = "0" + indate[1]
    if len(indate[2]) == 1:
        indate[2] = "0" + indate[2]
    return '-'.join(indate)
    



if __name__ == "__main__":
    import dbconn, tmparms
    
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
    
    # Define args and parse command line
    parms = tmparms.tmparms()
    parms.add_argument('--fromdate', default='yesterday', dest='fromdate')
    parms.add_argument('--todate', default='today', dest='todate')
    parms.add_argument('--notify', nargs='*', default=None, dest='notify', action='append')
    parms.add_argument('--mailpw', default=None, dest='mailpw')
    parms.add_argument('--mailserver', default=None, dest='mailserver')
    parms.add_argument('--mailfrom', default=None, dest='mailfrom')
    parms.parse()
    fromdate = cleandate(parms.fromdate)
    todate = cleandate(parms.todate)
    
    
    # print 'Connecting to %s:%s as %s' % (parms.dbhost, parms.dbname, parms.dbuser)
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
   
    # Get information for clubs as of the "from" date:

    curs.execute("SELECT * FROM clubs WHERE firstdate <= %s AND lastdate >= %s", (fromdate, fromdate))
    
    # Get the fieldnames before we get anything else:
    fieldnames = [f[0] for f in curs.description]
    Club.setfields(fieldnames)
    
    newclubs = {}   # Where clubs created during the period go
    changedclubs = {}  # Where clubs changed during the period go
    oldclubs = {}  # Clubs at the beginning; clubs still around at the end are removed
    
    # OK, now build the list of clubs at the beginning of the period
    for eachclub in curs.fetchall():
        club = Club(eachclub)
        oldclubs[club.clubnumber] = club
    
    # And compare to the the list of clubs at the end of the period
    curs.execute("SELECT * FROM clubs WHERE firstdate <= %s AND lastdate >= %s", (todate, todate))    
    for eachclub in curs.fetchall():
        club = Club(eachclub) 
        if club.clubnumber not in oldclubs:
            club.info = 'New Club'
            newclubs[club.clubnumber] = club
        elif club == oldclubs[club.clubnumber]:
            # Club is unchanged; just remove it
            del oldclubs[club.clubnumber]
        else:
            # Club has changed.  Get the list of changes as a tuple (item, old, new)
            changedclubs[club.clubnumber] = (oldclubs[club.clubnumber].clubname, 
                oldclubs[club.clubnumber].delta(club))
            del oldclubs[club.clubnumber]  # And we're done with the old club
            
    # And print results
    
    if oldclubs or newclubs or changedclubs:
        print "Club changes from %s to %s\n" % (fromdate, todate)
    
    if oldclubs:
        print "Clubs which have vanished:"
        for k in oldclubs:
            print k, oldclubs[k].clubname
         
    if newclubs:   
        print "-------------------------------------------------------"
        print "New clubs:"
        for k in newclubs:
            print newclubs[k]
        
    if changedclubs:
        print "-------------------------------------------------------"
        print "Changes:"
        for k in changedclubs:
            print k, changedclubs[k][0]
            for (item, old, new) in changedclubs[k][1]:
                print item, old, new
            print    


