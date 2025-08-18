from collections.abc import Callable
from typing import Any

from google.protobuf.internal.well_known_types import Any as Proto_Any

from tongsim.math.geometry import Quaternion, Vector3

from .generated.CommonDataStructsForUE_pb2 import (
    Arrayf,
    ArrayStr,
    CommonStruct,
    Quaternionf,
    Vector3f,
)
from .generated.TongosAgentGRPCForUE_pb2 import FunctionRequest, FunctionResponse

__all__ = [
    "pack_to_request",
    "parse_from_response",
]


class ResponseParseError(Exception):
    def __init__(self, message: str, index: int):
        super().__init__(
            f"Failed to parse legacy gRPC response at index {index}: {message}\n"
        )
        self.index = index
        self.message = message


# ========= Pack =========
def _pack_bool(value: bool, request: FunctionRequest):
    param = request.parameters.add()
    param.Pack(CommonStruct(b=value))


def _pack_int(value: int, request: FunctionRequest):
    param = request.parameters.add()
    param.Pack(CommonStruct(i=value))


def _pack_float(value: float, request: FunctionRequest):
    param = request.parameters.add()
    param.Pack(CommonStruct(f=value))


def _pack_str(value: str, request: FunctionRequest):
    param = request.parameters.add()
    param.Pack(CommonStruct(str=value))


def _pack_vector3(value: Vector3, request: FunctionRequest):
    param = request.parameters.add()
    param.Pack(Vector3f(x=value.x, y=value.y, z=value.z))


def _pack_quaternion(value: Quaternion, request: FunctionRequest):
    param = request.parameters.add()
    param.Pack(Quaternionf(w=value.w, x=value.x, y=value.y, z=value.z))


def _pack_list_str(value: list[str], request: FunctionRequest):
    param = request.parameters.add()
    param.Pack(ArrayStr(str=value))


_pack_dispatch_table: dict[type, Callable[[Any, FunctionRequest], None]] = {
    bool: _pack_bool,
    int: _pack_int,
    float: _pack_float,
    str: _pack_str,
    Vector3: _pack_vector3,
    Quaternion: _pack_quaternion,
    list: _pack_list_str,
}


def pack_to_request(value: Any, request: FunctionRequest) -> None:
    """
    根据值的类型，将其打包为 CommonStruct 并添加到请求中。

    :param value: 要打包的值
    :param request: 请求对象
    :raises TypeError: 如果值类型不受支持
    """
    handler = _pack_dispatch_table.get(type(value))
    if handler is None:
        raise TypeError(f"Unsupported pack type: {type(value)}")
    handler(value, request)


# ========= UnPack =========


def _parse_bool(value: Proto_Any) -> bool:
    result = CommonStruct()
    value.Unpack(result)
    return result.b


def _parse_int(value: Proto_Any) -> int:
    result = CommonStruct()
    value.Unpack(result)
    return result.i


def _parse_float(value: Proto_Any) -> int:
    result = CommonStruct()
    value.Unpack(result)
    return result.f


def _parse_str(value: Proto_Any) -> str:
    result = CommonStruct()
    value.Unpack(result)
    return result.str


def _parse_vec3(value: Proto_Any) -> Vector3:
    result = Vector3f()
    value.Unpack(result)
    return Vector3(result.x, result.y, result.z)


def _parse_quat(value: Proto_Any) -> Quaternion:
    result = Quaternionf()
    value.Unpack(result)
    return Quaternion(w=result.w, x=result.x, y=result.y, z=result.z)


def _parse_list_str(value: Proto_Any) -> list[str]:
    result = ArrayStr()
    value.Unpack(result)
    return list(result.str)


def _parse_list_float(value: Proto_Any) -> list[float]:
    result = Arrayf()
    value.Unpack(result)
    return list(result.numberf)


_parse_dispatch_table: dict[type, Callable[[FunctionResponse, int], Any]] = {
    bool: _parse_bool,
    int: _parse_int,
    float: _parse_float,
    str: _parse_str,
    Vector3: _parse_vec3,
    Quaternion: _parse_quat,
    list[str]: _parse_list_str,
    list[float]: _parse_list_float,
}


def parse_from_response(
    expected_type: type, response: FunctionResponse, index: int
) -> Any:
    """
    从响应中按指定类型解析结果。

    :param expected_type: 期望的返回值类型
    :param response: gRPC 响应对象
    :param index: 要解析的数据索引
    :return: 解析得到的值
    :raises TypeError: 如果类型不支持
    """
    if index >= len(response.data):
        raise ResponseParseError("Index out of range", index)

    value: Proto_Any = response.data[index]
    handler = _parse_dispatch_table.get(expected_type)
    if handler is None:
        raise TypeError(f"Unsupported parse type: {expected_type}")
    return handler(value)
