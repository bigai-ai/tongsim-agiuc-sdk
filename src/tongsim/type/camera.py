"""
tongsim.type.camera
"""

from typing import NamedTuple


class CameraIntrinsic(NamedTuple):
    """
    相机内参结构。
    """

    fov: float
    width: int
    height: int


class VisibleObjectInfo(NamedTuple):
    """
    单个可见物体信息
    """

    object_id: str
    segmentation_id: int
    distance_square: float
