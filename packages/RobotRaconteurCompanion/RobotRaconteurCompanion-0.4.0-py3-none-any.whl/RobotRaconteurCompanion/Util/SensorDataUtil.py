import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import numpy as np

from .DateTimeUtil import DateTimeUtil


class SensorDataUtil(object):
    """
    Fill in a SensorDataHeader with the current time and sequence number

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

        self._sensordataheader = self._node.GetStructureType(
            "com.robotraconteur.sensordata.SensorDataHeader", self._client_obj)
        self._sourceinfo = self._node.GetStructureType(
            "com.robotraconteur.sensordata.SensorDataSourceInfo", self._client_obj)
        self._pose_dt = self._node.GetNamedArrayDType("com.robotraconteur.geometry.Pose")

        self._datetime_util = DateTimeUtil(node, client_obj)

    def FillSensorDataHeader(self, device_info, seqno):
        """
        Fill in a SensorDataHeader with the current time and sequence number

        :param device_info: The device info to use for the source info
        :type device_info: com.robotraconteur.device.DeviceInfo
        :param seqno: The sequence number to use
        :type seqno: int
        """
        ret = self._sensordataheader()
        ret.seqno = seqno
        ret.ts = self._datetime_util.TimeSpec2Now(device_info)
        ret.source_info = self._sourceinfo()
        ret.source_info.source = device_info.device
        ret.source_info.source_world_pose = np.zeros((1,), self._pose_dt)
        return ret
