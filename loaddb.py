#!/usr/bin/env python3
""" Load the performance information already gathered into a database. 
    Run from the directory containing the YML file for parms and the CSV files 
    Return code:
       0 if changes were made to the database
       1 if no changes were made """

import csv, dbconn, sys, os, glob
from simpleclub import Club
from tmutil import cleandate
import geocode
import tmparms, tmglobals

globals = tmglobals.tmglobals()

# Global variable to see how many entries got changed.  All we really care about is zero/nonzero.
global changecount
changecount = 0

headersnotinboth = []


statelist = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get("suppress", 1)
    file = kwargs.get("file", sys.stderr)

    if parms.quiet < suppress:
        print(" ".join(args), file=file)


def normalize(str):
    if str:
        return " ".join(str.split())
    else:
        return ""


def different(new, old, headers):
    """ Returns a list of items which have changed, each of which is a tuple of (item, old, new)."""
    res = []
    # Do some type conversions so the comparison works
    old.latitude = float(old.latitude)
    old.longitude = float(old.longitude)

    for h in headers:
        try:
            if new.__dict__[h] != old.__dict__[h]:
                res.append((h, old.__dict__[h], new.__dict__[h]))
        except KeyError:
            if h not in headersnotinboth:
                if h not in new.__dict__:
                    sys.stdout.write("%s not in new headers\n" % h)
                else:
                    sys.stdout.write("%s not in old headers\n" % h)
                headersnotinboth.append(h)
    return res


def cleanheaders(hline):
    headers = [p.lower().replace(" ", "") for p in hline]
    headers = [p.replace("?", "") for p in headers]
    headers = [p.replace(".", "") for p in headers]
    headers = [p.replace("/", "") for p in headers]
    return headers


def cleanitem(item):
    """ Return the item with leading zeros and spaces stripped if it's an integer; leave it alone otherwise. """
    try:
        item = "%d" % int(item)
    except ValueError:
        pass
    return item


def doHistoricalClubs(conn, mapkey):
    clubfiles = glob.glob("clubs.*.csv")
    clubfiles.sort()
    curs = conn.cursor()
    firsttime = True

    for c in clubfiles:
        cdate = c.split(".")[1]
        curs.execute(
            'SELECT COUNT(*) FROM loaded WHERE tablename="clubs" AND loadedfor=%s',
            (cdate,),
        )
        if curs.fetchone()[0] > 0:
            continue
        infile = open(c, "r")
        doDailyClubs(infile, conn, cdate, firsttime)
        firsttime = False
        infile.close()
        conn.commit()

    # Commit all changes
    conn.commit()

    # And update the GEO table if necessary
    curs.execute("SELECT MAX(lastdate) FROM clubs")
    lastdate = curs.fetchone()[0]
    curs.execute(
        "SELECT c.clubnumber FROM clubs c INNER JOIN geo g ON g.clubnumber = c.clubnumber AND (c.address != g.address OR c.city != g.city OR c.state != g.state OR c.zip != g.zip OR c.country != g.country OR (c.latitude != c.longitude AND (c.latitude != g.whqlatitude OR c.longitude != g.whqlongitude))) WHERE lastdate = %s",
        (lastdate,),
    )
    clubstoupdate = ["%d" % c[0] for c in curs.fetchall()]
    # And get new clubs, too
    curs.execute(
        "SELECT clubnumber FROM clubs WHERE lastdate = %s AND clubnumber NOT IN (SELECT clubnumber FROM geo)",
        (lastdate,),
    )
    for c in curs.fetchall():
        clubstoupdate.append("%d" % c[0])
    if clubstoupdate:
        geocode.updateclubstocurrent(conn, clubstoupdate, mapkey)


def doDailyClubs(infile, conn, cdate, firsttime=False):
    """ infile is a file-like object """
    global changecount
    from datetime import datetime, timedelta

    curs = conn.cursor()
    reader = csv.reader(infile)

    hline = next(reader)
    headers = cleanheaders(hline)

    try:
        clubcol = headers.index("clubnumber")
    except ValueError:
        if not hline[0].startswith('{"Message"'):
            print("'clubnumber' not in '%s'" % hline)
        return

    try:
        prospectiveclubcol = headers.index("prospectiveclub")
    except ValueError:
        prospectiveclubcol = False

    # Find out what fields we have in the database itself
    dbfields = []
    curs.execute("describe clubs")
    for l in curs.fetchall():
        dbfields.append(l[0])

    inform("clubs for", cdate, suppress=1)
    dbheaders = [p for p in headers]

    # Convert between Toastmasters' names for address and location and ours; they've changed it a few times.  *sigh*
    if "address1" in dbheaders:
        addrcol1 = dbheaders.index("address1")
    else:
        addrcol1 = dbheaders.index("location")
    if "address2" in dbheaders:
        addrcol2 = dbheaders.index("address2")
    else:
        addrcol2 = dbheaders.index("address")

    dbheaders[addrcol1] = "place"
    dbheaders[addrcol2] = "address"
    expectedheaderscount = len(dbheaders)
    dbheaders.append("firstdate")
    dbheaders.append("lastdate")  # For now...

    areacol = dbheaders.index("area")
    divisioncol = dbheaders.index("division")
    statecol = dbheaders.index("state")

    # Now, suppress anything in the file that's not in the database:
    suppress = []
    oldheaders = dbheaders
    dbheaders = []
    for i in range(len(oldheaders)):
        if oldheaders[i] in dbfields:
            dbheaders.append(oldheaders[i])
        else:
            suppress.append(i)
    suppress.reverse()  # We remove these columns from the input

    Club.setfieldnames(dbheaders)

    # We need to get clubs for the most recent update so we know whether to update an entry
    #   or start a new one.
    yesterday = datetime.strftime(
        datetime.strptime(cdate, "%Y-%m-%d") - timedelta(1), "%Y-%m-%d"
    )
    clubhist = Club.getClubsOn(curs, date=yesterday)

    for row in reader:
        if len(row) < expectedheaderscount:
            break  # we're finished
        if prospectiveclubcol is not None and row[prospectiveclubcol]:
            continue  # Ignore prospective clubs

        for i in suppress:
            del row[i]


        if len(row) > expectedheaderscount:
            # Special case...Millbrae somehow snuck two club websites in!
            row[16] = row[16] + "," + row[17]
            del row[17]

        # print row[addrcol1]
        # print row[addrcol2]
        # Now, clean up the address:
        # Address line 1 is "place" information and can be multiple lines.
        # Address line 2 is the real address and should be treated as one line, with spaces normalized.
        place = "\n".join([x.strip() for x in row[addrcol1].split("  ")])
        row[addrcol1] = place
        address = normalize(row[addrcol2])
        row[addrcol2] = address

        # Toastmasters is currently reversing the "Area" and "Division" items.  "Area" should be a
        #    number; if not, swap the two.
        try:
            thearea = row[areacol]
            thedivision = row[divisioncol]
            areanum = int(row[areacol])
        except ValueError:
            row[areacol] = thedivision
            row[divisioncol] = thearea

        # Collapse state names into their abbreviations
        if row[statecol] in statelist:
            row[statecol] = statelist[row[statecol]]

        # Get the right number of items into the row by setting today as the
        #   tentative first and last date
        row.append(cdate)
        row.append(cdate)

        # And create the object
        club = Club(row)

        # Now, clean up things coming from Toastmasters

        if club.clubstatus.startswith("Open") or club.clubstatus.startswith("None"):
            club.clubstatus = "Open"
        else:
            club.clubstatus = "Restricted"

        # Clean up the club and district numbers and the area
        club.clubnumber = cleanitem(club.clubnumber)
        club.district = cleanitem(club.district)
        club.area = cleanitem(club.area)

        # If a club is partially unassigned, mark it as completely unassigned.
        if (
            (club.area == "0A")
            or (club.area == "0D")
            or (club.division == "0D")
            or (club.division == "0A")
        ):
            club.area = "0A"
            club.division = "0D"

        # Clean up the charter date
        club.charterdate = cleandate(club.charterdate)

        # Clean up advanced status
        club.advanced = "1" if (club.advanced != "") else "0"

        # Clean up online status
        club.allowsonlineattendance = (
            "1" if (club.allowsonlineattendance != "") else "0"
        )

        # Add missing schemes to any URLs
        club.fixURLSchemes()

        # Now, take care of missing latitude/longitude
        if ("latitude") in dbheaders:
            try:
                club.latitude = float(club.latitude)
            except ValueError:
                club.latitude = 0.0
        else:
            club.latitude = 0.0

        if ("longitude") in dbheaders:
            try:
                club.longitude = float(club.longitude)
            except ValueError:
                club.longitude = 0.0
        else:
            club.longitude = 0.0

        # Sometimes, Toastmasters gets the latitude and longitude backwards
        # If that turns out to create an impossible location (which it will in California),
        #    let's swap them.
        if abs(club.latitude) > 90.0:
            (club.latitude, club.longitude) = (club.longitude, club.latitude)

        # And put it into the database if need be
        if club.clubnumber in clubhist:
            changes = different(club, clubhist[club.clubnumber], dbheaders[:-2])
        else:
            changes = []

        if club.clubnumber not in clubhist and not firsttime:
            # This is a new (or reinstated) club; note it in the changes database.
            curs.execute(
                'INSERT IGNORE INTO clubchanges (clubnumber, changedate, item, old, new) VALUES (%s, %s, "New Club", "", "")',
                (club.clubnumber, cdate),
            )

        if club.clubnumber not in clubhist or changes:
            club.firstdate = club.lastdate
            # Encode newlines in the place as double-semicolons for the database
            club.place = club.place.replace("\n", ";;")
            values = [club.__dict__[x] for x in dbheaders]

            # And then put the place back into normal form
            club.place = club.place.replace(";;", "\n")

            thestr = (
                "INSERT IGNORE INTO clubs ("
                + ",".join(dbheaders)
                + ") VALUES ("
                + ",".join(["%s" for each in values])
                + ");"
            )

            try:
                changecount += curs.execute(thestr, values)
            except Exception as e:
                print(e)
            # Capture changes
            for (item, old, new) in changes:
                if item == "place":
                    # Clean up the place (old and new) for the database
                    old = old.replace("\n", ";;")
                    new = new.replace("\n", ";;")
                try:
                    curs.execute(
                        "INSERT IGNORE INTO clubchanges (clubnumber, changedate, item, old, new) VALUES (%s, %s, %s, %s, %s)",
                        (club.clubnumber, cdate, item, old, new),
                    )
                except Exception as e:
                    print(e)
            clubhist[club.clubnumber] = club
            if different(club, clubhist[club.clubnumber], dbheaders[:-2]):
                print("it's different after being set.")
                sys.exit(3)
        else:
            # update the lastdate
            changecount += curs.execute(
                "UPDATE clubs SET lastdate = %s WHERE clubnumber = %s AND lastdate = %s;",
                (cdate, club.clubnumber, clubhist[club.clubnumber].lastdate),
            )

    # If all the files were processed, today's work is done.
    curs.execute(
        'INSERT IGNORE INTO loaded (tablename, loadedfor) VALUES ("clubs", %s)',
        (cdate,),
    )


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
        (mpart, dpart) = line.split(",")
        month = 1 + [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ].index(mpart.split()[-1].lower()[0:3])
        date = cleandate(dpart.split()[-1])
        asofyear = int(date[0:4])
        asofmon = int(date[5:7])
        if month == 12 and asofmon == 1:
            asofyear = asofyear - 1
        monthstart = "%04d-%02d-%02d" % (asofyear, month, 1)

        retval = (monthstart, date)
        break
    infile.seek(filepos)
    return retval


def doHistorical(conn, name):
    inform("Processing", name, suppress=2)
    perffiles = glob.glob(name + ".*.csv")
    perffiles.sort()
    curs = conn.cursor()
    for c in perffiles:
        infile = open(c, "r")
        (monthstart, cdate) = getasof(infile)
        # Table names can't be dynamically substituted by the MySQLdb module, so we do that ourselves.
        # We let MySQLdb substitute the date, since that comes from outside sources and needs to be sandboxed.
        curs.execute(
            'SELECT COUNT(*) FROM loaded WHERE tablename="%s" AND loadedfor=%%s' % name,
            (cdate,),
        )
        if curs.fetchone()[0] == 0:
            # Don't have data for this date; call the appropriate routine.
            if name == "distperf":
                doDailyDistrictPerformance(infile, conn, cdate, monthstart)
            elif name == "areaperf":
                doDailyAreaPerformance(infile, conn, cdate, monthstart)
            elif name == "clubperf":
                doDailyClubPerformance(infile, conn, cdate, monthstart)
            else:
                sys.stderr.write(
                    "'%s' is not a valid name for historical performance requests."
                )
                sys.exit(1)
        infile.close()

    # Set 'final for month' indications for the appropriate items:
    #   For each club, set the indicator for the last entry for a month OTHER than the most recent month

    curs.execute(
        """
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
        % (name, name, name, name, name, name)
    )

    # Now, mark the latest daily entry
    curs.execute("UPDATE %s SET entrytype = 'D' WHERE entrytype = 'L'" % name)
    curs.execute("SELECT max(asof) FROM %s" % name)
    maxasof = curs.fetchone()[0]
    curs.execute(
        "UPDATE %s SET entrytype = 'L' WHERE entrytype = 'D' AND asof = %%s" % name,
        (maxasof,),
    )

    conn.commit()


def doDailyDistrictPerformance(infile, conn, cdate, monthstart):
    global changecount
    curs = conn.cursor()
    reader = csv.reader(infile)
    hline = next(reader)
    headers = cleanheaders(hline)
    # Do some renaming
    renames = (
        ("club", "clubnumber"),
        ("new", "newmembers"),
        ("lateren", "laterenewals"),
        ("octren", "octrenewals"),
        ("aprren", "aprrenewals"),
        ("totalren", "totalrenewals"),
        ("totalchart", "totalcharter"),
        ("distinguishedstatus", "dist"),
    )
    for (old, new) in renames:
        try:
            index = headers.index(old)
            headers[index] = new
        except:
            pass
    # Now, replace "charterdatesuspenddate" with one field for each.
    cdsdcol = headers.index("charterdatesuspenddate")
    headers = (
        headers[:cdsdcol] + ["charterdate", "suspenddate"] + headers[cdsdcol + 1 :]
    )
    try:
        clubcol = headers.index("clubnumber")
    except ValueError:
        print("'clubnumber' not in '%s'" % hline)
        return
    inform("distperf for", cdate, supress=1)
    areacol = headers.index("area")
    districtcol = headers.index("district")
    # We're going to use the last column for the effective date of the data
    headers.append("asof")
    valstr = ",".join(["%s" for each in headers])
    headstr = ",".join(headers)
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
            charterpos = action.index("Charter")
            charterdate = action[charterpos + 1]
        except ValueError:
            charterdate = ""
        try:
            susppos = action.index("Susp")
            suspdate = action[susppos + 1]
        except ValueError:
            suspdate = ""
        row = row[:cdsdcol] + [charterdate, suspdate] + row[cdsdcol + 1 :]

        changecount += curs.execute(
            "INSERT IGNORE INTO distperf (" + headstr + ") VALUES (" + valstr + ")", row
        )

        # If this item represents a suspended club, and it's the first time we've seen this suspension,
        # add it to the clubchanges database
        if suspdate:
            curs.execute(
                'SELECT * FROM clubchanges WHERE clubnumber=%s and item="Suspended" and new=%s',
                (clubnumber, suspdate),
            )
            if not curs.fetchone():
                # Add this suspension
                curs.execute(
                    'INSERT IGNORE INTO clubchanges (item, old, new, clubnumber, changedate) VALUES ("Suspended", "", %s, %s, %s)',
                    (suspdate, clubnumber, cdate),
                )

    conn.commit()
    # Now, insert the month into all of today's entries
    curs.execute(
        "UPDATE distperf SET monthstart = %s WHERE asof = %s", (monthstart, cdate)
    )
    curs.execute(
        'INSERT IGNORE INTO loaded (tablename, loadedfor, monthstart) VALUES ("distperf", %s, %s)',
        (cdate, monthstart),
    )
    conn.commit()


def doDailyClubPerformance(infile, conn, cdate, monthstart):
    global changecount
    curs = conn.cursor()
    reader = csv.reader(infile)
    hline = next(reader)
    headers = cleanheaders(hline)
    try:
        clubcol = headers.index("clubnumber")
    except ValueError:
        print("'clubnumber' not in '%s'" % hline)
        return
    inform("clubperf for", cdate, supress=1)
    areacol = headers.index("area")
    districtcol = headers.index("district")
    memcol = headers.index("activemembers")
    otr1col = headers.index("offtrainedround1")
    otr2col = headers.index("offtrainedround2")
    octduescol = headers.index("memduesontimeoct")
    aprduescol = headers.index("memduesontimeapr")
    offlistcol = headers.index("offlistontime")
    # We're going to use the last column for the effective date of the data
    headers.append("asof")
    headers.append("color")
    headers.append("goal9")
    headers.append("goal10")
    valstr = ",".join(["%s" for each in headers])
    headstr = ",".join(headers)
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
            row.append("Red")
        elif members < 20:
            row.append("Yellow")
        else:
            row.append("Green")

        # Compute Goal 9 (training):
        if int(row[otr1col]) >= 4 and int(row[otr2col]) >= 4:
            row.append(1)
        else:
            row.append(0)

        # Compute Goal 10 (paperwork):
        if ((int(row[octduescol]) > 0) or (int(row[aprduescol]) > 0)) and int(
            row[offlistcol]
        ) > 0:
            row.append(1)
        else:
            row.append(0)

        changecount += curs.execute(
            "INSERT IGNORE INTO clubperf (" + headstr + ") VALUES (" + valstr + ")", row
        )

        # Let's see if the club status has changed; if so, indicate that in the clubchanges table.
        curs.execute(
            "SELECT clubstatus, asof FROM clubperf WHERE clubnumber=%s ORDER BY ASOF DESC LIMIT 2 ",
            (clubnumber,),
        )
        ans = curs.fetchall()
        if len(ans) == 2:
            if ans[0][0] != ans[1][0]:
                curs2 = conn.cursor()
                curs2.execute(
                    'INSERT IGNORE INTO clubchanges (item, old, new, clubnumber, changedate) VALUES ("Status Change", %s, %s, %s, %s)',
                    (ans[1][0], ans[0][0], clubnumber, cdate),
                )

    conn.commit()
    # Now, insert the month into all of today's entries
    curs.execute(
        "UPDATE clubperf SET monthstart = %s WHERE asof = %s", (monthstart, cdate)
    )
    curs.execute(
        'INSERT IGNORE INTO loaded (tablename, loadedfor, monthstart) VALUES ("clubperf", %s, %s)',
        (cdate, monthstart),
    )
    conn.commit()


def doDailyAreaPerformance(infile, conn, cdate, monthstart):
    global changecount
    curs = conn.cursor()
    reader = csv.reader(infile)
    hline = next(reader)
    headers = cleanheaders(hline)
    try:
        clubcol = headers.index("club")
        headers[clubcol] = "clubnumber"
    except ValueError:
        print("'club' not in '%s'" % hline)
        return
    inform("areaperf for", cdate, supress=1)
    areacol = headers.index("area")
    districtcol = headers.index("district")

    # Now, replace "charterdatesuspenddate" with one field for each.
    cdsdcol = headers.index("charterdatesuspenddate")
    headers = (
        headers[:cdsdcol] + ["charterdate", "suspenddate"] + headers[cdsdcol + 1 :]
    )

    # We're going to use the last column for the effective date of the data
    headers.append("asof")
    valstr = ",".join(["%s" for each in headers])
    headstr = ",".join(headers)
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
            charterpos = action.index("Charter")
            charterdate = action[charterpos + 1]
        except ValueError:
            charterdate = ""
        try:
            susppos = action.index("Susp")
            suspdate = action[susppos + 1]
        except ValueError:
            suspdate = ""
        row = row[:cdsdcol] + [charterdate, suspdate] + row[cdsdcol + 1 :]

        changecount += curs.execute(
            "INSERT IGNORE INTO areaperf (" + headstr + ") VALUES (" + valstr + ")", row
        )

    conn.commit()
    # Now, insert the month into all of today's entries
    curs.execute(
        "UPDATE areaperf SET monthstart = %s WHERE asof = %s", (monthstart, cdate)
    )
    curs.execute(
        'INSERT IGNORE INTO loaded (tablename, loadedfor, monthstart) VALUES ("areaperf", %s, %s)',
        (cdate, monthstart),
    )
    conn.commit()


if __name__ == "__main__":

    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument("--quiet", "-q", action="count", default=0)

    # Do global setup
    globals.setup(parms)
    conn = globals.conn

    inform("Processing Clubs", supress=1)
    doHistoricalClubs(conn, parms.googlemapsapikey)
    doHistorical(conn, "distperf")
    doHistorical(conn, "clubperf")
    doHistorical(conn, "areaperf")

    conn.close()

    if changecount == 0:
        sys.exit(1)
