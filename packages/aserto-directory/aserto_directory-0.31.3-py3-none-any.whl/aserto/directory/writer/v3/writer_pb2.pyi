from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.api import annotations_pb2 as _annotations_pb2_1
from google.api import field_behavior_pb2 as _field_behavior_pb2
from buf.validate import validate_pb2 as _validate_pb2
from aserto.directory.common.v3 import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetObjectRequest(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.Object
    def __init__(self, object: _Optional[_Union[_common_pb2.Object, _Mapping]] = ...) -> None: ...

class SetObjectResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.Object
    def __init__(self, result: _Optional[_Union[_common_pb2.Object, _Mapping]] = ...) -> None: ...

class DeleteObjectRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "with_relations")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    WITH_RELATIONS_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    with_relations: bool
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., with_relations: bool = ...) -> None: ...

class DeleteObjectResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _empty_pb2.Empty
    def __init__(self, result: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class SetRelationRequest(_message.Message):
    __slots__ = ("relation",)
    RELATION_FIELD_NUMBER: _ClassVar[int]
    relation: _common_pb2.Relation
    def __init__(self, relation: _Optional[_Union[_common_pb2.Relation, _Mapping]] = ...) -> None: ...

class SetRelationResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.Relation
    def __init__(self, result: _Optional[_Union[_common_pb2.Relation, _Mapping]] = ...) -> None: ...

class DeleteRelationRequest(_message.Message):
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

class DeleteRelationResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _empty_pb2.Empty
    def __init__(self, result: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
