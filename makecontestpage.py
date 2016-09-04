#!/usr/bin/env python
""" Make Contest Page:

    Use the information from The Events Calendar to create a page with
    a complete listing of all contests in the District. 
"""

import dbconn, tmutil, sys, os
from datetime import datetime
import re

def ParseWPConfig(f):
    """ Parses a WordPress configuration file 
        Stolen from http://stackoverflow.com/questions/16881577/parse-php-file-variables-from-python-script """
    
    
    define_pattern = re.compile(r"""\bdefine\(\s*('|")(.*)\1\s*,\s*('|")(.*)\3\)\s*;""")
    assign_pattern = re.compile(r"""(^|;)\s*\$([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)\s*=\s*('|")(.*)\3\s*;""")


    php_vars = {}
    for line in f:
        for match in define_pattern.finditer(line):
            php_vars[match.group(2)]=match.group(4)
        for match in assign_pattern.finditer(line):
            php_vars[match.group(2)]=match.group(4)
    return php_vars


def getinfo(curs, table, post_list):
    venue_numbers = set()
    posts = {}
    # Get all the event information from the database
    stmt = "SELECT post_id, meta_key, meta_value FROM %s WHERE post_id IN (%s)" % (table,post_list)
    curs.execute(stmt)
    for (post_id, meta_key, meta_value) in curs.fetchall():
        if post_id not in posts:
            posts[post_id] = {'post_id':post_id}
        posts[post_id][meta_key] = meta_value
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
    def __init__(self, contents, area, venues):
        for item in contents:
            ours = item.replace("_","")
            self.__dict__[ours] = contents[item]
        if '_EventVenueID' in contents:
            v = int(self.EventVenueID)
            for item in venues[v]:
                ours = item.replace("_","")
                self.__dict__[ours] = venues[v][item]
        self.area = area

            
    def __repr__(self):
        if len(self.area) == 1:
            self.name = '<b>Division %s Contest</b>' % self.area
        else:
            self.name = '<b>Area %s Contest</b>' % self.area
        ptemplate = '%Y-%m-%d %H:%M:%S'
        start = datetime.strptime(self.EventStartDate, ptemplate)
        end = datetime.strptime(self.EventEndDate, ptemplate)
        self.date = start.strftime('%B %d').replace(' 0',' ')
        self.time = start.strftime(' %I:%M') + '-' + end.strftime(' %I:%M %p')
        self.time = self.time.replace(' 0', ' ').replace(' ','').lower()
        self.addr = '<td><b>%(VenueVenue)s</b><br>%(VenueAddress)s<br>%(VenueCity)s, %(VenueState)s %(VenueZip)s</td>' % self.__dict__
        ans = """<tr><td>%(name)s<br><a href="%(EventURL)s">Register</a></td><td><b>%(date)s</b><br>%(time)s%(addr)s</tr>""" % self.__dict__
        return ans

def tocome(what):
    return '<tr><td>%s</td><td>TBA</td><td>&nbsp;</td>' % what        
    
def output(what, outfile):
    outfile.write('%s\n' % what)

if __name__ == "__main__":
 
    import tmparms
    tmutil.gotodatadir()           # Move to the proper data directory
        
    reload(sys).setdefaultencoding('utf8')
    
    # Handle parameters
    parms = tmparms.tmparms()
    parms.add_argument('--quiet', '-q', action='count')
    parms.add_argument('--verbose', '-v', action='count')
    parms.add_argument('--configfile', type=str, default='wp-config.php')
    parms.add_argument('--uselocal', action='store_true')
    parms.add_argument('--outfile', type=str, default='contestschedule.html')
    # Add other parameters here
    parms.parse() 
   
 
    # Connect to the database        
    conn = dbconn.dbconn(parms.dbhost, parms.dbuser, parms.dbpass, parms.dbname)
    curs = conn.cursor()
      
    
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
    config = ParseWPConfig(open(parms.configfile,'r'))
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
    
    # And now, get the venue information.  
    venues = getinfo(curs, prefix+'postmeta', ','.join(venue_numbers))[0]
    
    # @@TODO@@ We need to select only events in the current period.
    events = {}
    for p in posts.values():
        id = p['post_id']
        m = re.match(title_pattern, post_titles[id])
        if m:
            for area in m.group(2).replace('/',' ').split():
                events[area] = Event(p, area, venues)
                if not events[area].EventURL:
                    print 'Area %s does not have a URL' % area
            
        else:
            print p['post_id'], 'does not have an Area'
            continue
            

            
    outfile = open(parms.outfile,'w')
    outfile.write("""<table border="1"><colgroup> <col> <col> <col> <col> </colgroup>
<thead>
<tr>
<th>Area/Division</th>
<th>When</th>
<th>Where</th>
</tr>
</thead>
<tbody>\n""")
    for div in sorted(divisions.keys()):
        d = divisions[div]
        if d in events:
            output(events[d], outfile)
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
        
        
    

        
        
    
    
    
    
 
    
    
