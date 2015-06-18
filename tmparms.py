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
        
    def __repr__(self):
        return '\n'.join(['%s: "%s"' % (k, self.__dict__[k]) for k in self.__dict__ if k != 'parser'])
        
    def parse(self):

        # Parameters are put directly into this object, based on their name in the YML file
        #   or the command line.
        # NOTE:  Parameters with defaults in the parser will ALWAYS override the file!
        # 
        # self.ymlvalues is the result of reading the YML file
        # self.args is the result from the parser

        # Parse the command line (in case the YMLfile has been overridden)
        self.args = self.parser.parse_args()
        
        # Set values from the YML file
        self.ymlvalues= yaml.load(open(self.args.YMLfile,'r'))
        for name in self.ymlvalues:
            self.__dict__[name] = self.ymlvalues[name]
            
            
        # Override with values from the command line:
        args = vars(self.args)
        for name in args.keys():
            if args[name]:
                self.__dict__[name] = args[name]
                
        # And handle dbhost specially to make sure it exists:
        if 'dbhost' not in self.__dict__:
            self.dbhost = 'localhost'
 

if __name__ == '__main__':
    # Make it easy to run under TextMate
    if 'TM_DIRECTORY' in os.environ:
        os.chdir(os.path.join(os.environ['TM_DIRECTORY'],'data'))
    parms = tmparms()
    parms.parse()
    print parms
