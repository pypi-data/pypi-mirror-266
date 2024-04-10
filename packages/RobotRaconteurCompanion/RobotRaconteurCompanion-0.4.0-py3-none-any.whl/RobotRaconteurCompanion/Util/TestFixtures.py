import RobotRaconteur as RR

from .RobDef import register_service_types_from_resources
from ..StdRobDef import RegisterStdRobDefServiceTypes


class IntraTaskFixture:
    """
    A test fixture for intra-process testing using Robot Raconteur.

    The IntraTestFixture class provides a convenient way to set up and tear down
    the necessary components for intra-process testing using Robot Raconteur.
    It initializes client and server nodes, registers transport, service types,
    and provides methods to register services and connect to services.

    To use this test fixture, create an instance of IntraTestFixture in your test
    and call the necessary methods to set up the test environment. The fixture will
    automatically clean up the resources when it goes out of scope.

    :ivar client_node: The client node
    :vartype client_node: RobotRaconteur.RobotRaconteurNode
    :ivar server_node: The server node
    :vartype server_node: RobotRaconteur.RobotRaconteurNode
    :ivar client_transport: The client transport
    :vartype client_transport: RobotRaconteur.IntraTransport
    :ivar server_transport: The server transport
    :vartype server_transport: RobotRaconteur.IntraTransport
    """

    def __init__(self):
        self.client_node = RR.RobotRaconteurNode()
        self.server_node = RR.RobotRaconteurNode()

        self.client_node.SetNodeName("client_node")
        self.server_node.SetNodeName("server_node")

        self.client_node.Init()
        self.server_node.Init()

        self.client_transport = RR.IntraTransport(self.client_node)
        self.server_transport = RR.IntraTransport(self.server_node)

        self.client_node.RegisterTransport(self.client_transport)
        self.server_node.RegisterTransport(self.server_transport)

        self.client_transport.StartClient()
        self.server_transport.StartServer()

    def register_service_types_text(self, robdef_text):
        """
        Register service types from text

        :param robdef_text: The service type text
        :type robdef_text: str
        """
        # self.client_node.RegisterServiceTypes(robdef_text)
        self.server_node.RegisterServiceTypes(robdef_text)

    def register_service_types_from_resources(self, package, resources):
        """
        Register service types from resources

        :param package: The package containing the resource
        :type package: str
        :param resources: The list of resource names
        :type resources: list[str]
        """

        # register_service_types_from_resources(self.client_node, package, resources)
        register_service_types_from_resources(self.server_node, package, resources)

    def register_service(self, name, objtype, obj):
        """
        Register a service

        :param name: The service name
        :type name: str
        :param objtype: The service object Robot Raconteur type
        :type objtype: str
        :param obj: The service object
        :type obj: object
        """
        return self.server_node.RegisterService(name, objtype, obj)

    def register_standard_service_types(self):
        """
        Register standard service types
        """
        # RegisterStdRobDefServiceTypes(self.client_node)
        RegisterStdRobDefServiceTypes(self.server_node)

    def connect_service(self, url):
        """
        Connect to a service

        :param url: The service URL
        :type url: str
        :return: The connected service
        :rtype: object
        """
        return self.client_node.ConnectService(url)

    def shutdown(self):
        """
        Shutdown the fixture
        """
        if self.client_node is None:
            return
        self.client_node.Shutdown()
        self.server_node.Shutdown()

        self.client_node = None
        self.server_node = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()
