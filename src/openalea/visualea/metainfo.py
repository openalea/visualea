"""Configuration file"""

__license__ = "Cecill-C"
__revision__ = " $Id$"


def get_version():
    "Returns openalea.visualea version."
    from importlib.metadata import metadata
    meta = metadata("openalea.visualea")
    release = meta.get("version")
    return release

url = "http://openalea.rtfd.io"

def get_copyright():

    return "Copyright \xa9 2006-2026 inria/CIRAD/INRAE\n"
