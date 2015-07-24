#!/usr/bin/env python2.7
from __future__ import print_function
import googlemaps
import urllib3
import logging
import dbconn, tmparms
import os, sys
from math import pi, sin, cos



clubs = {}
class myclub():
    
    fieldnames = 'clubnumber, clubname, place, address, city, state, zip, latitude, longitude, locationtype, partialmatch, nelat, nelong, swlat, swlong, area, formatted, types'
    fields = [k.strip() for k in fieldnames.replace(',',' ').split()]
    values = ('%s,' * len(fields))[:-1]
    
    def __init__(self, clubnumber, clubname, place, address, city, state, zip):
        self.clubnumber = clubnumber
        self.clubname = clubname
        self.place = place
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.latitude = 0.0
        self.longitude = 0.0
        self.locationtype = ''
        self.partialmatch = False
        self.nelat = 0.0
        self.nelong = 0.0
        self.swlat = 0.0
        self.swlong = 0.0
        self.formatted = ''
        self.types = ''
        self.area = 0.0
        
    def update(self, results, curs):
        if isinstance(results, basestring):
            results = eval(results)  # Yes, it's unsafe.  
        if len(results) != 1:
            print(len(results), 'results found for', self.clubnumber, self.clubname, '\n', self.address, self.city, self.state, self.zip, file=sys.stderr)
        if len(results) >= 1:
            curs.execute('DELETE FROM geo WHERE clubnumber = %s', (self.clubnumber,))
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
            if self.area > 0:
                print(self.clubnumber, self.clubname, '\n', self.address, self.city,self.state,self.zip,file=sys.stderr)
                if (self.area > 0.0001):
                    print('best choice (bounding box %f square miles)' % self.area, self.locationtype, file=sys.stderr)
                else:
                    print('best choice (bounding box %d square feet)' % (self.area * 5280.0 * 5280.0), self.locationtype, file=sys.stderr)
                print(self.formatted, file=sys.stderr)
                print('-----------------------------', file=sys.stderr)
            curs.execute('INSERT INTO geo  (' + self.fieldnames + ') VALUES (' + self.values + ')', 
                    ([self.__dict__[k] for k in self.fields]))
            
            
        
if __name__ == "__main__":
    
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
        
    reload(sys).setdefaultencoding('utf8')

    parms = tmparms.tmparms()
    parms.parse()
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    c = conn.cursor()
    c.execute("SELECT clubnumber, clubname, place, address, city, state, zip FROM clubs GROUP BY clubnumber ORDER BY lastdate DESC")
    for (clubnumber, clubname, place, address, city, state, zip)  in c.fetchall():
        clubs['%d' % clubnumber] = myclub(clubnumber, clubname, place, address, city, state, zip)
    


    infile = open('codeit.txt', 'r')
    line = infile.readline()
    while line:
        (clubnumber, clubname) = line.split(None,1)
        ret = []
        while True:
            line = infile.readline()
            if line[0] == '[':
                break
        ret.append(line)
        while True:
            line = infile.readline()
            if line[0] == '=':
                break
            ret.append(line)
        club = clubs[clubnumber]
        club.update(''.join(ret), c)
        line = infile.readline()
    
    conn.commit()    

