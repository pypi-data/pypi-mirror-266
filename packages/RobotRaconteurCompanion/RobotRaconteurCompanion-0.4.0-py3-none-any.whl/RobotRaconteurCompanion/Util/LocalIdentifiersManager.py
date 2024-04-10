
import os
import ctypes
from pathlib import Path
import re
import sys
import RobotRaconteur as RR
import uuid
import numpy as np
import stat
import errno


class _LocalIdentifiersManagerFD(object):
    """
    Class to hold lock on device identifier file
    """

    def __init__(self, fd):
        self.fd = fd

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if self.fd is not None:
            fd = self.fd
            self.fd = None
            del fd


class LocalIdentifiersManager(object):
    """
    Utility class to manage device identifiers and locks

    See the Robot Raconteur camera driver for an example of using this class.

    Users do not normally need to use this class directly.

    :param node: (optional) The Robot Raconteur node to use for parsing. Defaults to RobotRaconteurNode.s
    :type node: RobotRaconteur.RobotRaconteurNode
    :param client_object: (optional) The client object to use for finding types. Defaults to None
    :type client_object: RobotRaconteur.ClientObject
    """

    def __init__(self, node, client_object=None):
        self._node = node
        self._client_object = client_object

    def GetIdentifierForNameAndLock(self, category, name):
        """
        Get a device identifier for a given name and lock the identifier file for exclusive access.
        The category should be "device" for most devices.

        :param category: The category of the identifier
        :type category: str
        :param name: The name of the identifier
        :type name: str
        :return: The identifier and lock
        :rtype: (RobotRaconteur.Identifier, LocalIdentifiersManagerFD)
        """

        assert re.match("^[a-zA-Z][a-zA-Z0-9_\\.\\-]*$", name) is not None, "Invalid identifier name"
        category2 = category.lower()

        node_dirs = self._node.GetNodeDirectories()
        p = RR.GetUuidForNameAndLock(node_dirs, name, ["identifiers", category2])

        f = p.fd
        f_text = p.uuid.ToString("D")

        ident_uuid = uuid.UUID(str(f_text))

        ident_type = self._node.GetStructureType("com.robotraconteur.identifier.Identifier", self._client_object)
        uuid_dtype = self._node.GetNamedArrayDType("com.robotraconteur.uuid.UUID", self._client_object)
        ret = ident_type()
        ret.name = name
        ret.uuid = np.zeros((1,), dtype=uuid_dtype)
        ret.uuid["uuid_bytes"] = np.frombuffer(ident_uuid.bytes, dtype=np.uint8)

        return ret, _LocalIdentifiersManagerFD(f)
