from zepben.protobuf.hc import ModelConfig_pb2 as _ModelConfig_pb2
from zepben.protobuf.hc import SolveConfig_pb2 as _SolveConfig_pb2
from zepben.protobuf.hc import ResultsConfig_pb2 as _ResultsConfig_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Job(_message.Message):
    __slots__ = ["feeder", "scenarios", "years", "modelConfig", "solveConfig", "resultsConfig", "qualityAssuranceProcessing", "generatorConfig", "executorConfig", "resultsProcessorConfig"]
    FEEDER_FIELD_NUMBER: _ClassVar[int]
    SCENARIOS_FIELD_NUMBER: _ClassVar[int]
    YEARS_FIELD_NUMBER: _ClassVar[int]
    MODELCONFIG_FIELD_NUMBER: _ClassVar[int]
    SOLVECONFIG_FIELD_NUMBER: _ClassVar[int]
    RESULTSCONFIG_FIELD_NUMBER: _ClassVar[int]
    QUALITYASSURANCEPROCESSING_FIELD_NUMBER: _ClassVar[int]
    GENERATORCONFIG_FIELD_NUMBER: _ClassVar[int]
    EXECUTORCONFIG_FIELD_NUMBER: _ClassVar[int]
    RESULTSPROCESSORCONFIG_FIELD_NUMBER: _ClassVar[int]
    feeder: str
    scenarios: _containers.RepeatedScalarFieldContainer[str]
    years: _containers.RepeatedScalarFieldContainer[int]
    modelConfig: _ModelConfig_pb2.ModelConfig
    solveConfig: _SolveConfig_pb2.SolveConfig
    resultsConfig: _ResultsConfig_pb2.ResultsConfig
    qualityAssuranceProcessing: bool
    generatorConfig: str
    executorConfig: str
    resultsProcessorConfig: str
    def __init__(self, feeder: _Optional[str] = ..., scenarios: _Optional[_Iterable[str]] = ..., years: _Optional[_Iterable[int]] = ..., modelConfig: _Optional[_Union[_ModelConfig_pb2.ModelConfig, _Mapping]] = ..., solveConfig: _Optional[_Union[_SolveConfig_pb2.SolveConfig, _Mapping]] = ..., resultsConfig: _Optional[_Union[_ResultsConfig_pb2.ResultsConfig, _Mapping]] = ..., qualityAssuranceProcessing: bool = ..., generatorConfig: _Optional[str] = ..., executorConfig: _Optional[str] = ..., resultsProcessorConfig: _Optional[str] = ...) -> None: ...
