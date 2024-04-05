from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TenantKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TENANT_KIND_UNKNOWN: _ClassVar[TenantKind]
    TENANT_KIND_ORGANIZATION: _ClassVar[TenantKind]
    TENANT_KIND_ACCOUNT: _ClassVar[TenantKind]
TENANT_KIND_UNKNOWN: TenantKind
TENANT_KIND_ORGANIZATION: TenantKind
TENANT_KIND_ACCOUNT: TenantKind

class TenantProperties(_message.Message):
    __slots__ = ("kind", "directory_v2", "directory_v2_only", "account")
    KIND_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_V2_FIELD_NUMBER: _ClassVar[int]
    DIRECTORY_V2_ONLY_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    kind: TenantKind
    directory_v2: bool
    directory_v2_only: bool
    account: AccountProperties
    def __init__(self, kind: _Optional[_Union[TenantKind, str]] = ..., directory_v2: bool = ..., directory_v2_only: bool = ..., account: _Optional[_Union[AccountProperties, _Mapping]] = ...) -> None: ...

class AccountProperties(_message.Message):
    __slots__ = ("max_orgs", "getting_started", "default_tenant_id")
    MAX_ORGS_FIELD_NUMBER: _ClassVar[int]
    GETTING_STARTED_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    max_orgs: int
    getting_started: GuideState
    default_tenant_id: str
    def __init__(self, max_orgs: _Optional[int] = ..., getting_started: _Optional[_Union[GuideState, _Mapping]] = ..., default_tenant_id: _Optional[str] = ...) -> None: ...

class GuideState(_message.Message):
    __slots__ = ("show", "steps")
    SHOW_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    show: bool
    steps: _struct_pb2.Struct
    def __init__(self, show: bool = ..., steps: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
