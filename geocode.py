#!/usr/bin/env python3

import googlemaps
import dbconn, tmparms
import os, sys
from math import pi, sin, cos
import pprint
import datetime
import re
import tmglobals
globals = tmglobals.tmglobals()

# temphackfix
from requests.adapters import HTTPAdapter
orig_send = HTTPAdapter.send
def _send_no_verify(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
    return orig_send(self, request, stream, timeout, False, cert, proxies)
HTTPAdapter.send = _send_no_verify

from requests.packages import urllib3
urllib3.disable_warnings()

clubs = {}
class myclub():
    
    @classmethod
    def setgmaps(self, gmaps):
        self.gmaps = gmaps
    
    fieldnames = 'clubnumber, clubname, place, address, city, state, zip, country, latitude, longitude, locationtype, partialmatch, nelat, nelong, swlat, swlong, area, formatted, types, whqlatitude, whqlongitude, reverse, reversetype, whqreverse, whqreversetype'
    fieldnames += ', premise, outcity, outstate, outzip'
    fields = [k.strip() for k in fieldnames.replace(',',' ').split()]
    values = ('%s,' * len(fields))[:-1]
    
    def __init__(self, clubnumber, clubname, place, address, city, state, zip, country, whqlatitude, whqlongitude):
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.place = place
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country
        self.whqlatitude = whqlatitude
        self.whqlongitude = whqlongitude
        self.latitude = whqlatitude
        self.longitude = whqlongitude
        self.locationtype = ''
        self.partialmatch = False
        self.nelat = 0.0
        self.nelong = 0.0
        self.swlat = 0.0
        self.swlong = 0.0
        self.formatted = ''
        self.types = ''
        self.area = 0.0
        self.outcity = ''
        self.outstate = ''
        self.outzip = ''
        self.premise = ''
        self.reverse = ''
        self.reversetype = ''
        self.whqreverse = ''
        self.whqreversetype = ''
        
    def __repr__(self):
        return "%s (%s)\n  ours: (%f, %f)\n  whq: (%f, %f)" % (self.clubname, self.clubnumber, self.latitude, self.longitude, self.whqlatitude, self.whqlongitude)
        

    def updatefromwhq(self, curs):
        curs.execute('DELETE FROM geo WHERE clubnumber = %s', (self.clubnumber,))
        self.locationtype = 'WHQ'
        curs.execute('INSERT INTO geo  (' + self.fieldnames + ') VALUES (' + self.values + ')', 
                ([self.__dict__[k] for k in self.fields]))
        
        
    def process(self, results):
        
        if isinstance(results, str):
            results = eval(results)  # Yes, it's unsafe.  
        if len(results) != 1:
            print(len(results), 'results found for', self.clubnumber, self.clubname, '\n', self.address, self.city, self.state, self.zip, file=sys.stderr)

        # Let's see if there's a ROOFTOP address - if so, use it and only it.  If not, warn, and put all addresses in the database for now.
        for r in results:
            if r['geometry']['location_type'] == 'ROOFTOP':
                results = [r]
                break
        if len(results) > 1:
            print(len(results), 'results remain', file=sys.stderr)
            # Take the result with the smallest error
            bestarea = None
            best = None
            for r in results:
                geo = r['geometry']
                if 'bounds' not in geo:
                    # We have a zero error.  
                    best = r
                    break
                # Compute the area of the bounding box (error)
                nelat = geo['bounds']['northeast']['lat']
                nelong = geo['bounds']['northeast']['lng']
                swlat = geo['bounds']['southwest']['lat']
                swlong = geo['bounds']['southwest']['lng']
                area =  3959.0 * abs(sin(nelat) - sin(swlat)) * abs(nelong - swlong)
                if not bestarea or area < bestarea:
                    bestarea = area
                    best = r
            results = [best]
            
        if results:
            r = results[0] 
            geo = r['geometry']
            self.latitude = geo['location']['lat']
            self.longitude = geo['location']['lng']
            self.locationtype = geo['location_type']
            if 'bounds' in geo:
                self.nelat = geo['bounds']['northeast']['lat']
                self.nelong = geo['bounds']['northeast']['lng']
                self.swlat = geo['bounds']['southwest']['lat']
                self.swlong = geo['bounds']['southwest']['lng']
                self.area =  3959.0 * abs(sin(self.nelat) - sin(self.swlat)) * abs(self.nelong - self.swlong)
            else:
                self.nelat = 0.0
                self.nelong = 0.0
                self.swlat = 0.0
                self.swlong = 0.0
                self.area = 0.0
            if 'partial_match' in r:
                self.partialmatch = r['partial_match']
            else:
                self.partialmatch = False
        
            if 'formatted_address' in r:
                self.formatted = r['formatted_address']
            else:
                self.formatted = ''
            self.types = ', '.join(r['types'])
            
            # Now, disassemble the address components
            # We only care about premise, city, state, and zip
            ac = r['address_components']
            for each in ac:
                if 'locality' in each['types']:
                    self.outcity = each['long_name']
                elif 'administrative_area_level_1' in each['types']:
                    self.outstate = each['short_name']
                elif 'postal_code' in each['types']:
                    self.outzip = each['short_name']
                elif 'premise' in each['types']:
                    self.premise = each['short_name']
                    
            # Now, reverse-geocode the coordinates from WHQ
            if (self.whqlatitude != 0.0) and (self.whqlatitude != 0.0):
                try:        
                    rev = self.gmaps.reverse_geocode((self.whqlatitude, self.whqlongitude))[0]
                    self.whqreverse = rev['formatted_address']
                    self.whqreversetype = rev['geometry']['location_type']
                except Exception as e:
                    print(e)
                
                
            # And reverse-geocode the coordinates we calculated
            try:        
                rev = self.gmaps.reverse_geocode((self.latitude, self.longitude))[0]
                self.reverse = rev['formatted_address']
                self.reversetype = rev['geometry']['location_type']
            except Exception as e:
                print(e)
            
                
    def update(self, results, curs):
        # Process the information
        self.process(results)
        # Update the database
        curs.execute('DELETE FROM geo WHERE clubnumber = %s', (self.clubnumber,))
        curs.execute('INSERT INTO geo  (' + self.fieldnames + ') VALUES (' + self.values + ')', 
                ([self.__dict__[k] for k in self.fields]))
            
def updateclubstocurrent(conn, clubs, apikey, debug=False):
    # conn is a database connection
    # Clubs is an array of clubnumbers to update; if null, update all clubs.
    gmaps = googlemaps.Client(apikey)
    myclub.setgmaps(gmaps)
    c = conn.cursor()
    c.execute('SELECT MAX(lastdate) FROM clubs')
    lastdate = c.fetchone()[0]
    selector = "SELECT clubnumber, clubname, place, address, city, state, zip, country, latitude, longitude FROM clubs WHERE lastdate = %s"
    if clubs:
        clubs = '(%s)' % ','.join([repr(club) for club in clubs])
        print('Updating %s' % clubs)
        c.execute(selector + ' AND clubnumber IN ' + clubs, (lastdate,))
    else:
        c.execute(selector, (lastdate,))
       
    for (clubnumber, clubname, place, address, city, state, zip, country, whqlatitude, whqlongitude)  in c.fetchall():
        print (clubnumber, clubname)
        print (address, city, state, zip)
        gaddress = address
        # Let's clean up some common problems in the gaddress
        gaddress = gaddress.replace('Community Room','')
        gaddress = gaddress.replace('SW2-130','')
        if 'Lucas Hall' in gaddress:
            gaddress = 'Lucas Hall'
        patterns = (r'Classroom [A-Za-z0-9-]*',
                    r'Room [A-Za-z0-9-]*',
                    r'Rm [A-Za-z0-9-]*',
                    r'Suite [A-Za-z0-9-]*')
        patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        
        for p in patterns:
            gaddress = p.sub('', gaddress)
            
        if gaddress != address:
            print ('rewrote to', gaddress)

                    
        gres = gmaps.geocode("%s, %s, %s %s" % (gaddress, city, state, zip))
        if debug:
            pprint.pprint(gres)
        else:
            for each in gres:
                print ('formatted as %s' % each['formatted_address'])
                geo = each['geometry']
                print ('plotted at %s (%f, %f)' % (geo['location_type'], geo['location']['lat'], geo['location']['lng']))
        print ("=================")
        club = myclub(clubnumber, clubname, place, address, city, state, zip, country, whqlatitude, whqlongitude).update(gres, c)
        
    # And delete any clubs from GEO which aren't current
    c.execute('DELETE FROM geo WHERE clubnumber NOT IN (SELECT clubnumber FROM clubs WHERE lastdate = %s)', (lastdate,))
    conn.commit()
            
        
if __name__ == "__main__":
    
    import tmparms
    parms = tmparms.tmparms()    
    # Do Global Setup
    globals.setup(parms)
    
    updateclubstocurrent(globals.conn, [], parms.googlemapsapikey)
    
    
