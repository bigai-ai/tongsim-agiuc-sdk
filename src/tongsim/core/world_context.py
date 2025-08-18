"""
core.world_context

定义 WorldContext: 管理与单个 TongSim 实例绑定的底层资源，
包括异步事件循环、gRPC 通信等。

"""

import threading
import uuid
from collections.abc import Awaitable
from concurrent.futures import Future
from typing import Any, Final

from tongsim.connection.grpc import (
    GrpcConnection,
    GrpcLegacyConnection,
    LegacyStreamClient,
)
from tongsim.core import AsyncLoop
from tongsim.logger import get_logger

_logger = get_logger("world")


class WorldContext:
    """
    WorldContext 集中管理 TongSim 运行时上下文资源

    统一管理:
    - 异步事件主循环（AsyncLoop）
    - gRPC 连接（GrpcConnection、LegacyGrpcStreamClient）

    注意:
        - 析构时自动关闭所有资源。
    """

    def __init__(self, grpc_endpoint: str, legacy_grpc_endpoint: str):
        self._uuid: Final[uuid.UUID] = uuid.uuid4()
        self._loop: Final[AsyncLoop] = AsyncLoop(name=f"world-main-loop-{self._uuid}")
        self._loop.start()

        self._conn: Final[GrpcConnection]
        self._conn_legacy: Final[GrpcLegacyConnection]
        self._legacy_stream_client: Final[LegacyStreamClient]

        # gRPC 会检查 task 的 loop 一致性, 此处保证 gRPC stub 的初始化都在 AsyncLoop 下:
        self.sync_run(self._async_init_grpc(grpc_endpoint, legacy_grpc_endpoint))

        _logger.debug(f"[WorldContext {self._uuid}] started.")
        self._is_shutdown: bool = False

    # TODO: classmethod
    async def _async_init_grpc(self, grpc_endpoint: str, legacy_grpc_endpoint: str):
        self._conn = GrpcConnection(grpc_endpoint)
        self._conn_legacy = GrpcLegacyConnection(legacy_grpc_endpoint)
        self._legacy_stream_client = LegacyStreamClient(self._conn_legacy, self._loop)
        await self._legacy_stream_client.start()

    @property
    def uuid(self) -> str:
        """当前 World 实例的唯一标识符的前八位字符"""
        return str(self._uuid)[:8]

    @property
    def loop(self) -> AsyncLoop:
        """主事件循环"""
        return self._loop

    @property
    def conn(self) -> GrpcConnection:
        """gRPC 连接"""
        return self._conn

    @property
    def conn_legacy(self) -> GrpcLegacyConnection:
        """弃用的 gRPC 连接"""
        return self._conn_legacy

    @property
    def legacy_stream_client(self) -> LegacyStreamClient:
        """弃用的 gRPC 双向流客户端"""
        # if self._legacy_stream_client is None:
        #     with self._legacy_stream_client_lock:
        #         if self._legacy_stream_client is None:
        #             self._legacy_stream_client = LegacyStreamClient(
        #                 self._conn_legacy, self._loop
        #             )
        #             self.sync_run(self._legacy_stream_client.start())
        return self._legacy_stream_client

    def sync_run(self, coro: Awaitable, timeout: float | None = None) -> Any:
        """
        在事件循环中同步运行异步任务，并阻塞直到任务完成。

        Args:
            coro (Awaitable): 要执行的异步协程。
            timeout (float | None): 可选的超时时间（秒），超过此时间将抛出 TimeoutError。

        Returns:
            Any: 协程的返回结果。
        """
        if threading.current_thread() is self._loop.thread:
            raise RuntimeError(
                f"Cannot call `sync_run` from the same thread as AsyncLoop [{self._loop.name}] — this would cause a deadlock."
            )

        return self._loop.spawn(
            coro, name=f"[World-Context {self.uuid} sync task]"
        ).result(timeout=timeout)

    def async_task(self, coro: Awaitable[Any], name: str) -> Future[Any]:
        """
        启动一个异步任务
        """
        return self._loop.spawn(coro, name=name)

    def release(self):
        """
        释放所有资源，包括:
        - 停止任务组
        - 关闭 gRPC
        - 停止事件循环
        """
        if self._is_shutdown:
            return
        self._is_shutdown = True

        _logger.debug(f"[WorldContext {self._uuid}] releasing...")

        try:
            self._loop.cancel_tasks(timeout=1.0)
            self._loop.spawn(
                self._conn_legacy.aclose(),
                name=f"WorldContext {self.uuid} release legacy gRPC connection.",
            ).result(timeout=1.0)
            self._loop.spawn(
                self._conn.aclose(),
                name=f"WorldContext {self.uuid} release gRPC connection.",
            ).result(timeout=1.0)
        except Exception as e:
            _logger.warning(
                f"[WorldContext {self._uuid}] failed to release cleanly: {e}"
            )

        self._loop.stop()
        _logger.debug(f"[WorldContext {self._uuid}] release complete.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __del__(self):
        _logger.debug(f"[WorldContext {self._uuid}] gc.")
        self.release()
