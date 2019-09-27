#!/usr/bin/env python3
""" Handle parameters for the TMSTATS family of programs.
    Parameters can come on the command line or from the tmstats.ini file.

    Usage:
       Create the tmparms instance.
       If additional parameters are needed, add them to tmparms.parser.
       Call tmparser.parse() to handle common parameters.
       Interpret other parameters in self.args as needed.
    """

import argparse, os, configparser, sys


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


class Singleton(object):
    def __new__(type, *args, **kwargs):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance


class tmparms(Singleton):
    def __init__(self, description='A program in the TMSTATS suite.', configfile='tmstats.ini', includedbparms=True,
                 customformatter=True, **kwargs):
        if self.__dict__.get('parms', False):
            return
        if customformatter is True:
            formatter_class = CustomFormatter
        elif customformatter:
            formatter_class = customformatter
        else:
            formatter_class = None
        if formatter_class:
            self.parser = argparse.ArgumentParser(description=description, formatter_class=formatter_class, **kwargs)
        else:
            self.parser = argparse.ArgumentParser(description=description)
        if os.path.basename(configfile) == configfile:
            # If the configuration file is only a basename, take it from the same directory as the source code
            configfile = os.path.join(sys.path[0], 'tmstats.ini')
        self.parser.add_argument('--configfile', help="INI file with information for this program", default=configfile)
        if includedbparms:
            self.parser.add_argument('--dbname', help="MySQL database to use", dest='dbname')
            self.parser.add_argument('--dbhost', help="host for MySQL database", dest='dbhost')
            self.parser.add_argument('--dbuser', help="user for MySQL database", dest='dbuser')
            self.parser.add_argument('--dbpass', help="password for MySQL database", dest='dbpass')

    def __repr__(self):
        return '\n'.join(['%s: (%s) "%s"' % (k, type(self.__dict__[k]), self.__dict__[k]) for k in self.__dict__ if k != 'parser'])

    def add_argument(self, *args, **kwargs):
        if 'default' in kwargs and isinstance(kwargs['default'], str):
            kwargs['default'] = os.path.expandvars(kwargs['default'])
        self.parser.add_argument(*args, **kwargs)

    def add_argument_group(self, *args, **kwargs):
        return self.parser.add_argument_group(*args, **kwargs)

    def add_mutually_exclusive_group(self, *args, **kwargs):
        return self.parser.add_mutually_exclusive_group(*args, **kwargs)

    def parse(self, sections=None):

        # Parameters are put directly into this object, based on their name in the config file
        #   or the command line.
        # NOTE:  Parameters with default values which evaluate to TRUE will ALWAYS override the file!
        #
        # self.configValues is the result of reading the config file
        # self.args is the result from the parser

        # Parse the command line (in case the configfile has been overridden)
        self.args = self.parser.parse_args()

        # Set values from the configfile
        configParser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        configParser.read(self.args.configfile)

        # Get the default section
        configValues = dict(configParser[configParser.default_section])

        # Add any sections we've been asked to include.  If there is a collision between earlier and
        #   later sections, the later section wins; note that the default section is the earliest one.
        #   We use the consolidated dictionary for interpolation of values from the command line.
        if sections:
            if isinstance(sections, str):
                sections = (sections,)
            for s in sections:
                for name in configParser[s]:
                    configValues[name] = configParser[s][name]
                    
        # Now, put values from the configfile into the parms object:
        for name in configValues:
            self.__dict__[name] = configValues[name]
            
        # Override with non-false values from the command line (or the default).
        # If no value is in the configfile, use the command line or default whether it's true or false.
        # Do interpolation on strings against the consolidated dictionary of values from the configfile.
        
        # We use section and key 'xyzzy' for interpolation; by this point, everything we might 
        # interpolate against has been promoted to the configValues dictionary.
        configParser.remove_section('xyzzy')
        resolver_name = 'xyzzy'
        resolver_section = 'xyzzy'
        configParser.add_section(resolver_section)
        args = vars(self.args)
        for name in list(args.keys()):
            if (args[name] or name not in self.__dict__):
                if isinstance(args[name], str):
                    try:
                        configParser.set(resolver_section, resolver_name, args[name])
                        args[name] = configParser.get(resolver_section, resolver_name, vars=configValues)
                    except ValueError:
                        pass  # Ignore interpolation problems here
                self.__dict__[name] = args[name]

        # And handle dbhost specially to make sure it exists:
        if 'dbhost' not in self.__dict__ or not self.dbhost:
            self.dbhost = 'localhost'


if __name__ == '__main__':
    import tmglobals

    myglobals = tmglobals.tmglobals()
    parms = tmparms()
    myglobals.setup(parms)
    print(parms)
