from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SwitchClass(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    BREAKER: _ClassVar[SwitchClass]
    DISCONNECTOR: _ClassVar[SwitchClass]
    FUSE: _ClassVar[SwitchClass]
    JUMPER: _ClassVar[SwitchClass]
    LOAD_BREAK_SWITCH: _ClassVar[SwitchClass]
    RECLOSER: _ClassVar[SwitchClass]
BREAKER: SwitchClass
DISCONNECTOR: SwitchClass
FUSE: SwitchClass
JUMPER: SwitchClass
LOAD_BREAK_SWITCH: SwitchClass
RECLOSER: SwitchClass

class ModelConfig(_message.Message):
    __slots__ = ["vmPu", "vMinPu", "vMaxPu", "loadModel", "collapseSWER", "meterAtHVSource", "metersAtDistTransformers", "switchMeterPlacementConfigs", "fixedTime", "timePeriod", "timezone", "calibration"]
    VMPU_FIELD_NUMBER: _ClassVar[int]
    VMINPU_FIELD_NUMBER: _ClassVar[int]
    VMAXPU_FIELD_NUMBER: _ClassVar[int]
    LOADMODEL_FIELD_NUMBER: _ClassVar[int]
    COLLAPSESWER_FIELD_NUMBER: _ClassVar[int]
    METERATHVSOURCE_FIELD_NUMBER: _ClassVar[int]
    METERSATDISTTRANSFORMERS_FIELD_NUMBER: _ClassVar[int]
    SWITCHMETERPLACEMENTCONFIGS_FIELD_NUMBER: _ClassVar[int]
    FIXEDTIME_FIELD_NUMBER: _ClassVar[int]
    TIMEPERIOD_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    CALIBRATION_FIELD_NUMBER: _ClassVar[int]
    vmPu: float
    vMinPu: float
    vMaxPu: float
    loadModel: int
    collapseSWER: bool
    meterAtHVSource: bool
    metersAtDistTransformers: bool
    switchMeterPlacementConfigs: _containers.RepeatedCompositeFieldContainer[SwitchMeterPlacementConfig]
    fixedTime: FixedTime
    timePeriod: TimePeriod
    timezone: str
    calibration: bool
    def __init__(self, vmPu: _Optional[float] = ..., vMinPu: _Optional[float] = ..., vMaxPu: _Optional[float] = ..., loadModel: _Optional[int] = ..., collapseSWER: bool = ..., meterAtHVSource: bool = ..., metersAtDistTransformers: bool = ..., switchMeterPlacementConfigs: _Optional[_Iterable[_Union[SwitchMeterPlacementConfig, _Mapping]]] = ..., fixedTime: _Optional[_Union[FixedTime, _Mapping]] = ..., timePeriod: _Optional[_Union[TimePeriod, _Mapping]] = ..., timezone: _Optional[str] = ..., calibration: bool = ...) -> None: ...

class SwitchMeterPlacementConfig(_message.Message):
    __slots__ = ["meterSwitchClass", "namePattern"]
    METERSWITCHCLASS_FIELD_NUMBER: _ClassVar[int]
    NAMEPATTERN_FIELD_NUMBER: _ClassVar[int]
    meterSwitchClass: SwitchClass
    namePattern: str
    def __init__(self, meterSwitchClass: _Optional[_Union[SwitchClass, str]] = ..., namePattern: _Optional[str] = ...) -> None: ...

class FixedTime(_message.Message):
    __slots__ = ["time"]
    TIME_FIELD_NUMBER: _ClassVar[int]
    time: _timestamp_pb2.Timestamp
    def __init__(self, time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TimePeriod(_message.Message):
    __slots__ = ["startTime", "endTime"]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    ENDTIME_FIELD_NUMBER: _ClassVar[int]
    startTime: _timestamp_pb2.Timestamp
    endTime: _timestamp_pb2.Timestamp
    def __init__(self, startTime: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., endTime: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
