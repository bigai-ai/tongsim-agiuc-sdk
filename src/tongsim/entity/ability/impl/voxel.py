# tongsim/entity/ability/impl/voxel.py
import asyncio
from asyncio import Future
from collections.abc import AsyncIterator, Sequence
from typing import Protocol

from tongsim.connection.grpc import UnaryStreamAPI
from tongsim.entity.ability.base import AbilityImplBase
from tongsim.entity.ability.registry import AbilityRegistry
from tongsim.entity.entity import Entity
from tongsim.logger import get_logger
from tongsim.math import Vector3

_logger = get_logger("voxel")

__all__ = [
    "VoxelAbility",
]


class VoxelAbility(Protocol):
    """
    获取 Entity 周围体素的能力接口
    """

    def start_voxel_data_streaming(
        self,
        rate: float,
        voxel_half_resolution: tuple[int, int, int],
        voxel_extent: Vector3,
        center_offset: Vector3,
        is_ignore_self: bool = True,
        ignore_subjects: Sequence[str] | None = None,
    ) -> None:
        """
        启动体素数据流

        Args:
            rate (float): 数据流速率。
            voxel_half_resolution (tuple[int, int, int]): 体素分辨率的一半。
            voxel_extent (Vector3): 体素的范围。
            center_offset (Vector3): 偏移量。
            is_ignore_self (bool): 是否忽略自身。默认为 `True`。
            ignore_subjects (Sequence[str] | None): 要忽略的目标列表。默认为 `None`。
        """

    @property
    def is_streaming_started(self) -> bool:
        """
        是否开启告诉体素流

        Returns:
            bool: 是否开启体素流
        """

    @property
    def voxel_resolution(self) -> tuple[int, int, int]:
        """
        获取已开启体素流的分辨率

        Returns:
             tuple[int, int, int]: 体素流中半体素设置的分辨率
        """

    async def async_subscribe_voxel_data(
        self,
        rate: float,
        voxel_half_resolution: tuple[int, int, int],
        voxel_extent: Vector3,
        center_offset: Vector3,
        is_ignore_self: bool = True,
        ignore_subjects: Sequence[str] | None = None,
    ) -> AsyncIterator[bytes]:
        """
        异步直接订阅体素数据流

        Args:
            rate (float): 数据流速率。
            voxel_half_resolution (tuple[int, int, int]): 体素分辨率的一半。
            voxel_extent (Vector3): 体素的范围。
            center_offset (Vector3): 偏移量。
            is_ignore_self (bool): 是否忽略自身。默认为 `True`。
            ignore_subjects (Sequence[str] | None): 要忽略的目标列表。默认为 `None`。

        Returns:
            AsyncIterator[bytes]: 返回体素数据流。
        """

    async def async_fetch_voxel_data(self) -> bytes | None:
        """
        异步版本获取最新的体素数据

        Returns:
            bytes | None: 最新的体素数据或 `None`。
        """

    def block_fetch_voxel_data(self) -> bytes | None:
        """
        阻塞当前线程，直到获取到最新的体素数据。

        该方法暂时的等待，直到 `self._last_voxel` 不为 `None`，即获取到最新的体素数据。

        返回:
            bytes | None: 返回最新的体素数据（`bytes` 类型），超时则抛出异常。
        """


@AbilityRegistry.register(VoxelAbility)
class VoxelAbilityImpl(AbilityImplBase):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self._last_voxel: bytes | None = None
        self.component_id = entity.get_component_id("VoxelComponent")
        self._voxel_resolution: tuple[int, int, int] = (0, 0, 0)
        self._stream_task: Future | None = None
        self._voxel_data_event: asyncio.Event = asyncio.Event()

    @classmethod
    def is_applicable(cls, entity: "Entity") -> bool:
        return entity.has_component_type("VoxelComponent")

    @property
    def voxel_resolution(self) -> tuple[int, int, int]:
        return self._voxel_resolution

    @property
    def is_streaming_started(self):
        return self._stream_task and not self._stream_task.done()

    def start_voxel_data_streaming(
        self,
        rate: float,
        voxel_half_resolution: tuple[int, int, int],
        voxel_extent: Vector3,
        center_offset: Vector3,
        is_ignore_self: bool = True,
        ignore_subjects: Sequence[str] | None = None,
    ) -> None:
        self._voxel_resolution = tuple(x * 2 for x in voxel_half_resolution)

        async def handle_voxel():
            _logger.info(f"[Voxel {self._entity_id}] subscribe voxel starting")
            self._stream = UnaryStreamAPI.subscribe_voxel(
                self._context.conn,
                self.component_id,
                rate,
                voxel_half_resolution,
                voxel_extent,
                center_offset,
                is_ignore_self,
                ignore_subjects,
            )

            async for voxel in self._stream:
                _logger.debug(f"[Voxel {self._entity_id}] Received voxel batch")
                self._last_voxel = voxel
                self._voxel_data_event.set()
            _logger.info(f"[Voxel {self._entity_id}] subscribe voxel finished")

        self._stream_task = self._context.async_task(
            coro=handle_voxel(),
            name=f"[Voxel {self._entity_id} voxel_data streaming]",
        )

    async def _block_fetch_voxel(self, deepcopy: bool = False) -> bytes | None:
        await self._voxel_data_event.wait()
        self._voxel_data_event.clear()
        if deepcopy:
            return bytes(self._last_voxel)
        return self._last_voxel

    async def async_fetch_voxel_data(self, deepcopy: bool = False) -> bytes | None:
        if self._last_voxel is None:
            return None
        if deepcopy:
            return bytes(self._last_voxel)
        return self._last_voxel

    def block_fetch_voxel_data(
        self, deepcopy: bool = False, timeout: float = 2
    ) -> bytes | None:
        return self._context.sync_run(self._block_fetch_voxel(deepcopy), timeout)

    async def async_subscribe_voxel_data(
        self,
        rate: float,
        voxel_half_resolution: tuple[int, int, int],
        voxel_extent: Vector3,
        center_offset: Vector3,
        is_ignore_self: bool = True,
        ignore_subjects: Sequence[str] | None = None,
    ) -> AsyncIterator[bytes]:
        stream = UnaryStreamAPI.subscribe_voxel(
            rate=rate,
            component_id=self.component_id,
            voxel_half_resolution=voxel_half_resolution,
            voxel_extent=voxel_extent,
            center_offset=center_offset,
            is_ignore_self=is_ignore_self,
            ignore_subjects=ignore_subjects,
        )
        async for voxel in stream:
            yield voxel
