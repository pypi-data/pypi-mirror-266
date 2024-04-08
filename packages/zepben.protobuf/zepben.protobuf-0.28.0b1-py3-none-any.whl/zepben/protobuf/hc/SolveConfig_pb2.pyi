from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SolveMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    YEARLY: _ClassVar[SolveMode]
    DAILY: _ClassVar[SolveMode]
YEARLY: SolveMode
DAILY: SolveMode

class SolveConfig(_message.Message):
    __slots__ = ["normVMinPu", "normVMaxPu", "emergVMinPu", "emergVMaxPu", "baseFrequency", "voltageBases", "maxIter", "maxControlIter", "mode", "stepSizeMinutes"]
    NORMVMINPU_FIELD_NUMBER: _ClassVar[int]
    NORMVMAXPU_FIELD_NUMBER: _ClassVar[int]
    EMERGVMINPU_FIELD_NUMBER: _ClassVar[int]
    EMERGVMAXPU_FIELD_NUMBER: _ClassVar[int]
    BASEFREQUENCY_FIELD_NUMBER: _ClassVar[int]
    VOLTAGEBASES_FIELD_NUMBER: _ClassVar[int]
    MAXITER_FIELD_NUMBER: _ClassVar[int]
    MAXCONTROLITER_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    STEPSIZEMINUTES_FIELD_NUMBER: _ClassVar[int]
    normVMinPu: float
    normVMaxPu: float
    emergVMinPu: float
    emergVMaxPu: float
    baseFrequency: int
    voltageBases: _containers.RepeatedScalarFieldContainer[float]
    maxIter: int
    maxControlIter: int
    mode: SolveMode
    stepSizeMinutes: float
    def __init__(self, normVMinPu: _Optional[float] = ..., normVMaxPu: _Optional[float] = ..., emergVMinPu: _Optional[float] = ..., emergVMaxPu: _Optional[float] = ..., baseFrequency: _Optional[int] = ..., voltageBases: _Optional[_Iterable[float]] = ..., maxIter: _Optional[int] = ..., maxControlIter: _Optional[int] = ..., mode: _Optional[_Union[SolveMode, str]] = ..., stepSizeMinutes: _Optional[float] = ...) -> None: ...
