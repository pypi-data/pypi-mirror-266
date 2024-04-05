from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2
from google.api import annotations_pb2 as _annotations_pb2_1
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from buf.validate import validate_pb2 as _validate_pb2
from aserto.directory.common.v3 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetObjectRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "with_relations", "page")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    WITH_RELATIONS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    with_relations: bool
    page: _common_pb2.PaginationRequest
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., with_relations: bool = ..., page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class GetObjectResponse(_message.Message):
    __slots__ = ("result", "relations", "page")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    RELATIONS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.Object
    relations: _containers.RepeatedCompositeFieldContainer[_common_pb2.Relation]
    page: _common_pb2.PaginationResponse
    def __init__(self, result: _Optional[_Union[_common_pb2.Object, _Mapping]] = ..., relations: _Optional[_Iterable[_Union[_common_pb2.Relation, _Mapping]]] = ..., page: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class GetObjectManyRequest(_message.Message):
    __slots__ = ("param",)
    PARAM_FIELD_NUMBER: _ClassVar[int]
    param: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectIdentifier]
    def __init__(self, param: _Optional[_Iterable[_Union[_common_pb2.ObjectIdentifier, _Mapping]]] = ...) -> None: ...

class GetObjectManyResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.Object]
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.Object, _Mapping]]] = ...) -> None: ...

class GetObjectsRequest(_message.Message):
    __slots__ = ("object_type", "page")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    page: _common_pb2.PaginationRequest
    def __init__(self, object_type: _Optional[str] = ..., page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class GetObjectsResponse(_message.Message):
    __slots__ = ("results", "page")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.Object]
    page: _common_pb2.PaginationResponse
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.Object, _Mapping]]] = ..., page: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class GetRelationRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "relation", "subject_type", "subject_id", "subject_relation", "with_objects")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_RELATION_FIELD_NUMBER: _ClassVar[int]
    WITH_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    relation: str
    subject_type: str
    subject_id: str
    subject_relation: str
    with_objects: bool
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., relation: _Optional[str] = ..., subject_type: _Optional[str] = ..., subject_id: _Optional[str] = ..., subject_relation: _Optional[str] = ..., with_objects: bool = ...) -> None: ...

class GetRelationResponse(_message.Message):
    __slots__ = ("result", "objects")
    class ObjectsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.Object
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Object, _Mapping]] = ...) -> None: ...
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.Relation
    objects: _containers.MessageMap[str, _common_pb2.Object]
    def __init__(self, result: _Optional[_Union[_common_pb2.Relation, _Mapping]] = ..., objects: _Optional[_Mapping[str, _common_pb2.Object]] = ...) -> None: ...

class GetRelationsRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "relation", "subject_type", "subject_id", "subject_relation", "with_objects", "with_empty_subject_relation", "page")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_RELATION_FIELD_NUMBER: _ClassVar[int]
    WITH_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    WITH_EMPTY_SUBJECT_RELATION_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    relation: str
    subject_type: str
    subject_id: str
    subject_relation: str
    with_objects: bool
    with_empty_subject_relation: bool
    page: _common_pb2.PaginationRequest
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., relation: _Optional[str] = ..., subject_type: _Optional[str] = ..., subject_id: _Optional[str] = ..., subject_relation: _Optional[str] = ..., with_objects: bool = ..., with_empty_subject_relation: bool = ..., page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class GetRelationsResponse(_message.Message):
    __slots__ = ("results", "objects", "page")
    class ObjectsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.Object
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Object, _Mapping]] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.Relation]
    objects: _containers.MessageMap[str, _common_pb2.Object]
    page: _common_pb2.PaginationResponse
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.Relation, _Mapping]]] = ..., objects: _Optional[_Mapping[str, _common_pb2.Object]] = ..., page: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class CheckRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "relation", "subject_type", "subject_id", "trace")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    relation: str
    subject_type: str
    subject_id: str
    trace: bool
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., relation: _Optional[str] = ..., subject_type: _Optional[str] = ..., subject_id: _Optional[str] = ..., trace: bool = ...) -> None: ...

class CheckResponse(_message.Message):
    __slots__ = ("check", "trace")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    check: bool
    trace: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, check: bool = ..., trace: _Optional[_Iterable[str]] = ...) -> None: ...

class CheckPermissionRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "permission", "subject_type", "subject_id", "trace")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    permission: str
    subject_type: str
    subject_id: str
    trace: bool
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., permission: _Optional[str] = ..., subject_type: _Optional[str] = ..., subject_id: _Optional[str] = ..., trace: bool = ...) -> None: ...

class CheckPermissionResponse(_message.Message):
    __slots__ = ("check", "trace")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    check: bool
    trace: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, check: bool = ..., trace: _Optional[_Iterable[str]] = ...) -> None: ...

class CheckRelationRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "relation", "subject_type", "subject_id", "trace")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    relation: str
    subject_type: str
    subject_id: str
    trace: bool
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., relation: _Optional[str] = ..., subject_type: _Optional[str] = ..., subject_id: _Optional[str] = ..., trace: bool = ...) -> None: ...

class CheckRelationResponse(_message.Message):
    __slots__ = ("check", "trace")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    check: bool
    trace: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, check: bool = ..., trace: _Optional[_Iterable[str]] = ...) -> None: ...

class GetGraphRequest(_message.Message):
    __slots__ = ("object_type", "object_id", "relation", "subject_type", "subject_id", "subject_relation", "explain", "trace")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_RELATION_FIELD_NUMBER: _ClassVar[int]
    EXPLAIN_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: str
    relation: str
    subject_type: str
    subject_id: str
    subject_relation: str
    explain: bool
    trace: bool
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[str] = ..., relation: _Optional[str] = ..., subject_type: _Optional[str] = ..., subject_id: _Optional[str] = ..., subject_relation: _Optional[str] = ..., explain: bool = ..., trace: bool = ...) -> None: ...

class GetGraphResponse(_message.Message):
    __slots__ = ("results", "explanation", "trace")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectIdentifier]
    explanation: _struct_pb2.Struct
    trace: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.ObjectIdentifier, _Mapping]]] = ..., explanation: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., trace: _Optional[_Iterable[str]] = ...) -> None: ...
