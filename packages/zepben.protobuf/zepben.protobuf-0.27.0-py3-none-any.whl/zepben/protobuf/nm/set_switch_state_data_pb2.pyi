from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SwitchStateUpdate(_message.Message):
    __slots__ = ["mRID", "setOpen", "timestamp"]
    MRID_FIELD_NUMBER: _ClassVar[int]
    SETOPEN_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    mRID: str
    setOpen: bool
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, mRID: _Optional[str] = ..., setOpen: bool = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
