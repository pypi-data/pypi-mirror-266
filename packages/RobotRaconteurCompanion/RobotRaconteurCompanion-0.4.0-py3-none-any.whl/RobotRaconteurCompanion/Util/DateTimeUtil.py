import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import datetime
import numpy as np
import math


class DateTimeUtil(object):
    """
    Utility class to populate Robot Raconteur time structures

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

        self._datetimeutc_dt = self._node.GetPodDType("com.robotraconteur.datetime.DateTimeUTC", self._client_obj)
        self._datetimelocal = self._node.GetStructureType("com.robotraconteur.datetime.DateTimeLocal", self._client_obj)
        self._timespec2_dt = self._node.GetPodDType("com.robotraconteur.datetime.TimeSpec2", self._client_obj)
        self._timespec3_dt = self._node.GetNamedArrayDType("com.robotraconteur.datetime.TimeSpec3", self._client_obj)
        self._devicetime_dt = self._node.GetPodDType("com.robotraconteur.device.clock.DeviceTime", self._client_obj)

        self._datetime_const = self._node.GetConstants("com.robotraconteur.datetime")
        self._clock_codes = self._datetime_const["ClockTypeCode"]

    def UtcNow(self, device_info=None):
        """
        Get the current DateTimeUTC Time from the node

        :param device_info: (optional) The device info structure to use for the clock UUID. Defaults to None
        :type device_info: com.robotraconteur.device.DeviceInfo
        :return: The current UTC time
        :rtype: com.robotraconteur.datetime.DateTimeUTC
        """
        now_dt = self._node.NowUTC()
        now = (now_dt - datetime.datetime(1970, 1, 1, 0, 0, 0, 0)).total_seconds()
        ret = np.zeros((1,), dtype=self._datetimeutc_dt)
        ret[0]["seconds"] = int(math.floor(now))
        ret[0]["nanoseconds"] = int((now % 1.0) * 1e9)
        ret[0]["clock_info"]["clock_type"] = self._clock_codes["default"]
        if device_info is not None and device_info.device is not None:
            ret[0]["clock_info"]["clock_uuid"] = device_info.device.uuid
        return ret

    def TimeSpec2Now(self, device_info=None):
        """
        Get the current TimeSpec from the node, stored as TimeSpec2

        TimeSpec is based on the performance counter, and is not guaranteed to be
        synchronized between nodes or with the system real-time clock. It is expected
        to be close to the system real-time clock, but may drift over time and is
        guaranteed to remain stable even if the system real-time clock is changed.

        :param device_info: (optional) The device info structure to use for the clock UUID. Defaults to None
        :type device_info: com.robotraconteur.device.DeviceInfo
        :return: The current TimeSpec as TimeSpec2
        :rtype: com.robotraconteur.datetime.TimeSpec2
        """
        now_ts = self._node.NowTimeSpec()
        ret = np.zeros((1,), dtype=self._timespec2_dt)
        ret[0]["seconds"] = now_ts.seconds
        ret[0]["nanoseconds"] = now_ts.nanoseconds
        ret[0]["clock_info"]["clock_type"] = self._clock_codes["default"]
        if device_info is not None and device_info.device is not None:
            ret[0]["clock_info"]["clock_uuid"] = device_info.device.uuid
        return ret

    def TimeSpec3Now(self):
        """
        Get the current TimeSpec from the node, stored as TimeSpec3

        The TimeSpec3 is a 64-bit integer representing microseconds since the epoch
        of the real-time clock. It is intended to be a compact representation of the
        current time that can be used for timestamping data.

        TimeSpec is based on the performance counter, and is not guaranteed to be
        synchronized between nodes or with the system real-time clock. It is expected
        to be close to the system real-time clock, but may drift over time and is
        guaranteed to remain stable even if the system real-time clock is changed.

        :return: The current TimeSpec as TimeSpec3
        :rtype: com.robotraconteur.datetime.TimeSpec3
        """
        now_ts = self._node.NowTimeSpec()
        ret = np.zeros((1,), dtype=self._timespec3_dt)
        ret[0]["microseconds"] = now_ts.seconds * 1e6 + now_ts.nanoseconds * 1e-3
        return ret

    def FillDeviceTime(self, device_info, seqno):
        """
        Fill a DeviceTime structure with the current time

        :param device_info: The device info structure to use for the clock UUID
        :type device_info: com.robotraconteur.device.DeviceInfo
        :param seqno: The sequence number to use
        :type seqno: int
        :return: The DeviceTime structure
        :rtype: com.robotraconteur.device.clock.DeviceTime
        """
        ret = np.zeros((1,), self._devicetime_dt)
        ret[0]["device_seqno"] = seqno
        ret[0]["device_ts"] = self.TimeSpec2Now(device_info)
        ret[0]["device_utc"] = self.UtcNow(device_info)
        return ret
