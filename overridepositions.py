from geocode import myclub
import googlemaps
import csv
import requests



def overrideClubPositions(clubs, overridefile, apikey):
    """ Updates 'clubs' with information from the relocation spreadsheet """
    from geocode import myclub
    gmaps = googlemaps.Client(key=apikey)
    myclub.setgmaps(gmaps)
    r = requests.get(overridefile)
    reader = csv.DictReader(r.text.split('\n'))
    for row in reader:
        clubnumber = row['clubnumber']
        if clubnumber in clubs:
            club = clubs[clubnumber]
            try:
                # Use explicit coordinates if we find them
                club.latitude = float(row['latitude'])
                club.longitude = float(row['longitude'])
                # Both are specified, so we use them
            except:  # latitude and longitude not both specified
                if row['address']:
                    # No coordinates provided but an address is here; use it.
                    gres = gmaps.geocode(row['address']) # Includes city, state, zip, country if needed
                    # Make a dummy club entry for geocoding
                    reloinfo = myclub(clubnumber, club.clubname, club.place, club.address, club.city, club.state, club.zip, club.country, 0.0, 0.0)
                    # TODO: get rid of the need for a dummy club entry - have geocode return coordinates.
                    reloinfo.process(gres)
                    club.latitude = reloinfo.latitude
                    club.longitude = reloinfo.longitude
