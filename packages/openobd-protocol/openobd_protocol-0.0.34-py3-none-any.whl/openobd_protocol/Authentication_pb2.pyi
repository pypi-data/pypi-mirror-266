from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AuthenticationResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AUTHENTICATION_UNDEFINED: _ClassVar[AuthenticationResult]
    AUTHENTICATION_FAILED: _ClassVar[AuthenticationResult]
    AUTHENTICATION_SUCCESSFUL: _ClassVar[AuthenticationResult]
AUTHENTICATION_UNDEFINED: AuthenticationResult
AUTHENTICATION_FAILED: AuthenticationResult
AUTHENTICATION_SUCCESSFUL: AuthenticationResult

class AuthenticationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AuthenticationResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: AuthenticationResult
    def __init__(self, result: _Optional[_Union[AuthenticationResult, str]] = ...) -> None: ...
