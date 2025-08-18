from google.protobuf import any_pb2 as _any_pb2
from . import CommonDataStructsForUE_pb2 as _CommonDataStructsForUE_pb2
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

class FunctionRequest(_message.Message):
    __slots__ = ("code", "subject_name", "component_name", "action_name", "parameters")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTION_NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    code: int
    subject_name: str
    component_name: str
    action_name: str
    parameters: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(
        self,
        code: _Optional[int] = ...,
        subject_name: _Optional[str] = ...,
        component_name: _Optional[str] = ...,
        action_name: _Optional[str] = ...,
        parameters: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...,
    ) -> None: ...

class FunctionResponse(_message.Message):
    __slots__ = ("code", "msg", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    data: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(
        self,
        code: _Optional[int] = ...,
        msg: _Optional[str] = ...,
        data: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...,
    ) -> None: ...

class StreamingFunctionRequest(_message.Message):
    __slots__ = ("code", "subject_name", "component_name", "action_name", "parameters")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTION_NAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    code: int
    subject_name: str
    component_name: str
    action_name: str
    parameters: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(
        self,
        code: _Optional[int] = ...,
        subject_name: _Optional[str] = ...,
        component_name: _Optional[str] = ...,
        action_name: _Optional[str] = ...,
        parameters: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...,
    ) -> None: ...

class StreamingFunctionResponse(_message.Message):
    __slots__ = ("code", "subject_name", "component_name", "action_name", "data")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTION_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    code: int
    subject_name: str
    component_name: str
    action_name: str
    data: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(
        self,
        code: _Optional[int] = ...,
        subject_name: _Optional[str] = ...,
        component_name: _Optional[str] = ...,
        action_name: _Optional[str] = ...,
        data: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...,
    ) -> None: ...
