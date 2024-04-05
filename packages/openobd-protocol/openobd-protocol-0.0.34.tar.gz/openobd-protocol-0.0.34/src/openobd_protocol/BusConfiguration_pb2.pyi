from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CanProtocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAN_PROTOCOL_UNDEFINED: _ClassVar[CanProtocol]
    CAN_PROTOCOL_ISOTP: _ClassVar[CanProtocol]
    CAN_PROTOCOL_TP20: _ClassVar[CanProtocol]
    CAN_PROTOCOL_FRAMES: _ClassVar[CanProtocol]

class CanBitRate(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAN_BIT_RATE_UNDEFINED: _ClassVar[CanBitRate]
    CAN_BIT_RATE_1000: _ClassVar[CanBitRate]
    CAN_BIT_RATE_500: _ClassVar[CanBitRate]
    CAN_BIT_RATE_250: _ClassVar[CanBitRate]
    CAN_BIT_RATE_125: _ClassVar[CanBitRate]
    CAN_BIT_RATE_100: _ClassVar[CanBitRate]
    CAN_BIT_RATE_94: _ClassVar[CanBitRate]
    CAN_BIT_RATE_83_3: _ClassVar[CanBitRate]
    CAN_BIT_RATE_50: _ClassVar[CanBitRate]
    CAN_BIT_RATE_33_3: _ClassVar[CanBitRate]
    CAN_BIT_RATE_20: _ClassVar[CanBitRate]
    CAN_BIT_RATE_10: _ClassVar[CanBitRate]
    CAN_BIT_RATE_5: _ClassVar[CanBitRate]

class TransceiverSpeed(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRANSCEIVER_SPEED_UNDEFINED: _ClassVar[TransceiverSpeed]
    TRANSCEIVER_SPEED_HIGH: _ClassVar[TransceiverSpeed]
    TRANSCEIVER_SPEED_LOW: _ClassVar[TransceiverSpeed]

class KlineProtocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KLINE_PROTOCOL_UNDEFINED: _ClassVar[KlineProtocol]
    KLINE_PROTOCOL_GENERIC_SLOW: _ClassVar[KlineProtocol]
    KLINE_PROTOCOL_GENERIC_FAST: _ClassVar[KlineProtocol]
    KLINE_PROTOCOL_KWP841_SLOW: _ClassVar[KlineProtocol]
    KLINE_PROTOCOL_ISO14230_SLOW: _ClassVar[KlineProtocol]
    KLINE_PROTOCOL_ISO14230_FAST: _ClassVar[KlineProtocol]
    KLINE_PROTOCOL_KWP760_SLOW: _ClassVar[KlineProtocol]
    KLINE_PROTOCOL_HONDA_FAST: _ClassVar[KlineProtocol]

class KlineBitRate(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KLINE_BIT_RATE_UNDEFINED: _ClassVar[KlineBitRate]
    KLINE_BIT_RATE_9600: _ClassVar[KlineBitRate]
    KLINE_BIT_RATE_10400: _ClassVar[KlineBitRate]
    KLINE_BIT_RATE_15625: _ClassVar[KlineBitRate]

class Entity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENTITY_UNDEFINED: _ClassVar[Entity]
    ENTITY_LOCAL: _ClassVar[Entity]
    ENTITY_REMOTE: _ClassVar[Entity]
    ENTITY_BROADCAST: _ClassVar[Entity]
CAN_PROTOCOL_UNDEFINED: CanProtocol
CAN_PROTOCOL_ISOTP: CanProtocol
CAN_PROTOCOL_TP20: CanProtocol
CAN_PROTOCOL_FRAMES: CanProtocol
CAN_BIT_RATE_UNDEFINED: CanBitRate
CAN_BIT_RATE_1000: CanBitRate
CAN_BIT_RATE_500: CanBitRate
CAN_BIT_RATE_250: CanBitRate
CAN_BIT_RATE_125: CanBitRate
CAN_BIT_RATE_100: CanBitRate
CAN_BIT_RATE_94: CanBitRate
CAN_BIT_RATE_83_3: CanBitRate
CAN_BIT_RATE_50: CanBitRate
CAN_BIT_RATE_33_3: CanBitRate
CAN_BIT_RATE_20: CanBitRate
CAN_BIT_RATE_10: CanBitRate
CAN_BIT_RATE_5: CanBitRate
TRANSCEIVER_SPEED_UNDEFINED: TransceiverSpeed
TRANSCEIVER_SPEED_HIGH: TransceiverSpeed
TRANSCEIVER_SPEED_LOW: TransceiverSpeed
KLINE_PROTOCOL_UNDEFINED: KlineProtocol
KLINE_PROTOCOL_GENERIC_SLOW: KlineProtocol
KLINE_PROTOCOL_GENERIC_FAST: KlineProtocol
KLINE_PROTOCOL_KWP841_SLOW: KlineProtocol
KLINE_PROTOCOL_ISO14230_SLOW: KlineProtocol
KLINE_PROTOCOL_ISO14230_FAST: KlineProtocol
KLINE_PROTOCOL_KWP760_SLOW: KlineProtocol
KLINE_PROTOCOL_HONDA_FAST: KlineProtocol
KLINE_BIT_RATE_UNDEFINED: KlineBitRate
KLINE_BIT_RATE_9600: KlineBitRate
KLINE_BIT_RATE_10400: KlineBitRate
KLINE_BIT_RATE_15625: KlineBitRate
ENTITY_UNDEFINED: Entity
ENTITY_LOCAL: Entity
ENTITY_REMOTE: Entity
ENTITY_BROADCAST: Entity

class BusConfiguration(_message.Message):
    __slots__ = ("bus_name", "can_bus", "kline_bus", "plus15", "doip_bus")
    BUS_NAME_FIELD_NUMBER: _ClassVar[int]
    CAN_BUS_FIELD_NUMBER: _ClassVar[int]
    KLINE_BUS_FIELD_NUMBER: _ClassVar[int]
    PLUS15_FIELD_NUMBER: _ClassVar[int]
    DOIP_BUS_FIELD_NUMBER: _ClassVar[int]
    bus_name: str
    can_bus: CanBus
    kline_bus: KlineBus
    plus15: Plus15Bus
    doip_bus: DoipBus
    def __init__(self, bus_name: _Optional[str] = ..., can_bus: _Optional[_Union[CanBus, _Mapping]] = ..., kline_bus: _Optional[_Union[KlineBus, _Mapping]] = ..., plus15: _Optional[_Union[Plus15Bus, _Mapping]] = ..., doip_bus: _Optional[_Union[DoipBus, _Mapping]] = ...) -> None: ...

class CanBus(_message.Message):
    __slots__ = ("pin_plus", "pin_min", "can_protocol", "can_bit_rate", "transceiver")
    PIN_PLUS_FIELD_NUMBER: _ClassVar[int]
    PIN_MIN_FIELD_NUMBER: _ClassVar[int]
    CAN_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    CAN_BIT_RATE_FIELD_NUMBER: _ClassVar[int]
    TRANSCEIVER_FIELD_NUMBER: _ClassVar[int]
    pin_plus: int
    pin_min: int
    can_protocol: CanProtocol
    can_bit_rate: CanBitRate
    transceiver: TransceiverSpeed
    def __init__(self, pin_plus: _Optional[int] = ..., pin_min: _Optional[int] = ..., can_protocol: _Optional[_Union[CanProtocol, str]] = ..., can_bit_rate: _Optional[_Union[CanBitRate, str]] = ..., transceiver: _Optional[_Union[TransceiverSpeed, str]] = ...) -> None: ...

class KlineBus(_message.Message):
    __slots__ = ("pin", "kline_protocol", "kline_bit_rate")
    PIN_FIELD_NUMBER: _ClassVar[int]
    KLINE_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    KLINE_BIT_RATE_FIELD_NUMBER: _ClassVar[int]
    pin: int
    kline_protocol: KlineProtocol
    kline_bit_rate: KlineBitRate
    def __init__(self, pin: _Optional[int] = ..., kline_protocol: _Optional[_Union[KlineProtocol, str]] = ..., kline_bit_rate: _Optional[_Union[KlineBitRate, str]] = ...) -> None: ...

class Plus15Bus(_message.Message):
    __slots__ = ("pin",)
    PIN_FIELD_NUMBER: _ClassVar[int]
    pin: int
    def __init__(self, pin: _Optional[int] = ...) -> None: ...

class DoipBus(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
