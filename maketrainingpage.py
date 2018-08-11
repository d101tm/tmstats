#!/usr/bin/env python3
""" Make Training Page:

    Use the information from The Events Calendar to create a page with
    a complete listing of all trainings in the District. 
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
        
        
class Event:
    ptemplate = '%Y-%m-%d %H:%M:%S'
    
    def __init__(self, name, title, contents, venues, parms):
        for item in contents:
            ours = item.replace("_","")
            self.__dict__[ours] = contents[item]
        if '_EventVenueID' in contents:
            v = int(self.EventVenueID)
            for item in venues[v]:
                ours = item.replace("_","")
                self.__dict__[ours] = venues[v][item]
        self.start = datetime.strptime(self.EventStartDate, self.ptemplate)
        self.end = datetime.strptime(self.EventEndDate, self.ptemplate)
        self.include = (self.start >= parms.start) and (self.end <= parms.end)
        self.showreg = parms.showpast or (self.end > parms.now)
        self.name = name
        self.title = title

            
    def __repr__(self):
        self.date = self.start.strftime('%A, %B %d').replace(' 0',' ')
        self.time = self.start.strftime(' %I:%M') + '-' + self.end.strftime(' %I:%M %p')
        self.time = self.time.replace(' 0', ' ').replace(' ','').lower()
        self.addr = '<td><b>%(VenueName)s</b><br>%(VenueAddress)s<br>%(VenueCity)s, %(VenueState)s %(VenueZip)s</td>' % self.__dict__
        try:
            self.special = '<br>%s' % self.eventspecialnote
        except AttributeError:
            self.special = ''
        if self.showreg and self.EventURL:
            self.register = ' | <a href="%(EventURL)s">Register</a>' % self.__dict__
        else:
            self.register = ""
        ans = """<tr><td><b>%(name)s</b>%(special)s<br><a href="/%(title)s">More Information</a>%(register)s</td><td><b>%(date)s</b><br>%(time)s%(addr)s</tr>""" % self.__dict__
        return ans

    
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
    parms.add_argument('--outfile', type=str, default='trainingschedule.html')
    parms.add_argument('--showpastregistration', dest='showpast', action='store_true')
    # Add other parameters here
    globals.setup(parms, connect=False)

 
      
    # Figure out the training period.
    parms.now = datetime.now()   
    parms.start = parms.now
    parms.end = parms.now  
    if parms.now.month >= 5 and parms.now.month <= 9:
        parms.start = parms.start.replace(month=6,day=1)
        parms.end = parms.end.replace(month=9,day=30)
    else:
        parms.start = parms.start.replace(month=11,day=1)
        parms.end = parms.end.replace(month=3,day=31)
        if parms.now.month >= 10:
            parms.end = parms.end.replace(year=parms.end.year+1)
        else:
            parms.start = parms.start.replace(year=parms.start.year-1)
    # But we don't care about past trainings, set start to today
    parms.start = parms.now.replace(hour=0,minute=0,second=0)
    

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
    
    # Find the taxonomy value for 'training'
    stmt = "SELECT term_id FROM %s WHERE slug = 'training'" % (prefix+'terms')
    curs.execute(stmt)
    tax_training = curs.fetchone()[0]
    
    # Find all published training events in the database
    
    stmt = "SELECT ID, post_title, post_name from %s p INNER JOIN %s t ON p.ID = t.object_id WHERE p.post_type = 'tribe_events' AND p.post_status = 'publish' AND t.term_taxonomy_id = %%s" % (poststable, prefix+'term_relationships')
    curs.execute(stmt, (tax_training,))
    post_numbers = []
    post_titles = {}
    post_names = {}
    for (number, title, name) in curs.fetchall():
        post_numbers.append(number)
        post_titles[number] = title
        post_names[number] = name
    nums = ','.join(['%d' % p for p in post_numbers])
    
    
            
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
    
    
    events = []
    for p in list(posts.values()):
        id = p['post_id']
        this = Event(post_titles[id], post_names[id], p, venues, parms)
        if this.include:
            events.append(this)
            

    outfile = open(parms.outfile,'w')
    outfile.write("""<table class="d101eventtable"><colgroup> <col> <col> <col> </colgroup>
<thead>
<tr><th><b>Training</b></th><th><b>When</b></th><th><b>Where</b></th></tr>
</thead>
<tbody>\n""")
    for event in sorted(events,key=lambda l:l.start):
        output(event, outfile)
    
    outfile.write("""</tbody>
    </table>\n""")
        
        
    

        
        
    
    
    
    
 
    
    
