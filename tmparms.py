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
        return '\n'.join(['%s: "%s"' % (k, self.__dict__[k]) for k in self.__dict__ if k != 'parser'])

    def add_argument(self, *args, **kwargs):
        if 'default' in kwargs and isinstance(kwargs['default'], str):
            kwargs['default'] = os.path.expandvars(kwargs['default'])
        self.parser.add_argument(*args, **kwargs)

    def add_argument_group(self, *args, **kwargs):
        return self.parser.add_argument_group(*args, **kwargs)

    def add_mutually_exclusive_group(self, *args, **kwargs):
        return self.parser.add_mutually_exclusive_group(*args, **kwargs)

    def parse(self):

        # Parameters are put directly into this object, based on their name in the config file
        #   or the command line.
        # NOTE:  Parameters with default values which evaluate to TRUE will ALWAYS override the file!
        #
        # self.configvalues is the result of reading the config file
        # self.args is the result from the parser

        # Parse the command line (in case the configfile has been overridden)
        self.args = self.parser.parse_args()

        # Set values from the configfile
        configParser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        configParser.read(self.args.configfile)

        # Now, promote the values in the configuration file to top level.


        self.configvalues = dict(configParser['default'])
        for name in self.configvalues:
            self.__dict__[name] = self.configvalues[name]

        # @@TODO@@ Deal with non-default sections.  Does anything use them yet?

        # Override with non-false values from the command line (or the default).
        # If no value is in the configfile, use the command line or default whether it's true or false.
        # Resolve any strings against the configfile.
        resolver_section = 'internal-resolver'
        resolver_name = 'xyzzy'
        configParser.add_section(resolver_section)
        args = vars(self.args)
        for name in list(args.keys()):
            if (args[name] or name not in self.__dict__):
                if isinstance(args[name], str):
                    configParser.set(resolver_section, resolver_name, args[name])
                    args[name] = configParser.get(resolver_section, resolver_name)
                self.__dict__[name] = args[name]

        # And handle dbhost specially to make sure it exists:
        if 'dbhost' not in self.__dict__ or not self.dbhost:
            self.dbhost = 'localhost'


if __name__ == '__main__':
    import tmglobals

    globals = tmglobals.tmglobals()
    parms = tmparms()
    globals.setup(parms)
    print(parms)
