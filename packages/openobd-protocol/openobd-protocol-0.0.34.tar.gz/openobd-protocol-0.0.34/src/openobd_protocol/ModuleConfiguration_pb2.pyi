from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HardwareModule(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODULE_UNDEFINED: _ClassVar[HardwareModule]
    MODULE_CAN1: _ClassVar[HardwareModule]
    MODULE_CAN2: _ClassVar[HardwareModule]
    MODULE_CAN3: _ClassVar[HardwareModule]
    MODULE_K_LINE1: _ClassVar[HardwareModule]
    MODULE_K_LINE2: _ClassVar[HardwareModule]
    MODULE_K_LINE3: _ClassVar[HardwareModule]
    MODULE_L_LINE: _ClassVar[HardwareModule]
    MODULE_PLUS_15: _ClassVar[HardwareModule]
    MODULE_GPIO1: _ClassVar[HardwareModule]
    MODULE_GPIO2: _ClassVar[HardwareModule]
    MODULE_GPIO3: _ClassVar[HardwareModule]
    MODULE_GPIO4: _ClassVar[HardwareModule]
    MODULE_READUR: _ClassVar[HardwareModule]
    MODULE_CAN4: _ClassVar[HardwareModule]
    MODULE_DOIP: _ClassVar[HardwareModule]
    MODULE_KEYLINE: _ClassVar[HardwareModule]
    MODULE_GPIO5: _ClassVar[HardwareModule]
    MODULE_TRANSDUCER: _ClassVar[HardwareModule]
    MODULE_BUTTON: _ClassVar[HardwareModule]
    MODULE_RGB_LED: _ClassVar[HardwareModule]

class Bitrate(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BIT_RATE_UNDEFINED: _ClassVar[Bitrate]
    BIT_RATE_1000: _ClassVar[Bitrate]
    BIT_RATE_500: _ClassVar[Bitrate]
    BIT_RATE_250: _ClassVar[Bitrate]
    BIT_RATE_125: _ClassVar[Bitrate]
    BIT_RATE_100: _ClassVar[Bitrate]
    BIT_RATE_94: _ClassVar[Bitrate]
    BIT_RATE_83_3: _ClassVar[Bitrate]
    BIT_RATE_50: _ClassVar[Bitrate]
    BIT_RATE_33_3: _ClassVar[Bitrate]
    BIT_RATE_20: _ClassVar[Bitrate]
    BIT_RATE_10: _ClassVar[Bitrate]
    BIT_RATE_5: _ClassVar[Bitrate]
MODULE_UNDEFINED: HardwareModule
MODULE_CAN1: HardwareModule
MODULE_CAN2: HardwareModule
MODULE_CAN3: HardwareModule
MODULE_K_LINE1: HardwareModule
MODULE_K_LINE2: HardwareModule
MODULE_K_LINE3: HardwareModule
MODULE_L_LINE: HardwareModule
MODULE_PLUS_15: HardwareModule
MODULE_GPIO1: HardwareModule
MODULE_GPIO2: HardwareModule
MODULE_GPIO3: HardwareModule
MODULE_GPIO4: HardwareModule
MODULE_READUR: HardwareModule
MODULE_CAN4: HardwareModule
MODULE_DOIP: HardwareModule
MODULE_KEYLINE: HardwareModule
MODULE_GPIO5: HardwareModule
MODULE_TRANSDUCER: HardwareModule
MODULE_BUTTON: HardwareModule
MODULE_RGB_LED: HardwareModule
BIT_RATE_UNDEFINED: Bitrate
BIT_RATE_1000: Bitrate
BIT_RATE_500: Bitrate
BIT_RATE_250: Bitrate
BIT_RATE_125: Bitrate
BIT_RATE_100: Bitrate
BIT_RATE_94: Bitrate
BIT_RATE_83_3: Bitrate
BIT_RATE_50: Bitrate
BIT_RATE_33_3: Bitrate
BIT_RATE_20: Bitrate
BIT_RATE_10: Bitrate
BIT_RATE_5: Bitrate

class ModuleConfiguration(_message.Message):
    __slots__ = ("hardware_module_id", "module_info", "bitrate", "transport_type", "pin_positive", "pin_negative")
    HARDWARE_MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_INFO_FIELD_NUMBER: _ClassVar[int]
    BITRATE_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PIN_POSITIVE_FIELD_NUMBER: _ClassVar[int]
    PIN_NEGATIVE_FIELD_NUMBER: _ClassVar[int]
    hardware_module_id: HardwareModule
    module_info: int
    bitrate: Bitrate
    transport_type: int
    pin_positive: int
    pin_negative: int
    def __init__(self, hardware_module_id: _Optional[_Union[HardwareModule, str]] = ..., module_info: _Optional[int] = ..., bitrate: _Optional[_Union[Bitrate, str]] = ..., transport_type: _Optional[int] = ..., pin_positive: _Optional[int] = ..., pin_negative: _Optional[int] = ...) -> None: ...
