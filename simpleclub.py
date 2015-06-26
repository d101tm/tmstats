""" Simple class to maintain information about a club.
"""

import datetime, re

class Club:
    """ Keep information about a club """
    
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
        if isinstance(value, (int, long, float, bool)):
            value = '%s' % value
        if isinstance(value, bool):
            value = '1' if value else '0'
        elif isinstance(value, (datetime.datetime, datetime.date)):
            value = ('%s' % value)[0:10]

        return value
        
    @classmethod
    def getClubsOn(self, date, curs, setfields=False):
        """ Get the clubs which were in existence on a specified date 
            or the most recent occurrence of each club if date=None """
        if date:
            curs.execute("SELECT * FROM clubs WHERE firstdate <= %s AND lastdate >= %s", (date, date))
        else:
            curs.execute("SELECT clubs.* FROM clubs INNER JOIN (SELECT clubnumber, MAX(lastdate) AS m FROM clubs GROUP BY clubnumber) lasts ON lasts.m = clubs.lastdate AND lasts.clubnumber = clubs.clubnumber;")
        # Get the fieldnames before we get anything else:
        fieldnames = [f[0] for f in curs.description]
        if setfields:
            Club.setfieldnames(fieldnames)
    
        res = {}
    
        # OK, now build the list of clubs at the beginning of the period
        for eachclub in curs.fetchall():
            club = Club(eachclub, fieldnames)
            res[club.clubnumber] = club
            
        return res
        
    
    def __init__(self, values, fieldnames=None):
        self.cmp = []
        if not fieldnames:
            fieldnames = self.fieldnames
        for (name, value) in zip(fieldnames, values):
            value = self.stringify(value)
            self.__dict__[name] = value
            if name not in self.badnames:
                self.cmp.append(value)
                
    def addvalues(self, values, fieldnames):
        """ Add values to the club; don't change anything already there. """
        for (name, value) in zip(fieldnames, values):
            if name not in self.__dict__:
                # Let's normalize everything to strings/unicode strings
                value = self.stringify(value)
                self.__dict__[name] = value
                if name not in self.badnames:
                    self.cmp.append(value)
     
    def __eq__(self, other):
        return self.cmp == other.cmp
         
    def __ne__(self, other):
        return self.cmp != other.cmp
        
    def delta(self, other):
        """ Return tuples of (name, self, other) for any values which have changed """
        res = []
        for name in self.goodnames:
            if self.__dict__[name] != other.__dict__[name]:
                res.append((name, self.__dict__[name], other.__dict__[name]))
        return res
        
    def __repr__(self):
        return '; '.join(['%s = "%s"' % (name, self.__dict__[name]) for name in self.__dict__])
        
    def getLink(self):
        """ Create the link to Toastmasters' web page for this club """
        namepart = re.sub(r'[^a-z0-9 ]','',self.clubname.lower()).replace(' ','-')
        return 'http://www.toastmasters.org/Find-a-Club/%s-%s' % (self.clubnumber.rjust(8,'0'), namepart)
