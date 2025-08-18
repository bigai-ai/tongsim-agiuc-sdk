"""
connection.grpc.core

此模块封装了 gRPC.aio 通信通道与 Stub 的集中管理逻辑，提供统一的连接入口 `GrpcConnection`。

依赖:
- 所有服务 Stub 需由 `iter_all_grpc_stubs()` 函数动态发现并返回；
- 废弃的接口通过 `ServiceInterfaceStub` 单独处理。

"""

from typing import TypeVar

import grpc.aio
from tongsim_api_protocol.subsystem.mujoco_manager_pb2_grpc import (
    MujocoManagerServiceStub,
)

from tongsim.logger import get_logger

from ._legacy.generated.TongosAgentGRPCForUE_pb2_grpc import (
    ServiceInterfaceStub,
)
from .utils import iter_all_grpc_stubs

_logger = get_logger("gRPC")

T = TypeVar("T")  # 泛型变量，用于 get_stub 返回类型推断


class GrpcConnection:
    """
    自动初始化所有 gRPC stub 实例，提供访问和统一关闭通道功能。
    """

    def __init__(self, endpoint: str = "localhost:5056"):
        self._endpoint = endpoint
        self._channel: grpc.aio.Channel | None = grpc.aio.insecure_channel(
            self._endpoint
        )
        self._stubs: dict[type[object], object] = {}
        self._initialize()

    def _initialize(self):
        """
        加载 tongsim_api_protocol 包中所有 gRPC stub 并实例化。
        """
        for _service_name, stub_cls in iter_all_grpc_stubs():
            try:
                _logger.debug(f"GrpcConnection instantiate stub: {_service_name}")
                self._stubs[stub_cls] = stub_cls(self._channel)
            except Exception as e:
                raise RuntimeError(
                    f"GrpcConnection failed to instantiate stub: {_service_name}. {e}"
                ) from e

    def __enter__(self):
        raise RuntimeError("GrpcConnection must be used with 'async'")

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise RuntimeError("GrpcConnection must be used with 'async'")

    def get_stub(self, stub_cls: type[T]) -> T:
        """
        获取指定类型的 gRPC stub 实例。
        stub_cls: 例如 ExampleServiceStub
        返回值类型为 T（调用者传入的 stub_cls 类型）
        """
        if stub_cls not in self._stubs:
            raise ValueError(f"[GrpcConnection] Stub {stub_cls.__name__} not found.")
        return self._stubs[stub_cls]

    def __del__(self):
        if self._channel:
            _logger.error("GrpcConnection was not properly closed.")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()

    async def aclose(self):
        """
        关闭 gRPC 通道并释放资源。
        """
        if self._channel:
            await self._channel.close()
            self._channel = None
            _logger.debug(f"[GrpcConnection {self._endpoint}] closed channel")
        self._stubs.clear()


class GrpcLegacyConnection(GrpcConnection):
    """
    针对丢弃的通信接口，提供访问和统一关闭通道功能。
    """

    def __init__(self, endpoint: str = "localhost:50052"):
        self.tongos_service_interface_stub = None
        super().__init__(endpoint)

    def _initialize(self):
        """
        特殊处理已丢弃接口，仅初始化 tongos_service_interface_stub。
        """
        try:
            _logger.debug(
                "GrpcLegacyConnection instantiate stub: tongos_service_interface_stub"
            )
            self.tongos_service_interface_stub = ServiceInterfaceStub(self._channel)
        except Exception as e:
            raise RuntimeError(
                f"GrpcLegacyConnection failed to instantiate stub: tongos_service_interface_stub. {e}"
            ) from e

    def get_stub(self, stub_cls: type[T]) -> T:
        """
        返回 tongos_service_interface_stub
        """
        if stub_cls is not ServiceInterfaceStub:
            raise ValueError(
                f"[GrpcLegacyConnection] Unsupported stub type: {stub_cls.__name__}"
            )
        return self.tongos_service_interface_stub


class GrpcMujocoConnection(GrpcConnection):
    """
    Mujoco对接UE的功能接口。
    """

    def __init__(self, endpoint: str = "localhost:5066"):
        self.mujoco_stub = None
        super().__init__(endpoint)

    def _initialize(self):
        """
        仅初始化 mujoco_stub。
        """
        try:
            _logger.debug("GrpcMujocoConnection instantiate stub: mujoco_stub")
            self.mujoco_stub = MujocoManagerServiceStub(self._channel)
        except Exception as e:
            raise RuntimeError(
                f"GrpcMujocoConnection failed to instantiate stub: mujoco_stub. {e}"
            ) from e

    def get_stub(self, stub_cls: type[T]) -> T:
        """
        返回 mujoco_stub，忽略参数。
        """
        if stub_cls is not MujocoManagerServiceStub:
            raise ValueError(
                f"[GrpcMujocoConnection] Unsupported stub type: {stub_cls.__name__}"
            )
        return self.mujoco_stub
