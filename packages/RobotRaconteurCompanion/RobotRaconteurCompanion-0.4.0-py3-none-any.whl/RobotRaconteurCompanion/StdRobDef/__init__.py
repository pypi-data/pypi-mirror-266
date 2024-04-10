
STANDARD_ROBDEF_NAMES = [
    'com.robotraconteur.action',
    'com.robotraconteur.actuator',
    'com.robotraconteur.bignum',
    'com.robotraconteur.color',
    'com.robotraconteur.datatype',
    'com.robotraconteur.datetime.clock',
    'com.robotraconteur.datetime',
    'com.robotraconteur.device.clock',
    'com.robotraconteur.device.isoch',
    'com.robotraconteur.device',
    'com.robotraconteur.eventlog',
    'com.robotraconteur.fiducial',
    'com.robotraconteur.geometry',
    'com.robotraconteur.geometry.shapes',
    'com.robotraconteur.geometryf',
    'com.robotraconteur.geometryi',
    'com.robotraconteur.gps',
    'com.robotraconteur.hid.joystick',
    'com.robotraconteur.identifier',
    'com.robotraconteur.image',
    'com.robotraconteur.imaging.camerainfo',
    'com.robotraconteur.imaging',
    'com.robotraconteur.imu',
    'com.robotraconteur.laserscan',
    'com.robotraconteur.laserscanner',
    'com.robotraconteur.lighting',
    'com.robotraconteur.objectrecognition',
    'com.robotraconteur.octree',
    'com.robotraconteur.param',
    'com.robotraconteur.pid',
    'com.robotraconteur.pointcloud',
    'com.robotraconteur.pointcloud.sensor',
    'com.robotraconteur.resource',
    'com.robotraconteur.resource.device',
    'com.robotraconteur.robotics.joints',
    'com.robotraconteur.robotics.payload',
    'com.robotraconteur.robotics.robot',
    'com.robotraconteur.robotics.tool',
    'com.robotraconteur.robotics.trajectory',
    'com.robotraconteur.sensor',
    'com.robotraconteur.sensordata',
    'com.robotraconteur.servo',
    'com.robotraconteur.signal',
    'com.robotraconteur.units',
    'com.robotraconteur.uuid'
]

STANDARD_ROBDEF_TEXT = {}


def _load_standard_robdef_text():
    import importlib_resources
    for n in STANDARD_ROBDEF_NAMES:
        robdef_text = (importlib_resources.files(__package__) / (n + '.robdef')).read_text()
        STANDARD_ROBDEF_TEXT[n] = robdef_text


_load_standard_robdef_text()


def RegisterStdRobDefServiceTypes(node):
    """
    Register standard Robot Raconteur service types to a node. This function will call RegisterServiceTypes() for
    the standard services types to register them into the node.

    :param node: The node to register the service types to. Typically this will be ``RRN`` for the default node.
    :type node: RobotRaconteur.RobotRaconteurNode
    """

    robdefs_text = list(STANDARD_ROBDEF_TEXT.values())
    node.RegisterServiceTypes(robdefs_text)
