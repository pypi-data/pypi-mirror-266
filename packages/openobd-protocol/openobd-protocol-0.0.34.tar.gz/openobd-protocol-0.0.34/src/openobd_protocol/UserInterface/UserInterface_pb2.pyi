from openobd_protocol import Status_pb2 as _Status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InterfaceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INTERFACE_UNDEFINED: _ClassVar[InterfaceType]
    INTERFACE_USER: _ClassVar[InterfaceType]
    INTERFACE_OPERATOR: _ClassVar[InterfaceType]
INTERFACE_UNDEFINED: InterfaceType
INTERFACE_USER: InterfaceType
INTERFACE_OPERATOR: InterfaceType

class UserInterface(_message.Message):
    __slots__ = ("target", "control_label", "control_options", "control_continue", "control_yesno", "control_freetext", "control_number", "user_interface_status")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    CONTROL_LABEL_FIELD_NUMBER: _ClassVar[int]
    CONTROL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CONTROL_CONTINUE_FIELD_NUMBER: _ClassVar[int]
    CONTROL_YESNO_FIELD_NUMBER: _ClassVar[int]
    CONTROL_FREETEXT_FIELD_NUMBER: _ClassVar[int]
    CONTROL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    USER_INTERFACE_STATUS_FIELD_NUMBER: _ClassVar[int]
    target: InterfaceType
    control_label: Label
    control_options: Options
    control_continue: Continue
    control_yesno: YesNo
    control_freetext: FreeText
    control_number: Numbers
    user_interface_status: _Status_pb2.Status
    def __init__(self, target: _Optional[_Union[InterfaceType, str]] = ..., control_label: _Optional[_Union[Label, _Mapping]] = ..., control_options: _Optional[_Union[Options, _Mapping]] = ..., control_continue: _Optional[_Union[Continue, _Mapping]] = ..., control_yesno: _Optional[_Union[YesNo, _Mapping]] = ..., control_freetext: _Optional[_Union[FreeText, _Mapping]] = ..., control_number: _Optional[_Union[Numbers, _Mapping]] = ..., user_interface_status: _Optional[_Union[_Status_pb2.Status, _Mapping]] = ...) -> None: ...

class Label(_message.Message):
    __slots__ = ("label", "minimal_display_time", "timeout")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    MINIMAL_DISPLAY_TIME_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    label: str
    minimal_display_time: int
    timeout: int
    def __init__(self, label: _Optional[str] = ..., minimal_display_time: _Optional[int] = ..., timeout: _Optional[int] = ...) -> None: ...

class Options(_message.Message):
    __slots__ = ("label", "options", "answer")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    label: str
    options: _containers.RepeatedScalarFieldContainer[str]
    answer: int
    def __init__(self, label: _Optional[str] = ..., options: _Optional[_Iterable[str]] = ..., answer: _Optional[int] = ...) -> None: ...

class Continue(_message.Message):
    __slots__ = ("label",)
    LABEL_FIELD_NUMBER: _ClassVar[int]
    label: str
    def __init__(self, label: _Optional[str] = ...) -> None: ...

class YesNo(_message.Message):
    __slots__ = ("label", "answer")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    label: str
    answer: bool
    def __init__(self, label: _Optional[str] = ..., answer: bool = ...) -> None: ...

class FreeText(_message.Message):
    __slots__ = ("label", "answer")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    label: str
    answer: str
    def __init__(self, label: _Optional[str] = ..., answer: _Optional[str] = ...) -> None: ...

class Numbers(_message.Message):
    __slots__ = ("label", "minimum", "answer", "maximum")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_FIELD_NUMBER: _ClassVar[int]
    label: str
    minimum: int
    answer: int
    maximum: int
    def __init__(self, label: _Optional[str] = ..., minimum: _Optional[int] = ..., answer: _Optional[int] = ..., maximum: _Optional[int] = ...) -> None: ...
