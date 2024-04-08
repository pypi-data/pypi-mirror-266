from zepben.protobuf.hc.measurement import MeasurementZoneInfo_pb2 as _MeasurementZoneInfo_pb2
from zepben.protobuf.hc import ModelConfig_pb2 as _ModelConfig_pb2
from zepben.protobuf.hc import ResultsConfig_pb2 as _ResultsConfig_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Syf(_message.Message):
    __slots__ = ["scenario", "year", "feeder", "installedTxCapacity", "normVMinPu", "normVMaxPu", "emergVMinPu", "emergVMaxPu", "resultsConfig", "qualityAssuranceProcessing", "fixedTime", "timePeriod", "timezone", "executorConfig", "resultsProcessorConfig", "mzInfo"]
    class InstalledTxCapacityEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class MzInfoEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _MeasurementZoneInfo_pb2.MeasurementZoneInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_MeasurementZoneInfo_pb2.MeasurementZoneInfo, _Mapping]] = ...) -> None: ...
    SCENARIO_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    FEEDER_FIELD_NUMBER: _ClassVar[int]
    INSTALLEDTXCAPACITY_FIELD_NUMBER: _ClassVar[int]
    NORMVMINPU_FIELD_NUMBER: _ClassVar[int]
    NORMVMAXPU_FIELD_NUMBER: _ClassVar[int]
    EMERGVMINPU_FIELD_NUMBER: _ClassVar[int]
    EMERGVMAXPU_FIELD_NUMBER: _ClassVar[int]
    RESULTSCONFIG_FIELD_NUMBER: _ClassVar[int]
    QUALITYASSURANCEPROCESSING_FIELD_NUMBER: _ClassVar[int]
    FIXEDTIME_FIELD_NUMBER: _ClassVar[int]
    TIMEPERIOD_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    EXECUTORCONFIG_FIELD_NUMBER: _ClassVar[int]
    RESULTSPROCESSORCONFIG_FIELD_NUMBER: _ClassVar[int]
    MZINFO_FIELD_NUMBER: _ClassVar[int]
    scenario: str
    year: int
    feeder: str
    installedTxCapacity: _containers.ScalarMap[str, int]
    normVMinPu: float
    normVMaxPu: float
    emergVMinPu: float
    emergVMaxPu: float
    resultsConfig: _ResultsConfig_pb2.ResultsConfig
    qualityAssuranceProcessing: bool
    fixedTime: _ModelConfig_pb2.FixedTime
    timePeriod: _ModelConfig_pb2.TimePeriod
    timezone: str
    executorConfig: str
    resultsProcessorConfig: str
    mzInfo: _containers.MessageMap[str, _MeasurementZoneInfo_pb2.MeasurementZoneInfo]
    def __init__(self, scenario: _Optional[str] = ..., year: _Optional[int] = ..., feeder: _Optional[str] = ..., installedTxCapacity: _Optional[_Mapping[str, int]] = ..., normVMinPu: _Optional[float] = ..., normVMaxPu: _Optional[float] = ..., emergVMinPu: _Optional[float] = ..., emergVMaxPu: _Optional[float] = ..., resultsConfig: _Optional[_Union[_ResultsConfig_pb2.ResultsConfig, _Mapping]] = ..., qualityAssuranceProcessing: bool = ..., fixedTime: _Optional[_Union[_ModelConfig_pb2.FixedTime, _Mapping]] = ..., timePeriod: _Optional[_Union[_ModelConfig_pb2.TimePeriod, _Mapping]] = ..., timezone: _Optional[str] = ..., executorConfig: _Optional[str] = ..., resultsProcessorConfig: _Optional[str] = ..., mzInfo: _Optional[_Mapping[str, _MeasurementZoneInfo_pb2.MeasurementZoneInfo]] = ...) -> None: ...
