#!/usr/bin/env python3
""" Make Contest Page:

    Use the information from The Events Calendar to create a page with
    a complete listing of all contests in the District. 
"""

import dbconn, tmutil, sys, os
from datetime import datetime
import re
import tmglobals
globals = tmglobals.tmglobals()



def getinfo(curs, table, post_list):
    venue_numbers = set()
    posts = {}
    # Get all the event information from the database
    stmt = "SELECT post_id, meta_key, meta_value FROM %s WHERE post_id IN (%s)" % (table,post_list)
    curs.execute(stmt)
    for (post_id, meta_key, meta_value) in curs.fetchall():
        if post_id not in posts:
            posts[post_id] = {'post_id':post_id}
        posts[post_id][meta_key] = meta_value.strip()
        if meta_key == '_EventVenueID':
            venue_numbers.add(meta_value)
        
    return (posts, venue_numbers)  
        
class Division:
    def __init__(self, name):
        self.areas = set()
        self.name = name
        
    def addArea(self, area):
        self.areas.add(self.name + area)
        
    def arealist(self):
        return sorted(self.areas)
        
class Event:
    ptemplate = '%Y-%m-%d %H:%M:%S'
    
    def __init__(self, contents, area, venues, parms):
        for item in contents:
            ours = item.replace("_","")
            self.__dict__[ours] = contents[item]
        if '_EventVenueID' in contents:
            v = int(self.EventVenueID)
            for item in venues[v]:
                ours = item.replace("_","")
                self.__dict__[ours] = venues[v][item]
        self.area = area
        self.start = datetime.strptime(self.EventStartDate, self.ptemplate)
        self.end = datetime.strptime(self.EventEndDate, self.ptemplate)
        self.include = (self.start >= parms.start) and (self.end <= parms.end)
        self.showreg = parms.showpast or (self.start > parms.now)

            
    def __repr__(self):
        if len(self.area) == 1:
            self.name = '<b>Division %s Contest</b>' % self.area
        else:
            self.name = '<b>Area %s Contest</b>' % self.area
        self.date = self.start.strftime('%B %d').replace(' 0',' ')
        self.time = self.start.strftime(' %I:%M') + '-' + self.end.strftime(' %I:%M %p')
        self.time = self.time.replace(' 0', ' ').replace(' ','').lower()
        self.addr = '<td><b>%(VenueName)s</b><br>%(VenueAddress)s<br>%(VenueCity)s, %(VenueState)s %(VenueZip)s</td>' % self.__dict__
        if self.showreg:
            self.register = '<br><a href="%(EventURL)s">Register</a>' % self.__dict__
        else:
            self.register = ""
        ans = """<tr><td>%(name)s%(register)s</td><td><b>%(date)s</b><br>%(time)s%(addr)s</tr>""" % self.__dict__
        return ans

def tocome(what):
    return '<tr><td>%s</td><td>TBA</td><td>&nbsp;</td>' % what        
    
def output(what, outfile):
    outfile.write('%s\n' % what)

if __name__ == "__main__":
 
    import tmparms
    
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--verbose', '-v', action='count')
    parms.add_argument('--configfile', type=str, default='wp-config.php')
    parms.add_argument('--uselocal', action='store_true')
    parms.add_argument('--outfile', type=str, default='contestschedule.html')
    parms.add_argument('--season', type=str, choices=['fall', 'spring', 'Fall', 'Spring', ''], default='')
    parms.add_argument('--year', type=int, default=0)
    parms.add_argument('--showpastregistration', dest='showpast', action='store_true')
    
    # Do global setup
    globals.setup(parms)
    conn = globals.conn
    curs = globals.curs
   

      
    # Figure out the contest period.
    parms.now = datetime.now()   
    parms.start = parms.now
    parms.end = parms.now  
    if parms.now.month <= 6 or parms.season.lower() == 'spring':
        parms.start = parms.start.replace(month=1,day=1)
        parms.end = parms.end.replace(month=6,day=30)
    else:
        parms.start = parms.start.replace(month=7,day=1)
        parms.end = parms.end.replace(month=12,day=31)
    if parms.year:
        parms.start = parms.start.replace(year=parms.year)
        parms.end = parms.end.replace(year=parms.year)
        
    
    # We need a complete list of Areas and Divisions
    divisions = {}
    curs.execute("SELECT district, division, area FROM areaperf WHERE entrytype='L' GROUP BY district, division, area")
    for (district, division, area) in curs.fetchall():
        if division != '0D':
            if division not in divisions:
                divisions[division] = Division(division)
            divisions[division].addArea(area)
    conn.close()

    # Parse the configuration file
    config = tmutil.parseWPConfig(open(parms.configfile,'r'))
    if parms.uselocal:
        config['DB_HOST'] = 'localhost'


    # Connect to the WP database     
    conn = dbconn.dbconn(config['DB_HOST'], config['DB_USER'], config['DB_PASSWORD'], config['DB_NAME'])
    curs = conn.cursor()
    prefix = config['table_prefix']
    poststable = prefix + 'posts'
    optionstable = prefix + 'options'
    
    # Find the taxonomy value for 'contest'
    stmt = "SELECT term_id FROM %s WHERE slug = 'contest'" % (prefix+'terms')
    curs.execute(stmt)
    tax_contest = curs.fetchone()[0]
    
    
    # Find all published contest events in the database
    
    stmt = "SELECT ID, post_title from %s p INNER JOIN %s t ON p.ID = t.object_id WHERE p.post_type = 'tribe_events' AND p.post_status = 'publish' AND t.term_taxonomy_id = %%s" % (poststable, prefix+'term_relationships')
    curs.execute(stmt, (tax_contest,))
    post_numbers = []
    post_titles = {}
    for (number, title) in curs.fetchall():
        post_numbers.append(number)
        post_titles[number] = title
    nums = ','.join(['%d' % p for p in post_numbers])
    title_pattern = re.compile(r"""(Division|Area)\s+(.*)\s+Contest""")
    
    
            
    # Now, get all the event information from the database
    (posts, venue_numbers) = getinfo(curs, prefix+'postmeta', nums)
    # Everything in the postmeta table is a string, including venue_numbers
    venuelist = ','.join(venue_numbers)
    
    # And now, get the venue information.  
    venues = getinfo(curs, prefix+'postmeta', venuelist)[0]
    
    
    # Patch in the actual name of the venue as VenueName
    stmt = "SELECT id, post_title from %s WHERE id IN (%s)" % (poststable, venuelist)
    curs.execute(stmt)
    for (id, title) in curs.fetchall():
        venues[id]['VenueName'] = title
    
    
    events = {}
    for p in list(posts.values()):
        id = p['post_id']
        m = re.match(title_pattern, post_titles[id])
        if m:
            for area in m.group(2).replace('/',' ').split():
                this = Event(p, area, venues, parms)
                if this.include:
                    events[area] = this
                    if not events[area].EventURL:
                        print('Area %s does not have a URL' % area)
            
        else:
            print(p['post_id'], 'does not have an Area')
            continue
            

    outfile = open(parms.outfile,'w')
    outfile.write("""<table border="1"><colgroup> <col> <col> <col> </colgroup>
<thead>

</thead>
<tbody>\n""")
    outfile.write("<style>td.divhead {background: #F2DF74; font-size: 200%; font-weight: bold; text-align: center; border: none;}</style>\n")
    for div in sorted(divisions.keys()):
        d = divisions[div]
        outfile.write('<tr><td colspan="3" class="divhead">Division %s</td></tr>\n' % div)
        outfile.write('<tr><td><b>Area/Division</b></td><td><b>When</b></td><td><b>Where</b></td></tr>\n')
        if div in events:
            output(events[div], outfile)
        else:
            output(tocome('<b>Division %s</b>' % div), outfile)
        pending = None
        for a in d.arealist():
            if a in events:
                if pending:
                    if pending.EventURL == events[a].EventURL:
                        pending.area += '/' + a
                    else:
                        output(pending, outfile)
                        pending = events[a]
                else:
                    pending = events[a]
            else:
                if pending:
                    output(pending, outfile)
                    pending = None
                output(tocome('Area %s' % a), outfile)
        if pending:
            output(pending, outfile)
    
    outfile.write("""</tbody>
    </table>\n""")
        
        
    

        
        
    
    
    
    
 
    
    
