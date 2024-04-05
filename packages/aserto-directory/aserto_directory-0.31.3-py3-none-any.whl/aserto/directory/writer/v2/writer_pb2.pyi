from google.protobuf import empty_pb2 as _empty_pb2
from aserto.directory.common.v2 import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetObjectTypeRequest(_message.Message):
    __slots__ = ("object_type",)
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    object_type: _common_pb2.ObjectType
    def __init__(self, object_type: _Optional[_Union[_common_pb2.ObjectType, _Mapping]] = ...) -> None: ...

class SetObjectTypeResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.ObjectType
    def __init__(self, result: _Optional[_Union[_common_pb2.ObjectType, _Mapping]] = ...) -> None: ...

class DeleteObjectTypeRequest(_message.Message):
    __slots__ = ("param",)
    PARAM_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.ObjectTypeIdentifier
    def __init__(self, param: _Optional[_Union[_common_pb2.ObjectTypeIdentifier, _Mapping]] = ...) -> None: ...

class DeleteObjectTypeResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _empty_pb2.Empty
    def __init__(self, result: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class SetRelationTypeRequest(_message.Message):
    __slots__ = ("relation_type",)
    RELATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    relation_type: _common_pb2.RelationType
    def __init__(self, relation_type: _Optional[_Union[_common_pb2.RelationType, _Mapping]] = ...) -> None: ...

class SetRelationTypeResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.RelationType
    def __init__(self, result: _Optional[_Union[_common_pb2.RelationType, _Mapping]] = ...) -> None: ...

class DeleteRelationTypeRequest(_message.Message):
    __slots__ = ("param",)
    PARAM_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.RelationTypeIdentifier
    def __init__(self, param: _Optional[_Union[_common_pb2.RelationTypeIdentifier, _Mapping]] = ...) -> None: ...

class DeleteRelationTypeResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _empty_pb2.Empty
    def __init__(self, result: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class SetPermissionRequest(_message.Message):
    __slots__ = ("permission",)
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    permission: _common_pb2.Permission
    def __init__(self, permission: _Optional[_Union[_common_pb2.Permission, _Mapping]] = ...) -> None: ...

class SetPermissionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _common_pb2.Permission
    def __init__(self, result: _Optional[_Union[_common_pb2.Permission, _Mapping]] = ...) -> None: ...

class DeletePermissionRequest(_message.Message):
    __slots__ = ("param",)
    PARAM_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.PermissionIdentifier
    def __init__(self, param: _Optional[_Union[_common_pb2.PermissionIdentifier, _Mapping]] = ...) -> None: ...

class DeletePermissionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _empty_pb2.Empty
    def __init__(self, result: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

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
    __slots__ = ("param", "with_relations")
    PARAM_FIELD_NUMBER: _ClassVar[int]
    WITH_RELATIONS_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.ObjectIdentifier
    with_relations: bool
    def __init__(self, param: _Optional[_Union[_common_pb2.ObjectIdentifier, _Mapping]] = ..., with_relations: bool = ...) -> None: ...

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
    __slots__ = ("param",)
    PARAM_FIELD_NUMBER: _ClassVar[int]
    param: _common_pb2.RelationIdentifier
    def __init__(self, param: _Optional[_Union[_common_pb2.RelationIdentifier, _Mapping]] = ...) -> None: ...

class DeleteRelationResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _empty_pb2.Empty
    def __init__(self, result: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...
