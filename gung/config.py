import ConfigParser
import os


class GungConfig(object):
    """
    Singleton class that holds the config of the whole Gung.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if GungConfig._instance is None:
            GungConfig._instance = ConfigParser.ConfigParser()

            try:
                GungConfig._instance.readfp(open(os.path.dirname(__file__) + os.path.sep + "gung.cfg", "r"))
            except ConfigParser.ParsingError, e:
                print "Failed to read config file."
                print e
        return GungConfig._instance
