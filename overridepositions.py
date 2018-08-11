from geocode import myclub
import googlemaps
import re
from googleapiclient import discovery
from pprint import pprint
from simpleclub import Club

def normalizespaces(s):
    # Removes extra spaces; turns non-breaking spaces into spaces
    return re.sub(r'\s+',' ',s.strip().replace('\xa0',' '))

def overrideClubPositions(clubs, overridefile, apikey, log=False, ignorefields=[], donotlog=[], createnewclubs=False):
    """ Updates 'clubs' with information from the override spreadsheet
        Note:  the same apikey is used for Google Maps and the Google spreadsheet """
    from geocode import myclub
    gmaps = googlemaps.Client(key=apikey)
    myclub.setgmaps(gmaps)
    
    # Get the data from the spreadsheet
    # We may be passed a whole URL or just the key
    if '/' in overridefile:
        # Have a whole URL; get the key
        overridefile = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', overridefile).groups()[0]

    
    # Connect to the spreadsheet and get the values
    service = discovery.build('sheets', 'v4', developerKey=apikey)
    request = service.spreadsheets().values().get(spreadsheetId=overridefile, range='a1:zz999')
    values = request.execute()['values']
    
    keys = values[0]
    # Make sure all clubs have all the keys in our override, plus "touchedby"
    requiredkeys = list(keys)
    requiredkeys.append('touchedby')
    # We may be creating new keys; the default for each is None.
    for c in clubs:
        for k in requiredkeys:
            club = clubs[c]
            if k not in club.__dict__:
                club.__dict__[k] = None
                
    
    # Now, work through the overrides
    for line in values[1:]:
        # Convert the values to a dictionary, based on the keys.
        row = {}
        for i, key in enumerate(keys):
            try:
                # Normalize whitespace, including non-breaking spaces
                row[key] = normalizespaces(line[i])
            except IndexError:
                row[key] = ''
        
        # Now, process the data.
        clubnumber = row['clubnumber']
        if clubnumber not in clubs and createnewclubs:            
            club = Club([normalizespaces(f) for f in line], fieldnames=keys)  
            clubs[clubnumber] = club
                
            if log:
                print(("%8s/%s *** New Club ***" % (club.clubnumber, club.clubname)))

        if clubnumber in clubs:
            club = clubs[clubnumber]
            
            # Indicate we touched this club
            club.touchedby = overridefile
            
            # Override anything specified
            for key in keys:
                if key not in ignorefields and row[key]:
                    if log and key not in donotlog and club.__dict__[key] != row[key]:
                        print(("%8s/%s: Updating '%s' from '%s' to '%s'" % (club.clubnumber, club.clubname, key, club.__dict__[key], row[key])))
                    club.__dict__[key] = row[key]
                    
                    
            # Now, compute latitude and longitude if need be
           
            try:
                # Use explicit coordinates if we find them
                club.latitude = float(club.latitude)
                club.longitude = float(club.longitude)
                # Both are specified, so we use them
            except:  # latitude and longitude not both specified
                if row['address']:
                    parts = ['address', 'city', 'state', 'zip', 'country']
                    address = ', '.join([row[p] for p in parts])
                    # No coordinates provided but an address is here; use it.
                    gres = gmaps.geocode(address) # Includes city, state, zip, country if needed
                    # Make a dummy club entry for geocoding
                    reloinfo = myclub(clubnumber, club.clubname, club.place, club.address, club.city, club.state, club.zip, club.country, 0.0, 0.0)
                    # TODO: get rid of the need for a dummy club entry - have geocode return coordinates.
                    reloinfo.process(gres)
                    club.latitude = reloinfo.latitude
                    club.longitude = reloinfo.longitude
                    

if __name__ == '__main__':
    #!/usr/bin/env python3
    """ If called as a main program, prints the current overrides """

    import tmutil, sys
    import tmglobals
    globals = tmglobals.tmglobals()
 

    import tmparms

    # Establish parameters
    parms = tmparms.tmparms()
    # Add other parameters here

    # Do global setup
    globals.setup(parms)
    curs = globals.curs
    conn = globals.conn
    
    clubs = Club.getClubsOn(curs)
    print(('Using %s as the override spreadsheet' % parms.mapoverride))
    overrideClubPositions(clubs, parms.mapoverride, parms.googlesheetsapikey, log=True)
