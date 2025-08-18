from asyncio import Future
from collections.abc import AsyncIterator
from typing import Protocol

from tongsim.connection.grpc import UnaryStreamAPI
from tongsim.connection.grpc.type import CameraImageWrapper
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity
from tongsim.logger import get_logger

_logger = get_logger("hf_camera")

__all__ = [
    "HFCameraAbility",
]


class HFCameraAbility(Protocol):
    """
    高速相机能力接口定义，主要为图像数据采集（当前帧、流）
    """

    def start_imagedata_streaming(
        self, rgb=True, depth=False, segmentation=False
    ) -> None:
        """
        启动图像数据流接收任务。

        启动后，将持续接收来自服务器的图像帧数据，并缓存最近一帧。
        """

    @property
    def is_streaming_started(self) -> bool:
        """
        是否开启告诉相机流

        Returns:
            bool: 是否开启相机流
        """

    async def async_fetch_image_data_from_streaming(self) -> CameraImageWrapper | None:
        """
        获取最新接收到的图像数据（无阻塞）。

        返回缓存的最新图像数据（如果存在），如果没有接收到数据则返回 `None`。

        Returns:
            CameraImageWrapper | None: 最新的图像数据，若没有接收到图像则为 `None`。
        """

    async def async_fetch_rgb_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        """
        异步从图像数据流中获取最近接收到的 RGB 图像帧。

        Args:
            deep_copy (bool): 是否返回深拷贝副本。

        Returns:
            memoryview | bytes | None: RGB 图像数据（如果存在），如果没有数据则返回 `None`。
        """

    async def async_fetch_depth_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        """
        异步从图像数据流中获取最近接收到的深度图像帧。

        Args:
            deep_copy (bool): 是否返回深拷贝副本。

        Returns:
            memoryview | bytes | None: 深度图像数据（如果存在），如果没有数据则返回 `None`。
        """

    async def async_fetch_segmentation_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        """
        异步从图像数据流中获取最近接收到的图像帧。

        Args:
            deep_copy (bool): 是否返回深拷贝副本。

        Returns:
            memoryview | bytes | None: 分割图像数据（如果存在），如果没有数据则返回 `None`。
        """

    async def async_subscribe_imagedata(
        self, rgb: bool = True, depth: bool = True, segmentation: bool = True
    ) -> AsyncIterator[CameraImageWrapper]:
        """
        异步订阅图像数据流，返回一个异步迭代器，逐帧返回图像。

        该方法用于获取持续传输的图像流数据，可以在后台持续获取图像帧。

        Args:
            rgb (bool): 是否订阅rgb
            depth (bool): 是否订阅depth
            segmentation (bool): 是否订阅segmentation

        Returns:
            AsyncIterator[CameraImageWrapper]: 图像帧异步迭代器，每次迭代会返回一个 `CameraImageWrapper`。
        """


@AbilityRegistry.register(HFCameraAbility)
class HFCameraAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._last_imagedata: CameraImageWrapper | None = None
        self._stream_task: Future | None = None

    @classmethod
    def is_applicable(cls, entity: Entity) -> bool:
        return True

    @property
    def is_streaming_started(self):
        return self._stream_task and not self._stream_task.done()

    def start_imagedata_streaming(
        self, rgb=True, depth=False, segmentation=False
    ) -> None:
        async def handle_image():
            _logger.info(f"[HFCamera {self._entity_id}] subscribe image starting")
            stream = UnaryStreamAPI.subscribe_hf_image(
                self._context.conn,
                camera_id=self._entity_id,
                rgb=rgb,
                depth=depth,
                segmentation=segmentation,
            )

            # 缓存最新一帧的图像:
            async for image_batch in stream:
                _logger.debug(f"[HFCamera {self._entity_id}] Received image batch")
                if len(image_batch) != 1:
                    _logger.warning(
                        f"HFCamera stream received unexpected response length: {len(image_batch)}"
                    )
                self._last_imagedata = image_batch[0]
            _logger.info(f"[HFCamera {self._entity_id}] subscribe image finished")

        # 启动异步取图Task
        self._stream_task = self._context.async_task(
            coro=handle_image(),
            name=f"[HFCamera {self._entity_id} imagedata streaming]",
        )

    async def async_fetch_image_data_from_streaming(self) -> CameraImageWrapper | None:
        return self._last_imagedata

    async def async_fetch_rgb_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        return self._fetch_image_data(deep_copy, data_type="rgb")

    async def async_fetch_depth_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        return self._fetch_image_data(deep_copy, data_type="depth")

    async def async_fetch_segmentation_from_streaming(
        self, deep_copy: bool = False
    ) -> memoryview | bytes | None:
        return self._fetch_image_data(deep_copy, data_type="segmentation")

    async def async_subscribe_imagedata(
        self, rgb: bool = True, depth: bool = True, segmentation: bool = True
    ) -> AsyncIterator[CameraImageWrapper]:
        stream = UnaryStreamAPI.subscribe_hf_image(
            self._context.conn,
            self._entity_id,
            rgb,
            depth,
            segmentation,
        )
        async for image_batch in stream:
            if len(image_batch) != 1:
                _logger.warning(
                    f"HFCamera stream received unexpected response length: {len(image_batch)}"
                )
            yield image_batch[0]

    def _fetch_image_data(
        self, deep_copy: bool = False, data_type: str = "rgb"
    ) -> memoryview | bytes | None:
        if self._last_imagedata is None:
            return None

        data = getattr(self._last_imagedata, data_type, None)
        if data is None:
            return None

        return bytes(data) if deep_copy else data
