from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ObdMessage(_message.Message):
    __slots__ = ("bus_name", "ecu", "payload")
    BUS_NAME_FIELD_NUMBER: _ClassVar[int]
    ECU_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    bus_name: str
    ecu: EcuId
    payload: bytes
    def __init__(self, bus_name: _Optional[str] = ..., ecu: _Optional[_Union[EcuId, _Mapping]] = ..., payload: _Optional[bytes] = ...) -> None: ...

class EcuId(_message.Message):
    __slots__ = ("request_id", "response_id", "extended_request_address", "extended_response_address", "padding", "gateway_id")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    EXTENDED_REQUEST_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    EXTENDED_RESPONSE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PADDING_FIELD_NUMBER: _ClassVar[int]
    GATEWAY_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: bytes
    response_id: bytes
    extended_request_address: bytes
    extended_response_address: bytes
    padding: bytes
    gateway_id: bytes
    def __init__(self, request_id: _Optional[bytes] = ..., response_id: _Optional[bytes] = ..., extended_request_address: _Optional[bytes] = ..., extended_response_address: _Optional[bytes] = ..., padding: _Optional[bytes] = ..., gateway_id: _Optional[bytes] = ...) -> None: ...
