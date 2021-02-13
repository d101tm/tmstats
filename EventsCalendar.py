"""EventsCalendar - Pythonic interface to The Events Calendar in the WordPress database """

import tmutil
import tmglobals
import dbconn
import os
from datetime import datetime

myglobals = tmglobals.tmglobals()

class EventsCalendar:
    def __init__(self, parms):
        config = tmutil.parseWPConfig(open(os.path.join(parms.wpdir, 'wp-config.php'), 'r'))
        if parms.uselocal:
            config['DB_HOST'] = 'localhost'

        # Connect to the WP Database
        self.conn = dbconn.dbconn(config['DB_HOST'], config['DB_USER'], config['DB_PASSWORD'], config['DB_NAME'])
        self.curs = self.conn.cursor()
        self.prefix = config['table_prefix']
        self.poststable = self.prefix + 'posts'
        self.optionstable = self.prefix + 'options'
        self.postmeta = self.prefix + 'postmeta'
        self.venue_numbers = set()

    def getTaxonomyValue(self, slug):
        stmt = f"SELECT term_id FROM {self.prefix}terms WHERE slug = %s"
        self.curs.execute(stmt, (slug,))
        return self.curs.fetchone()[0]

    def getEvents(self, slug, startfrom=None, endbefore=None):
        """Get all events of a given type from the calendar"""
        stmt = f'SELECT id, post_title, post_name from {self.poststable} p '\
               f'INNER JOIN {self.prefix}term_relationships t ON p.id = t.object_id '\
               f'WHERE p.post_type = "tribe_events" AND p.post_status = "publish" AND '\
               f't.term_taxonomy_id = {self.getTaxonomyValue(slug)}'

        self.curs.execute(stmt)
        events = {}
        for (number, title, name) in self.curs.fetchall():
            events[number] = CalEvent(number, title, name)

        # Add the data from the postmeta table.  Collect Venue IDs.

        eventnums = ','.join([f'{p}' for p in events.keys()])
        self.curs.execute(f'SELECT post_id, meta_key, meta_value FROM {self.postmeta} WHERE post_id IN ({eventnums})')
        for (post_id, meta_key, meta_value) in self.curs.fetchall():
            events[post_id].meta[meta_key] = meta_value.strip()

        # Merge metatable information into the events themselves
        for e in events.values():
            e.cleanup()

        # Filter by time interval, if specified
        if startfrom and endbefore:
            events = {k: events[k] for k in events.keys() if events[k].start >= startfrom and events[k].end <= endbefore}

        # Collect venue keys from remaining events
        for e in events.values():
            if e.venue:
                self.venue_numbers.add(e.venue)

        return events

    def getVenues(self):
        venues = {v: Venue(v) for v in self.venue_numbers}
        venuenums = ','.join(self.venue_numbers)  # Already a string because it's from postmeta
        self.curs.execute(f'SELECT post_id, meta_key, meta_value FROM {self.postmeta} WHERE post_id IN ({venuenums})')
        for (post_id, meta_key, meta_value) in self.curs.fetchall():
            venues[f'{post_id}'].meta[meta_key] = meta_value.strip()  # post_id is a number, we need a string

        for v in venues.values():
            v.cleanup()

        return venues


class Venue:
    def __init__(self, venue_number):
        self.venue_number = venue_number
        self.meta = {}

    def cleanup(self):
        # Convert items in the meta table to attributes; ensure all needed attributes exist
        self.name = self.meta.get('_VenueVenue', '')
        self.address = self.meta.get('_VenueAddress', '')
        self.city = self.meta.get('_VenueCity', '')
        self.country = self.meta.get('_VenueCountry', '')
        self.state = self.meta.get('_VenueState', '')
        self.zip = self.meta.get('_VenueZip', '')

        # Is this a real-world venue?
        if not self.name or self.name.lower().startswith('online'):
            self.realworld = False
        elif self.address and self.city and self.state:
            self.realworld = True
        else:
            self.realworld = False

    @property
    def addr(self):
        ret = f'{self.name}'
        if self.address:
            ret += '\n' if ret else ''
            ret += f'{self.address}\n{self.city}, {self.state} {self.zip}'
        return ret




class CalEvent:
    def __init__(self, number, title, name):
        self.number = number
        self.title = title
        self.name = name
        self.meta = {}

    def gettimefromitem(self, item):
        try:
            return datetime.strptime(self.meta[item], '%Y-%m-%d %H:%M:%S')
        except KeyError:
            return datetime(1989, 1, 1, 0, 0, 0)


    def cleanup(self):
        # Convert items in the meta table to attributes, converting times as appropriate
        self.start = self.gettimefromitem('_EventStartDate')
        self.end = self.gettimefromitem('_EventEndDate')
        self.url = self.meta.get('_EventURL', '')
        self.venue = self.meta.get('_EventVenueID', None)
        self.specialnote = self.meta.get('event_special_note', '')