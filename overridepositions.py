from geocode import myclub
import googlemaps
import urllib2, csv

class Relocate:
    relocations = {}
    def __init__(self, clubnumber, latitude, longitude):
        self.clubnumber = clubnumber
        self.latitude = latitude
        self.longitude = longitude
        self.relocations[int(clubnumber)] = self
        
    def __repr__(self):
        return "%s at (%f, %f)" % (self.clubnumber, self.latitude, self.longitude)

def overrideClubPositions(clubs, overridefile, apikey):
    from geocode import myclub
    gmaps = googlemaps.Client(key=apikey)
    myclub.setgmaps(gmaps)
    data = urllib2.urlopen(overridefile, 'rb')
    reader = csv.DictReader(data)
    for row in reader:
        clubnumber = row['clubnumber']
        if clubnumber in clubs:
            club = clubs[clubnumber]
            try:
                # Use explicit coordinates if we find them
                latitude = float(row['latitude'])
                longitude = float(row['longitude'])
                Relocate(clubnumber, latitude, longitude)   # Create the relocation entry
                # Both are specified, so we use them
            except:
                if row['address']:
                    # No coordinates provided but an address is here; use it.
                    gres = gmaps.geocode(row['address']) # Includes city, state, zip, country if needed
                    reloinfo = myclub(clubnumber, club.clubname, club.place, club.address, club.city, club.state, club.zip, club.country, 0.0, 0.0)
                    reloinfo.process(gres)
                    Relocate(clubnumber, reloinfo.latitude, reloinfo.longitude)
    data.close()
    

