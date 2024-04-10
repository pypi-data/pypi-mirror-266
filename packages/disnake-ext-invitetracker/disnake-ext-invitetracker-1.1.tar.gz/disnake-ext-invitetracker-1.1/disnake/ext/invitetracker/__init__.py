import collections

from .invite_tracker import *

_VersionInfo = collections.namedtuple("_VersionInfo", "major release serial")

version = "1.1"
version_info = _VersionInfo(1, 1, "final", 0)
