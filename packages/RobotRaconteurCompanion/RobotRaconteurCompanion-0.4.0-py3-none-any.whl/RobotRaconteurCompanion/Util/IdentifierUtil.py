import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import numpy as np
import re

from .UuidUtil import UuidUtil


class IdentifierUtil(object):
    """
    Utility class for working with Robot Raconteur identifiers

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

        self._identifier = self._node.GetStructureType("com.robotraconteur.identifier.Identifier", self._client_obj)
        self._uuid_dt = self._node.GetNamedArrayDType("com.robotraconteur.uuid.UUID", self._client_obj)

        self._uuid_util = UuidUtil(node, client_obj)

    def IsIdentifierAnyUuid(self, identifier):
        """
        Check if an identifier is "any" (UUID is all zeros)

        :param identifier: The identifier to check
        :type identifier: com.robotraconteur.identifier.Identifier
        :return: True if the identifier is "any"
        :rtype: bool
        """
        if identifier is None or identifier.uuid is None:
            return True
        return np.all(identifier.uuid["uuid_bytes"] == 0)

    def IsIdentifierAnyName(self, identifier):
        """
        Check if an identifier is "any" (name is empty)

        :param identifier: The identifier to check
        :type identifier: com.robotraconteur.identifier.Identifier
        :return: True if the identifier is "any"
        :rtype: bool
        """
        if identifier is None or identifier.name is None:
            return True
        return len(identifier.name) == 0

    def IsIdentifierAny(self, identifier):
        """
        Check if an identifier is "any" (UUID is all zeros and name is empty)

        :param identifier: The identifier to check
        :type identifier: com.robotraconteur.identifier.Identifier
        :return: True if the identifier is "any"
        :rtype: bool
        """
        if identifier is None:
            return True
        if not self.IsIdentifierAnyUuid(identifier):
            return False
        if not self.IsIdentifierAnyName(identifier):
            return False
        return True

    def IsIdentifierMatch(self, expected, test):
        """
        Check if two identifiers match

        Identifiers have a complex matching rules:

        - If both identifiers are "any", they match
        - If either identifier is "any", they match
        - If both identifiers have the same name and UUID, they match
        - If the name is Any for either identifier and UUID matches, they match
        - If the UUID is Any for either identifier and name matches, they match
        - Otherwise, they do not match

        :param expected: The expected identifier
        :type expected: com.robotraconteur.identifier.Identifier
        :param test: The test identifier
        :type test: com.robotraconteur.identifier.Identifier
        :return: True if the identifiers match
        :rtype: bool
        """
        if self.IsIdentifierAny(expected) or self.IsIdentifierAny(test):
            return True

        name_match = False
        uuid_match = False

        if self.IsIdentifierAnyName(expected) or self.IsIdentifierAnyName(test):
            name_match = True
        else:
            if expected.name == test.name:
                name_match = True

        if self.IsIdentifierAnyUuid(expected) or self.IsIdentifierAnyUuid(test):
            uuid_match = True
        else:
            if np.all(expected.uuid["uuid_bytes"] == test.uuid["uuid_bytes"]):
                uuid_match = True

        return name_match and uuid_match

    def CreateIdentifier(self, name, uuid):
        """
        Create an identifier from a name and UUID

        :param name: The name of the identifier
        :type name: str
        :param uuid: The UUID of the identifier
        :type uuid: str
        :return: The created identifier
        :rtype: com.robotraconteur.identifier.Identifier
        """
        ret = self._identifier()
        ret.name = name if name is not None else ""
        if uuid is not None:
            ret.uuid = self._uuid_util.ParseUuid(uuid)
        else:
            ret.uuid = np.zeros((1,), dtype=self._uuid_dt)
        return ret

    def CreateIdentifierFromName(self, name):
        """
        Create an identifier from a name. The UUID will be all zeros.

        :param name: The name of the identifier
        :type name: str
        :return: The created identifier
        :rtype: com.robotraconteur.identifier.Identifier
        """
        assert name is not None
        ret = self._identifier()
        ret.name = name
        ret.uuid = np.zeros((1,), dtype=self._uuid_dt)
        return ret

    def IdentifierToString(self, identifier):
        """
        Create a string representation of an identifier. The string representation is in the form "name|uuid".

        :param identifier: The identifier to convert to a string
        :type identifier: com.robotraconteur.identifier.Identifier
        :return: The string representation of the identifier
        :rtype: str
        """
        if identifier is None:
            return ""
        if not self.IsIdentifierAnyName(identifier) and not self.IsIdentifierAnyUuid(identifier):
            return identifier.name + "|" + self._uuid_util.UuidToString(identifier.uuid)
        if not self.IsIdentifierAnyName(identifier):
            return identifier.name
        if not self.IsIdentifierAnyUuid(identifier):
            return self._uuid_util.UuidToString(identifier.uuid)
        return ""

    def StringToIdentifier(self, string_id):
        """
        Parse a string representation of an identifier. The string representation is in the form "name|uuid".

        :param string_id: The string representation of the identifier
        :type string_id: str
        :return: The parsed identifier
        :rtype: com.robotraconteur.identifier.Identifier
        """
        name_regex_str = "(?:[a-zA-Z](?:[a-zA-Z0-9_]*[a-zA-Z0-9])?)(?:\\.[a-zA-Z](?:[a-zA-Z0-9_]*[a-zA-Z0-9])?)*"
        uuid_regex_str = "\\{?[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\}?"
        identifier_regex = "(?:(" + name_regex_str + ")\\|(" + uuid_regex_str + "))|(" + \
            name_regex_str + ")|(" + uuid_regex_str + ")"

        r_res = re.match(identifier_regex, string_id)
        if r_res is None:
            raise RR.InvalidArgumentException("Invalid identifier string")

        if r_res.group(1) is not None and r_res.group(2) is not None:
            return self.CreateIdentifier(r_res.group(1), r_res.group(2))

        if r_res.group(3) is not None:
            return self.CreateIdentifierFromName(r_res.group(3))

        if r_res.group(4) is not None:
            return self.CreateIdentifier("", r_res.group(4))

        raise RR.InvalidArgumentException("Invalid identifier string")
