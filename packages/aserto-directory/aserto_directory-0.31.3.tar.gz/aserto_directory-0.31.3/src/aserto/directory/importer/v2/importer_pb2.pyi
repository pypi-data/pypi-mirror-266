from aserto.directory.common.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Opcode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPCODE_UNKNOWN: _ClassVar[Opcode]
    OPCODE_SET: _ClassVar[Opcode]
    OPCODE_DELETE: _ClassVar[Opcode]
OPCODE_UNKNOWN: Opcode
OPCODE_SET: Opcode
OPCODE_DELETE: Opcode

class ImportRequest(_message.Message):
    __slots__ = ("op_code", "object_type", "permission", "relation_type", "object", "relation")
    OP_CODE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    RELATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    op_code: Opcode
    object_type: _common_pb2.ObjectType
    permission: _common_pb2.Permission
    relation_type: _common_pb2.RelationType
    object: _common_pb2.Object
    relation: _common_pb2.Relation
    def __init__(self, op_code: _Optional[_Union[Opcode, str]] = ..., object_type: _Optional[_Union[_common_pb2.ObjectType, _Mapping]] = ..., permission: _Optional[_Union[_common_pb2.Permission, _Mapping]] = ..., relation_type: _Optional[_Union[_common_pb2.RelationType, _Mapping]] = ..., object: _Optional[_Union[_common_pb2.Object, _Mapping]] = ..., relation: _Optional[_Union[_common_pb2.Relation, _Mapping]] = ...) -> None: ...

class ImportResponse(_message.Message):
    __slots__ = ("object_type", "permission", "relation_type", "object", "relation")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    RELATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    object_type: ImportCounter
    permission: ImportCounter
    relation_type: ImportCounter
    object: ImportCounter
    relation: ImportCounter
    def __init__(self, object_type: _Optional[_Union[ImportCounter, _Mapping]] = ..., permission: _Optional[_Union[ImportCounter, _Mapping]] = ..., relation_type: _Optional[_Union[ImportCounter, _Mapping]] = ..., object: _Optional[_Union[ImportCounter, _Mapping]] = ..., relation: _Optional[_Union[ImportCounter, _Mapping]] = ...) -> None: ...

class ImportCounter(_message.Message):
    __slots__ = ("recv", "set", "delete", "error")
    RECV_FIELD_NUMBER: _ClassVar[int]
    SET_FIELD_NUMBER: _ClassVar[int]
    DELETE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    recv: int
    set: int
    delete: int
    error: int
    def __init__(self, recv: _Optional[int] = ..., set: _Optional[int] = ..., delete: _Optional[int] = ..., error: _Optional[int] = ...) -> None: ...
