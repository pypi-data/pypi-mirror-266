from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RawResultsConfig(_message.Message):
    __slots__ = ["energyMeterVoltagesRaw", "energyMetersRaw", "resultsPerMeter", "overloadsRaw", "voltageExceptionsRaw"]
    ENERGYMETERVOLTAGESRAW_FIELD_NUMBER: _ClassVar[int]
    ENERGYMETERSRAW_FIELD_NUMBER: _ClassVar[int]
    RESULTSPERMETER_FIELD_NUMBER: _ClassVar[int]
    OVERLOADSRAW_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEEXCEPTIONSRAW_FIELD_NUMBER: _ClassVar[int]
    energyMeterVoltagesRaw: bool
    energyMetersRaw: bool
    resultsPerMeter: bool
    overloadsRaw: bool
    voltageExceptionsRaw: bool
    def __init__(self, energyMeterVoltagesRaw: bool = ..., energyMetersRaw: bool = ..., resultsPerMeter: bool = ..., overloadsRaw: bool = ..., voltageExceptionsRaw: bool = ...) -> None: ...

class StoredResultsConfig(_message.Message):
    __slots__ = ["energyMeterVoltagesRaw", "energyMetersRaw", "overloadsRaw", "voltageExceptionsRaw"]
    ENERGYMETERVOLTAGESRAW_FIELD_NUMBER: _ClassVar[int]
    ENERGYMETERSRAW_FIELD_NUMBER: _ClassVar[int]
    OVERLOADSRAW_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEEXCEPTIONSRAW_FIELD_NUMBER: _ClassVar[int]
    energyMeterVoltagesRaw: bool
    energyMetersRaw: bool
    overloadsRaw: bool
    voltageExceptionsRaw: bool
    def __init__(self, energyMeterVoltagesRaw: bool = ..., energyMetersRaw: bool = ..., overloadsRaw: bool = ..., voltageExceptionsRaw: bool = ...) -> None: ...

class MetricsResultsConfig(_message.Message):
    __slots__ = ["calculatePerformanceMetrics"]
    CALCULATEPERFORMANCEMETRICS_FIELD_NUMBER: _ClassVar[int]
    calculatePerformanceMetrics: bool
    def __init__(self, calculatePerformanceMetrics: bool = ...) -> None: ...

class ResultsConfig(_message.Message):
    __slots__ = ["rawConfig", "metricsConfig", "storedResultsConfig"]
    RAWCONFIG_FIELD_NUMBER: _ClassVar[int]
    METRICSCONFIG_FIELD_NUMBER: _ClassVar[int]
    STOREDRESULTSCONFIG_FIELD_NUMBER: _ClassVar[int]
    rawConfig: RawResultsConfig
    metricsConfig: MetricsResultsConfig
    storedResultsConfig: StoredResultsConfig
    def __init__(self, rawConfig: _Optional[_Union[RawResultsConfig, _Mapping]] = ..., metricsConfig: _Optional[_Union[MetricsResultsConfig, _Mapping]] = ..., storedResultsConfig: _Optional[_Union[StoredResultsConfig, _Mapping]] = ...) -> None: ...
