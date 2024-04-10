from __future__ import absolute_import

try:
    from .StdRobDef import RegisterStdRobDefServiceTypes
except:
    import warnings
    warnings.warn("Could not initialize RobotRaconteurCompanion.StdRobDef")

try:
    from .InfoParser import InfoParser
except:
    import warnings
    warnings.warn("Could not initialize RobotRaconteurCompanion.InfoParser")
