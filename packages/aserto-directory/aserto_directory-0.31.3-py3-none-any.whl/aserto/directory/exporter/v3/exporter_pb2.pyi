from aserto.directory.common.v3 import common_pb2 as _common_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Option(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPTION_UNKNOWN: _ClassVar[Option]
    OPTION_DATA_OBJECTS: _ClassVar[Option]
    OPTION_DATA_RELATIONS: _ClassVar[Option]
    OPTION_DATA: _ClassVar[Option]
    OPTION_STATS: _ClassVar[Option]
OPTION_UNKNOWN: Option
OPTION_DATA_OBJECTS: Option
OPTION_DATA_RELATIONS: Option
OPTION_DATA: Option
OPTION_STATS: Option

class ExportRequest(_message.Message):
    __slots__ = ("options", "start_from")
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    START_FROM_FIELD_NUMBER: _ClassVar[int]
    options: int
    start_from: _timestamp_pb2.Timestamp
    def __init__(self, options: _Optional[int] = ..., start_from: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ExportResponse(_message.Message):
    __slots__ = ("object", "relation", "stats")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.Object
    relation: _common_pb2.Relation
    stats: _struct_pb2.Struct
    def __init__(self, object: _Optional[_Union[_common_pb2.Object, _Mapping]] = ..., relation: _Optional[_Union[_common_pb2.Relation, _Mapping]] = ..., stats: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
