"""
connection.grpc.bidi_stream

本模块导出:
- BidiStream: gRPC 双向流控制器
- BidiStreamReader: gRPC → Python 的消息读取接口
- BidiStreamWriter: Python → gRPC 的消息发送接口
"""

import abc
import asyncio
import contextlib
from collections.abc import AsyncIterator, Callable
from typing import Any, Generic, TypeVar

import grpc
from grpc.aio import AioRpcError

from tongsim.logger import get_logger

__all__ = ["BidiStream", "BidiStreamReader", "BidiStreamWriter"]

_logger = get_logger("gRPC")

GrpcReq = TypeVar("GrpcReq")
GrpcResp = TypeVar("GrpcResp")
T = TypeVar("T")


class StreamNotStartedError(RuntimeError):
    """标识未调用 start() 就开始通信的错误"""

    def __init__(self):
        super().__init__("Stream not started")


class BidiStream(Generic[GrpcReq, GrpcResp]):
    """
    封装 gRPC stream-stream 通信核心，提供读写状态管理与生命周期控制。
    通信调度逻辑交由外部执行，适配结构化并发管理模型。
    """

    def __init__(
        self, stub_func: Callable[[], grpc.aio.StreamStreamCall], name: str = ""
    ):
        self._stub_func = stub_func
        self._name = name
        self._running: bool = False
        self._stream: grpc.aio.StreamStreamCall | None = None

    async def start(self):
        """初始化 gRPC 流（必须在读写前调用）"""
        if self._stream is not None:
            raise RuntimeError("Stream already started")
        self._stream = self._stub_func()
        self._running = True
        _logger.info(f"[{self._name}] Stream started.")

    def is_running(self) -> bool:
        return self._running

    async def write(self, req: GrpcReq) -> bool:
        if not self._running or self._stream is None:
            raise StreamNotStartedError
        try:
            await self._stream.write(req)
            return True
        except AioRpcError as e:
            _logger.warning(f"[{self._name}] Write failed: {e}")
            return False

    async def aclose(self):
        if not self._stream:
            return
        _logger.debug(f"[{self._name}] Closing stream.")
        self._running = False
        with contextlib.suppress(Exception):
            await self._stream.done_writing()
        with contextlib.suppress(Exception):
            await self._stream.cancel()

    async def done_writing(self):
        """关闭写入端，但保留读取端。"""
        if self._stream and self._running:
            try:
                await self._stream.done_writing()
                _logger.debug(f"[{self._name}] Done writing.")
            except AioRpcError as e:
                _logger.warning(f"[{self._name}] done_writing failed: {e}")
        self._running = False

    async def read(self) -> GrpcResp:
        """单次读取响应。"""
        if self._stream is None:
            raise StreamNotStartedError
        try:
            return await self._stream.read()
        except AioRpcError as e:
            _logger.warning(f"[{self._name}] Read failed: {e}")
            raise

    def __aiter__(self):
        if self._stream is None:
            raise StreamNotStartedError
        return self._read_iterator()

    async def _read_iterator(self):
        if not self._stream:
            raise StreamNotStartedError

        while self._running:
            try:
                result = await self._stream.read()
                if result is None:
                    break
                yield result
            except asyncio.CancelledError:
                _logger.debug(f"[{self._name}] Read loop cancelled.")
                break
            except AioRpcError as e:
                _logger.warning(f"[{self._name}] Read loop error: {e}")
                break
            except Exception as e:
                _logger.exception(f"[{self._name}] Unexpected error in read loop: {e}")
                break

        self._running = False
        _logger.info(f"[{self._name}] Stream exited.")


class BidiStreamReader(abc.ABC, Generic[T]):
    """
    抽象类: BidiStreamReader 接收 gRPC 消息并解码为 Python 内部对象。
    子类需实现 _decode() 方法。
    """

    def __init__(self, stream: BidiStream):
        self._stream = stream

    async def read(self) -> T:
        grpc_resp = await self._stream.read()
        return self._decode(grpc_resp)

    def __aiter__(self) -> AsyncIterator[T]:
        return self._internal_iterator()

    async def _internal_iterator(self) -> AsyncIterator[T]:
        async for grpc_resp in self._stream:
            yield self._decode(grpc_resp)

    @abc.abstractmethod
    def _decode(self, grpc_resp: Any) -> T:
        """
        将 gRPC 响应消息转换为 Python 内部类型。
        """
        ...


class BidiStreamWriter(abc.ABC):
    """
    抽象类: BidiStreamWriter 接收 Python 参数并编码为 gRPC 请求消息。
    子类需实现 _encode() 方法。
    """

    def __init__(self, stream: BidiStream):
        self._stream = stream

    async def write(self, *args, **kwargs) -> bool:
        grpc_req = self._encode(*args, **kwargs)
        return await self._stream.write(grpc_req)

    async def done(self):
        await self._stream.done_writing()

    @abc.abstractmethod
    def _encode(self, *args, **kwargs) -> GrpcReq:
        """
        将 Python 参数编码为 gRPC 请求消息。
        """
        ...
