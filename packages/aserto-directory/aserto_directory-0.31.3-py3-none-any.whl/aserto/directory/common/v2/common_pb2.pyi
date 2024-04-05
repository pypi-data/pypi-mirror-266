from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Flag(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FLAG_UNKNOWN: _ClassVar[Flag]
    FLAG_HIDDEN: _ClassVar[Flag]
    FLAG_READONLY: _ClassVar[Flag]
    FLAG_SYSTEM: _ClassVar[Flag]
    FLAG_SHADOW: _ClassVar[Flag]
FLAG_UNKNOWN: Flag
FLAG_HIDDEN: Flag
FLAG_READONLY: Flag
FLAG_SYSTEM: Flag
FLAG_SHADOW: Flag

class ObjectType(_message.Message):
    __slots__ = ("name", "display_name", "is_subject", "ordinal", "status", "schema", "created_at", "updated_at", "hash")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_SUBJECT_FIELD_NUMBER: _ClassVar[int]
    ORDINAL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    name: str
    display_name: str
    is_subject: bool
    ordinal: int
    status: int
    schema: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    hash: str
    def __init__(self, name: _Optional[str] = ..., display_name: _Optional[str] = ..., is_subject: bool = ..., ordinal: _Optional[int] = ..., status: _Optional[int] = ..., schema: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., hash: _Optional[str] = ...) -> None: ...

class Permission(_message.Message):
    __slots__ = ("name", "display_name", "created_at", "updated_at", "hash")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    name: str
    display_name: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    hash: str
    def __init__(self, name: _Optional[str] = ..., display_name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., hash: _Optional[str] = ...) -> None: ...

class RelationType(_message.Message):
    __slots__ = ("name", "object_type", "display_name", "ordinal", "status", "unions", "permissions", "created_at", "updated_at", "hash")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    ORDINAL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    UNIONS_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    name: str
    object_type: str
    display_name: str
    ordinal: int
    status: int
    unions: _containers.RepeatedScalarFieldContainer[str]
    permissions: _containers.RepeatedScalarFieldContainer[str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    hash: str
    def __init__(self, name: _Optional[str] = ..., object_type: _Optional[str] = ..., display_name: _Optional[str] = ..., ordinal: _Optional[int] = ..., status: _Optional[int] = ..., unions: _Optional[_Iterable[str]] = ..., permissions: _Optional[_Iterable[str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., hash: _Optional[str] = ...) -> None: ...

class Object(_message.Message):
    __slots__ = ("key", "type", "display_name", "properties", "created_at", "updated_at", "hash")
    KEY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    key: str
    type: str
    display_name: str
    properties: _struct_pb2.Struct
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    hash: str
    def __init__(self, key: _Optional[str] = ..., type: _Optional[str] = ..., display_name: _Optional[str] = ..., properties: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., hash: _Optional[str] = ...) -> None: ...

class Relation(_message.Message):
    __slots__ = ("subject", "relation", "object", "created_at", "updated_at", "hash")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    subject: ObjectIdentifier
    relation: str
    object: ObjectIdentifier
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    hash: str
    def __init__(self, subject: _Optional[_Union[ObjectIdentifier, _Mapping]] = ..., relation: _Optional[str] = ..., object: _Optional[_Union[ObjectIdentifier, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., hash: _Optional[str] = ...) -> None: ...

class ObjectDependency(_message.Message):
    __slots__ = ("object_type", "object_key", "relation", "subject_type", "subject_key", "depth", "is_cycle", "path")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_KEY_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_KEY_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    IS_CYCLE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_key: str
    relation: str
    subject_type: str
    subject_key: str
    depth: int
    is_cycle: bool
    path: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, object_type: _Optional[str] = ..., object_key: _Optional[str] = ..., relation: _Optional[str] = ..., subject_type: _Optional[str] = ..., subject_key: _Optional[str] = ..., depth: _Optional[int] = ..., is_cycle: bool = ..., path: _Optional[_Iterable[str]] = ...) -> None: ...

class ObjectTypeIdentifier(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class PermissionIdentifier(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class RelationTypeIdentifier(_message.Message):
    __slots__ = ("name", "object_type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    object_type: str
    def __init__(self, name: _Optional[str] = ..., object_type: _Optional[str] = ...) -> None: ...

class ObjectIdentifier(_message.Message):
    __slots__ = ("type", "key")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    type: str
    key: str
    def __init__(self, type: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class RelationIdentifier(_message.Message):
    __slots__ = ("subject", "relation", "object")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    subject: ObjectIdentifier
    relation: RelationTypeIdentifier
    object: ObjectIdentifier
    def __init__(self, subject: _Optional[_Union[ObjectIdentifier, _Mapping]] = ..., relation: _Optional[_Union[RelationTypeIdentifier, _Mapping]] = ..., object: _Optional[_Union[ObjectIdentifier, _Mapping]] = ...) -> None: ...

class PaginationRequest(_message.Message):
    __slots__ = ("size", "token")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    size: int
    token: str
    def __init__(self, size: _Optional[int] = ..., token: _Optional[str] = ...) -> None: ...

class PaginationResponse(_message.Message):
    __slots__ = ("next_token", "result_size")
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    RESULT_SIZE_FIELD_NUMBER: _ClassVar[int]
    next_token: str
    result_size: int
    def __init__(self, next_token: _Optional[str] = ..., result_size: _Optional[int] = ...) -> None: ...
