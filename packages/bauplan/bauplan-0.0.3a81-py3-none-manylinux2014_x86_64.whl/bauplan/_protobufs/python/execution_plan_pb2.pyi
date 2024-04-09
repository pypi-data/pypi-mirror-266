import runner_task_pb2 as _runner_task_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN: _ClassVar[JobStatus]
    PENDING: _ClassVar[JobStatus]
    RUNNING: _ClassVar[JobStatus]
    COMPLETED: _ClassVar[JobStatus]
    FAILED: _ClassVar[JobStatus]
    CANCELED: _ClassVar[JobStatus]
UNKNOWN: JobStatus
PENDING: JobStatus
RUNNING: JobStatus
COMPLETED: JobStatus
FAILED: JobStatus
CANCELED: JobStatus

class JobRequest(_message.Message):
    __slots__ = ["job_data", "detach", "direct_connect_logs", "physical_plan_id", "args", "status", "steps", "scheduled_runner_id"]
    JOB_DATA_FIELD_NUMBER: _ClassVar[int]
    DETACH_FIELD_NUMBER: _ClassVar[int]
    DIRECT_CONNECT_LOGS_FIELD_NUMBER: _ClassVar[int]
    PHYSICAL_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STEPS_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_RUNNER_ID_FIELD_NUMBER: _ClassVar[int]
    job_data: str
    detach: bool
    direct_connect_logs: bool
    physical_plan_id: str
    args: _containers.RepeatedCompositeFieldContainer[JobArg]
    status: JobStatus
    steps: _containers.RepeatedCompositeFieldContainer[Step]
    scheduled_runner_id: str
    def __init__(self, job_data: _Optional[str] = ..., detach: bool = ..., direct_connect_logs: bool = ..., physical_plan_id: _Optional[str] = ..., args: _Optional[_Iterable[_Union[JobArg, _Mapping]]] = ..., status: _Optional[_Union[JobStatus, str]] = ..., steps: _Optional[_Iterable[_Union[Step, _Mapping]]] = ..., scheduled_runner_id: _Optional[str] = ...) -> None: ...

class JobArg(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class Step(_message.Message):
    __slots__ = ["id", "task", "invokable", "run_after", "log_group_id", "run_if", "run_when", "name", "exit_codes"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    INVOKABLE_FIELD_NUMBER: _ClassVar[int]
    RUN_AFTER_FIELD_NUMBER: _ClassVar[int]
    LOG_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_IF_FIELD_NUMBER: _ClassVar[int]
    RUN_WHEN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXIT_CODES_FIELD_NUMBER: _ClassVar[int]
    id: str
    task: _runner_task_pb2.Task
    invokable: bool
    run_after: _containers.RepeatedScalarFieldContainer[str]
    log_group_id: str
    run_if: str
    run_when: str
    name: str
    exit_codes: _containers.RepeatedCompositeFieldContainer[_runner_task_pb2.TaskExitCode]
    def __init__(self, id: _Optional[str] = ..., task: _Optional[_Union[_runner_task_pb2.Task, _Mapping]] = ..., invokable: bool = ..., run_after: _Optional[_Iterable[str]] = ..., log_group_id: _Optional[str] = ..., run_if: _Optional[str] = ..., run_when: _Optional[str] = ..., name: _Optional[str] = ..., exit_codes: _Optional[_Iterable[_Union[_runner_task_pb2.TaskExitCode, _Mapping]]] = ...) -> None: ...
