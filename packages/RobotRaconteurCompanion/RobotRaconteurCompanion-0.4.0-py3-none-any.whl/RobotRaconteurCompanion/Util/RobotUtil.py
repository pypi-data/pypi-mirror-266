import general_robotics_toolbox as rox
import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import numpy as np


def _check_list(l, error_msg, expected_count=-1):
    if l is None:
        raise RR.InvalidArgumentException(error_msg)

    if expected_count >= 0:
        if len(l) != expected_count:
            raise RR.InvalidArgumentException(error_msg)


class RobotUtil:
    """
    Utility class to convert a Robot Raconteur com.robotraconteur.robotics.robot.RobotInfo to
    a general_robotics_toolbox.Robot object.

    The RobotInfo is provided by robot drivers and is used to describe the kinematics of the robot.

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

    def robot_info_to_rox_robot(self, robot_info, chain_number):
        """
        Convert a RobotInfo to a general_robotics_toolbox.Robot object

        :param robot_info: The RobotInfo to convert
        :type robot_info: com.robotraconteur.robotics.robot.RobotInfo
        :param chain_number: The kinematic chain number to convert. For a single arm robot, this is 0.
            For a dual arm robot, this is 0 for the left arm and 1 for the right arm.
        :type chain_number: int
        :return: The converted robot
        :rtype: general_robotics_toolbox.Robot
        """
        _check_list(robot_info.chains, f"could not find kinematic chain number {chain_number}")
        if chain_number >= len(robot_info.chains):
            raise RR.InvalidArgumentException(f"invalid kinematic chain number {chain_number}")

        chain = robot_info.chains[chain_number]
        joint_count = len(chain.joint_numbers)
        for i in range(1, joint_count):
            if chain.joint_numbers[i - 1] >= chain.joint_numbers[i]:
                raise RR.InvalidArgumentException(f"joint numbers must be increasing in chain number {chain_number}")

            if chain.joint_numbers[i] >= len(robot_info.joint_info):
                raise RR.InvalidArgumentException(f"joint number out of bounds in chain number {chain_number}")

        _check_list(chain.H, f"invalid shape for H in chain number {chain_number}", joint_count)
        _check_list(chain.P, f"invalid shape for P in chain number {chain_number}", joint_count + 1)

        H = np.zeros((3, joint_count), dtype=np.float64)
        for i in range(joint_count):
            H[0, i] = chain.H[i]["x"]
            H[1, i] = chain.H[i]["y"]
            H[2, i] = chain.H[i]["z"]

        P = np.zeros((3, joint_count + 1), dtype=np.float64)
        for i in range(joint_count + 1):
            P[0, i] = chain.P[i]["x"]
            P[1, i] = chain.P[i]["y"]
            P[2, i] = chain.P[i]["z"]

        joint_type = [0] * joint_count
        joint_lower_limit = np.zeros((joint_count,), dtype=np.float64)
        joint_upper_limit = np.zeros((joint_count,), dtype=np.float64)
        joint_vel_limit = np.zeros((joint_count,), dtype=np.float64)
        joint_acc_limit = np.zeros((joint_count,), dtype=np.float64)
        joint_names = [None] * joint_count

        for i in range(joint_count):
            j = robot_info.joint_info[i]
            if j.joint_type == 1:
                # Revolute joint
                joint_type[i] = 0
            elif j.joint_type == 3:
                # Prismatic joint
                joint_type[i] = 1
            else:
                raise RR.InvalidArgumentException(f"invalid joint type: {j.joint_type}")

            if j.joint_limits is None:
                raise RR.InvalidArgumentException("joint_limits must not be null")
            joint_lower_limit[i] = j.joint_limits.lower
            joint_upper_limit[i] = j.joint_limits.upper
            joint_vel_limit[i] = j.joint_limits.velocity
            joint_acc_limit[i] = j.joint_limits.acceleration
            if j.joint_identifier is not None:
                joint_names[i] = j.joint_identifier.name
            else:
                joint_names[i] = ""

        root_link_name = None
        if chain.link_identifiers is not None and len(chain.link_identifiers) > 0 and chain.link_identifiers[0] is not None:
            root_link_name = chain.link_identifiers[0].name

        tip_link_name = None
        if chain.flange_identifier is not None:
            tip_link_name = chain.flange_identifier.name

        flange_q = chain.flange_pose["orientation"]
        flange_p = chain.flange_pose["position"]

        r_flange = rox.q2R(self._node.NamedArrayToArray(flange_q).flatten())
        p_flange = np.array(self._node.NamedArrayToArray(flange_p).flatten())

        T_base = None
        if robot_info.device_info is not None:
            robot_device_info = robot_info.device_info
            if robot_device_info.device_origin_pose is not None:
                robot_origin_pose = robot_device_info.device_origin_pose
                if robot_origin_pose.pose is not None:
                    r_base = rox.q2R(self._node.NamedArrayToArray(robot_origin_pose.pose["orientation"]).flatten())
                    p_base = np.array(self._node.NamedArrayToArray(robot_origin_pose.pose["position"]).flatten())
                    T_base = rox.Transform(r_base, p_base)

        rox_robot = rox.Robot(H, P, joint_type, joint_lower_limit, joint_upper_limit, joint_vel_limit,
                              joint_acc_limit, joint_names=joint_names, root_link_name=root_link_name, tip_link_name=tip_link_name,
                              T_flange=rox.Transform(r_flange, p_flange), T_base=T_base)

        return rox_robot
