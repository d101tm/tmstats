select
'Clubnumber', 'Club Name', 'Area', 'Place', 'Address', 'City', 'State', 'Zip',
    'Google Lat', 'Google Long', 'Formatted', 'Location Type', 'Map Lat', 'Map Long', 'Map Addr', 'Distance (Mi)' 

UNION ALL 
SELECT * FROM (SELECT
geo.clubnumber, geo.clubname, concat(clubperf.division,clubperf.area), place, geo.address as ga, city, state, zip, latitude, longitude, formatted, geo.locationtype, map.lat, map.lng, map.address as ma, 3959 * acos( cos( radians(latitude) ) 
      * cos( radians(map.lat) ) 
      * cos( radians(map.lng) - radians(longitude)) + sin(radians(latitude))
      * sin( radians(map.lat) ) ) as delta from geo join map on geo.clubnumber = map.clubnumber join clubperf on geo.clubnumber = clubperf.clubnumber where clubperf.entrytype = 'L' order by delta) realstuff
INTO OUTFILE '~/Downloads/delta.csv'
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
;
