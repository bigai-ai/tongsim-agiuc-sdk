from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class CommonStruct(_message.Message):
    __slots__ = ("str", "i", "b", "f", "d", "map_str_i", "bts")

    class MapStrIEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[int] = ...
        ) -> None: ...

    STR_FIELD_NUMBER: _ClassVar[int]
    I_FIELD_NUMBER: _ClassVar[int]
    B_FIELD_NUMBER: _ClassVar[int]
    F_FIELD_NUMBER: _ClassVar[int]
    D_FIELD_NUMBER: _ClassVar[int]
    MAP_STR_I_FIELD_NUMBER: _ClassVar[int]
    BTS_FIELD_NUMBER: _ClassVar[int]
    str: str
    i: int
    b: bool
    f: float
    d: float
    map_str_i: _containers.ScalarMap[str, int]
    bts: bytes
    def __init__(
        self,
        str: _Optional[str] = ...,
        i: _Optional[int] = ...,
        b: bool = ...,
        f: _Optional[float] = ...,
        d: _Optional[float] = ...,
        map_str_i: _Optional[_Mapping[str, int]] = ...,
        bts: _Optional[bytes] = ...,
    ) -> None: ...

class Vector2f(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(
        self, x: _Optional[float] = ..., y: _Optional[float] = ...
    ) -> None: ...

class Vector3f(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(
        self,
        x: _Optional[float] = ...,
        y: _Optional[float] = ...,
        z: _Optional[float] = ...,
    ) -> None: ...

class Vector2d(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(
        self, x: _Optional[float] = ..., y: _Optional[float] = ...
    ) -> None: ...

class Vector3d(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(
        self,
        x: _Optional[float] = ...,
        y: _Optional[float] = ...,
        z: _Optional[float] = ...,
    ) -> None: ...

class Quaternionf(_message.Message):
    __slots__ = ("x", "y", "z", "w")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    W_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    w: float
    def __init__(
        self,
        x: _Optional[float] = ...,
        y: _Optional[float] = ...,
        z: _Optional[float] = ...,
        w: _Optional[float] = ...,
    ) -> None: ...

class Quaterniond(_message.Message):
    __slots__ = ("x", "y", "z", "w")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    W_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    w: float
    def __init__(
        self,
        x: _Optional[float] = ...,
        y: _Optional[float] = ...,
        z: _Optional[float] = ...,
        w: _Optional[float] = ...,
    ) -> None: ...

class Matrix3x3f(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(
        self,
        x: _Optional[float] = ...,
        y: _Optional[float] = ...,
        z: _Optional[float] = ...,
    ) -> None: ...

class Matrix3x3d(_message.Message):
    __slots__ = ("x", "y", "z")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    z: float
    def __init__(
        self,
        x: _Optional[float] = ...,
        y: _Optional[float] = ...,
        z: _Optional[float] = ...,
    ) -> None: ...

class Arrayi(_message.Message):
    __slots__ = ("numberi",)
    NUMBERI_FIELD_NUMBER: _ClassVar[int]
    numberi: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, numberi: _Optional[_Iterable[int]] = ...) -> None: ...

class Arrayf(_message.Message):
    __slots__ = ("numberf",)
    NUMBERF_FIELD_NUMBER: _ClassVar[int]
    numberf: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, numberf: _Optional[_Iterable[float]] = ...) -> None: ...

class Arrayd(_message.Message):
    __slots__ = ("numberd",)
    NUMBERD_FIELD_NUMBER: _ClassVar[int]
    numberd: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, numberd: _Optional[_Iterable[float]] = ...) -> None: ...

class ArrayStr(_message.Message):
    __slots__ = ("str",)
    STR_FIELD_NUMBER: _ClassVar[int]
    str: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, str: _Optional[_Iterable[str]] = ...) -> None: ...

class Posef(_message.Message):
    __slots__ = ("vector3f", "quaternionf")
    VECTOR3F_FIELD_NUMBER: _ClassVar[int]
    QUATERNIONF_FIELD_NUMBER: _ClassVar[int]
    vector3f: Vector3f
    quaternionf: Quaternionf
    def __init__(
        self,
        vector3f: _Optional[_Union[Vector3f, _Mapping]] = ...,
        quaternionf: _Optional[_Union[Quaternionf, _Mapping]] = ...,
    ) -> None: ...

class Posed(_message.Message):
    __slots__ = ("vector3d", "quaterniond")
    VECTOR3D_FIELD_NUMBER: _ClassVar[int]
    QUATERNIOND_FIELD_NUMBER: _ClassVar[int]
    vector3d: Vector3f
    quaterniond: Quaternionf
    def __init__(
        self,
        vector3d: _Optional[_Union[Vector3f, _Mapping]] = ...,
        quaterniond: _Optional[_Union[Quaternionf, _Mapping]] = ...,
    ) -> None: ...

class Transformf(_message.Message):
    __slots__ = ("vector3f", "quaternionf")
    VECTOR3F_FIELD_NUMBER: _ClassVar[int]
    QUATERNIONF_FIELD_NUMBER: _ClassVar[int]
    vector3f: Vector3f
    quaternionf: Quaternionf
    def __init__(
        self,
        vector3f: _Optional[_Union[Vector3f, _Mapping]] = ...,
        quaternionf: _Optional[_Union[Quaternionf, _Mapping]] = ...,
    ) -> None: ...

class Transformd(_message.Message):
    __slots__ = ("vector3d", "quaterniond")
    VECTOR3D_FIELD_NUMBER: _ClassVar[int]
    QUATERNIOND_FIELD_NUMBER: _ClassVar[int]
    vector3d: Vector3d
    quaterniond: Quaterniond
    def __init__(
        self,
        vector3d: _Optional[_Union[Vector3d, _Mapping]] = ...,
        quaterniond: _Optional[_Union[Quaterniond, _Mapping]] = ...,
    ) -> None: ...

class GeoPoint(_message.Message):
    __slots__ = ("latitude", "longitude", "altitude")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float
    altitude: float
    def __init__(
        self,
        latitude: _Optional[float] = ...,
        longitude: _Optional[float] = ...,
        altitude: _Optional[float] = ...,
    ) -> None: ...

class JointLocationsMap(_message.Message):
    __slots__ = ("map",)

    class MapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Arrayf
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[Arrayf, _Mapping]] = ...,
        ) -> None: ...

    MAP_FIELD_NUMBER: _ClassVar[int]
    map: _containers.MessageMap[str, Arrayf]
    def __init__(self, map: _Optional[_Mapping[str, Arrayf]] = ...) -> None: ...

class PosefMap(_message.Message):
    __slots__ = ("map",)

    class MapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Posef
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[Posef, _Mapping]] = ...,
        ) -> None: ...

    MAP_FIELD_NUMBER: _ClassVar[int]
    map: _containers.MessageMap[str, Posef]
    def __init__(self, map: _Optional[_Mapping[str, Posef]] = ...) -> None: ...

class ImageRequestList(_message.Message):
    __slots__ = ("image_requests",)
    IMAGE_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    image_requests: _containers.RepeatedCompositeFieldContainer[ImageRequest]
    def __init__(
        self, image_requests: _Optional[_Iterable[_Union[ImageRequest, _Mapping]]] = ...
    ) -> None: ...

class ImageRequest(_message.Message):
    __slots__ = ("camera_name", "image_type", "pixels_as_float", "compress")
    CAMERA_NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PIXELS_AS_FLOAT_FIELD_NUMBER: _ClassVar[int]
    COMPRESS_FIELD_NUMBER: _ClassVar[int]
    camera_name: str
    image_type: int
    pixels_as_float: bool
    compress: bool
    def __init__(
        self,
        camera_name: _Optional[str] = ...,
        image_type: _Optional[int] = ...,
        pixels_as_float: bool = ...,
        compress: bool = ...,
    ) -> None: ...

class ImageResponseList(_message.Message):
    __slots__ = ("image_response",)
    IMAGE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    image_response: _containers.RepeatedCompositeFieldContainer[ImageResponse]
    def __init__(
        self,
        image_response: _Optional[_Iterable[_Union[ImageResponse, _Mapping]]] = ...,
    ) -> None: ...

class ImageResponse(_message.Message):
    __slots__ = (
        "image_data_float",
        "image_data_bytes",
        "camera_name",
        "camera_position",
        "camera_orientation",
        "message",
        "pixels_as_float",
        "compress",
        "width",
        "height",
        "ImageType",
        "time_stamp",
    )
    IMAGE_DATA_FLOAT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_BYTES_FIELD_NUMBER: _ClassVar[int]
    CAMERA_NAME_FIELD_NUMBER: _ClassVar[int]
    CAMERA_POSITION_FIELD_NUMBER: _ClassVar[int]
    CAMERA_ORIENTATION_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PIXELS_AS_FLOAT_FIELD_NUMBER: _ClassVar[int]
    COMPRESS_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    IMAGETYPE_FIELD_NUMBER: _ClassVar[int]
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    image_data_float: _containers.RepeatedScalarFieldContainer[float]
    image_data_bytes: bytes
    camera_name: str
    camera_position: Vector3f
    camera_orientation: Quaternionf
    message: str
    pixels_as_float: bool
    compress: bool
    width: int
    height: int
    ImageType: str
    time_stamp: int
    def __init__(
        self,
        image_data_float: _Optional[_Iterable[float]] = ...,
        image_data_bytes: _Optional[bytes] = ...,
        camera_name: _Optional[str] = ...,
        camera_position: _Optional[_Union[Vector3f, _Mapping]] = ...,
        camera_orientation: _Optional[_Union[Quaternionf, _Mapping]] = ...,
        message: _Optional[str] = ...,
        pixels_as_float: bool = ...,
        compress: bool = ...,
        width: _Optional[int] = ...,
        height: _Optional[int] = ...,
        ImageType: _Optional[str] = ...,
        time_stamp: _Optional[int] = ...,
    ) -> None: ...

class UECameraIntrinsicParams(_message.Message):
    __slots__ = ("fov", "width", "height")
    FOV_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    fov: float
    width: float
    height: float
    def __init__(
        self,
        fov: _Optional[float] = ...,
        width: _Optional[float] = ...,
        height: _Optional[float] = ...,
    ) -> None: ...
