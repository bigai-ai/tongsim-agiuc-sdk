"""
connection.grpc.utils

该模块提供对 protobuf 与 gRPC 相关模块的工具函数
"""

import functools
import importlib
import inspect
import pkgutil
from collections.abc import AsyncIterator, Awaitable, Callable, Generator
from typing import Any, ParamSpec, TypeVar, cast

from google.protobuf.message import Message as ProtoMessage
from tongsim_api_protocol.basic_pb2 import AABB
from tongsim_api_protocol.basic_pb2 import Pose as ProtoPose
from tongsim_api_protocol.basic_pb2 import Quaternion as ProtoQuaternion
from tongsim_api_protocol.basic_pb2 import Transform as ProtoTransform
from tongsim_api_protocol.basic_pb2 import Vector2 as ProtoVector2
from tongsim_api_protocol.basic_pb2 import Vector3 as ProtoVector3

from tongsim.logger import get_logger
from tongsim.math.geometry import Pose, Quaternion, Transform, Vector2, Vector3
from tongsim.math.geometry.type import Box

_logger = get_logger("gRPC")

__all__ = [
    "iter_all_grpc_stubs",
    "iter_all_proto_messages",
    "proto_to_sdk",
    "safe_async_rpc",
    "safe_unary_stream",
    "sdk_to_proto",
]

_PACKAGE = "tongsim_api_protocol"

T = TypeVar("T")
P = ParamSpec("P")


def iter_all_proto_messages() -> Generator[tuple[str, type[ProtoMessage]], None, None]:
    """遍历 tongsim_api_protocol 中所有模块中的 protobuf message 类型。

    Yields:
        tuple[str, type[ProtoMessage]]: 每个消息的全名与类定义。
    """
    pkg = importlib.import_module(_PACKAGE)
    for _, modname, ispkg in pkgutil.walk_packages(pkg.__path__, prefix=_PACKAGE + "."):
        if not ispkg and not modname.endswith("_pb2_grpc") and modname.endswith("_pb2"):
            proto_module = importlib.import_module(modname)
            for _, obj in inspect.getmembers(proto_module):
                if inspect.isclass(obj) and issubclass(obj, ProtoMessage):
                    yield obj.DESCRIPTOR.full_name, obj


def iter_all_grpc_stubs() -> Generator[tuple[str, type], None, None]:
    """遍历 tongsim_api_protocol 中所有模块中的 gRPC Stub 类型。

    Yields:
        tuple[str, type]: 每个 Stub 类名与类定义。
    """
    pkg = importlib.import_module(_PACKAGE)
    for _, modname, ispkg in pkgutil.walk_packages(pkg.__path__, prefix=_PACKAGE + "."):
        if not ispkg and modname.endswith("_pb2_grpc"):
            grpc_module = importlib.import_module(modname)
            for name, obj in inspect.getmembers(grpc_module, inspect.isclass):
                if name.endswith("Stub"):
                    yield name, obj


def safe_async_rpc(
    default: T | None = None, raise_on_error: bool = False
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    #     """
    #     装饰器: 用于 gRPC 调用安全封装。

    #     参数:
    #         default: 出错时返回的默认值
    #         raise_on_error: 是否在捕获异常后重新抛出（用于调试）

    #     用法:
    #         @safe_async_rpc(default={}, raise_on_error=False)
    #         def my_method(...): ...
    #     """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                _logger.debug(f"gRPC async call {func.__name__}")
                return await func(*args, **kwargs)
            except Exception:
                _logger.error(f"gRPC async call {func.__name__} failed", exc_info=True)
                if raise_on_error:
                    raise
            if callable(default) and inspect.iscoroutinefunction(default):
                return await default()
            return default

        return cast(Callable[P, Awaitable[T]], wrapper)

    return decorator


def safe_unary_stream(
    raise_on_error: bool = False,
) -> Callable[[Callable[P, AsyncIterator[T]]], Callable[P, AsyncIterator[T]]]:
    """
    装饰器: 用于 gRPC unary-stream 异步生成器的安全封装。

    参数:
        raise_on_error: 是否在异常时抛出错误，默认 False 则静默终止生成器。
    """

    def decorator(func: Callable[P, AsyncIterator[T]]) -> Callable[P, AsyncIterator[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> AsyncIterator[T]:
            _logger.debug(f"gRPC Unary-Stream  {func.__name__} starting.")

            try:
                async for item in func(*args, **kwargs):
                    yield item
            except Exception as e:
                _logger.error(
                    f"gRPC Unary-Stream Error in {func.__name__}: {e}", exc_info=True
                )
                if raise_on_error:
                    raise
                return  # 停止 async for

            _logger.debug(f"gRPC Unary-Stream {func.__name__} completed.")

        return cast(Callable[P, AsyncIterator[T]], wrapper)

    return decorator


# ========== SDK -> Proto ==========


def _sdk_to_proto_vector3(v: Vector3) -> ProtoVector3:
    return ProtoVector3(x=v.x, y=v.y, z=v.z)


def _sdk_to_proto_vector2(v: Vector2) -> ProtoVector2:
    return ProtoVector2(x=v.x, y=v.y)


def _sdk_to_proto_quaternion(q: Quaternion) -> ProtoQuaternion:
    return ProtoQuaternion(x=q.x, y=q.y, z=q.z, w=q.w)


def _sdk_to_proto_pose(p: Pose) -> ProtoPose:
    return ProtoPose(
        location=_sdk_to_proto_vector3(p.location),
        rotation=_sdk_to_proto_quaternion(p.rotation),
    )


def _sdk_to_proto_transform(t: Transform) -> ProtoTransform:
    return ProtoTransform(
        location=_sdk_to_proto_vector3(t.location),
        rotation=_sdk_to_proto_quaternion(t.rotation),
        scale=_sdk_to_proto_vector3(t.scale),
    )


_sdk_to_proto_dispatch: dict[type, Callable[[Any], ProtoMessage]] = {
    Vector3: _sdk_to_proto_vector3,
    Quaternion: _sdk_to_proto_quaternion,
    Pose: _sdk_to_proto_pose,
    Transform: _sdk_to_proto_transform,
    Vector2: _sdk_to_proto_vector2,
}


def sdk_to_proto(obj: Any) -> ProtoMessage:
    handler = _sdk_to_proto_dispatch.get(type(obj))
    if handler is None:
        raise TypeError(f"Unsupported SDK type: {type(obj)}")
    return handler(obj)


# ========== Proto -> SDK ==========


def _proto_to_sdk_vector3(v: ProtoVector3) -> Vector3:
    return Vector3(v.x, v.y, v.z)


def _proto_to_sdk_vector2(v: ProtoVector2) -> Vector2:
    return Vector2(v.x, v.y)


def _proto_to_sdk_quaternion(q: ProtoQuaternion) -> Quaternion:
    return Quaternion(w=q.w, x=q.x, y=q.y, z=q.z)


def _proto_to_sdk_pose(p: ProtoPose) -> Pose:
    return Pose(_proto_to_sdk_vector3(p.location), _proto_to_sdk_quaternion(p.rotation))


def _proto_to_sdk_transform(t: ProtoTransform) -> Transform:
    return Transform(
        _proto_to_sdk_vector3(t.location),
        _proto_to_sdk_quaternion(t.rotation),
        _proto_to_sdk_vector3(t.scale),
    )


def _proto_to_sdk_box(t: AABB) -> Box:
    return Box(
        _proto_to_sdk_vector3(t.min_vertex),
        _proto_to_sdk_vector3(t.max_vertex),
    )


_proto_to_sdk_dispatch: dict[type[ProtoMessage], Callable[[ProtoMessage], Any]] = {
    ProtoVector3: _proto_to_sdk_vector3,
    ProtoQuaternion: _proto_to_sdk_quaternion,
    ProtoPose: _proto_to_sdk_pose,
    ProtoTransform: _proto_to_sdk_transform,
    AABB: _proto_to_sdk_box,
    ProtoVector2: _sdk_to_proto_vector2,
}


def proto_to_sdk(message: ProtoMessage) -> Any:
    handler = _proto_to_sdk_dispatch.get(type(message))
    if handler is None:
        raise TypeError(f"Unsupported Proto message: {type(message)}")
    return handler(message)
