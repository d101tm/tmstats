#!/usr/bin/env python3
""" Set up for TMSTATS programs:

    1)  Parse arguments (via tmparse)
    2)  Open database (via dbconn)
    3)  Save parms and database as globals
    4)  Establish current TM year
    5)  Establish current date
    6)  Go to the data directory (via tmutil)

"""
import dbconn, sys, os
from datetime import date
import imp

class Singleton(object):
    def __new__(type, *args, **kwargs):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

class tmglobals(Singleton):
    def __init__(self, *args, **kwargs):
        if args:
            self.setup(*args,**kwargs)
        return

    def setup(self, *args, **kwargs):
        self.parms = args[0]
        self.conn = None
        self.curs = None
        self.tmyear = None
        if kwargs.get('gotodatadir', True):
            curdir = os.path.realpath(os.curdir)  # Get the canonical directory
            lastpart = curdir.split(os.sep)[-1]
            if lastpart.lower() != 'data':
                os.chdir('data')   # Fails if there is no data directory; that is intentional.
        if kwargs.get('defaultencoding', ''):
            imp.reload(sys).setdefaultencoding(defaultencoding)
        if kwargs.get('parse', True):
            self.parms.parse()
        if kwargs.get('connect', True):
            self.conn = dbconn.dbconn(self.parms.dbhost, self.parms.dbuser, self.parms.dbpass, self.parms.dbname)
            self.curs = self.conn.cursor()
            self.curs.execute("SELECT MAX(tmyear) FROM lastfor")
            self.tmyear = self.curs.fetchone()[0]
        self.today = date.today()
        return self

if __name__ == '__main__':
    import tmparms
    p = tmparms.tmparms()
    g = tmglobals()
    g.setup(p)
