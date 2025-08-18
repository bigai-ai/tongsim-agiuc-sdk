"""
connection.grpc.type.camera
"""

from dataclasses import dataclass, field

from tongsim_api_protocol.subsystem.camera_pb2 import CameraConfig, CameraImage

from tongsim.math.geometry import Quaternion, Vector3
from tongsim.type.camera import VisibleObjectInfo

__all__ = ["CameraImageWrapper"]


@dataclass(slots=True)
class CameraImageRequest:
    camera_id: str
    b_rgb: bool = True
    b_depth: bool = False
    b_segmentation: bool = False
    b_mirror_segmentation: bool = False
    b_fake_visible_object: bool = False

    def to_proto(self) -> CameraConfig:
        return CameraConfig(
            camera_id=self.camera_id,
            b_rgb=self.b_rgb,
            b_depth=self.b_depth,
            b_segmentation=self.b_segmentation,
            b_mirror_segmentation=self.b_mirror_segmentation,
            b_fake_visible_object=self.b_fake_visible_object,
        )


@dataclass(slots=True)
class CameraImageWrapper:
    """
    高性能 wrapper: 仅引用 proto，不复制字段。
    提供 memoryview 支持，避免图像字段拷贝。
    """

    _camera_image_grpc_message: CameraImage = field(repr=False)

    def __post_init__(self):
        if not isinstance(self._camera_image_grpc_message, CameraImage):
            raise TypeError("Expected CameraImage proto")

    @property
    def camera_id(self) -> str:
        return self._camera_image_grpc_message.camera_id

    @property
    def ts(self) -> int:
        return self._camera_image_grpc_message.ts

    @property
    def width(self) -> int:
        return self._camera_image_grpc_message.width

    @property
    def height(self) -> int:
        return self._camera_image_grpc_message.height

    @property
    def rgb(self) -> memoryview:
        return memoryview(self._camera_image_grpc_message.rgb or b"")

    @property
    def depth(self) -> memoryview:
        return memoryview(self._camera_image_grpc_message.depth or b"")

    @property
    def segmentation(self) -> memoryview:
        return memoryview(self._camera_image_grpc_message.segmentation or b"")

    @property
    def mirror_segmentation(self) -> memoryview:
        return memoryview(self._camera_image_grpc_message.mirror_segmentation or b"")

    @property
    def render_time(self) -> int:
        return self._camera_image_grpc_message.render_time

    @property
    def position(self) -> Vector3:
        pos = self._camera_image_grpc_message.position
        return Vector3(pos.x, pos.y, pos.z)

    @property
    def quaternion(self) -> Quaternion:
        q = self._camera_image_grpc_message.quaternion
        return Quaternion(w=q.w, x=q.x, y=q.y, z=q.z)

    @property
    def visible_objects(self) -> list[VisibleObjectInfo] | None:
        if not self._camera_image_grpc_message.HasField("fake_visible_object_list"):
            return None
        return [
            VisibleObjectInfo(
                object_id=vo.object_id,
                segmentation_id=vo.segmentation_id,
                distance_square=vo.distance_square,
            )
            for vo in self._camera_image_grpc_message.fake_visible_object_list.visible_object_info
        ]
