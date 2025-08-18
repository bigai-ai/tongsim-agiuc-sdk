# tongsim/entity/ability/impl/camera.py

from collections.abc import AsyncIterator
from typing import Protocol

from tongsim.connection.grpc import UnaryAPI, UnaryStreamAPI
from tongsim.connection.grpc.type import CameraImageRequest, CameraImageWrapper
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity
from tongsim.logger import get_logger
from tongsim.type.camera import CameraIntrinsic, VisibleObjectInfo

_logger = get_logger("camera")

__all__ = [
    "CameraAbility",
]


class CameraAbility(Protocol):
    """
    相机能力接口定义，包括:
    - 相机挂载
    - 内参配置
    - 图像数据采集（当前帧、历史帧、流）
    - 可见物体检测结果访问等。
    """

    def attach_to_target_socket(self, target_id: str, socket_name: str) -> bool:
        """
        将当前相机挂载到目标 Entity 的指定 socket 上。

        Args:
            target_id (str): 目标实体 ID
            socket_name (str): 目标 socket 名称。常用socket:["MidCameraSocket","LeftCameraSocket","RightCameraSocket"]

        Returns:
            bool: 是否成功挂载。
        """

    def set_intrinsic_params(self, fov: float, width: int, height: int) -> bool:
        """
        设置相机的内参，包括视场角、分辨率等。

        Args:
            fov (float): 相机的视场角（Field of View）。
            width (int): 图像宽度（单位: 像素）。
            height (int): 图像高度（单位: 像素）。

        Returns:
            bool: 是否设置成功。
        """

    def get_intrinsic_params(self) -> CameraIntrinsic:
        """
        获取当前相机的内参配置。

        Returns:
            CameraIntrinsic: 包含 fov、width 和 height 的内参信息。
        """

    def start_imagedata_streaming(
        self,
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
        mirror_segmentation: bool = False,
        visible_object_list: bool = False,
    ) -> None:
        """
        启动图像数据流接收任务。

        启动后，将持续接收来自服务器的图像帧数据，并缓存最近一帧。

        Args:
            rgb (bool): 是否接收 RGB 图像数据。
            depth (bool): 是否接收深度图像。
            segmentation (bool): 是否接收分割图像。
            mirror_segmentation (bool): 是否接收镜子中的分割图像。
            visible_object_list (bool): 是否接收可见物体列表。
        """

    def stop_imagedata_streaming(self) -> bool:
        """
        停止图像数据流接收任务（暂未实现）。

        Returns:
            bool: 停止是否成功。
        """

    def fetch_image_data_from_streaming(self) -> CameraImageWrapper | None:
        """
        从图像数据流中获取最近一帧的完整图像数据封装。

        返回:
            CameraImageWrapper | None: 图像数据封装对象，包含 RGB、深度、分割、可见物体信息等；
                                    若当前尚未接收到任何图像帧，则返回 None。
        """

    def fetch_rgb_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        """
        从图像数据流中获取最近接收到的 RGB 图像帧。

        Args:
            deep_copy (bool): 是否返回深拷贝副本。

        Returns:
            memoryview | bytes | None: RGB 图像数据（如果存在）。
        """

    def fetch_depth_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        """
        从图像数据流中获取最近接收到的深度图像帧。

        Args:
            deep_copy (bool): 是否返回深拷贝副本。

        Returns:
            memoryview | bytes | None: 深度图像数据（如果存在）。
        """

    def fetch_segmentation_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        """
        从图像数据流中获取最近接收到的分割图像帧。

        Args:
            deep_copy (bool): 是否返回深拷贝副本。

        Returns:
            memoryview | bytes | None: 分割图像数据（如果存在）。
        """

    def fetch_mirror_segmentation_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        """
        从图像数据流中获取最近接收到的镜子中的分割图像帧。

        Args:
            deep_copy (bool): 是否返回深拷贝副本。

        Returns:
            memoryview | bytes | None: 镜子中的分割图像数据（如果存在）。
        """

    def fetch_visible_object_list_from_streaming(
        self,
    ) -> list[VisibleObjectInfo] | None:
        """
        从图像数据流中获取最近一帧图像数据中检测到的可见物体信息列表。

        Returns:
            list[VisibleObjectInfo] | None: 可见物体信息列表，若尚未接收或未启用则为 None。
        """

    def get_current_imageshot(
        self,
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
        mirror_segmentation: bool = False,
        visible_object_list: bool = False,
    ) -> CameraImageWrapper | None:
        """
        以同步方式请求当前图像帧（一次性抓拍）。

        Args:
            rgb (bool): 是否获取 RGB 图像。
            depth (bool): 是否获取深度图像。
            segmentation (bool): 是否获取语义分割图像。
            mirror_segmentation (bool): 是否获取镜像分割图像。
            visible_object_list (bool): 是否包含可见物体列表。

        Returns:
            CameraImageWrapper | None: 包含图像内容的封装对象，若失败则为 None。
        """

    async def async_get_current_imageshot(
        self,
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
        mirror_segmentation: bool = False,
        visible_object_list: bool = False,
    ) -> CameraImageWrapper | None:
        """
        以异步方式请求当前图像帧（一次性抓拍）。

        Args:
            rgb (bool): 是否获取 RGB 图像。
            depth (bool): 是否获取深度图像。
            segmentation (bool): 是否获取语义分割图像。
            mirror_segmentation (bool): 是否获取镜像分割图像。
            visible_object_list (bool): 是否包含可见物体列表。

        Returns:
            CameraImageWrapper | None: 包含图像内容的封装对象，若失败则为 None。
        """

    async def async_subscribe_imagedata(
        self,
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
        mirror_segmentation: bool = False,
        visible_object_list: bool = False,
    ) -> AsyncIterator[CameraImageWrapper]:
        """
        异步订阅图像数据流，返回一个异步迭代器，逐帧返回图像。

        Args:
            rgb (bool): 是否订阅 RGB 图像。
            depth (bool): 是否订阅深度图像。
            segmentation (bool): 是否订阅语义分割图像。
            mirror_segmentation (bool): 是否订阅镜像分割图像。
            visible_object_list (bool): 是否订阅可见物体列表。

        Returns:
            AsyncIterator[CameraImageWrapper]: 图像帧异步迭代器。
        """


@AbilityRegistry.register(CameraAbility)
class CameraAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._is_streaming_imagedata: bool = False
        self._last_imagedata: CameraImageWrapper | None = None

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        # TODO: 判断 camera param  component
        return True

    def attach_to_target_socket(self, target_id: str, socket_name: str) -> bool:
        return self._context.sync_run(
            UnaryAPI.attach_camera_to_target_socket(
                self._context.conn, self._entity_id, target_id, socket_name
            )
        )

    def set_intrinsic_params(self, fov: float, width: int, height: int) -> bool:
        return self._context.sync_run(
            UnaryAPI.set_camera_intrinsic_params(
                self._context.conn, self._entity_id, fov, width, height
            )
        )

    def get_intrinsic_params(self) -> CameraIntrinsic:
        fov, width, height = self._context.sync_run(
            UnaryAPI.get_camera_intrinsic_params(self._context.conn, self._entity_id)
        )
        return CameraIntrinsic(fov, width, height)

    def start_imagedata_streaming(
        self,
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
        mirror_segmentation: bool = False,
        visible_object_list: bool = False,
    ) -> None:
        async def handle_image():
            _logger.info(f"[Camera {self._entity_id}] subscribe image starting")
            stream = UnaryStreamAPI.subscribe_image(
                self._context.conn,
                [
                    CameraImageRequest(
                        self._entity_id,
                        rgb,
                        depth,
                        segmentation,
                        mirror_segmentation,
                        visible_object_list,
                    ),
                ],
                # TODO: stream name
                stream_name=self._entity_id,
            )
            _logger.debug(f"[Camera {self._entity_id}] subscribe image")

            # 缓存最新一帧的图像:
            async for image_batch in stream:
                _logger.debug(f"[Camera {self._entity_id}] Received image batch")
                if len(image_batch) != 1:
                    _logger.warning(
                        f"Camera stream received unexpected response length: {len(image_batch)}"
                    )
                self._last_imagedata = image_batch[0]
            _logger.info(f"[Camera {self._entity_id}] subscribe image finished")

        if self._is_streaming_imagedata:
            return

        self._is_streaming_imagedata = True
        # 启动异步取图Task
        self._context.async_task(
            coro=handle_image(),
            name=f"[Camera {self._entity_id} imagedata streaming]",
        )

    def stop_imagedata_streaming(self) -> bool:
        is_stopped = self._context.sync_run(
            UnaryAPI.cancel_image_stream(self._context.conn, self._entity_id)
        )
        if is_stopped:
            self._is_streaming_imagedata = False

    def fetch_image_data_from_streaming(self) -> CameraImageWrapper | None:
        return self._last_imagedata

    def fetch_rgb_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        if self._last_imagedata is None or self._last_imagedata.rgb is None:
            return None
        return (
            bytes(self._last_imagedata.rgb) if deep_copy else self._last_imagedata.rgb
        )

    def fetch_depth_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        if self._last_imagedata is None or self._last_imagedata.depth is None:
            return None
        return (
            bytes(self._last_imagedata.depth)
            if deep_copy
            else self._last_imagedata.depth
        )

    def fetch_segmentation_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        if self._last_imagedata is None or self._last_imagedata.segmentation is None:
            return None
        return (
            bytes(self._last_imagedata.segmentation)
            if deep_copy
            else self._last_imagedata.segmentation
        )

    def fetch_mirror_segmentation_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        if (
            self._last_imagedata is None
            or self._last_imagedata.mirror_segmentation is None
        ):
            return None
        return (
            bytes(self._last_imagedata.mirror_segmentation)
            if deep_copy
            else self._last_imagedata.mirror_segmentation
        )

    def fetch_visible_object_list_from_streaming(
        self,
    ) -> list[VisibleObjectInfo] | None:
        if self._last_imagedata is None or not self._last_imagedata.visible_objects:
            return None
        return self._last_imagedata.visible_objects

    def get_current_imageshot(
        self,
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
        mirror_segmentation: bool = False,
        visible_object_list: bool = False,
    ) -> CameraImageWrapper | None:
        return self._context.sync_run(
            self.async_get_current_imageshot(
                rgb, depth, segmentation, mirror_segmentation, visible_object_list
            )
        )

    async def async_get_current_imageshot(
        self,
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
        mirror_segmentation: bool = False,
        visible_object_list: bool = False,
    ) -> CameraImageWrapper | None:
        return await UnaryAPI.get_camera_image(
            self._context.conn,
            CameraImageRequest(
                self._entity_id,
                rgb,
                depth,
                segmentation,
                mirror_segmentation,
                visible_object_list,
            ),
        )

    async def async_subscribe_imagedata(
        self,
        rgb: bool = True,
        depth: bool = False,
        segmentation: bool = False,
        mirror_segmentation: bool = False,
        visible_object_list: bool = False,
    ) -> AsyncIterator[CameraImageWrapper]:
        stream = UnaryStreamAPI.subscribe_image(
            self._context.conn,
            [
                CameraImageRequest(
                    self._entity_id,
                    rgb,
                    depth,
                    segmentation,
                    mirror_segmentation,
                    visible_object_list,
                ),
            ],
        )
        async for image_batch in stream:
            if len(image_batch) != 1:
                _logger.warning(
                    f"Camera stream received unexpected response length: {len(image_batch)}"
                )
            yield image_batch[0]
