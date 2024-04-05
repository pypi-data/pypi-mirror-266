from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OverviewRequest(_message.Message):
    __slots__ = ("overview_uuid", "chart_uuids", "params")
    OVERVIEW_UUID_FIELD_NUMBER: _ClassVar[int]
    CHART_UUIDS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    overview_uuid: str
    chart_uuids: _containers.RepeatedScalarFieldContainer[str]
    params: DispatcherParams
    def __init__(self, overview_uuid: _Optional[str] = ..., chart_uuids: _Optional[_Iterable[str]] = ..., params: _Optional[_Union[DispatcherParams, _Mapping]] = ...) -> None: ...

class DispatcherRequest(_message.Message):
    __slots__ = ("chart_uuid", "params")
    CHART_UUID_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    chart_uuid: str
    params: DispatcherParams
    def __init__(self, chart_uuid: _Optional[str] = ..., params: _Optional[_Union[DispatcherParams, _Mapping]] = ...) -> None: ...

class DispatcherFilter(_message.Message):
    __slots__ = ("metric", "operator", "values")
    METRIC_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    metric: str
    operator: str
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, metric: _Optional[str] = ..., operator: _Optional[str] = ..., values: _Optional[_Iterable[str]] = ...) -> None: ...

class DispatcherParams(_message.Message):
    __slots__ = ("start_date", "end_date", "filters", "requested_fields", "session_uuid")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    SESSION_UUID_FIELD_NUMBER: _ClassVar[int]
    start_date: str
    end_date: str
    filters: _containers.RepeatedCompositeFieldContainer[DispatcherFilter]
    requested_fields: _containers.RepeatedScalarFieldContainer[str]
    session_uuid: str
    def __init__(self, start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., filters: _Optional[_Iterable[_Union[DispatcherFilter, _Mapping]]] = ..., requested_fields: _Optional[_Iterable[str]] = ..., session_uuid: _Optional[str] = ...) -> None: ...

class DispatcherResponse(_message.Message):
    __slots__ = ("complete", "success", "cached", "payload")
    COMPLETE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CACHED_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    complete: bool
    success: bool
    cached: bool
    payload: _any_pb2.Any
    def __init__(self, complete: bool = ..., success: bool = ..., cached: bool = ..., payload: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
