import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import numpy as np
import re

from .LocalIdentifiersManager import LocalIdentifiersManager
from .IdentifierUtil import IdentifierUtil
from ..InfoParser import InfoParser


class InfoFileLoader(object):
    """
    Utility class to load device info Yaml structures from file

    See the Robot Raconteur camera driver for an example of using this class.

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

        self._info_parser = InfoParser(self._node, self._client_obj)
        self._id_manager = LocalIdentifiersManager(self._node, self._client_obj)
        self._id_util = IdentifierUtil(self._node, self._client_obj)

    def _load_device_identifier(self, info_file, category):

        if hasattr(info_file, "device_info"):
            if info_file is not None and info_file.device_info is not None and info_file.device_info.device is not None \
                    and not self._id_util.IsIdentifierAnyName(info_file.device_info.device) and \
                    self._id_util.IsIdentifierAnyUuid(info_file.device_info.device):

                dev_id, lock_fd = self._id_manager.GetIdentifierForNameAndLock(
                    category, info_file.device_info.device.name)
                info_file.device_info.device = dev_id
                return True, dev_id, lock_fd
            return False, None, None
        elif hasattr(info_file, "device"):
            if info_file is not None and info_file.device \
                    and not self._id_util.IsIdentifierAnyName(info_file.device) and \
                    self._id_util.IsIdentifierAnyUuid(info_file.device):

                dev_id, lock_fd = self._id_manager.GetIdentifierForNameAndLock(category, info_file.device.name)
                info_file.device = dev_id
                return True, dev_id, lock_fd
            return False, None, None
        return False, None, None

    def LoadInfoFileFromString(self, info_text, info_type_name, category="unspecified"):
        """
        Load a device info Yaml structure from a string and assign a device identifier

        In most cases the category should be set to "device".

        :param info_text: The info Yaml structure to load
        :type info_text: str
        :param info_type_name: The type name of the info Yaml structure
        :type info_type_name: str
        :param category: (optional) The category of the device identifier. Defaults to "unspecified".
        :type category: str
        :return: The loaded info Yaml structure and the device identifier lock file descriptor
        :rtype: tuple
        """
        info = self._info_parser.ParseInfoString(info_text, info_type_name)
        _, _, fds = self._load_device_identifier(info, category)
        return info, fds

    def LoadInfoFileFromDict(self, info_dict, info_type_name, category="unspecified"):
        """
        Load a device info Yaml structure from a dictionary and assign a device identifier

        In most cases the category should be set to "device".

        :param info_dict: The dictionary containing the info parsed from a Yaml file
        :type info_dict: dict
        :param info_type_name: The type name of the info Yaml structure
        :type info_type_name: str
        :param category: (optional) The category of the device identifier. Defaults to "unspecified".
        :type category: str
        :return: The loaded info Yaml structure and the device identifier lock file descriptor
        :rtype: tuple
        """
        info = self._info_parser.ParseInfoDict(info_dict, info_type_name)
        _, _, fds = self._load_device_identifier(info, category)
        return info, fds

    def LoadInfoFile(self, file_name, info_type_name, category="unspecified"):
        """
        Load a device info Yaml structure from a file and assign a device identifier

        In most cases the category should be set to "device".

        :param file_name: The file name of the info Yaml structure to load
        :type file_name: str
        :param info_type_name: The type name of the info Yaml structure
        :type info_type_name: str
        :param category: (optional) The category of the device identifier. Defaults to "unspecified".
        :type category: str
        :return: The loaded info Yaml structure and the device identifier lock file descriptor
        :rtype: tuple
        """
        info = self._info_parser.ParseInfoFile(file_name, info_type_name)
        _, _, fds = self._load_device_identifier(info, category)
        return info, fds
