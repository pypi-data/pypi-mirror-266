from zepben.protobuf.nm import set_switch_state_data_pb2 as _set_switch_state_data_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SetCurrentSwitchStatesRequest(_message.Message):
    __slots__ = ["messageId", "switchesToUpdate"]
    MESSAGEID_FIELD_NUMBER: _ClassVar[int]
    SWITCHESTOUPDATE_FIELD_NUMBER: _ClassVar[int]
    messageId: int
    switchesToUpdate: _containers.RepeatedCompositeFieldContainer[_set_switch_state_data_pb2.SwitchStateUpdate]
    def __init__(self, messageId: _Optional[int] = ..., switchesToUpdate: _Optional[_Iterable[_Union[_set_switch_state_data_pb2.SwitchStateUpdate, _Mapping]]] = ...) -> None: ...
