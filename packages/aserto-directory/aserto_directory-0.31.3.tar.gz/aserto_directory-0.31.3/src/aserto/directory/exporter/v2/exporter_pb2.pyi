from aserto.directory.common.v2 import common_pb2 as _common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Option(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPTION_UNKNOWN: _ClassVar[Option]
    OPTION_METADATA_OBJECT_TYPES: _ClassVar[Option]
    OPTION_METADATA_RELATION_TYPES: _ClassVar[Option]
    OPTION_METADATA_PERMISSIONS: _ClassVar[Option]
    OPTION_METADATA: _ClassVar[Option]
    OPTION_DATA_OBJECTS: _ClassVar[Option]
    OPTION_DATA_RELATIONS: _ClassVar[Option]
    OPTION_DATA_RELATIONS_WITH_KEYS: _ClassVar[Option]
    OPTION_DATA: _ClassVar[Option]
    OPTION_DATA_WITH_KEYS: _ClassVar[Option]
    OPTION_ALL: _ClassVar[Option]
    OPTION_ALL_WITH_KEYS: _ClassVar[Option]
OPTION_UNKNOWN: Option
OPTION_METADATA_OBJECT_TYPES: Option
OPTION_METADATA_RELATION_TYPES: Option
OPTION_METADATA_PERMISSIONS: Option
OPTION_METADATA: Option
OPTION_DATA_OBJECTS: Option
OPTION_DATA_RELATIONS: Option
OPTION_DATA_RELATIONS_WITH_KEYS: Option
OPTION_DATA: Option
OPTION_DATA_WITH_KEYS: Option
OPTION_ALL: Option
OPTION_ALL_WITH_KEYS: Option

class ExportRequest(_message.Message):
    __slots__ = ("options", "start_from")
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    START_FROM_FIELD_NUMBER: _ClassVar[int]
    options: int
    start_from: _timestamp_pb2.Timestamp
    def __init__(self, options: _Optional[int] = ..., start_from: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ExportResponse(_message.Message):
    __slots__ = ("object", "object_type", "relation", "relation_type", "permission")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    RELATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.Object
    object_type: _common_pb2.ObjectType
    relation: _common_pb2.Relation
    relation_type: _common_pb2.RelationType
    permission: _common_pb2.Permission
    def __init__(self, object: _Optional[_Union[_common_pb2.Object, _Mapping]] = ..., object_type: _Optional[_Union[_common_pb2.ObjectType, _Mapping]] = ..., relation: _Optional[_Union[_common_pb2.Relation, _Mapping]] = ..., relation_type: _Optional[_Union[_common_pb2.RelationType, _Mapping]] = ..., permission: _Optional[_Union[_common_pb2.Permission, _Mapping]] = ...) -> None: ...
