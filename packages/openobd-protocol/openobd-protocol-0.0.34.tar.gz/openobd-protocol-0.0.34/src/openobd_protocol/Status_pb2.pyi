from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNDEFINED: _ClassVar[StatusCode]
    SUCCESS: _ClassVar[StatusCode]
    FAILURE: _ClassVar[StatusCode]
    ERROR: _ClassVar[StatusCode]
    WARNING: _ClassVar[StatusCode]
    DEPRECATED_UNUSED: _ClassVar[StatusCode]
UNDEFINED: StatusCode
SUCCESS: StatusCode
FAILURE: StatusCode
ERROR: StatusCode
WARNING: StatusCode
DEPRECATED_UNUSED: StatusCode

class Status(_message.Message):
    __slots__ = ("success", "status_code", "status_description")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    success: bool
    status_code: StatusCode
    status_description: str
    def __init__(self, success: bool = ..., status_code: _Optional[_Union[StatusCode, str]] = ..., status_description: _Optional[str] = ...) -> None: ...
