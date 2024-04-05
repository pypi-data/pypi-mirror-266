from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IdentityKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IDENTITY_KIND_UNKNOWN: _ClassVar[IdentityKind]
    IDENTITY_KIND_PID: _ClassVar[IdentityKind]
    IDENTITY_KIND_EMAIL: _ClassVar[IdentityKind]
    IDENTITY_KIND_USERNAME: _ClassVar[IdentityKind]
    IDENTITY_KIND_DN: _ClassVar[IdentityKind]
    IDENTITY_KIND_PHONE: _ClassVar[IdentityKind]
    IDENTITY_KIND_EMPID: _ClassVar[IdentityKind]
IDENTITY_KIND_UNKNOWN: IdentityKind
IDENTITY_KIND_PID: IdentityKind
IDENTITY_KIND_EMAIL: IdentityKind
IDENTITY_KIND_USERNAME: IdentityKind
IDENTITY_KIND_DN: IdentityKind
IDENTITY_KIND_PHONE: IdentityKind
IDENTITY_KIND_EMPID: IdentityKind

class IdentityProperties(_message.Message):
    __slots__ = ("kind", "provider", "verified", "connection_id")
    KIND_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    kind: IdentityKind
    provider: str
    verified: bool
    connection_id: str
    def __init__(self, kind: _Optional[_Union[IdentityKind, str]] = ..., provider: _Optional[str] = ..., verified: bool = ..., connection_id: _Optional[str] = ...) -> None: ...
