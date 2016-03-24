#!/usr/bin/env python
""" Get the CLUBS data from WHQ using the JSON interface and build a CSV file. """

# This is a standard skeleton to use in creating a new program in the TMSTATS suite.

import dbconn, tmutil, sys, os
import json, urllib2


def inform(*args, **kwargs):
    """ Print information to 'file' unless suppressed by the -quiet option.
          suppress is the minimum number of 'quiet's that need be specified for
          this message NOT to be printed. """
    suppress = kwargs.get('suppress', 1)
    file = kwargs.get('file', sys.stderr)
    
    if parms.quiet < suppress:
        print >> file, ' '.join(args)

### Insert classes and functions here.  The main program begins in the "if" statement below.

def getresponse(url):
    req = urllib2.Request(url=url)
    req.add_header('User-Agent', 'Mozilla/6.0')
    req.add_header('content-type', "application/json; charset=utf-8")
    s = urllib2.urlopen(req)
    clubinfo = s.read()


    if len(clubinfo) < 10:
        # We didn't get anything of value
        clubinfo = False

    
    return clubinfo

if __name__ == "__main__":
 
    import tmparms
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--savejson', action='store_true')
    parms.add_argument('--fileprefix', type=str, default="fromjson")
    # Add other parameters here
    parms.parse() 
   
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
    
    # Your main program begins here.
    url = "https://www.toastmasters.org/service/clubs/Search/GetClubsBy?district=%02d&advanced=1&longitude=0&latitude=0" % parms.district
    resp = getresponse(url)

    if resp:
        all = json.loads(resp)
            
        # headline was copied from the Clubs export on 2015-11-24.    
        headline = "District,Area,Division,Club Number,Club Name,Charter Date,Location,Address,City,State,Zip,Country,Phone,Meeting Time,Meeting Day,Club Status,Club Website,Club Email,Facebook,Twitter,Longitude,Latitude,Advanced?"
        
        # fields is the set of fields in the JSON that correspond to the columns in the CSV
        fields = "District,AreaPrefix,AreaNumber,Number,Name,CharterDate,Location,Address,City,StateName,Zip,Country,Phone,MeetingTime,MeetingDay,Restricted,Website,Email,FacebookLink,TwitterLink,Longitude,Latitude,Note"
        fieldnames = fields.split(',')
        
        # Save the JSON if desired
        if parms.savejson:
            f = open(parms.fileprefix+'.json', 'w')
            f.write(json.dumps(all, sort_keys=True, indent=4, separators = (',', ': ')))
            f.close()

        f = open(parms.fileprefix+'.csv', 'wb')
        f.write(headline)
        f.write('\n')
        for club in all:
            line = []
            for item in fieldnames:
                val = club[item]
                # Do transformations to match the 2015-11-24 CSV file. 
                if item == "CharterDate":
                    # Convert date to m/d/y.
                    year = int(val[0:4])
                    month = int(val[5:7])
                    day = int(val[8:10])
                    val = '%d/%d/%d' % (month, day, year)
                elif item == "Restricted":
                    # Convert to very long verbiage.  
                    val = val.strip()
                    if val == 'O':
                        val = "None; the club is open to all interested parties."
                    elif val == 'G' or val == 'OPEN':
                        # OPEN takes care of "Talk The Line"
                        val = "This club may have professional and/or educational prerequisites for membership. Please contact the club for further information."
                elif item == "Note":
                    # Note seems to map to Advanced club status
                    if val.startswith("This club"):
                        val = "Yes"
                elif item in ["Latitude", "Longitude"]:
                    # Some clubs haven't been geocoded by WHQ.
                    if val is None:
                        val = ""
                    else:
                        val = '%.8f' % val
                elif val is None:
                    # Any null value goes into the CSV as an empty string
                    val = ""
                try:
                    # For any string, change <br> to a comma and a double-quote to a single
                    val = ', '.join(val.split('<br>')).strip().replace('"','\'')
                except AttributeError:
                    pass
                if line:
                    line.append('"%s"' % val)
                else:
                    line.append(val)    # District isn't quoted.
            f.write(','.join(line))
            f.write('\n')
        f.close()    