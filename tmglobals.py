#!/usr/bin/env python
""" Set up for TMSTATS programs:

    1)  Parse arguments (via tmparse)
    2)  Open database (via dbconn)
    3)  Save parms and database as globals
    4)  Establish current TM year
    5)  Establish current date
    6)  Go to the data directory (via tmutil)

"""
import tmutil, tmparms, dbconn, sys
from datetime import date

class Singleton(object):
    def __new__(type, *args, **kwargs):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

class tmglobals(Singleton):
    def __init__(self, *args, **kwargs):
        if args:
            self.setup(args[0],kwargs)
        return

    def setup(self, parms, kwargs):
        self.parms = parms
        self.conn = None
        self.curs = None
        self.tmyear = None
        if kwargs.get('gotodatadir', True):
            tmutil.gotodatadir()
        if kwargs.get('defaultencoding', ''):
            reload(sys).setdefaultencoding(defaultencoding)
        if kwargs.get('parse', True):
            self.parms.parse()
        if kwargs.get('connect', True):
            self.conn = dbconn.dbconn(self.parms.dbhost, self.parms.dbuser, self.parms.dbpass, self.parms.dbname)
            self.curs = self.conn.cursor()
            self.tmyear = tmutil.getTMYearFromDB(self.curs)
        self.today = date.today()
        return self

