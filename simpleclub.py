#!/usr/bin/env python3
""" Simple class to maintain information about a club.
"""

import datetime, re
from copy import deepcopy
from tmutil import getTMYearFromDB
from urllib.parse import urlsplit

npatt = re.compile('\W+', re.UNICODE)  # Get rid of anything that isn't a Unicode alphameric

def normalize(s):
    """ Normalize a string to minimize irrelevant miscompares """
    try:
        return (' '.join(re.split(npatt, s))).strip().lower()
    except TypeError:
        return s
        
class Club:
    """ Keep information about a club """
    
    namegroups = {}
    
    urlfixups = {'clubemail':'mailto', 
                 'clubwebsite':'http',
                 'facebook':'https',
                 'twitter':'https'}

    
    @classmethod
    def fixcn(self, s):
        try:
            return('%d' % int(s))
        except:
            return None
    
    @classmethod
    def setfieldnames(self, names):
        self.fieldnames = names
        self.badnames = ['firstdate', 'lastdate']
        self.goodnames = [n for n in names if n not in self.badnames]

        
    @classmethod
    def setgoodnames(self, names):
        """ Replace the set of "good" names and "bad" names (used in comparisons).
            Does NOT recompute the compare value for previously-defined clubs. """
        self.badnames = []
        self.goodnames = []
        for n in self.fieldnames:
            if n in names:
                self.goodnames.append(n)
            else:
                self.badnames.append(n)

        
        
    @classmethod
    def addfieldnames(self, goodnames, badnames=[]):
        """ Adds fieldnames to the club class.  Returns new fieldnames, if any. """
        newfields = []
        for name in goodnames:
            if name not in self.fieldnames:
                self.fieldnames.append(name)
                self.goodnames.append(name)
                newfields.append(name)
        for name in badnames:
            if name not in self.fieldnames:
                self.fieldnames.append(name)
                self.badnames.append(name)
                newfields.append(name)
        return newfields
        
    @classmethod
    def stringify(self, value):
        """ Convert values coming out of the database to strings """

        # Let's normalize everything to strings/unicode strings
        if isinstance(value, (int, float, bool)):
            value = '%s' % value
        if isinstance(value, bool):
            value = '1' if value else '0'
        elif isinstance(value, (datetime.datetime, datetime.date)):
            value = ('%s' % value)[0:10]

        return value
        
    @classmethod
    def getClubsOn(self, curs, date=None, goodnames=[]):
        """ Get the clubs which were in existence on a specified date (or the last date in the database)
            or the most recent occurrence of each club if date=None (which includes suspended clubs) """
        if date:
            # Make sure it's not past the end of the data
            curs.execute("SELECT MAX(lastdate) from clubs")
            lastdate = self.stringify(curs.fetchone()[0])
            date = min(date, lastdate)
            # And just in case there was no data for the specified date, back up to a date where there
            #   was data
            curs.execute("SELECT MAX(loadedfor) FROM loaded where tablename = 'clubs' AND loadedfor <= %s", (date,))
            date = self.stringify(curs.fetchone()[0])
            curs.execute("SELECT * FROM clubs WHERE firstdate <= %s AND lastdate >= %s", (date, date))
        else:
            tmyearstart = '%d-07-01' % getTMYearFromDB(curs)
            curs.execute("SELECT clubs.* FROM clubs INNER JOIN (SELECT clubnumber, MAX(lastdate) AS m FROM clubs GROUP BY clubnumber) lasts ON lasts.m = clubs.lastdate AND lasts.clubnumber = clubs.clubnumber WHERE lasts.m >= %s", (tmyearstart,))
        # Get the fieldnames before we get anything else:
        fieldnames = [f[0] for f in curs.description]
        if 'fieldnames' not in self.__dict__:
            Club.setfieldnames(fieldnames)
        if goodnames:
            Club.setgoodnames(goodnames)
    
        res = {}
    
        # OK, now build the list of clubs at the beginning of the period
        for eachclub in curs.fetchall():
            club = Club(eachclub, fieldnames)
            res[club.clubnumber] = club
            
        return res
        
    
    def __init__(self, values, fieldnames=None, fillall=False):
        self.cmp = []
        if not fieldnames:
            fieldnames = self.fieldnames
        if fillall:
            # We must ensure all defined fields have a value
            for name in self.fieldnames:
                self.__dict__[name] = ''

        for (name, value) in zip(fieldnames, values):
            value = self.stringify(value)
            if name == 'place':
                value = '\n'.join(value.split(';;'))  ## Clean up the database encoding of newlines in the address
            self.__dict__[name] = value
            if name in self.goodnames and name not in self.badnames:
                self.cmp.append(normalize(value))
                
    def setvalue(self, name, value, evenIfEmpty=False):
        """ Set a single value. """
        value = self.stringify(value)
        if value or evenIfEmpty or name not in self.__dict__:
            self.__dict__[name] = value
            if name not in self.badnames:
                self.cmp.append(normalize(value))
                
    def addvalues(self, values, fieldnames):
        """ Add values to the club; don't change anything already there. """
        for (name, value) in zip(fieldnames, values):
            if name not in self.__dict__:
                self.setvalue(name, value, evenIfEmpty=True)
                    
    def updatevalues(self, values, fieldnames):
        """ Add or replace values to the club. """
        for (name, value) in zip(fieldnames, values):
            self.setvalue(name, value)

     
    def __eq__(self, other):
        return self.cmp == other.cmp
         
    def __ne__(self, other):
        return self.cmp != other.cmp
        
    def delta(self, other):
        """ Return tuples of (name, self, other) for any values which have changed that we care about.
            Items in 'namegroups' are grouped together into one item by the function provided. """
            
        res = []
        namelist = sorted(self.goodnames)
        myng = deepcopy(self.namegroups)
        
        for name in namelist:
            if name in myng:
                # Handle a field which gets a combined value
                fn = myng[name][1]
                if fn:
                    mine = fn(self)   # Get the combined result for me
                    his = fn(other)   # And for the other instance
                else:
                    mine = None
                    his = None
                # Now, inactivate the rest of the items from the list of desired fields
                for n in myng[name][0]:
                    myng[n][1] = None
            else:
                # Just a normal single value
                mine = self.__dict__.get(name,'')
                his = other.__dict__.get(name,'')
            if mine != his:
                res.append((name, mine, his))
        return res
        
    def __repr__(self):
        return '; '.join(['%s = "%s"' % (name, self.__dict__[name]) for name in self.__dict__])
        
    def makeaddress(self):
        if 'fmtaddr' not in self.__class__.__dict__:
            self.__class__.fmtaddr = '%(address)s\n%(city)s, %(state)s  %(zip)s'
        return self.fmtaddr % self.__dict__
        
    def makemeeting(self):
        if 'fmtmeet' not in self.__class__.__dict__:
            self.__class__.fmtmeet = '%(meetingtime)s\n%(meetingday)s'
        return self.fmtmeet % self.__dict__
        
    def getLink(self):
        """ Create the link to Toastmasters' web page for this club """
        namepart = re.sub(r'[^a-z0-9 ]','',self.clubname.lower()).replace(' ','-')
        return 'http://www.toastmasters.org/Find-a-Club/%s-%s' % (self.clubnumber.rjust(8,'0'), namepart)
        
    def fixURLSchemes(self):
        """ Fix nonempty URLs (clubemail, clubwebsite, facebook, twitter) to include
            mailto: or http: if not specified """
        for item in self.urlfixups:
            val = self.__dict__.get(item,'').strip()
            if val:
                self.__dict__[item] = urlsplit(val, self.urlfixups[item]).geturl()

        
    addrgroup = ('address', 'city', 'state', 'zip', 'country')
    for n in addrgroup:
        namegroups[n] = [addrgroup, makeaddress]
    meetgroup = ('meetingtime', 'meetingday')
    for n in meetgroup:
        namegroups[n] = [meetgroup, makemeeting]
