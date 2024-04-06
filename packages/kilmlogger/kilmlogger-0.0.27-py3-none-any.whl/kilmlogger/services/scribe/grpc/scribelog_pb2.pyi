from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class Ping(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...

class Pong(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...

class ListOfEntryRequest(_message.Message):
    __slots__ = ("logEntryRequest",)
    LOGENTRYREQUEST_FIELD_NUMBER: _ClassVar[int]
    logEntryRequest: _containers.RepeatedCompositeFieldContainer[LogEntryRequest]
    def __init__(
        self,
        logEntryRequest: _Optional[_Iterable[_Union[LogEntryRequest, _Mapping]]] = ...,
    ) -> None: ...

class ListOfActionLogRequest(_message.Message):
    __slots__ = ("actionLogRequest",)
    ACTIONLOGREQUEST_FIELD_NUMBER: _ClassVar[int]
    actionLogRequest: _containers.RepeatedCompositeFieldContainer[ActionLogRequest]
    def __init__(
        self,
        actionLogRequest: _Optional[
            _Iterable[_Union[ActionLogRequest, _Mapping]]
        ] = ...,
    ) -> None: ...

class ActionLogRequest(_message.Message):
    __slots__ = ("timestamp", "json_param")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    JSON_PARAM_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    json_param: str
    def __init__(
        self, timestamp: _Optional[int] = ..., json_param: _Optional[str] = ...
    ) -> None: ...

class LogEntryRequest(_message.Message):
    __slots__ = ("timestamp", "category", "app_name", "app_prop", "log_entry")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    APP_PROP_FIELD_NUMBER: _ClassVar[int]
    LOG_ENTRY_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    category: str
    app_name: str
    app_prop: str
    log_entry: LogEntry
    def __init__(
        self,
        timestamp: _Optional[int] = ...,
        category: _Optional[str] = ...,
        app_name: _Optional[str] = ...,
        app_prop: _Optional[str] = ...,
        log_entry: _Optional[_Union[LogEntry, _Mapping]] = ...,
    ) -> None: ...

class LogEntryResult(_message.Message):
    __slots__ = ("error", "error_message")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    error: int
    error_message: str
    def __init__(
        self, error: _Optional[int] = ..., error_message: _Optional[str] = ...
    ) -> None: ...

class LogEntry(_message.Message):
    __slots__ = (
        "ip",
        "src_id",
        "des_id",
        "command",
        "sub_command",
        "result",
        "start_time",
        "execute_time",
        "json_param",
        "json_ext_param",
        "client_type",
        "client_version",
        "type",
        "dp_log",
        "dp_cate",
    )
    IP_FIELD_NUMBER: _ClassVar[int]
    SRC_ID_FIELD_NUMBER: _ClassVar[int]
    DES_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    SUB_COMMAND_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_TIME_FIELD_NUMBER: _ClassVar[int]
    JSON_PARAM_FIELD_NUMBER: _ClassVar[int]
    JSON_EXT_PARAM_FIELD_NUMBER: _ClassVar[int]
    CLIENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DP_LOG_FIELD_NUMBER: _ClassVar[int]
    DP_CATE_FIELD_NUMBER: _ClassVar[int]
    ip: str
    src_id: int
    des_id: int
    command: int
    sub_command: int
    result: int
    start_time: int
    execute_time: int
    json_param: str
    json_ext_param: str
    client_type: int
    client_version: int
    type: int
    dp_log: str
    dp_cate: str
    def __init__(
        self,
        ip: _Optional[str] = ...,
        src_id: _Optional[int] = ...,
        des_id: _Optional[int] = ...,
        command: _Optional[int] = ...,
        sub_command: _Optional[int] = ...,
        result: _Optional[int] = ...,
        start_time: _Optional[int] = ...,
        execute_time: _Optional[int] = ...,
        json_param: _Optional[str] = ...,
        json_ext_param: _Optional[str] = ...,
        client_type: _Optional[int] = ...,
        client_version: _Optional[int] = ...,
        type: _Optional[int] = ...,
        dp_log: _Optional[str] = ...,
        dp_cate: _Optional[str] = ...,
    ) -> None: ...
