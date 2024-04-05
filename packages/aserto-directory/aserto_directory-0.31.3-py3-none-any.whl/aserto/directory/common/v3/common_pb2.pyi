from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Object(_message.Message):
    __slots__ = ("type", "id", "display_name", "properties", "created_at", "updated_at", "etag")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ETAG_FIELD_NUMBER: _ClassVar[int]
    type: str
    id: str
    display_name: str
    properties: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    etag: str
    def __init__(self, type: _Optional[str] = ..., id: _Optional[str] = ..., display_name: _Optional[str] = ..., properties: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., etag: _Optional[str] = ...) -> None: ...

class Relation(_message.Message):
    __slots__ = ("object_type", "object_id", "relation", "subject_type", "subject_id", "subject_relation", "created_at", "updated_at", "etag")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_RELATION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ETAG_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    relation: str
    subject_type: str
    subject_id: str
    subject_relation: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    etag: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., relation: _Optional[str] = ..., subject_type: _Optional[str] = ..., subject_id: _Optional[str] = ..., subject_relation: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., etag: _Optional[str] = ...) -> None: ...

class ObjectIdentifier(_message.Message):
    __slots__ = ("object_type", "object_id")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ...) -> None: ...

class RelationIdentifier(_message.Message):
    __slots__ = ("object_type", "object_id", "relation", "subject_type", "subject_id", "subject_relation")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_RELATION_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    relation: str
    subject_type: str
    subject_id: str
    subject_relation: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., relation: _Optional[str] = ..., subject_type: _Optional[str] = ..., subject_id: _Optional[str] = ..., subject_relation: _Optional[str] = ...) -> None: ...

class PaginationRequest(_message.Message):
    __slots__ = ("size", "token")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    size: int
    token: str
    def __init__(self, size: _Optional[int] = ..., token: _Optional[str] = ...) -> None: ...

class PaginationResponse(_message.Message):
    __slots__ = ("next_token",)
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    next_token: str
    def __init__(self, next_token: _Optional[str] = ...) -> None: ...
