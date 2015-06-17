#!/usr/bin/python
""" Handle parameters for the TMSTATS family of programs.
    Parameters can come on the command line or from the tmstats.yml file.
    
    Usage:
       Create the tmparms instance.
       If additional parameters are needed, add them to tmparms.parser.
       Call tmparser.parse() to handle common parameters.
       Interpret other parameters in self.args as needed.
    """

import argparse, yaml, os


class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance
    
class tmparms(Singleton):
    def __init__(self):
        if self.__dict__.get('parms', False):
            return
        self.parser = argparse.ArgumentParser(description="Process parameters for the TMSTATS suite of programs.")
        self.parser.add_argument('YMLfile', help="YML file with information such as database, user, etc...", default="tmstats.yml", nargs='?')
        self.parser.add_argument('--dbname', help="MySQL database to use", dest='dbname')
        self.parser.add_argument('--dbhost', help="host for MySQL database", dest='dbhost')
        self.parser.add_argument('--dbuser', help="user for MySQL database", dest='dbuser')
        self.parser.add_argument('--dbpass', help="password for MySQL database", dest='dbpass')
        
        
    def parse(self):
        # Actually use the parameters.  Handle the general parameters here; others are left to the caller to interpret.
        
        # Now merge parameters with values from the YML file; parameters override the file.
        # Known parameters here go directly into the tmparms (self) object; others go into self.args.
        # Parameters read from the YML file go into self.ymlvalues
        self.args = self.parser.parse_args()
        self.ymlvalues= yaml.load(open(self.args.YMLfile,'r'))
        self.dbhost = self.args.dbhost if self.args.dbhost else self.ymlvalues.get('dbhost', 'localhost')
        self.dbname = self.args.dbname if self.args.dbname else self.ymlvalues.get('dbname', '')
        self.dbuser = self.args.dbuser if self.args.dbuser else self.ymlvalues.get('dbuser', '')
        self.dbpass = self.args.dbpass if self.args.dbpass else self.ymlvalues.get('dbpass', '')

if __name__ == '__main__':
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
    parms = tmparms()
    parms.parse()
    show = ['dbhost', 'dbname', 'dbuser', 'dbpass', 'args']
    for k in show:
        print k, parms.__dict__[k]