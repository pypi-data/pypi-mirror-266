from google.api import annotations_pb2 as _annotations_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetManifestRequest(_message.Message):
    __slots__ = ("empty",)
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class GetManifestResponse(_message.Message):
    __slots__ = ("metadata", "body", "model")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    metadata: Metadata
    body: Body
    model: _struct_pb2.Struct
    def __init__(self, metadata: _Optional[_Union[Metadata, _Mapping]] = ..., body: _Optional[_Union[Body, _Mapping]] = ..., model: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class SetManifestRequest(_message.Message):
    __slots__ = ("body",)
    BODY_FIELD_NUMBER: _ClassVar[int]
    body: Body
    def __init__(self, body: _Optional[_Union[Body, _Mapping]] = ...) -> None: ...

class SetManifestResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _empty_pb2.Empty
    def __init__(self, result: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class DeleteManifestRequest(_message.Message):
    __slots__ = ("empty",)
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    empty: _empty_pb2.Empty
    def __init__(self, empty: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class DeleteManifestResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _empty_pb2.Empty
    def __init__(self, result: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class Metadata(_message.Message):
    __slots__ = ("updated_at", "etag")
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ETAG_FIELD_NUMBER: _ClassVar[int]
    updated_at: _timestamp_pb2.Timestamp
    etag: str
    def __init__(self, updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., etag: _Optional[str] = ...) -> None: ...

class Body(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...
