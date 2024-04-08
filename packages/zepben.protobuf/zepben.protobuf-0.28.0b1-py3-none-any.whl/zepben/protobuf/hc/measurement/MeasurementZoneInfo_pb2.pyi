from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MeasurementZoneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN: _ClassVar[MeasurementZoneType]
    TRANSFORMER: _ClassVar[MeasurementZoneType]
    BREAKER: _ClassVar[MeasurementZoneType]
    DISCONNECTOR: _ClassVar[MeasurementZoneType]
    FUSE: _ClassVar[MeasurementZoneType]
    JUMPER: _ClassVar[MeasurementZoneType]
    LOAD_BREAK_SWITCH: _ClassVar[MeasurementZoneType]
    RECLOSER: _ClassVar[MeasurementZoneType]
    ENERGY_CONSUMER: _ClassVar[MeasurementZoneType]
    FEEDER_HEAD: _ClassVar[MeasurementZoneType]
    CALIBRATION: _ClassVar[MeasurementZoneType]
UNKNOWN: MeasurementZoneType
TRANSFORMER: MeasurementZoneType
BREAKER: MeasurementZoneType
DISCONNECTOR: MeasurementZoneType
FUSE: MeasurementZoneType
JUMPER: MeasurementZoneType
LOAD_BREAK_SWITCH: MeasurementZoneType
RECLOSER: MeasurementZoneType
ENERGY_CONSUMER: MeasurementZoneType
FEEDER_HEAD: MeasurementZoneType
CALIBRATION: MeasurementZoneType

class MeasurementZoneInfo(_message.Message):
    __slots__ = ["conductingEquipmentMRID", "terminalSequenceNumber", "voltageBase", "type"]
    CONDUCTINGEQUIPMENTMRID_FIELD_NUMBER: _ClassVar[int]
    TERMINALSEQUENCENUMBER_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEBASE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    conductingEquipmentMRID: str
    terminalSequenceNumber: int
    voltageBase: int
    type: MeasurementZoneType
    def __init__(self, conductingEquipmentMRID: _Optional[str] = ..., terminalSequenceNumber: _Optional[int] = ..., voltageBase: _Optional[int] = ..., type: _Optional[_Union[MeasurementZoneType, str]] = ...) -> None: ...
