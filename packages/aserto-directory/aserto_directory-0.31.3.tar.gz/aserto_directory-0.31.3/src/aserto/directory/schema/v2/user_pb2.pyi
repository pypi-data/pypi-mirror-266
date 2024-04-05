from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USER_STATUS_UNKNOWN: _ClassVar[UserStatus]
    USER_STATUS_STAGED: _ClassVar[UserStatus]
    USER_STATUS_PROVISIONED: _ClassVar[UserStatus]
    USER_STATUS_ACTIVE: _ClassVar[UserStatus]
    USER_STATUS_RECOVERY: _ClassVar[UserStatus]
    USER_STATUS_PASSWORD_EXPIRED: _ClassVar[UserStatus]
    USER_STATUS_LOCKED_OUT: _ClassVar[UserStatus]
    USER_STATUS_SUSPENDED: _ClassVar[UserStatus]
    USER_STATUS_DEPROVISIONED: _ClassVar[UserStatus]
USER_STATUS_UNKNOWN: UserStatus
USER_STATUS_STAGED: UserStatus
USER_STATUS_PROVISIONED: UserStatus
USER_STATUS_ACTIVE: UserStatus
USER_STATUS_RECOVERY: UserStatus
USER_STATUS_PASSWORD_EXPIRED: UserStatus
USER_STATUS_LOCKED_OUT: UserStatus
USER_STATUS_SUSPENDED: UserStatus
USER_STATUS_DEPROVISIONED: UserStatus

class UserProperties(_message.Message):
    __slots__ = ("email", "picture", "status", "enabled", "connection_id")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    email: str
    picture: str
    status: UserStatus
    enabled: bool
    connection_id: str
    def __init__(self, email: _Optional[str] = ..., picture: _Optional[str] = ..., status: _Optional[_Union[UserStatus, str]] = ..., enabled: bool = ..., connection_id: _Optional[str] = ...) -> None: ...
