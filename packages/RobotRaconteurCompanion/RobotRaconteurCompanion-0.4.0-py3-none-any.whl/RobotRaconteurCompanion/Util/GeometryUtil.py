"""
Utility class to convert between Robot Raconteur types and Python types. Python numpy or general_robotics_toolbox
types are used when applicable.

:param node: (optional) The Robot Raconteur node to use for parsing. Defaults to RobotRaconteurNode.s
:type node: RobotRaconteur.RobotRaconteurNode
:param client_obj: (optional) The client object to use for finding types. Defaults to None
:type client_obj: RobotRaconteur.ClientObject
"""

import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import numpy as np
import general_robotics_toolbox as rox
from .IdentifierUtil import IdentifierUtil


def _name_from_identifier(id_):
    if id_ is None:
        return None
    return id_.name


class GeometryUtil(object):
    def __init__(self, node=None, client_obj=None):
        if node is None:
            self._node = RRN
        else:
            self._node = node
        self._client_obj = client_obj

        self._vector2_type = self._create_dtypes("Vector2")
        self._vector3_type = self._create_dtypes("Vector3")
        self._vector6_type = self._create_dtypes("Vector6")
        self._point2d_type = self._create_dtypes("Point2D")
        self._point_type = self._create_dtypes("Point")
        self._size2d_type = self._create_dtypes("Size2D")
        self._size_type = self._create_dtypes("Size")
        self._quaternion_type = self._create_dtypes("Quaternion")
        self._transform_type = self._create_dtypes("Transform")
        self._named_transform_type = self._create_structtypes("NamedTransform")
        self._pose_type = self._create_dtypes("Pose")
        self._named_pose_type = self._create_structtypes("NamedPose")
        self._spatial_velocity_type = self._create_dtypes("SpatialVelocity")
        self._spatial_acceleration_type = self._create_dtypes("SpatialAcceleration")
        self._wrench_type = self._create_dtypes("Wrench")

        self._ident_util = IdentifierUtil(self._node, self._client_obj)

    def _create_dtypes(self, type_name):
        try:
            d_type = self._node.GetNamedArrayDType(f"com.robotraconteur.geometry.{type_name}", self._client_obj)
        except:
            d_type = None
        try:
            f_type = self._node.GetNamedArrayDType(f"com.robotraconteur.geometryf.{type_name}", self._client_obj)
        except:
            f_type = None
        try:
            i_type = self._node.GetNamedArrayDType(f"com.robotraconteur.geometryi.{type_name}", self._client_obj)
        except:
            i_type = None

        assert any((d_type, f_type, i_type)), "No geometry service types registered"
        return d_type, f_type, i_type

    def _create_structtypes(self, type_name):
        try:
            d_type = self._node.GetStructureType(f"com.robotraconteur.geometry.{type_name}", self._client_obj)
        except:
            d_type = None
        try:
            f_type = self._node.GetStructureType(f"com.robotraconteur.geometryf.{type_name}", self._client_obj)
        except:
            f_type = None
        try:
            i_type = self._node.GetStructureType(f"com.robotraconteur.geometryi.{type_name}", self._client_obj)
        except:
            i_type = None

        assert any((d_type, f_type, i_type)), "No geometry service types registered"
        return d_type, f_type, i_type

    def _create_return_np(self, rr_dtypes, dtype):
        if dtype == np.float64:
            assert rr_dtypes[0], "com.robotraconteur.geometry not registered"
            return np.zeros((1,), dtype=rr_dtypes[0])
        elif dtype == np.float32:
            assert rr_dtypes[1], "com.robotraconteur.geometryf not registered"
            return np.zeros((1,), dtype=rr_dtypes[1])
        elif dtype == np.int32:
            assert rr_dtypes[2], "com.robotraconteur.geometryi not registered"
            return np.zeros((1,), dtype=rr_dtypes[2])
        else:
            assert False, "Invalid dtype"

    def _create_return_struct(self, rr_struct_types, dtype):
        if dtype == np.float64:
            assert rr_struct_types[0], "com.robotraconteur.geometry not registered"
            return rr_struct_types[0]()
        elif dtype == np.float32:
            assert rr_struct_types[1], "com.robotraconteur.geometryf not registered"
            return rr_struct_types[1]()
        elif dtype == np.int32:
            assert rr_struct_types[2], "com.robotraconteur.geometryi not registered"
            return rr_struct_types[2]()
        else:
            assert False, "Invalid dtype"

    def xy_to_vector2(self, xy, dtype=np.float64):
        """
        Converts a 2 element vector to a Robot Raconteur Vector2 type

        :param xy: The 2D vector
        :type xy: numpy.ndarray
        :param dtype: The numpy dtype of the vector. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Vector2
        """
        ret = self._create_return_np(self._vector2_type, dtype)
        ret[0]["x"] = xy[0]
        ret[0]["y"] = xy[1]
        return ret

    def vector2_to_xy(self, rr_vector2):
        """
        Converts a Robot Raconteur Vector2 to a 2 element vector

        :param rr_vector2: The Robot Raconteur Vector2
        :type rr_vector2: com.robotraconteur.geometry.Vector2
        :return: The 2D vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_vector2[0]["x"], rr_vector2[0]["y"]])

    def xyz_to_vector3(self, xyz, dtype=np.float64):
        ret = self._create_return_np(self._vector3_type, dtype)
        ret[0]["x"] = xyz[0]
        ret[0]["y"] = xyz[1]
        ret[0]["z"] = xyz[2]
        return ret

    def vector3_to_xyz(self, rr_vector3):
        """"
        Converts a Robot Raconteur Vector3 to a 3 element vector

        :param rr_vector3: The Robot Raconteur Vector3
        :type rr_vector3: com.robotraconteur.geometry.Vector3
        :return: The 3D vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_vector3[0]["x"], rr_vector3[0]["y"], rr_vector3[0]["z"]])

    def abgxyz_to_vector6(self, abgxyz, dtype=np.float64):
        """
        Converts a 6 element vector to a Robot Raconteur Vector6

        :param abgxyz: The 6D vector
        :type abgxyz: numpy.ndarray
        :param dtype: The numpy dtype of the vector. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Vector6
        :return: The Robot Raconteur Vector6
        :rtype: com.robotraconteur.geometry.Vector6
        """
        ret = self._create_return_np(self._vector6_type, dtype)
        ret[0]["alpha"] = abgxyz[0]
        ret[0]["beta"] = abgxyz[1]
        ret[0]["gamma"] = abgxyz[2]
        ret[0]["x"] = abgxyz[3]
        ret[0]["y"] = abgxyz[4]
        ret[0]["z"] = abgxyz[5]
        return ret

    def vector6_to_abgxyz(self, rr_vector6):
        """
        Converts a Robot Raconteur Vector6 to a 6 element vector

        :param rr_vector6: The Robot Raconteur Vector6
        :type rr_vector6: com.robotraconteur.geometry.Vector6
        :return: The 6D vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_vector6[0]["alpha"], rr_vector6[0]["beta"], rr_vector6[0]["gamma"],
                         rr_vector6[0]["x"], rr_vector6[0]["y"], rr_vector6[0]["z"]])

    def xy_to_point2d(self, xy, dtype=np.float64):
        """
        Converts a 2 element vector to a Robot Raconteur Point2D

        :param xy: The 2 element vector
        :type xy: numpy.ndarray
        :param dtype: The numpy dtype of the vector. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Point2D
        """
        ret = self._create_return_np(self._point2d_type, dtype)
        ret[0]["x"] = xy[0]
        ret[0]["y"] = xy[1]
        return ret

    def point2d_to_xy(self, rr_point2d):
        """
        Converts a Robot Raconteur Point2D to a 2 element vector

        :param rr_point2d: The Robot Raconteur Point2D
        :type rr_point2d: com.robotraconteur.geometry.Point2D
        :return: The 2D vector
        :rtype: numpy.ndarray
        """

        return np.array([rr_point2d[0]["x"], rr_point2d[0]["y"]])

    def xyz_to_point(self, xyz, dtype=np.float64):
        """
        Converts a 3 element vector to a Robot Raconteur Point

        :param xyz: The 3 element vector
        :type xyz: numpy.ndarray
        :param dtype: The numpy dtype of the vector. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Point
        :return: The Robot Raconteur Point
        :rtype: com.robotraconteur.geometry.Point
        """
        ret = self._create_return_np(self._point_type, dtype)
        ret[0]["x"] = xyz[0]
        ret[0]["y"] = xyz[1]
        ret[0]["z"] = xyz[2]
        return ret

    def point_to_xyz(self, rr_point):
        """
        Converts a Robot Raconteur Point to a 3 element vector

        :param rr_point: The Robot Raconteur Point
        :type rr_point: com.robotraconteur.geometry.Point
        :return: The 3 element vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_point[0]["x"], rr_point[0]["y"], rr_point[0]["z"]])

    def wh_to_size2d(self, wh, dtype=np.float64):
        """
        Converts a 2 element vector to a Robot Raconteur Size2D

        :param wh: The 2 element vector
        :type wh: numpy.ndarray
        :param dtype: The numpy dtype of the vector. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Size2D
        :return: The Robot Raconteur Size2D
        :rtype: com.robotraconteur.geometry.Size2D
        """
        ret = self._create_return_np(self._size2d_type, dtype)
        ret[0]["width"] = wh[0]
        ret[0]["height"] = wh[1]
        return ret

    def size2d_to_wh(self, rr_size2d):
        """
        Converts a Robot Raconteur Size2D to a 2 element vector

        :param rr_size2d: The Robot Raconteur Size2D
        :type rr_size2d: com.robotraconteur.geometry.Size2D
        :return: The 2 element vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_size2d[0]["width"], rr_size2d[0]["height"]])

    def whd_to_size(self, whd, dtype=np.float64):
        """
        Converts a 3 element vector to a Robot Raconteur Size

        :param whd: The 3 element vector
        :type whd: numpy.ndarray
        :param dtype: The numpy dtype of the vector. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Size
        :return: The Robot Raconteur Size
        :rtype: com.robotraconteur.geometry.Size
        """
        ret = self._create_return_np(self._size_type, dtype)
        ret[0]["width"] = whd[0]
        ret[0]["height"] = whd[1]
        ret[0]["depth"] = whd[2]
        return ret

    def size_to_whd(self, rr_size):
        """
        Converts a Robot Raconteur Size to a 3 element vector

        :param rr_size: The Robot Raconteur Size
        :type rr_size: com.robotraconteur.geometry.Size
        :return: The 3 element vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_size[0]["width"], rr_size[0]["height"], rr_size[0]["depth"]])

    def q_to_quaternion(self, q, dtype=np.float64):
        """
        Converts a 4 element vector to a Robot Raconteur Quaternion. The order of the elements is [w,x,y,z]

        :param q: The 4 element vector
        :type q: numpy.ndarray
        :param dtype: The numpy dtype of the vector. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Quaternion
        :return: The Robot Raconteur Quaternion
        :rtype: com.robotraconteur.geometry.Quaternion
        """
        ret = self._create_return_np(self._quaternion_type, dtype)
        ret[0]["w"] = q[0]
        ret[0]["x"] = q[1]
        ret[0]["y"] = q[2]
        ret[0]["z"] = q[3]
        return ret

    def quaternion_to_q(self, rr_quaternion):
        """
        Converts a Robot Raconteur Quaternion to a 4 element vector. The order of the elements is [w,x,y,z]

        :param rr_quaternion: The Robot Raconteur Quaternion
        :type rr_quaternion: com.robotraconteur.geometry.Quaternion
        :return: The 4 element vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_quaternion[0]["w"], rr_quaternion[0]["x"], rr_quaternion[0]["y"], rr_quaternion[0]["z"]])

    def R_to_quaternion(self, R, dtype=np.float64):
        """
        Converts a 3x3 rotation matrix to a Robot Raconteur Quaternion

        :param R: The 3x3 rotation matrix
        :type R: numpy.ndarray
        :param dtype: The numpy dtype of the vector. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Quaternion
        :return: The Robot Raconteur Quaternion
        :rtype: com.robotraconteur.geometry.Quaternion
        """
        return self.q_to_quaternion(rox.R2q(R), dtype)

    def quaternion_to_R(self, rr_quaternion):
        """
        Converts a Robot Raconteur Quaternion to a 3x3 rotation matrix

        :param rr_quaternion: The Robot Raconteur Quaternion
        :type rr_quaternion: com.robotraconteur.geometry.Quaternion
        :return: The 3x3 rotation matrix
        :rtype: numpy.ndarray
        """
        return rox.q2R(self.quaternion_to_q(rr_quaternion))

    def rpy_to_quaternion(self, rpy, dtype=np.float64):
        """
        Convert a roll-pitch-yaw vector in radians to a Robot Raconteur Quaternion

        :param rpy: The roll-pitch-yaw vector
        :type rpy: numpy.ndarray
        :param dtype: The numpy dtype of the vector. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Quaternion
        :return: The Robot Raconteur Quaternion
        :rtype: com.robotraconteur.geometry.Quaternion
        """
        return self.q_to_quaternion(rox.R2q(rox.rpy2R(rpy)), dtype)

    def quaternion_to_rpy(self, rr_quaternion):
        """
        Convert a Robot Raconteur Quaternion to a roll-pitch-yaw vector in radians

        :param rr_quaternion: The Robot Raconteur Quaternion
        :type rr_quaternion: com.robotraconteur.geometry.Quaternion
        :return: The roll-pitch-yaw vector
        :rtype: numpy.ndarray
        """
        return rox.R2rpy(rox.q2R(self.quaternion_to_q(rr_quaternion)))

    def rox_transform_to_transform(self, rox_transform, dtype=np.float64):
        """
        Converts a general_robotics_toolbox Transform to a Robot Raconteur Transform

        :param rox_transform: The general_robotics_toolbox Transform
        :type rox_transform: general_robotics_toolbox.Transform
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Transform
        :return: The Robot Raconteur Transform
        """
        ret = self._create_return_np(self._transform_type, dtype)
        ret[0]["rotation"] = self.R_to_quaternion(rox_transform.R)
        ret[0]["translation"] = self.xyz_to_vector3(rox_transform.p)
        return ret

    def transform_to_rox_transform(self, rr_transform):
        """
        Converts a Robot Raconteur Transform to a general_robotics_toolbox Transform

        :param rr_transform: The Robot Raconteur Transform
        :type rr_transform: com.robotraconteur.geometry.Transform
        :return: The general_robotics_toolbox Transform
        :rtype: general_robotics_toolbox.Transform
        """
        R = self.quaternion_to_R(rr_transform["rotation"])
        p = self.vector3_to_xyz(rr_transform["translation"])
        return rox.Transform(R, p)

    def _xyz_rpy_to_rox_transform(self, xyz, rpy, parent_frame_id=None, child_frame_id=None):
        p = xyz
        R = rox.rpy2R(rpy)
        return rox.Transform(R, p, parent_frame_id, child_frame_id)

    def _rox_transform_to_xyz_rpy(self, rox_transform):
        R = rox_transform.R
        p = rox_transform.p
        return p, rox.R2rpy(R)

    def _rox_transform_to_xyz_rpy_named(self, rox_transform):
        R = rox_transform.R
        p = rox_transform.p
        parent_frame_id = rox_transform.parent_frame_id
        child_frame_id = rox_transform.child_frame_id
        return p, rox.R2rpy(R), parent_frame_id, child_frame_id

    def xyz_rpy_to_transform(self, xyz, rpy, dtype=np.float64):
        """
        Converts a 3 element position vector and 3 element roll-pitch-yaw vector in radians to a
        Robot Raconteur Transform

        :param xyz: The 3 element position vector
        :type xyz: numpy.ndarray
        :param rpy: The 3 element roll-pitch-yaw vector in radians
        :type rpy: numpy.ndarray
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Transform
        :return: The Robot Raconteur Transform
        :rtype: com.robotraconteur.geometry.Transform
        """
        return self.rox_transform_to_transform(self._xyz_rpy_to_rox_transform(xyz, rpy), dtype)

    def transform_to_xyz_rpy(self, transform):
        """
        Converts a Robot Raconteur Transform to a 3 element position vector and 3 element roll-pitch-yaw vector
        in radians.

        :param transform: The Robot Raconteur Transform
        :type transform: com.robotraconteur.geometry.Transform
        :return: The 3 element position vector and 3 element roll-pitch-yaw vector in radians
        :rtype: Tuple[numpy.ndarray, numpy.ndarray]
        """
        return self._rox_transform_to_xyz_rpy(self.transform_to_rox_transform(transform))

    def rox_transform_to_named_transform(self, rox_transform, dtype=np.float64):
        """
        Converts a general_robotics_toolbox Transform to a Robot Raconteur NamedTransform. The rox_transform
        must have parent_frame_id and child_frame_id set.

        :param rox_transform: The general_robotics_toolbox Transform
        :type rox_transform: general_robotics_toolbox.Transform
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.NamedTransform
        :return: The Robot Raconteur NamedTransform
        :rtype: com.robotraconteur.geometry.NamedTransform
        """
        ret = self._create_return_struct(self._named_transform_type, dtype)
        ret.transform = self.rox_transform_to_transform(rox_transform)
        ret.child_frame = self._ident_util.CreateIdentifierFromName(rox_transform.child_frame_id)
        ret.parent_frame = self._ident_util.CreateIdentifierFromName(rox_transform.parent_frame_id)
        return ret

    def named_transform_to_rox_transform(self, rr_named_transform):
        """
        Convert a Robot Raconteur NamedTransform to a general_robotics_toolbox Transform

        :param rr_named_transform: The Robot Raconteur NamedTransform
        :type rr_named_transform: com.robotraconteur.geometry.NamedTransform
        :return: The general_robotics_toolbox Transform
        :rtype: general_robotics_toolbox.Transform
        """
        R = self.quaternion_to_R(rr_named_transform.transform["rotation"])
        p = self.vector3_to_xyz(rr_named_transform.transform["translation"])
        return rox.Transform(R, p, _name_from_identifier(rr_named_transform.parent_frame),
                             _name_from_identifier(rr_named_transform.child_frame))

    def xyz_rpy_to_named_transform(self, xyz, rpy, parent_frame_id, child_frame_id, dtype=np.float64):
        """
        Converts a 3 element position vector and 3 element roll-pitch-yaw vector in radians to a
        Robot Raconteur NamedTransform

        :param xyz: The 3 element position vector
        :type xyz: numpy.ndarray
        :param rpy: The 3 element roll-pitch-yaw vector in radians
        :type rpy: numpy.ndarray
        :param parent_frame_id: The parent frame name
        :type parent_frame_id: str
        :param child_frame_id: The child frame name
        :type child_frame_id: str
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.NamedTransform
        :return: The Robot Raconteur NamedTransform
        :rtype: com.robotraconteur.geometry.NamedTransform
        """
        return self.rox_transform_to_named_transform(self._xyz_rpy_to_rox_transform(xyz, rpy, parent_frame_id, child_frame_id), dtype)

    def named_transform_to_xyz_rpy(self, transform):
        """
        Converts a Robot Raconteur NamedTransform to a 3 element position vector and 3 element roll-pitch-yaw vector
        in radians.

        :param transform: The Robot Raconteur NamedTransform
        :type transform: com.robotraconteur.geometry.NamedTransform
        :return: The 3 element position vector and 3 element roll-pitch-yaw vector in radians
        :rtype: Tuple[numpy.ndarray, numpy.ndarray]
        """
        return self._rox_transform_to_xyz_rpy_named(self.named_transform_to_rox_transform(transform))

    def rox_transform_to_pose(self, rox_transform, dtype=np.float64):
        """
        Converts a general_robotics_toolbox Transform to a Robot Raconteur Pose

        :param rox_transform: The general_robotics_toolbox Transform
        :type rox_transform: general_robotics_toolbox.Transform
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Pose
        :return: The Robot Raconteur Pose
        :rtype: com.robotraconteur.geometry.Pose
        """
        ret = self._create_return_np(self._pose_type, dtype)
        ret[0]["orientation"] = self.R_to_quaternion(rox_transform.R)
        ret[0]["position"] = self.xyz_to_point(rox_transform.p)
        return ret

    def pose_to_rox_transform(self, rr_pose):
        """
        Convert a Robot Raconteur Pose to a general_robotics_toolbox Transform

        :param rr_pose: The Robot Raconteur Pose
        :type rr_pose: com.robotraconteur.geometry.Pose
        :return: The general_robotics_toolbox Transform
        :rtype: general_robotics_toolbox.Transform
        """
        R = self.quaternion_to_R(rr_pose["orientation"])
        p = self.vector3_to_xyz(rr_pose["position"])
        return rox.Transform(R, p)

    def xyz_rpy_to_pose(self, xyz, rpy, dtype=np.float64):
        """
        Converts a 3 element position vector and 3 element roll-pitch-yaw vector in radians to a
        Robot Raconteur Pose

        :param xyz: The 3 element position vector
        :type xyz: numpy.ndarray
        :param rpy: The 3 element roll-pitch-yaw vector in radians
        :type rpy: numpy.ndarray
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Pose
        :return: The Robot Raconteur Pose
        :rtype: com.robotraconteur.geometry.Pose
        """
        return self.rox_transform_to_pose(self._xyz_rpy_to_rox_transform(xyz, rpy), dtype)

    def pose_to_xyz_rpy(self, transform):
        """
        Converts a Robot Raconteur Pose to a 3 element position vector and 3 element roll-pitch-yaw vector

        :param transform: The Robot Raconteur Pose
        :type transform: com.robotraconteur.geometry.Pose
        :return: The 3 element position vector and 3 element roll-pitch-yaw vector
        :rtype: Tuple[numpy.ndarray, numpy.ndarray]
        """
        return self._rox_transform_to_xyz_rpy(self.pose_to_rox_transform(transform))

    def rox_transform_to_named_pose(self, rox_transform, dtype=np.float64):
        """
        Converts a general_robotics_toolbox Transform to a Robot Raconteur NamedPose. The client_frame_id
        and parent_frame_id must be set in the general_robotics_toolbox Transform.

        :param rox_transform: The general_robotics_toolbox Transform
        :type rox_transform: general_robotics_toolbox.Transform
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.NamedPose
        :return: The Robot Raconteur NamedPose
        :rtype: com.robotraconteur.geometry.NamedPose
        """
        ret = self._create_return_struct(self._named_pose_type, dtype)
        ret.pose = self.rox_transform_to_pose(rox_transform)
        ret.frame = self._ident_util.CreateIdentifierFromName(rox_transform.child_frame_id)
        ret.parent_frame = self._ident_util.CreateIdentifierFromName(rox_transform.parent_frame_id)
        return ret

    def named_pose_to_rox_transform(self, rr_named_pose):
        """
        Convert a Robot Raconteur NamedPose to a general_robotics_toolbox Transform

        :param rr_named_pose: The Robot Raconteur NamedPose
        :type rr_named_pose: com.robotraconteur.geometry.NamedPose
        :return: The general_robotics_toolbox Transform
        :rtype: general_robotics_toolbox.Transform
        """
        R = self.quaternion_to_R(rr_named_pose.pose["orientation"])
        p = self.vector3_to_xyz(rr_named_pose.pose["position"])
        return rox.Transform(R, p, _name_from_identifier(rr_named_pose.parent_frame),
                             _name_from_identifier(rr_named_pose.frame))

    def xyz_rpy_to_named_pose(self, xyz, rpy, parent_frame_id, child_frame_id, dtype=np.float64):
        """
        Converts a 3 element position vector and 3 element roll-pitch-yaw vector in radians to a
        Robot Raconteur NamedPose

        :param xyz: The 3 element position vector
        :type xyz: numpy.ndarray
        :param rpy: The 3 element roll-pitch-yaw vector in radians
        :type rpy: numpy.ndarray
        :param parent_frame_id: The parent frame identifier
        :type parent_frame_id: str
        :param child_frame_id: The child frame identifier
        :type child_frame_id: str

        """
        return self.rox_transform_to_named_pose(self._xyz_rpy_to_rox_transform(xyz, rpy, parent_frame_id, child_frame_id), dtype)

    def named_pose_to_xyz_rpy(self, transform):
        """
        Convert a Robot Raconteur NamedPose to a 3 element position vector and 3 element roll-pitch-yaw vector in radians

        :param transform: The Robot Raconteur NamedPose
        :type transform: com.robotraconteur.geometry.NamedPose
        :return: The 3 element position vector and 3 element roll-pitch-yaw vector
        :rtype: Tuple[numpy.ndarray, numpy.ndarray]
        """
        return self._rox_transform_to_xyz_rpy_named(self.named_pose_to_rox_transform(transform))

    def array_to_spatial_velocity(self, spatial_velocity, dtype=np.float64):
        """
        Converts a 6 element spatial velocity vector to a Robot Raconteur SpatialVelocity

        :param spatial_velocity: The 6 element spatial velocity vector
        :type spatial_velocity: numpy.ndarray
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.SpatialVelocity
        :return: The Robot Raconteur SpatialVelocity
        :rtype: com.robotraconteur.geometry.SpatialVelocity
        """
        ret = self._create_return_np(self._spatial_velocity_type, dtype)
        ret[0]["angular"]["x"] = spatial_velocity[0]
        ret[0]["angular"]["y"] = spatial_velocity[1]
        ret[0]["angular"]["z"] = spatial_velocity[2]
        ret[0]["linear"]["x"] = spatial_velocity[3]
        ret[0]["linear"]["y"] = spatial_velocity[4]
        ret[0]["linear"]["z"] = spatial_velocity[5]
        return ret

    def spatial_velocity_to_array(self, rr_spatial_velocity):
        """
        Converts a Robot Raconteur SpatialVelocity to a 6 element spatial velocity vector

        :param rr_spatial_velocity: The Robot Raconteur SpatialVelocity
        :type rr_spatial_velocity: com.robotraconteur.geometry.SpatialVelocity
        :return: The 6 element spatial velocity vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_spatial_velocity[0]["angular"]["x"], rr_spatial_velocity[0]["angular"]["y"],
                         rr_spatial_velocity[0]["angular"]["z"], rr_spatial_velocity[0]["linear"]["x"],
                         rr_spatial_velocity[0]["linear"]["y"], rr_spatial_velocity[0]["linear"]["z"]])

    def array_to_spatial_acceleration(self, spatial_acceleration, dtype=np.float64):
        """
        Converts a 6 element spatial acceleration vector to a Robot Raconteur SpatialAcceleration

        :param spatial_acceleration: The 6 element spatial acceleration vector
        :type spatial_acceleration: numpy.ndarray
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.SpatialAcceleration
        :return: The Robot Raconteur SpatialAcceleration
        :rtype: com.robotraconteur.geometry.SpatialAcceleration
        """
        ret = self._create_return_np(self._spatial_acceleration_type, dtype)
        ret[0]["angular"]["x"] = spatial_acceleration[0]
        ret[0]["angular"]["y"] = spatial_acceleration[1]
        ret[0]["angular"]["z"] = spatial_acceleration[2]
        ret[0]["linear"]["x"] = spatial_acceleration[3]
        ret[0]["linear"]["y"] = spatial_acceleration[4]
        ret[0]["linear"]["z"] = spatial_acceleration[5]
        return ret

    def spatial_acceleration_to_array(self, rr_spatial_acceleration):
        """
        Converts a Robot Raconteur SpatialAcceleration to a 6 element spatial acceleration vector

        :param rr_spatial_acceleration: The Robot Raconteur SpatialAcceleration
        :type rr_spatial_acceleration: com.robotraconteur.geometry.SpatialAcceleration
        :return: The 6 element spatial acceleration vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_spatial_acceleration[0]["angular"]["x"], rr_spatial_acceleration[0]["angular"]["y"],
                         rr_spatial_acceleration[0]["angular"]["z"], rr_spatial_acceleration[0]["linear"]["x"],
                         rr_spatial_acceleration[0]["linear"]["y"], rr_spatial_acceleration[0]["linear"]["z"]])

    def array_to_wrench(self, wrench, dtype=np.float64):
        """
        Converts a 6 element wrench vector to a Robot Raconteur Wrench

        :param wrench: The 6 element wrench vector
        :type wrench: numpy.ndarray
        :param dtype: The numpy dtype of the transform. Must be float64, float32, or int32. Defaults to float64
        :type dtype: com.robotraconteur.geometry.Wrench
        :return: The Robot Raconteur Wrench
        :rtype: com.robotraconteur.geometry.Wrench
        """
        ret = self._create_return_np(self._wrench_type, dtype)
        ret[0]["torque"]["x"] = wrench[0]
        ret[0]["torque"]["y"] = wrench[1]
        ret[0]["torque"]["z"] = wrench[2]
        ret[0]["force"]["x"] = wrench[3]
        ret[0]["force"]["y"] = wrench[4]
        ret[0]["force"]["z"] = wrench[5]
        return ret

    def wrench_to_array(self, rr_wrench):
        """
        Converts a Robot Raconteur Wrench to a 6 element wrench vector

        :param rr_wrench: The Robot Raconteur Wrench
        :type rr_wrench: com.robotraconteur.geometry.Wrench
        :return: The 6 element wrench vector
        :rtype: numpy.ndarray
        """
        return np.array([rr_wrench[0]["torque"]["x"], rr_wrench[0]["torque"]["y"],
                         rr_wrench[0]["torque"]["z"], rr_wrench[0]["force"]["x"],
                         rr_wrench[0]["force"]["y"], rr_wrench[0]["force"]["z"]])
