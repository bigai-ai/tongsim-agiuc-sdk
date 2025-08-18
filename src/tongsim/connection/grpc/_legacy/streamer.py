import asyncio

import grpc

from tongsim.connection.grpc._legacy.generated.TongosAgentGRPCForUE_pb2 import (
    StreamingFunctionRequest,
    StreamingFunctionResponse,
)
from tongsim.connection.grpc._legacy.generated.TongosAgentGRPCForUE_pb2_grpc import (
    ServiceInterfaceStub,
)
from tongsim.connection.grpc.bidi_stream import (
    BidiStream,
    BidiStreamReader,
    BidiStreamWriter,
)
from tongsim.connection.grpc.core import GrpcConnection
from tongsim.core import AsyncLoop
from tongsim.logger import get_logger

__all__ = ["LegacyStreamClient"]

_logger = get_logger("gRPC")

_SERVE_SUCCESS = 1


class _StreamingFunctionWriter(BidiStreamWriter):
    def _encode(self, req: StreamingFunctionRequest) -> StreamingFunctionRequest:
        return req


class _StreamingFunctionReader(BidiStreamReader[int]):
    def _decode(self, grpc_resp: StreamingFunctionResponse) -> int:
        return grpc_resp.code


class LegacyStreamClient:
    """
    LegacyStreamClient: 基于 tongos.service.ServiceInterface.StreamingFunction 的 gRPC 双向流通信层封装

    提供:
    - send(...) 发送程序组 StreamingFunctionRequest
    - 自动启动读写 loop, 用于分解 gRPC消息
    - on_receive(...) 注册 callback 处理解析后的数据
    """

    # Note:
    # 1. request:  废弃接口的 双向流 仅用于 set value，此处不加上 异步task 单独处理， 直接阻塞调用过程即可
    #   TODO: (wukunlun)  当前同步阻塞这一设计 是否会因为 TongSim 的 FPS 过低导致 Python 层出现问题？
    # 2. response: 废弃接口的 双向流 返回只有 code 一个字段有含义，处理 code 后直接 丢弃 response

    def __init__(self, conn: GrpcConnection, async_loop: AsyncLoop):
        self._stub: ServiceInterfaceStub = conn.get_stub(ServiceInterfaceStub)
        self._stream: BidiStream[
            StreamingFunctionRequest, StreamingFunctionResponse
        ] = BidiStream(self._stub.StreamingFunction, "Legacy gRPC bidi-stream")
        self._writer: _StreamingFunctionWriter = _StreamingFunctionWriter(self._stream)
        self._reader: _StreamingFunctionReader = _StreamingFunctionReader(self._stream)
        self._async_loop: AsyncLoop = async_loop

    async def start(self):
        await self._stream.start()
        self._async_loop.spawn(self._read_loop(), name="LegacyStreamClient:read_loop")

    async def write(self, req: StreamingFunctionRequest) -> bool:
        return await self._writer.write(req)

    async def close(self):
        await self._writer.done()

    async def _read_loop(self):
        try:
            async for resp in self._reader:
                if resp != _SERVE_SUCCESS:
                    _logger.warning(
                        f"[LegacyStreamClient] received code != {_SERVE_SUCCESS}: {resp}"
                    )
        except grpc.aio.AioRpcError as e:
            _logger.warning(f"[LegacyStreamClient] read failed: {e}")
        except asyncio.CancelledError:
            _logger.debug("[LegacyStreamClient] read loop cancelled.")
        finally:
            _logger.debug("[LegacyStreamClient] read loop exited.")
