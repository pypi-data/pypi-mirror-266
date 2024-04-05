from aserto.directory.common.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetObjectTypeRequest(_message.Message):
    __slots__ = ("param",)
    PARAM_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.ObjectTypeIdentifier
    def __init__(self, param: _Optional[_Union[_common_pb2.ObjectTypeIdentifier, _Mapping]] = ...) -> None: ...

class GetObjectTypeResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.ObjectType
    def __init__(self, result: _Optional[_Union[_common_pb2.ObjectType, _Mapping]] = ...) -> None: ...

class GetObjectTypesRequest(_message.Message):
    __slots__ = ("page",)
    PAGE_FIELD_NUMBER: _ClassVar[int]
    page: _common_pb2.PaginationRequest
    def __init__(self, page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class GetObjectTypesResponse(_message.Message):
    __slots__ = ("results", "page")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectType]
    page: _common_pb2.PaginationResponse
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.ObjectType, _Mapping]]] = ..., page: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class GetRelationTypeRequest(_message.Message):
    __slots__ = ("param",)
    PARAM_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.RelationTypeIdentifier
    def __init__(self, param: _Optional[_Union[_common_pb2.RelationTypeIdentifier, _Mapping]] = ...) -> None: ...

class GetRelationTypeResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.RelationType
    def __init__(self, result: _Optional[_Union[_common_pb2.RelationType, _Mapping]] = ...) -> None: ...

class GetRelationTypesRequest(_message.Message):
    __slots__ = ("param", "page")
    PARAM_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.ObjectTypeIdentifier
    page: _common_pb2.PaginationRequest
    def __init__(self, param: _Optional[_Union[_common_pb2.ObjectTypeIdentifier, _Mapping]] = ..., page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class GetRelationTypesResponse(_message.Message):
    __slots__ = ("results", "page")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.RelationType]
    page: _common_pb2.PaginationResponse
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.RelationType, _Mapping]]] = ..., page: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class GetObjectRequest(_message.Message):
    __slots__ = ("param", "with_relations", "page")
    PARAM_FIELD_NUMBER: _ClassVar[int]
    WITH_RELATIONS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.ObjectIdentifier
    with_relations: bool
    page: _common_pb2.PaginationRequest
    def __init__(self, param: _Optional[_Union[_common_pb2.ObjectIdentifier, _Mapping]] = ..., with_relations: bool = ..., page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

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
    __slots__ = ("param", "page")
    PARAM_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.ObjectTypeIdentifier
    page: _common_pb2.PaginationRequest
    def __init__(self, param: _Optional[_Union[_common_pb2.ObjectTypeIdentifier, _Mapping]] = ..., page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class GetObjectsResponse(_message.Message):
    __slots__ = ("results", "page")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.Object]
    page: _common_pb2.PaginationResponse
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.Object, _Mapping]]] = ..., page: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class GetRelationRequest(_message.Message):
    __slots__ = ("param", "with_objects")
    PARAM_FIELD_NUMBER: _ClassVar[int]
    WITH_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.RelationIdentifier
    with_objects: bool
    def __init__(self, param: _Optional[_Union[_common_pb2.RelationIdentifier, _Mapping]] = ..., with_objects: bool = ...) -> None: ...

class GetRelationResponse(_message.Message):
    __slots__ = ("results", "objects")
    class ObjectsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _common_pb2.Object
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Object, _Mapping]] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.Relation]
    objects: _containers.MessageMap[str, _common_pb2.Object]
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.Relation, _Mapping]]] = ..., objects: _Optional[_Mapping[str, _common_pb2.Object]] = ...) -> None: ...

class GetRelationsRequest(_message.Message):
    __slots__ = ("param", "page")
    PARAM_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.RelationIdentifier
    page: _common_pb2.PaginationRequest
    def __init__(self, param: _Optional[_Union[_common_pb2.RelationIdentifier, _Mapping]] = ..., page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class GetRelationsResponse(_message.Message):
    __slots__ = ("results", "page")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.Relation]
    page: _common_pb2.PaginationResponse
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.Relation, _Mapping]]] = ..., page: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class GetPermissionRequest(_message.Message):
    __slots__ = ("param",)
    PARAM_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.PermissionIdentifier
    def __init__(self, param: _Optional[_Union[_common_pb2.PermissionIdentifier, _Mapping]] = ...) -> None: ...

class GetPermissionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.Permission
    def __init__(self, result: _Optional[_Union[_common_pb2.Permission, _Mapping]] = ...) -> None: ...

class GetPermissionsRequest(_message.Message):
    __slots__ = ("page",)
    PAGE_FIELD_NUMBER: _ClassVar[int]
    page: _common_pb2.PaginationRequest
    def __init__(self, page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class GetPermissionsResponse(_message.Message):
    __slots__ = ("results", "page")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.Permission]
    page: _common_pb2.PaginationResponse
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.Permission, _Mapping]]] = ..., page: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class CheckPermissionRequest(_message.Message):
    __slots__ = ("subject", "permission", "object", "trace")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    subject: _common_pb2.ObjectIdentifier
    permission: _common_pb2.PermissionIdentifier
    object: _common_pb2.ObjectIdentifier
    trace: bool
    def __init__(self, subject: _Optional[_Union[_common_pb2.ObjectIdentifier, _Mapping]] = ..., permission: _Optional[_Union[_common_pb2.PermissionIdentifier, _Mapping]] = ..., object: _Optional[_Union[_common_pb2.ObjectIdentifier, _Mapping]] = ..., trace: bool = ...) -> None: ...

class CheckPermissionResponse(_message.Message):
    __slots__ = ("check", "trace")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    check: bool
    trace: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, check: bool = ..., trace: _Optional[_Iterable[str]] = ...) -> None: ...

class CheckRelationRequest(_message.Message):
    __slots__ = ("subject", "relation", "object", "trace")
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    subject: _common_pb2.ObjectIdentifier
    relation: _common_pb2.RelationTypeIdentifier
    object: _common_pb2.ObjectIdentifier
    trace: bool
    def __init__(self, subject: _Optional[_Union[_common_pb2.ObjectIdentifier, _Mapping]] = ..., relation: _Optional[_Union[_common_pb2.RelationTypeIdentifier, _Mapping]] = ..., object: _Optional[_Union[_common_pb2.ObjectIdentifier, _Mapping]] = ..., trace: bool = ...) -> None: ...

class CheckRelationResponse(_message.Message):
    __slots__ = ("check", "trace")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    check: bool
    trace: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, check: bool = ..., trace: _Optional[_Iterable[str]] = ...) -> None: ...

class CheckResponse(_message.Message):
    __slots__ = ("check", "trace")
    CHECK_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    check: bool
    trace: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, check: bool = ..., trace: _Optional[_Iterable[str]] = ...) -> None: ...

class GetGraphRequest(_message.Message):
    __slots__ = ("anchor", "subject", "relation", "object")
    ANCHOR_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RELATION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    anchor: _common_pb2.ObjectIdentifier
    subject: _common_pb2.ObjectIdentifier
    relation: _common_pb2.RelationTypeIdentifier
    object: _common_pb2.ObjectIdentifier
    def __init__(self, anchor: _Optional[_Union[_common_pb2.ObjectIdentifier, _Mapping]] = ..., subject: _Optional[_Union[_common_pb2.ObjectIdentifier, _Mapping]] = ..., relation: _Optional[_Union[_common_pb2.RelationTypeIdentifier, _Mapping]] = ..., object: _Optional[_Union[_common_pb2.ObjectIdentifier, _Mapping]] = ...) -> None: ...

class GetGraphResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectDependency]
    def __init__(self, results: _Optional[_Iterable[_Union[_common_pb2.ObjectDependency, _Mapping]]] = ...) -> None: ...
