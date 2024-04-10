import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import numpy as np

from .IdentifierUtil import IdentifierUtil


class AttributesUtil(object):
    """
    Utility class to get the default attributes from a DeviceInfo structure. These attributes are
    used to populate the default service attributes when registering a service
    with a device.

    The following attributes are used:

    - device
    - parent_device
    - manufacturer
    - model
    - serial_number
    - user_description

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

        self._ident_util = IdentifierUtil(self._node, self._client_obj)

    def _try_add_identifier(self, o, name, id_):
        if not self._ident_util.IsIdentifierAny(id_):
            o[name] = RR.VarValue(self._ident_util.IdentifierToString(id_), "string")
            return True
        return False

    def _try_add_string(self, o, name, str_):
        if str_ is not None and len(str_) > 0:
            o[name] = RR.VarValue(str_, "string")
            return True
        return False

    def _try_add_identifier_list(self, o, name, id_list):
        tags_str_list = []
        if id_list is not None and len(id_list) > 0:
            for x in id_list:
                if hasattr(x, "data"):
                    x = x.data
                if not self._ident_util.IsIdentifierAny(x):
                    tags_str_list.append(self._ident_util.IdentifierToString(x))
            if len(tags_str_list) > 0:
                o[name] = RR.VarValue(",".join(tags_str_list), "string")
            return True
        return False

    def GetDefaultServiceAttributesFromDeviceInfo(self, device_info):
        """
        Get the default service attributes from a DeviceInfo structure. These attributes are
        used to populate the default service attributes when registering a service.

        :param device_info: The device info structure
        :type device_info: com.robotraconteur.DeviceInfo
        :return: The default service attributes
        :rtype: dict
        """
        o = dict()
        self._try_add_identifier(o, "device", device_info.device)
        self._try_add_identifier(o, "parent_device", device_info.parent_device)
        self._try_add_identifier(o, "manufacturer", device_info.manufacturer)
        self._try_add_identifier(o, "model", device_info.model)
        self._try_add_string(o, "serial_number", device_info.serial_number)
        self._try_add_string(o, "user_description", device_info.user_description)
        if device_info.extended is not None:
            self._try_add_identifier_list(o, "tags", device_info.extended.get("tags"))
        return o
