import execution_plan_pb2 as _execution_plan_pb2
import runner_task_pb2 as _runner_task_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from opentelemetry.proto.logs.v1 import logs_pb2 as _logs_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
from execution_plan_pb2 import JobRequest
from execution_plan_pb2 import JobArg
from execution_plan_pb2 import Step
from execution_plan_pb2 import JobStatus

DESCRIPTOR: _descriptor.FileDescriptor
UNKNOWN: _execution_plan_pb2.JobStatus
PENDING: _execution_plan_pb2.JobStatus
RUNNING: _execution_plan_pb2.JobStatus
COMPLETED: _execution_plan_pb2.JobStatus
FAILED: _execution_plan_pb2.JobStatus
CANCELED: _execution_plan_pb2.JobStatus

class LogType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    STDOUT: _ClassVar[LogType]
    STDERR: _ClassVar[LogType]

class RunnerInfoType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    JOB_COMPLETE: _ClassVar[RunnerInfoType]
    JOB_FAILED: _ClassVar[RunnerInfoType]
    JOB_TIMEOUT: _ClassVar[RunnerInfoType]
    JOB_RUNNER_TELEMETRY: _ClassVar[RunnerInfoType]
    JOB_USER_LOG: _ClassVar[RunnerInfoType]

class TaskLifecycleType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    TASK_STARTED: _ClassVar[TaskLifecycleType]
    TASK_FINISHED_SUCCESS: _ClassVar[TaskLifecycleType]
    TASK_FINISHED_FAILURE: _ClassVar[TaskLifecycleType]
    TASK_FINISHED_TIMED_OUT: _ClassVar[TaskLifecycleType]
    TASK_FINISHED_SKIPPED: _ClassVar[TaskLifecycleType]

class AllocationStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    DISK: _ClassVar[AllocationStrategy]
    SHMEM: _ClassVar[AllocationStrategy]
STDOUT: LogType
STDERR: LogType
JOB_COMPLETE: RunnerInfoType
JOB_FAILED: RunnerInfoType
JOB_TIMEOUT: RunnerInfoType
JOB_RUNNER_TELEMETRY: RunnerInfoType
JOB_USER_LOG: RunnerInfoType
TASK_STARTED: TaskLifecycleType
TASK_FINISHED_SUCCESS: TaskLifecycleType
TASK_FINISHED_FAILURE: TaskLifecycleType
TASK_FINISHED_TIMED_OUT: TaskLifecycleType
TASK_FINISHED_SKIPPED: TaskLifecycleType
DISK: AllocationStrategy
SHMEM: AllocationStrategy

class MemoryRelease(_message.Message):
    __slots__ = ["id", "input_object"]
    ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_OBJECT_FIELD_NUMBER: _ClassVar[int]
    id: str
    input_object: str
    def __init__(self, id: _Optional[str] = ..., input_object: _Optional[str] = ...) -> None: ...

class JobId(_message.Message):
    __slots__ = ["id", "snapshot_key", "dag_graphviz", "dag_ascii"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_KEY_FIELD_NUMBER: _ClassVar[int]
    DAG_GRAPHVIZ_FIELD_NUMBER: _ClassVar[int]
    DAG_ASCII_FIELD_NUMBER: _ClassVar[int]
    id: str
    snapshot_key: str
    dag_graphviz: str
    dag_ascii: str
    def __init__(self, id: _Optional[str] = ..., snapshot_key: _Optional[str] = ..., dag_graphviz: _Optional[str] = ..., dag_ascii: _Optional[str] = ...) -> None: ...

class JobLogs(_message.Message):
    __slots__ = ["logs"]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[RunnerInfo]
    def __init__(self, logs: _Optional[_Iterable[_Union[RunnerInfo, _Mapping]]] = ...) -> None: ...

class JobResult(_message.Message):
    __slots__ = ["job_id", "result_data", "error"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    job_id: JobId
    result_data: str
    error: str
    def __init__(self, job_id: _Optional[_Union[JobId, _Mapping]] = ..., result_data: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class CancelJobRequest(_message.Message):
    __slots__ = ["job_id"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: JobId
    def __init__(self, job_id: _Optional[_Union[JobId, _Mapping]] = ...) -> None: ...

class CancelJobResponse(_message.Message):
    __slots__ = ["status", "message"]
    class CancelStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        SUCCESS: _ClassVar[CancelJobResponse.CancelStatus]
        FAILURE: _ClassVar[CancelJobResponse.CancelStatus]
    SUCCESS: CancelJobResponse.CancelStatus
    FAILURE: CancelJobResponse.CancelStatus
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: CancelJobResponse.CancelStatus
    message: str
    def __init__(self, status: _Optional[_Union[CancelJobResponse.CancelStatus, str]] = ..., message: _Optional[str] = ...) -> None: ...

class RunnerAction(_message.Message):
    __slots__ = ["job_id", "action", "job_request", "trace_id", "parent_span_id", "job_args"]
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        START: _ClassVar[RunnerAction.Action]
        CANCEL: _ClassVar[RunnerAction.Action]
        UPLOAD: _ClassVar[RunnerAction.Action]
        QUERY: _ClassVar[RunnerAction.Action]
    START: RunnerAction.Action
    CANCEL: RunnerAction.Action
    UPLOAD: RunnerAction.Action
    QUERY: RunnerAction.Action
    class JobArgsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    JOB_REQUEST_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_SPAN_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ARGS_FIELD_NUMBER: _ClassVar[int]
    job_id: JobId
    action: RunnerAction.Action
    job_request: _execution_plan_pb2.JobRequest
    trace_id: str
    parent_span_id: str
    job_args: _containers.ScalarMap[str, str]
    def __init__(self, job_id: _Optional[_Union[JobId, _Mapping]] = ..., action: _Optional[_Union[RunnerAction.Action, str]] = ..., job_request: _Optional[_Union[_execution_plan_pb2.JobRequest, _Mapping]] = ..., trace_id: _Optional[str] = ..., parent_span_id: _Optional[str] = ..., job_args: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RunnerInfo(_message.Message):
    __slots__ = ["job_id", "info_type", "log_timestamp", "runner_log", "task_lifecycle_event"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    INFO_TYPE_FIELD_NUMBER: _ClassVar[int]
    LOG_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RUNNER_LOG_FIELD_NUMBER: _ClassVar[int]
    TASK_LIFECYCLE_EVENT_FIELD_NUMBER: _ClassVar[int]
    job_id: JobId
    info_type: RunnerInfoType
    log_timestamp: _timestamp_pb2.Timestamp
    runner_log: RunnerLog
    task_lifecycle_event: TaskLifecycleEvent
    def __init__(self, job_id: _Optional[_Union[JobId, _Mapping]] = ..., info_type: _Optional[_Union[RunnerInfoType, str]] = ..., log_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., runner_log: _Optional[_Union[RunnerLog, _Mapping]] = ..., task_lifecycle_event: _Optional[_Union[TaskLifecycleEvent, _Mapping]] = ...) -> None: ...

class TaskLifecycleEvent(_message.Message):
    __slots__ = ["lifecycle_type", "task_description", "timestamp", "task_id", "task_name", "task_metadata", "flight_endpoint"]
    LIFECYCLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TASK_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_METADATA_FIELD_NUMBER: _ClassVar[int]
    FLIGHT_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    lifecycle_type: TaskLifecycleType
    task_description: str
    timestamp: _timestamp_pb2.Timestamp
    task_id: str
    task_name: str
    task_metadata: _runner_task_pb2.TaskMetadata
    flight_endpoint: str
    def __init__(self, lifecycle_type: _Optional[_Union[TaskLifecycleType, str]] = ..., task_description: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., task_id: _Optional[str] = ..., task_name: _Optional[str] = ..., task_metadata: _Optional[_Union[_runner_task_pb2.TaskMetadata, _Mapping]] = ..., flight_endpoint: _Optional[str] = ...) -> None: ...

class RunnerLog(_message.Message):
    __slots__ = ["log_type", "otel_log"]
    LOG_TYPE_FIELD_NUMBER: _ClassVar[int]
    OTEL_LOG_FIELD_NUMBER: _ClassVar[int]
    log_type: LogType
    otel_log: _logs_pb2.LogRecord
    def __init__(self, log_type: _Optional[_Union[LogType, str]] = ..., otel_log: _Optional[_Union[_logs_pb2.LogRecord, _Mapping]] = ...) -> None: ...

class RunnerLabel(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class JoinRunnerRequest(_message.Message):
    __slots__ = ["public_key", "hostname", "resources", "labels"]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    public_key: str
    hostname: str
    resources: Resources
    labels: _containers.RepeatedCompositeFieldContainer[RunnerLabel]
    def __init__(self, public_key: _Optional[str] = ..., hostname: _Optional[str] = ..., resources: _Optional[_Union[Resources, _Mapping]] = ..., labels: _Optional[_Iterable[_Union[RunnerLabel, _Mapping]]] = ...) -> None: ...

class NodeInfo(_message.Message):
    __slots__ = ["nodes"]
    NODES_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.RepeatedCompositeFieldContainer[Node]
    def __init__(self, nodes: _Optional[_Iterable[_Union[Node, _Mapping]]] = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ["id", "public_key", "hostname", "resources", "labels"]
    ID_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    id: str
    public_key: str
    hostname: str
    resources: Resources
    labels: _containers.RepeatedCompositeFieldContainer[RunnerLabel]
    def __init__(self, id: _Optional[str] = ..., public_key: _Optional[str] = ..., hostname: _Optional[str] = ..., resources: _Optional[_Union[Resources, _Mapping]] = ..., labels: _Optional[_Iterable[_Union[RunnerLabel, _Mapping]]] = ...) -> None: ...

class JoinRunnerResponse(_message.Message):
    __slots__ = ["success"]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class Resources(_message.Message):
    __slots__ = ["cpus", "memory_bytes", "disk_space_bytes", "client_version"]
    CPUS_FIELD_NUMBER: _ClassVar[int]
    MEMORY_BYTES_FIELD_NUMBER: _ClassVar[int]
    DISK_SPACE_BYTES_FIELD_NUMBER: _ClassVar[int]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    cpus: int
    memory_bytes: int
    disk_space_bytes: int
    client_version: str
    def __init__(self, cpus: _Optional[int] = ..., memory_bytes: _Optional[int] = ..., disk_space_bytes: _Optional[int] = ..., client_version: _Optional[str] = ...) -> None: ...

class TableInfo(_message.Message):
    __slots__ = ["name", "columns", "rows", "size", "active_branch"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    ROWS_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_BRANCH_FIELD_NUMBER: _ClassVar[int]
    name: str
    columns: int
    rows: int
    size: int
    active_branch: str
    def __init__(self, name: _Optional[str] = ..., columns: _Optional[int] = ..., rows: _Optional[int] = ..., size: _Optional[int] = ..., active_branch: _Optional[str] = ...) -> None: ...

class ColumnInfo(_message.Message):
    __slots__ = ["name", "type", "nulls", "compression", "encoding", "min", "max", "distinct_count", "total_rows", "num_values"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NULLS_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    DISTINCT_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    NUM_VALUES_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    nulls: int
    compression: str
    encoding: str
    min: str
    max: str
    distinct_count: int
    total_rows: int
    num_values: int
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., nulls: _Optional[int] = ..., compression: _Optional[str] = ..., encoding: _Optional[str] = ..., min: _Optional[str] = ..., max: _Optional[str] = ..., distinct_count: _Optional[int] = ..., total_rows: _Optional[int] = ..., num_values: _Optional[int] = ...) -> None: ...

class BranchInfo(_message.Message):
    __slots__ = ["table", "branch", "snapshotted_at", "active"]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOTTED_AT_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    table: str
    branch: str
    snapshotted_at: _timestamp_pb2.Timestamp
    active: bool
    def __init__(self, table: _Optional[str] = ..., branch: _Optional[str] = ..., snapshotted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., active: bool = ...) -> None: ...

class TriggerRunRequest(_message.Message):
    __slots__ = ["zip_file", "module_version", "allocation_strategy", "client_hostname", "args", "is_flight_query", "query_for_flight", "run_id"]
    class ArgsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ZIP_FILE_FIELD_NUMBER: _ClassVar[int]
    MODULE_VERSION_FIELD_NUMBER: _ClassVar[int]
    ALLOCATION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    IS_FLIGHT_QUERY_FIELD_NUMBER: _ClassVar[int]
    QUERY_FOR_FLIGHT_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    zip_file: bytes
    module_version: str
    allocation_strategy: AllocationStrategy
    client_hostname: str
    args: _containers.ScalarMap[str, str]
    is_flight_query: bool
    query_for_flight: str
    run_id: str
    def __init__(self, zip_file: _Optional[bytes] = ..., module_version: _Optional[str] = ..., allocation_strategy: _Optional[_Union[AllocationStrategy, str]] = ..., client_hostname: _Optional[str] = ..., args: _Optional[_Mapping[str, str]] = ..., is_flight_query: bool = ..., query_for_flight: _Optional[str] = ..., run_id: _Optional[str] = ...) -> None: ...

class GetBranchesRequest(_message.Message):
    __slots__ = ["request_id", "request_ts", "branch_name"]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TS_FIELD_NUMBER: _ClassVar[int]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    request_ts: int
    branch_name: str
    def __init__(self, request_id: _Optional[str] = ..., request_ts: _Optional[int] = ..., branch_name: _Optional[str] = ...) -> None: ...

class GetBranchesResponseData(_message.Message):
    __slots__ = ["branches", "has_more", "token"]
    BRANCHES_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    branches: _containers.RepeatedCompositeFieldContainer[Branch]
    has_more: bool
    token: str
    def __init__(self, branches: _Optional[_Iterable[_Union[Branch, _Mapping]]] = ..., has_more: bool = ..., token: _Optional[str] = ...) -> None: ...

class GetBranchesResponse(_message.Message):
    __slots__ = ["data", "metadata"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    data: GetBranchesResponseData
    metadata: ResponseMetadata
    def __init__(self, data: _Optional[_Union[GetBranchesResponseData, _Mapping]] = ..., metadata: _Optional[_Union[ResponseMetadata, _Mapping]] = ...) -> None: ...

class GetBranchRequest(_message.Message):
    __slots__ = ["branch_name", "request_id", "request_ts", "hash_or_ref", "page_token"]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TS_FIELD_NUMBER: _ClassVar[int]
    HASH_OR_REF_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    branch_name: str
    request_id: str
    request_ts: int
    hash_or_ref: str
    page_token: str
    def __init__(self, branch_name: _Optional[str] = ..., request_id: _Optional[str] = ..., request_ts: _Optional[int] = ..., hash_or_ref: _Optional[str] = ..., page_token: _Optional[str] = ...) -> None: ...

class GetBranchResponseData(_message.Message):
    __slots__ = ["has_more", "token", "entries", "branch_name", "hash_on_ref"]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    HASH_ON_REF_FIELD_NUMBER: _ClassVar[int]
    has_more: bool
    token: str
    entries: _containers.RepeatedCompositeFieldContainer[BranchEntry]
    branch_name: str
    hash_on_ref: str
    def __init__(self, has_more: bool = ..., token: _Optional[str] = ..., entries: _Optional[_Iterable[_Union[BranchEntry, _Mapping]]] = ..., branch_name: _Optional[str] = ..., hash_on_ref: _Optional[str] = ...) -> None: ...

class GetBranchResponse(_message.Message):
    __slots__ = ["data", "metadata"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    data: GetBranchResponseData
    metadata: ResponseMetadata
    def __init__(self, data: _Optional[_Union[GetBranchResponseData, _Mapping]] = ..., metadata: _Optional[_Union[ResponseMetadata, _Mapping]] = ...) -> None: ...

class DeleteBranchRequest(_message.Message):
    __slots__ = ["branch_name", "request_id", "request_ts"]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TS_FIELD_NUMBER: _ClassVar[int]
    branch_name: str
    request_id: str
    request_ts: int
    def __init__(self, branch_name: _Optional[str] = ..., request_id: _Optional[str] = ..., request_ts: _Optional[int] = ...) -> None: ...

class DeleteBranchResponseData(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class DeleteBranchResponse(_message.Message):
    __slots__ = ["data", "metadata"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    data: DeleteBranchResponseData
    metadata: ResponseMetadata
    def __init__(self, data: _Optional[_Union[DeleteBranchResponseData, _Mapping]] = ..., metadata: _Optional[_Union[ResponseMetadata, _Mapping]] = ...) -> None: ...

class CodeIntelligenceError(_message.Message):
    __slots__ = ["type", "message", "traceback"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TRACEBACK_FIELD_NUMBER: _ClassVar[int]
    type: str
    message: str
    traceback: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[str] = ..., message: _Optional[str] = ..., traceback: _Optional[_Iterable[str]] = ...) -> None: ...

class PostRunResponse(_message.Message):
    __slots__ = ["metadata", "data", "error"]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    metadata: PostRunMetaData
    data: PostRunData
    error: CodeIntelligenceError
    def __init__(self, metadata: _Optional[_Union[PostRunMetaData, _Mapping]] = ..., data: _Optional[_Union[PostRunData, _Mapping]] = ..., error: _Optional[_Union[CodeIntelligenceError, _Mapping]] = ...) -> None: ...

class PostRunMetaData(_message.Message):
    __slots__ = ["status_code", "response_id", "response_ts"]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TS_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response_id: str
    response_ts: int
    def __init__(self, status_code: _Optional[int] = ..., response_id: _Optional[str] = ..., response_ts: _Optional[int] = ...) -> None: ...

class PostRunData(_message.Message):
    __slots__ = ["id", "logical_plan_id", "steps", "log_groups", "created_ts", "physical_plan_id", "snapshot_id", "object_key"]
    ID_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    LOG_GROUPS_FIELD_NUMBER: _ClassVar[int]
    CREATED_TS_FIELD_NUMBER: _ClassVar[int]
    PHYSICAL_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_KEY_FIELD_NUMBER: _ClassVar[int]
    id: str
    logical_plan_id: str
    steps: _containers.RepeatedCompositeFieldContainer[_execution_plan_pb2.Step]
    log_groups: _containers.RepeatedCompositeFieldContainer[_runner_task_pb2.LogGroup]
    created_ts: int
    physical_plan_id: str
    snapshot_id: str
    object_key: str
    def __init__(self, id: _Optional[str] = ..., logical_plan_id: _Optional[str] = ..., steps: _Optional[_Iterable[_Union[_execution_plan_pb2.Step, _Mapping]]] = ..., log_groups: _Optional[_Iterable[_Union[_runner_task_pb2.LogGroup, _Mapping]]] = ..., created_ts: _Optional[int] = ..., physical_plan_id: _Optional[str] = ..., snapshot_id: _Optional[str] = ..., object_key: _Optional[str] = ...) -> None: ...

class GetTableRequest(_message.Message):
    __slots__ = ["branch_name", "table_name", "request_id", "request_ts"]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TS_FIELD_NUMBER: _ClassVar[int]
    branch_name: str
    table_name: str
    request_id: str
    request_ts: int
    def __init__(self, branch_name: _Optional[str] = ..., table_name: _Optional[str] = ..., request_id: _Optional[str] = ..., request_ts: _Optional[int] = ...) -> None: ...

class GetTableResponse(_message.Message):
    __slots__ = ["data", "metadata"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    data: TableData
    metadata: ResponseMetadata
    def __init__(self, data: _Optional[_Union[TableData, _Mapping]] = ..., metadata: _Optional[_Union[ResponseMetadata, _Mapping]] = ...) -> None: ...

class TableEntry(_message.Message):
    __slots__ = ["id", "branch_name", "name", "fields", "snapshots", "records", "size", "last_updated_ms"]
    ID_FIELD_NUMBER: _ClassVar[int]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOTS_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_MS_FIELD_NUMBER: _ClassVar[int]
    id: str
    branch_name: str
    name: str
    fields: _containers.RepeatedCompositeFieldContainer[TableField]
    snapshots: int
    records: int
    size: int
    last_updated_ms: str
    def __init__(self, id: _Optional[str] = ..., branch_name: _Optional[str] = ..., name: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[TableField, _Mapping]]] = ..., snapshots: _Optional[int] = ..., records: _Optional[int] = ..., size: _Optional[int] = ..., last_updated_ms: _Optional[str] = ...) -> None: ...

class BranchEntry(_message.Message):
    __slots__ = ["kind", "name"]
    KIND_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    kind: str
    name: str
    def __init__(self, kind: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class Branch(_message.Message):
    __slots__ = ["name", "hash", "user", "data_name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    DATA_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    hash: str
    user: User
    data_name: str
    def __init__(self, name: _Optional[str] = ..., hash: _Optional[str] = ..., user: _Optional[_Union[User, _Mapping]] = ..., data_name: _Optional[str] = ...) -> None: ...

class TableField(_message.Message):
    __slots__ = ["name", "required", "type"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    required: bool
    type: str
    def __init__(self, name: _Optional[str] = ..., required: bool = ..., type: _Optional[str] = ...) -> None: ...

class TableData(_message.Message):
    __slots__ = ["has_more", "token", "entry"]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    has_more: bool
    token: str
    entry: TableEntry
    def __init__(self, has_more: bool = ..., token: _Optional[str] = ..., entry: _Optional[_Union[TableEntry, _Mapping]] = ...) -> None: ...

class ResponseMetadata(_message.Message):
    __slots__ = ["status_code", "response_id", "response_ts"]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TS_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response_id: str
    response_ts: int
    def __init__(self, status_code: _Optional[int] = ..., response_id: _Optional[str] = ..., response_ts: _Optional[int] = ...) -> None: ...

class PostRunRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class User(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
