from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Result(_message.Message):
    __slots__ = ("result", "description")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    result: int
    description: str
    def __init__(self, result: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...
