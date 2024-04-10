import runner_task_pb2 as _runner_task_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Component(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    Runner: _ClassVar[Component]
    Runtime: _ClassVar[Component]

class JobErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    RUNTIME_TASK_OUT_OF_MEMORY: _ClassVar[JobErrorCode]
    RUNTIME_TASK_USER_CODE_ERROR: _ClassVar[JobErrorCode]
Runner: Component
Runtime: Component
RUNTIME_TASK_OUT_OF_MEMORY: JobErrorCode
RUNTIME_TASK_USER_CODE_ERROR: JobErrorCode

class JobCompleteEvent(_message.Message):
    __slots__ = ["success", "failure", "cancellation", "timeout", "rejected", "job_id"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    CANCELLATION_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    REJECTED_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    success: JobSuccess
    failure: JobFailure
    cancellation: JobCancellation
    timeout: JobTimeout
    rejected: JobRejected
    job_id: str
    def __init__(self, success: _Optional[_Union[JobSuccess, _Mapping]] = ..., failure: _Optional[_Union[JobFailure, _Mapping]] = ..., cancellation: _Optional[_Union[JobCancellation, _Mapping]] = ..., timeout: _Optional[_Union[JobTimeout, _Mapping]] = ..., rejected: _Optional[_Union[JobRejected, _Mapping]] = ..., job_id: _Optional[str] = ...) -> None: ...

class JobSuccess(_message.Message):
    __slots__ = ["msg"]
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: str
    def __init__(self, msg: _Optional[str] = ...) -> None: ...

class JobRejected(_message.Message):
    __slots__ = ["reason"]
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class JobFailure(_message.Message):
    __slots__ = ["component", "error_message", "error_code", "stack_trace"]
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    component: Component
    error_message: str
    error_code: int
    stack_trace: str
    def __init__(self, component: _Optional[_Union[Component, str]] = ..., error_message: _Optional[str] = ..., error_code: _Optional[int] = ..., stack_trace: _Optional[str] = ...) -> None: ...

class JobCancellation(_message.Message):
    __slots__ = ["reason"]
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class JobTimeout(_message.Message):
    __slots__ = ["msg"]
    MSG_FIELD_NUMBER: _ClassVar[int]
    msg: str
    def __init__(self, msg: _Optional[str] = ...) -> None: ...

class TaskStartEvent(_message.Message):
    __slots__ = ["task_metadata", "timestamp", "task_id", "task_name"]
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    task_metadata: _runner_task_pb2.TaskMetadata
    timestamp: _timestamp_pb2.Timestamp
    task_id: str
    task_name: str
    def __init__(self, task_metadata: _Optional[_Union[_runner_task_pb2.TaskMetadata, _Mapping]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., task_id: _Optional[str] = ..., task_name: _Optional[str] = ...) -> None: ...

class TaskCompleteEvent(_message.Message):
    __slots__ = ["success", "failure", "cancel", "timeout", "skipped", "task_metadata", "timestamp", "task_id", "task_name"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    SKIPPED_FIELD_NUMBER: _ClassVar[int]
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    success: TaskSuccess
    failure: TaskFailure
    cancel: TaskCancelled
    timeout: TaskTimeout
    skipped: TaskSkipped
    task_metadata: _runner_task_pb2.TaskMetadata
    timestamp: _timestamp_pb2.Timestamp
    task_id: str
    task_name: str
    def __init__(self, success: _Optional[_Union[TaskSuccess, _Mapping]] = ..., failure: _Optional[_Union[TaskFailure, _Mapping]] = ..., cancel: _Optional[_Union[TaskCancelled, _Mapping]] = ..., timeout: _Optional[_Union[TaskTimeout, _Mapping]] = ..., skipped: _Optional[_Union[TaskSkipped, _Mapping]] = ..., task_metadata: _Optional[_Union[_runner_task_pb2.TaskMetadata, _Mapping]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., task_id: _Optional[str] = ..., task_name: _Optional[str] = ...) -> None: ...

class TaskSuccess(_message.Message):
    __slots__ = ["message", "runtime_table_preview"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_TABLE_PREVIEW_FIELD_NUMBER: _ClassVar[int]
    message: str
    runtime_table_preview: _containers.RepeatedCompositeFieldContainer[RuntimeTablePreview]
    def __init__(self, message: _Optional[str] = ..., runtime_table_preview: _Optional[_Iterable[_Union[RuntimeTablePreview, _Mapping]]] = ...) -> None: ...

class RuntimeTablePreview(_message.Message):
    __slots__ = ["columns", "table_name"]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    columns: _containers.RepeatedCompositeFieldContainer[RuntimeTableColumnInfo]
    table_name: str
    def __init__(self, columns: _Optional[_Iterable[_Union[RuntimeTableColumnInfo, _Mapping]]] = ..., table_name: _Optional[str] = ...) -> None: ...

class RuntimeTableColumnInfo(_message.Message):
    __slots__ = ["column_name", "column_type", "values"]
    COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    COLUMN_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    column_name: str
    column_type: str
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, column_name: _Optional[str] = ..., column_type: _Optional[str] = ..., values: _Optional[_Iterable[str]] = ...) -> None: ...

class TaskSkipped(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class TaskFailure(_message.Message):
    __slots__ = ["component", "error_message", "error_code", "stack_trace", "is_fatal"]
    COMPONENT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    STACK_TRACE_FIELD_NUMBER: _ClassVar[int]
    IS_FATAL_FIELD_NUMBER: _ClassVar[int]
    component: Component
    error_message: str
    error_code: int
    stack_trace: str
    is_fatal: bool
    def __init__(self, component: _Optional[_Union[Component, str]] = ..., error_message: _Optional[str] = ..., error_code: _Optional[int] = ..., stack_trace: _Optional[str] = ..., is_fatal: bool = ...) -> None: ...

class TaskCancelled(_message.Message):
    __slots__ = ["reason"]
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str
    def __init__(self, reason: _Optional[str] = ...) -> None: ...

class TaskTimeout(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class FlightServerStartEvent(_message.Message):
    __slots__ = ["endpoint", "job_id", "task_id", "num_rows"]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    NUM_ROWS_FIELD_NUMBER: _ClassVar[int]
    endpoint: str
    job_id: str
    task_id: str
    num_rows: int
    def __init__(self, endpoint: _Optional[str] = ..., job_id: _Optional[str] = ..., task_id: _Optional[str] = ..., num_rows: _Optional[int] = ...) -> None: ...

class RuntimeLogEvent(_message.Message):
    __slots__ = ["level", "output_stream", "type", "emit_timestamp_ns", "msg", "task_metadata", "job_id"]
    class LogLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNKNOWN: _ClassVar[RuntimeLogEvent.LogLevel]
        ERROR: _ClassVar[RuntimeLogEvent.LogLevel]
        WARNING: _ClassVar[RuntimeLogEvent.LogLevel]
        DEBUG: _ClassVar[RuntimeLogEvent.LogLevel]
        INFO: _ClassVar[RuntimeLogEvent.LogLevel]
        TRACE: _ClassVar[RuntimeLogEvent.LogLevel]
    UNKNOWN: RuntimeLogEvent.LogLevel
    ERROR: RuntimeLogEvent.LogLevel
    WARNING: RuntimeLogEvent.LogLevel
    DEBUG: RuntimeLogEvent.LogLevel
    INFO: RuntimeLogEvent.LogLevel
    TRACE: RuntimeLogEvent.LogLevel
    class OutputStream(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        STDOUT: _ClassVar[RuntimeLogEvent.OutputStream]
        STDERR: _ClassVar[RuntimeLogEvent.OutputStream]
    STDOUT: RuntimeLogEvent.OutputStream
    STDERR: RuntimeLogEvent.OutputStream
    class LogType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        SYSTEM: _ClassVar[RuntimeLogEvent.LogType]
        USER: _ClassVar[RuntimeLogEvent.LogType]
    SYSTEM: RuntimeLogEvent.LogType
    USER: RuntimeLogEvent.LogType
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_STREAM_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EMIT_TIMESTAMP_NS_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    level: RuntimeLogEvent.LogLevel
    output_stream: RuntimeLogEvent.OutputStream
    type: RuntimeLogEvent.LogType
    emit_timestamp_ns: int
    msg: str
    task_metadata: _runner_task_pb2.TaskMetadata
    job_id: str
    def __init__(self, level: _Optional[_Union[RuntimeLogEvent.LogLevel, str]] = ..., output_stream: _Optional[_Union[RuntimeLogEvent.OutputStream, str]] = ..., type: _Optional[_Union[RuntimeLogEvent.LogType, str]] = ..., emit_timestamp_ns: _Optional[int] = ..., msg: _Optional[str] = ..., task_metadata: _Optional[_Union[_runner_task_pb2.TaskMetadata, _Mapping]] = ..., job_id: _Optional[str] = ...) -> None: ...

class RuntimeLogMsg(_message.Message):
    __slots__ = ["level", "message"]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    level: str
    message: str
    def __init__(self, level: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class RunnerEvent(_message.Message):
    __slots__ = ["task_start", "task_completion", "job_completion", "runtime_user_log", "flight_server_start"]
    TASK_START_FIELD_NUMBER: _ClassVar[int]
    TASK_COMPLETION_FIELD_NUMBER: _ClassVar[int]
    JOB_COMPLETION_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_USER_LOG_FIELD_NUMBER: _ClassVar[int]
    FLIGHT_SERVER_START_FIELD_NUMBER: _ClassVar[int]
    task_start: TaskStartEvent
    task_completion: TaskCompleteEvent
    job_completion: JobCompleteEvent
    runtime_user_log: RuntimeLogEvent
    flight_server_start: FlightServerStartEvent
    def __init__(self, task_start: _Optional[_Union[TaskStartEvent, _Mapping]] = ..., task_completion: _Optional[_Union[TaskCompleteEvent, _Mapping]] = ..., job_completion: _Optional[_Union[JobCompleteEvent, _Mapping]] = ..., runtime_user_log: _Optional[_Union[RuntimeLogEvent, _Mapping]] = ..., flight_server_start: _Optional[_Union[FlightServerStartEvent, _Mapping]] = ...) -> None: ...
