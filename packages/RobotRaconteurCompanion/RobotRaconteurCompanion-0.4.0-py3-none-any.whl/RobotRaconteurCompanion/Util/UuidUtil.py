import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import numpy as np
import uuid as py_uuid


class UuidUtil(object):
    """
    Utility class for working with Robot Raconteur UUIDs

    :param node: (optional) The Robot Raconteur node to use for parsing. Defaults to RobotRaconteurNode.s
    :type node: RobotRaconteur.RobotRaconteurNode
    :param client_obj: (optional) The client object to use for finding types. Defaults to None
    :type client_obj: RobotRaconteur.ClientObject
    """

    def __init__(self, node=None, client_obj=None):
        if node is None:
            self._node = RRN
        else:
            self._node = node
        self._client_obj = client_obj

        self._uuid_dt = self._node.GetNamedArrayDType("com.robotraconteur.uuid.UUID", self._client_obj)

    def UuidFromPyUuid(self, py_uuid):
        """
        Create a Robot Raconteur UUID from a Python UUID

        :param py_uuid: The Python UUID to convert
        :type py_uuid: uuid.UUID
        :return: The Robot Raconteur UUID
        :rtype: com.robotraconteur.uuid.UUID
        """
        ret_bytes = np.frombuffer(py_uuid.bytes, dtype=np.uint8)
        ret = np.zeros((1,), dtype=self._uuid_dt)
        ret[0]["uuid_bytes"] = ret_bytes
        return ret

    def UuidToPyUuid(self, uuid):
        """
        Create a Python UUID from a Robot Raconteur UUID

        :param uuid: The Robot Raconteur UUID to convert
        :type uuid: com.robotraconteur.uuid.UUID
        :return: The Python UUID
        :rtype: uuid.UUID
        """
        uuid_bytes = uuid["uuid_bytes"].tobytes()
        return py_uuid.UUID(bytes=uuid_bytes)

    def NewRandomUuid(self):
        """
        Create a new random Robot Raconteur UUID

        :return: The new UUID
        :rtype: com.robotraconteur.uuid.UUID
        """
        new_uuid = py_uuid.uuid4()
        return self.UuidFromPyUuid(new_uuid)

    def ParseUuid(self, uuid_str):
        """
        Parse a UUID string into a Robot Raconteur UUID

        :param uuid_str: The UUID string to parse
        :type uuid_str: str
        """
        return self.UuidFromPyUuid(py_uuid.UUID(uuid_str))

    def UuidToString(self, uuid):
        """
        Convert a Robot Raconteur UUID to a string

        :param uuid: The Robot Raconteur UUID to convert
        :type uuid: com.robotraconteur.uuid.UUID
        :return: The UUID string
        :rtype: str
        """
        return str(self.UuidToPyUuid(uuid))
