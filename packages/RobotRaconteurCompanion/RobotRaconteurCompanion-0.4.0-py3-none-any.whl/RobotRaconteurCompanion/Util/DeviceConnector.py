import threading
import RobotRaconteur as RR
import collections.abc
import uuid as py_uuid
from contextlib import suppress
import yaml


class DeviceConnectorDetails:
    """
    Device connection information for use with DeviceConnector class.

    The DeviceConnectorDetails contains information that is used by the DeviceConnector class to connect to devices.
    The DeviceConnector can connect to devicues using three different methods:

        1. Discovery devices using device identifier (name, uuid) in combination with optional serial
           number and/or device tags
        2. Connection using a list of URLs. Using URLs is the most direct way to connect to a device.
        3. Connection using specified list of service root object types and optional subscription filter.

    Different combinations of fields are valid depending on the connection method used. See the DeviceConnector
    documentation for more information on how to use the DeviceConnectorDetails class.

    :ivar device_nickname: The nickname of the device
    :vartype device_nickname: str
    :ivar device: The device identifier (name, uuid) of the device. This can be either a string, a dictionary with
                    "name" and "uuid" keys, or a com.robotraconteur.identifier.Identifier structure
    :vartype device: str | dict | com.robotraconteur.identifier.Identifier
    :ivar serial_number: The serial number of the device
    :vartype serial_number: str
    :ivar tags: The tags of the device. This a list of strings, a list of a dictionaries with "name" and "uuid" keys,
                    or a list com.robotraconteur.identifier.Identifier structure in any combination
    :vartype tags: list[str | dict | com.robotraconteur.identifier.Identifier]
    :ivar tag_match_operation: The operation to use when matching tags. Can be "and", "or", "nand", or "nor"
    :vartype tag_match_operation: str
    :ivar service_nodes: A list of RobotRaconteur.SubscriptionFilterNode to use for service discovery. This is intended
                            for advanced users needing to provide authentication or other advanced options.
    :vartype service_nodes: list[RobotRaconteur.SubscriptionFilterNode]
    :ivar transport_schemes: A list of transport schemes to use for service discovery. This is intended for advanced
                                users needing to provide authentication or other advanced options.
    :vartype transport_schemes: list[str]
    :ivar urls: A list of URLs to use for direct connection to the device
    :vartype urls: str | list[str]
    :ivar url_auth: The username and password to use for authentication when connecting using URLs
    :vartype url_auth: RobotRaconteur.SubscriptionFilterNode
    :ivar root_object_type: The root object type to use for service discovery. This is a list of strings
    :vartype root_object_type: str | list[str]
    :ivar subscription_filter: The subscription filter to use for service discovery.
    :vartype subscription_filter: RobotRaconteur.ServiceSubscriptionFilter
    :ivar max_connections: The maximum number of connections to the device. Defaults to 10. Should be set to 1 for
                            connecting to a single device
    :vartype max_connections: int

    :param device_nickname: The nickname of the device
    :type device_nickname: str
    :param device: The device identifier (name, uuid) of the device. This can be either a string, a dictionary with
                    "name" and "uuid" keys, or a com.robotraconteur.identifier.Identifier structure
    :type device: str | dict | com.robotraconteur.identifier.Identifier
    :param serial_number: The serial number of the device
    :type serial_number: str
    :param tags: The tags of the device. This a list of strings, a list of a dictionaries with "name" and "uuid" keys,
                    or a list com.robotraconteur.identifier.Identifier structure in any combination
    :type tags: list[str | dict | com.robotraconteur.identifier.Identifier]
    :param tag_match_operation: The operation to use when matching tags. Can be "and", "or", "nand", or "nor"
    :type tag_match_operation: str
    :param service_nodes: A list of RobotRaconteur.SubscriptionFilterNode to use for service discovery. This is intended
                            for advanced users needing to provide authentication or other advanced options.
    :type service_nodes: list[RobotRaconteur.SubscriptionFilterNode]
    :param transport_schemes: A list of transport schemes to use for service discovery. This is intended for advanced
                                users needing to provide authentication or other advanced options.
    :type transport_schemes: list[str]
    :param urls: A list of URLs to use for direct connection to the device
    :type urls: str | list[str]
    :param url_auth: The username and password to use for authentication when connecting using URLs
    :type url_auth: RobotRaconteur.SubscriptionFilterNode
    :param root_object_type: The root object type to use for service discovery. This is a list of strings
    :type root_object_type: str | list[str]
    :param subscription_filter: The subscription filter to use for service discovery.
    :type subscription_filter: RobotRaconteur.ServiceSubscriptionFilter
    :param max_connections: The maximum number of connections to the device. Defaults to 10. Should be set to 1 for
                            connecting to a single device
    :type max_connections: int
    """

    def __init__(self, device_nickname, device=None, serial_number=None, tags=None, tag_match_operation="and",
                 service_nodes=None,
                 transport_schemes=None, urls=None, url_auth=None, root_object_type=None, subscription_filter=None,
                 max_connections=10):
        if not any([device is not None, serial_number is not None, urls is not None, root_object_type is not None]):
            raise RR.InvalidArgumentException(
                "At least one of device, serial_number, urls, or root_object_type must be specified")

        if (any([device is not None, serial_number is not None, tags is not None]) and any([urls is not None, url_auth is not None, subscription_filter is not None])):
            raise RR.InvalidArgumentException(
                "If device, serial_number, or tags are specified, urls and subscription_filter must not be specified")

        if (urls is not None and any([subscription_filter is not None, service_nodes is not None, transport_schemes is not None])):
            raise RR.InvalidArgumentException(
                "If urls are specified, service_nodes, transport_schemes, and subscription_filter must not be specified")
        if (subscription_filter is not None and any([device is not None, serial_number is not None, tags is not None, service_nodes is not None, transport_schemes is not None])):
            raise RR.InvalidArgumentException(
                "If subscription_filter is specified, device, serial_number, tags, service_nodes, and transport_schemes must not be specified")

        self.device_nickname = device_nickname
        self.device = device
        self.serial_number = serial_number
        self.tags = tags
        self.service_nodes = service_nodes
        self.urls = urls
        self.root_object_type = root_object_type
        self.subscription_filter = subscription_filter
        self.transport_schemes = transport_schemes
        self.url_auth = url_auth
        self.max_connections = max_connections
        self.tag_match_operation = tag_match_operation


class DeviceConnector:
    """
    Device connection manager for connecting to devices using Robot Raconteur.

    The DeviceConnector class is designed to simplify connecting to devices using Robot Raconteur. Finding and
    connecting to multiple services can be complex, especially when using advanced features such as service
    discovery filters. The DeviceConnector takes advantage of the "device" concept introduced by the Robot Raconteur
    standard types. The "device" concept introduces the `com.robotraconteur.device.Device` interface, which provides
    the structure `com.robotraconteur.device.DeviceInfo` containing metadata about the device. The "device" concept
    provides a more descriptive way to identify, connect, and interrogate devices.

    Three fields in the `com.robotraconteur.device.DeviceInfo` structure are used to identify devices by the DeviceConnector:

        1. `device`: The device identifier (name and/or uuid) of the device.
        2. `serial_number`: The serial number of the device.
        3. `tags`: A list of tags associated with the device. These tags are typically strings or identifiers.

    For the "device" concept, an identifier is a combination of a human readable name and a UUID. The name is not
    guaranteed to be unique, but the combination of the name and UUID is expected unique. The UUID should be used
    in a production environment, but the simple name can be used for testing and development.

    The combination of `device`, `serial_number`, and `tags` is used to generate a `ServiceSubscriptionFilter` that
    is used to create a subscription to the device.

    The DeviceConnector is used by software like the PyRI Open Source Teaching Pendant to connect to devices. The
    DeviceConnector should be used by production level software that provides the option to users to select and
    connect to devices.

    The DeviceConnectorDetails structure is used to provide information to the DeviceConnector about how to connect
    to a device. See the DeviceConnectorDetails documentation for more information on each field.
    DeviceConnectorDetails contains information that is used by the DeviceConnector class to connect to devices.
    The DeviceConnector can connect to devicues using three different methods:

        1. Discovery devices using device identifier (name, uuid) in combination with optional serial
           number and/or device tags
        2. Connection using a list of URLs. Using URLs is the most direct way to connect to a device.
        3. Connection using specified list of service root object types and optional subscription filter.

    Different combinations of fields are valid depending on the connection method used.

    The following fields are used to connect to devices with the methods described above:

        1. `device`, `serial_number`, `tags`, `tag_match_operation`, `service_nodes`, `transport_schemes`, `max_connections`
        2. `urls`, `url_auth`
        3. `root_object_type`, `subscription_filter`

    For all methods, the `device_nickname` field is used to identify the device in the DeviceConnector and must
    be unique.

    The device details can also be loaded from a YAML file using the `devices_yaml_f` parameter, or using the
    utility functions `load_device_details_from_yaml`, `load_device_details_from_yaml_path`, and
    `load_device_details_from_yaml_dict`.

    The YAML file should match the following example format:

    ..  code-block:: yaml

        devices:
            device1:
                # Connect to device using URLs
                urls: rr+intra:///?nodename=server_node&service=robot1
            device2:
                # Connect to device using device identifier, serial number, and tags
                device: robot2
                serial_number: "1234"
                tags:
                - tag1
                - tag2
            device3:
                # Connect to device using device identifier and tags
                device:
                    name: robot3
                    uuid: "b92fda92-c74e-4fd1-8174-0163b4dc182a"
                tags:
                - name: tag1
                uuid: "a9d4e339-f248-49c7-9443-e2f3ebba9c02"
                - tag2
            device4:
                # Match any tags or serial number
                device: robot3

    Use io.StringIO to load the YAML from a string.

    :param device_list: (optional) A list of DeviceConnectorDetails to connect to devices
    :type device_list: list[DeviceConnectorDetails]
    :param devices_yaml_f: (optional) A file object containing YAML formatted device details
    :type devices_yaml_f: file
    :param autoconnect: (optional) If True, the DeviceConnector will automatically connect to devices
    :type autoconnect: bool
    :param node: (optional) The Robot Raconteur node to use for parsing. Defaults to RobotRaconteurNode.s
    :type node: RobotRaconteur.RobotRaconteurNode
    """

    def __init__(self, device_list=None, devices_yaml_f=None, autoconnect=True, node=None):
        self._lock = threading.Lock()
        if node is None:
            self._node = RR.RobotRaconteurNode.s
        else:
            self._node = node

        self.subscription_manager = RR.ServiceSubscriptionManager(node=self._node)

        self._autoconnect = autoconnect

        if devices_yaml_f is not None:
            if device_list is not None:
                raise RR.InvalidArgumentException("Cannot specify both device_list and devices_yaml_f")
            device_list = load_device_details_from_yaml(devices_yaml_f)

        if device_list is not None:
            try:
                for device in device_list:
                    self._do_update_device(device)
            except:
                with suppress(Exception):
                    self.subscription_manager.Close()
                raise

    def _do_update_device(self, device_details, force_connect=False):
        sub_details = _device_details_to_subscription_details(
            self._node, device_details.device_nickname, device_details)
        sub_details.Enabled = self._autoconnect or force_connect
        self.subscription_manager.AddSubscription(sub_details)

    def AddDevice(self, device_details, force_connect=False):
        """
        Add a device to the DeviceConnector

        :param device_details: The device details to add
        :type device_details: DeviceConnectorDetails
        """

        self._do_update_device(device_details, force_connect)

    def RemoveDevice(self, device_nickname, close=True):
        """
        Remove a device from the DeviceConnector

        :param device_nickname: The nickname of the device to remove
        :type device_nickname: str
        :param close: (optional) If True, close the device connection
        :type close: bool
        """

        self.subscription_manager.RemoveSubscription(device_nickname, close)

    def ConnectDevice(self, device_nickname):
        """
        Connect to a device previously added to the DeviceConnector but not connected

        :param device_nickname: The nickname of the device to connect
        :type device_nickname: str
        """

        self.subscription_manager.EnableSubscription(device_nickname)

    def DisconnectDevice(self, device_nickname, close=True):
        """
        Disconnect from a device previously connected to the DeviceConnector

        :param device_nickname: The nickname of the device to disconnect
        :type device_nickname: str
        :param close: (optional) If True, close the device subscription
        :type close: bool
        """

        self.subscription_manager.DisableSubscription(device_nickname, close)

    def GetDevice(self, device_nickname, force_create=False):
        """
        Get a the subscription to a device previously added to the DeviceConnector

        :param device_nickname: The nickname of the device to get
        :type device_nickname: str
        :param force_create: (optional) If True, create the subscription if it does not exist
        :type force_create: bool
        :return: The subscription to the device
        :rtype: RobotRaconteur.ServiceSubscription
        """

        return self.subscription_manager.GetSubscription(device_nickname, force_create)

    def TryGetDevice(self, device_nickname):
        """
        Try to get a the subscription to a device previously added to the DeviceConnector

        :param device_nickname: The nickname of the device to get
        :type device_nickname: str
        :return: A tuple containing a boolean indicating if the device was found and the subscription
        :rtype: (bool, RobotRaconteur.ServiceSubscription)
        """
        try:
            return True, self.get_device(device_nickname)
        except:
            return False, None

    def Close(self):
        """
        Close the DeviceConnector and all subscriptions
        """

        self.subscription_manager.Close()

    @property
    def DeviceNicknames(self):
        """
        Get a list of device nicknames

        :return: A list of device nicknames
        :rtype: list[str]
        """
        return self.subscription_manager.SubscriptionNames


def _device_details_to_subscription_details(node, nickname, device_details):
    if device_details.urls is not None:
        url_param = device_details.urls
        if not isinstance(device_details.urls, collections.abc.Sequence) and not isinstance(device_details.urls, str):
            url_param = [device_details.urls]
        username = None
        credentials = None
        if device_details.url_auth is not None:
            username = device_details.url_auth.username
            credentials = device_details.url_auth.credentials

        return RR.ServiceSubscriptionManagerDetails(Name=nickname,
                                                    ConnectionMethod=RR.ServiceSubscriptionManager_CONNECTION_METHOD_URL,
                                                    Urls=url_param, UrlUsername=username, UrlCredentials=credentials)
    elif device_details.subscription_filter is not None:
        return RR.ServiceSubscriptionManagerDetails(Name=nickname,
                                                    ConnectionMethod=RR.ServiceSubscriptionManager_CONNECTION_METHOD_TYPE,
                                                    Filter=device_details.subscription_filter,
                                                    ServiceTypes=device_details.root_object_type)
    else:
        service_types, details_filter = _device_details_to_subscription_filter(node, device_details)
        return RR.ServiceSubscriptionManagerDetails(Name=nickname,
                                                    ConnectionMethod=RR.ServiceSubscriptionManager_CONNECTION_METHOD_TYPE,
                                                    Filter=details_filter,
                                                    ServiceTypes=service_types)


def _device_details_identifier_to_filter_attribute(details_ident):
    if details_ident is None:
        return None
    details_ident_name = None
    details_ident_uuid = None
    if isinstance(details_ident, str):
        return RR.CreateServiceSubscriptionFilterAttributeCombinedIdentifier(details_ident)
    else:
        details_ident_name = getattr(details_ident, "name", None)
        details_ident_uuid = getattr(details_ident, "uuid", None)
        if (details_ident_name is None and details_ident_uuid is None and isinstance(details_ident, dict)):
            details_ident_name = details_ident.get("name", None)
            details_ident_uuid = details_ident.get("uuid", None)
        if not (details_ident_name is not None or details_ident_uuid is not None):
            raise RR.InvalidArgumentException("Invalid identifier")

        if details_ident_uuid is not None and not isinstance(details_ident_uuid, str):
            uuid_bytes = details_ident_uuid["uuid_bytes"].tobytes()
            details_ident_uuid = str(py_uuid.UUID(bytes=uuid_bytes))

        return RR.CreateServiceSubscriptionFilterAttributeIdentifier(details_ident_name or "", details_ident_uuid or "")


def _device_details_to_subscription_filter(node, device_details):
    if device_details.device_nickname is None or device_details.device_nickname == "":
        raise RR.InvalidArgumentException("Device details to filter must contain device_nickname")
    try:
        if device_details.urls is not None:
            raise RR.InvalidArgumentException("Device details to filter must not contain urls")
        if device_details.subscription_filter is not None:
            raise RR.InvalidArgumentException("Device details to filter must contain subscription filter")

        sub_filter = RR.ServiceSubscriptionFilter()

        root_object_type = ["com.robotraconteur.device.Device"]

        if device_details.root_object_type is not None:
            if isinstance(device_details.root_object_type, str):
                root_object_type = [device_details.root_object_type]
            else:
                root_object_type = device_details.root_object_type

        sub_filter.MaxConnections = device_details.max_connections

        attr_filter = {}

        if device_details.device is not None:
            dev_attr_group = RR.ServiceSubscriptionFilterAttributeGroup()
            dev_attr_group.Attributes.append(_device_details_identifier_to_filter_attribute(device_details.device))
            attr_filter["device"] = dev_attr_group

        if device_details.serial_number is not None:
            attr_filter["serial_number"] = RR.ServiceSubscriptionFilterAttribute(device_details.serial_number)

        if device_details.tags is not None and len(device_details.tags) > 0:
            tags = device_details.tags
            if not isinstance(tags, collections.abc.Sequence) and not isinstance(tags, str):
                tags = [tags]

            tag_grp = RR.ServiceSubscriptionFilterAttributeGroup()
            if device_details.tag_match_operation is None:
                tag_grp.Operation = RR.ServiceSubscriptionFilterAttributeGroupOperation_AND
            elif device_details.tag_match_operation.lower() == "and":
                tag_grp.Operation = RR.ServiceSubscriptionFilterAttributeGroupOperation_AND
            elif device_details.tag_match_operation.lower() == "or":
                tag_grp.Operation = RR.ServiceSubscriptionFilterAttributeGroupOperation_OR
            elif device_details.tag_match_operation.lower() == "nand":
                tag_grp.Operation = RR.ServiceSubscriptionFilterAttributeGroupOperation_NAND
            elif device_details.tag_match_operation.lower() == "nor":
                tag_grp.Operation = RR.ServiceSubscriptionFilterAttributeGroupOperation_NOR
            else:
                raise RR.InvalidArgumentException("Invalid tag match operation")

            for tag in tags:
                tag_grp.Attributes.append(_device_details_identifier_to_filter_attribute(tag))
            attr_filter["tags"] = tag_grp

        sub_filter.Attributes = attr_filter
        sub_filter.AttributesMatchOperation = RR.ServiceSubscriptionFilterAttributeGroupOperation_AND

        if device_details.transport_schemes is not None:
            sub_filter.TransportSchemes = device_details.transport_schemes

        if device_details.service_nodes is not None:
            sub_filter.Nodes = device_details.service_nodes

        return root_object_type, sub_filter
    except Exception as e:
        raise RR.InvalidArgumentException(
            f"Invalid device details for device {device_details.device_nickname}: {str(e)}") from e


def load_device_details_from_yaml_path(yaml_filename):
    """
    Load device details from a YAML file specified by the file path

    :param yaml_filename: The path to the YAML file
    :type yaml_filename: str | pathlib.Path
    """
    with open(yaml_filename, "r") as f:
        return load_device_details_from_yaml(f)


def load_device_details_from_yaml(yaml_file):
    """
    Load device details from a YAML file object

    :param yaml_file: The file object containing the YAML file
    :type yaml_file: file
    """
    yaml_dict = yaml.safe_load(yaml_file)
    return load_device_details_from_yaml_dict(yaml_dict)


def load_device_details_from_yaml_dict(yaml_dict):
    """
    Load device details from a YAML dictionary

    :param yaml_dict: The dictionary containing the YAML file contents
    :type yaml_dict: dict
    """
    details_out = []
    details_in = yaml_dict["devices"]
    for k, v in details_in.items():
        args = {}
        urls = v.get("urls", None)
        if urls is not None:
            args["urls"] = urls
        if v.get("device") is not None:
            args["device"] = v["device"]
        if v.get("serial_number") is not None:
            args["serial_number"] = v["serial_number"]
        if v.get("tags") is not None:
            args["tags"] = v["tags"]
        details_out1 = DeviceConnectorDetails(k, **args)
        details_out.append(details_out1)
    return details_out
