"""
Utility class to convert between Robot Raconteur Image structures and OpenCV format images. The OpenCV format
images are typically numpy arrays in monochrom, BGR, or BGRA format.

:param node: (optional) The Robot Raconteur node to use for parsing. Defaults to RobotRaconteurNode.s
:type node: RobotRaconteur.RobotRaconteurNode
:param client_obj: (optional) The client object to use for finding types. Defaults to None
:type client_obj: RobotRaconteur.ClientObject
"""

import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import numpy as np

import sys

try:
    import cv2
except:
    cv2 = None


class ImageUtil(object):

    def __init__(self, node=None, client_obj=None):
        if node is None:
            self._node = RRN
        else:
            self._node = node
        self._client_obj = client_obj

        self._image_type = self._node.GetStructureType("com.robotraconteur.image.Image", self._client_obj)
        self._image_info_type = self._node.GetStructureType("com.robotraconteur.image.ImageInfo", self._client_obj)
        self._compressed_image_type = self._node.GetStructureType(
            "com.robotraconteur.image.CompressedImage", self._client_obj)
        self._image_const = self._node.GetConstants("com.robotraconteur.image", self._client_obj)

    def image_to_array(self, rr_image):
        """
        Convert a Robot Raconteur Image to an array. The array will be in the format specified by the image encoding.

        The following image encoding codes are supported:

        - bgr888
        - rgb888
        - bgra8888
        - rgba8888
        - mono8
        - mono16
        - mono32
        - depth_f32

        :param rr_image: The Robot Raconteur Image to convert
        :type rr_image: com.robotraconteur.image.Image
        :return: The converted image
        :rtype: numpy.ndarray
        """

        encoding = rr_image.image_info.encoding

        encodings = self._image_const["ImageEncoding"]

        if encoding == encodings["bgr888"]:
            return rr_image.data.reshape([rr_image.image_info.height, rr_image.image_info.width, 3], order='C')

        if encoding == encodings["rgb888"]:
            img1 = rr_image.data.reshape([rr_image.image_info.height, rr_image.image_info.width, 3], order='C')
            return img1[..., ::-1].copy()

        if encoding == encodings["bgra8888"]:
            return rr_image.data.reshape([rr_image.image_info.height, rr_image.image_info.width, 4], order='C')

        if encoding == encodings["rgba8888"]:
            img1 = rr_image.data.reshape([rr_image.image_info.height, rr_image.image_info.width, 4], order='C')
            img2 = img1.copy()
            img2[..., 0] = img1[..., 2]
            img2[..., 2] = img1[..., 0]
            return img2

        if encoding == encodings["mono8"]:
            return rr_image.data.reshape([rr_image.image_info.height, rr_image.image_info.width], order='C')

        if encoding == encodings["mono16"] or encoding == encodings["depth_u16"]:
            assert sys.byteorder == "little"
            return rr_image.data.view(dtype=np.uint16).reshape([rr_image.image_info.height, rr_image.image_info.width], order='C').copy()

        if encoding == encodings["mono32"] or encoding == encodings["depth_u32"]:
            assert sys.byteorder == "little"
            return rr_image.data.view(dtype=np.uint32).reshape([rr_image.image_info.height, rr_image.image_info.width], order='C').copy()

        if encoding == encodings["depth_f32"]:
            assert sys.byteorder == "little"
            return rr_image.data.view(dtype=np.float32).reshape([rr_image.image_info.height, rr_image.image_info.width], order='C').copy()

        assert False, f"Unknown image encoding: {encoding}"

    def array_to_image(self, arr, encoding):
        """
        Convert a numpy array to a Robot Raconteur Image. The array must be in the format specified by the image encoding.

        The following image encoding codes are supported:

        - bgr888
        - rgb888
        - bgra8888
        - rgba8888
        - mono8
        - mono16
        - mono32
        - depth_f32

        :param arr: The array to convert
        :type arr: numpy.ndarray
        :encoding: The image encoding
        :type encoding: str
        :return: The converted image
        :rtype: com.robotraconteur.image.Image
        """

        encodings = self._image_const["ImageEncoding"]

        rr_image = self._image_type()
        rr_image_info = self._image_info_type()

        rr_image.image_info = rr_image_info
        rr_image_info.width = arr.shape[1]
        rr_image_info.height = arr.shape[0]

        if encoding == "bgr888":
            assert arr.shape[2] == 3
            assert arr.dtype == np.uint8
            rr_image.image_info.encoding = encodings["bgr888"]
            rr_image.image_info.step = rr_image.image_info.width * 3
            rr_image.data = arr.flatten(order="C")
            return rr_image

        if encoding == "rgb888":
            assert arr.shape[2] == 3
            assert arr.dtype == np.uint8
            rr_image.image_info.encoding = encodings["rgb888"]
            rr_image.image_info.step = rr_image.image_info.width * 3
            rr_image.data = arr.flatten(order="C")
            rr_image.data[0::3] = arr[..., 2].flatten(order="C")
            rr_image.data[2::3] = arr[..., 0].flatten(order="C")
            return rr_image

        if encoding == "bgra8888":
            assert arr.shape[2] == 4
            assert arr.dtype == np.uint8
            rr_image.image_info.encoding = encodings["bgra8888"]
            rr_image.image_info.step = rr_image.image_info.width * 4
            rr_image.data = arr.flatten(order="C")
            return rr_image

        if encoding == "rgba8888":
            assert arr.shape[2] == 4
            assert arr.dtype == np.uint8
            rr_image.image_info.encoding = encodings["rgba8888"]
            rr_image.image_info.step = rr_image.image_info.width * 4
            rr_image.data = np.zeros((arr.size,), dtype=np.uint8)
            rr_image.data[0::4] = arr[..., 2].flatten(order="C")
            rr_image.data[1::4] = arr[..., 1].flatten(order="C")
            rr_image.data[2::4] = arr[..., 0].flatten(order="C")
            rr_image.data[3::4] = arr[..., 3].flatten(order="C")
            return rr_image

        if encoding == "mono8":
            assert arr.ndim == 2 or arr.shape[2] == 1
            assert arr.dtype == np.uint8
            rr_image.image_info.encoding = encodings["mono8"]
            rr_image.image_info.step = rr_image.image_info.width
            rr_image.data = arr.flatten(order="C")
            return rr_image

        if encoding == "mono16" or encoding == "depth_u16":
            assert arr.ndim == 2 or arr.shape[2] == 1
            assert arr.dtype == np.uint16
            assert sys.byteorder == "little"
            rr_image.image_info.encoding = encodings[encoding]
            rr_image.image_info.step = rr_image.image_info.width * 2
            rr_image.data = arr.flatten(order="C").view(dtype=np.uint8).copy()
            return rr_image

        if encoding == "mono32" or encoding == "depth_u32":
            assert arr.ndim == 2 or arr.shape[2] == 1
            assert arr.dtype == np.uint32
            assert sys.byteorder == "little"
            rr_image.image_info.encoding = encodings[encoding]
            rr_image.image_info.step = rr_image.image_info.width * 4
            rr_image.data = arr.flatten(order="C").view(dtype=np.uint8).copy()
            return rr_image

        if encoding == "depth_f32":
            assert arr.ndim == 2 or arr.shape[2] == 1
            assert arr.dtype == np.float32
            assert sys.byteorder == "little"
            rr_image.image_info.encoding = encodings[encoding]
            rr_image.image_info.step = rr_image.image_info.width * 4
            rr_image.data = arr.flatten(order="C").view(dtype=np.uint8).copy()
            return rr_image

        assert False, f"Unknown image encoding: {encoding}"

    def array_to_compressed_image_jpg(self, arr, quality=95):
        """
        Convert a numpy array to a compressed Robot Raconteur Image in jpg format.

        :param arr: The array to convert
        :type arr: numpy.ndarray
        :param quality: The JPEG quality (0-100). Default is 95.
        :type quality: int
        :return: The converted image
        :rtype: com.robotraconteur.image.CompressedImage
        """
        assert cv2, "OpenCV required for image compression"

        rr_image = self._compressed_image_type()
        rr_image_info = self._image_info_type()

        rr_image.image_info = rr_image_info
        rr_image_info.width = arr.shape[1]
        rr_image_info.height = arr.shape[0]
        rr_image_info.encoding = self._image_const["ImageEncoding"]["compressed"]

        res, encimg = cv2.imencode(".jpg", arr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

        assert res, "Image compression failed"

        rr_image.data = encimg
        return rr_image

    def array_to_compressed_image_png(self, arr):
        """
        Convert a numpy array to a compressed Robot Raconteur Image in png format.

        :param arr: The array to convert
        :type arr: numpy.ndarray
        :return: The converted image
        :rtype: com.robotraconteur.image.CompressedImage
        """
        assert cv2, "OpenCV required for image compression"

        rr_image = self._compressed_image_type()
        rr_image_info = self._image_info_type()

        rr_image.image_info = rr_image_info
        rr_image_info.width = arr.shape[1]
        rr_image_info.height = arr.shape[0]
        rr_image_info.encoding = self._image_const["ImageEncoding"]["compressed"]

        res, encimg = cv2.imencode(".png", arr)

        assert res, "Image compression failed"

        rr_image.data = encimg
        return rr_image

    def compressed_image_to_array(self, rr_compressed_image, flags=-1):
        """
        Convert a compressed Robot Raconteur Image to a numpy array. This function uses cv2.imdecode to decode the image.

        :param rr_compressed_image: The image to convert
        :type rr_compressed_image: com.robotraconteur.image.CompressedImage
        :param flags: OpenCV flags for decoding. Default is -1.
        :type flags: int
        """

        return cv2.imdecode(rr_compressed_image.data, flags)
