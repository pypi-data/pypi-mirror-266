from google.protobuf import empty_pb2 as _empty_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from aserto.directory.common.v3 import common_pb2 as _common_pb2
from aserto.directory.reader.v3 import reader_pb2 as _reader_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAssertionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class GetAssertionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: Assert
    def __init__(self, result: _Optional[_Union[Assert, _Mapping]] = ...) -> None: ...

class ListAssertionsRequest(_message.Message):
    __slots__ = ("page",)
    PAGE_FIELD_NUMBER: _ClassVar[int]
    page: _common_pb2.PaginationRequest
    def __init__(self, page: _Optional[_Union[_common_pb2.PaginationRequest, _Mapping]] = ...) -> None: ...

class ListAssertionsResponse(_message.Message):
    __slots__ = ("results", "page")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[Assert]
    page: _common_pb2.PaginationResponse
    def __init__(self, results: _Optional[_Iterable[_Union[Assert, _Mapping]]] = ..., page: _Optional[_Union[_common_pb2.PaginationResponse, _Mapping]] = ...) -> None: ...

class SetAssertionRequest(_message.Message):
    __slots__ = ()
    ASSERT_FIELD_NUMBER: _ClassVar[int]
    def __init__(self, **kwargs) -> None: ...

class SetAssertionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: Assert
    def __init__(self, result: _Optional[_Union[Assert, _Mapping]] = ...) -> None: ...

class DeleteAssertionRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteAssertionResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: _empty_pb2.Empty
    def __init__(self, result: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class Assert(_message.Message):
    __slots__ = ("id", "expected", "check", "check_relation", "check_permission")
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_FIELD_NUMBER: _ClassVar[int]
    CHECK_FIELD_NUMBER: _ClassVar[int]
    CHECK_RELATION_FIELD_NUMBER: _ClassVar[int]
    CHECK_PERMISSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    expected: bool
    check: _reader_pb2.CheckRequest
    check_relation: _reader_pb2.CheckRelationRequest
    check_permission: _reader_pb2.CheckPermissionRequest
    def __init__(self, id: _Optional[int] = ..., expected: bool = ..., check: _Optional[_Union[_reader_pb2.CheckRequest, _Mapping]] = ..., check_relation: _Optional[_Union[_reader_pb2.CheckRelationRequest, _Mapping]] = ..., check_permission: _Optional[_Union[_reader_pb2.CheckPermissionRequest, _Mapping]] = ...) -> None: ...
