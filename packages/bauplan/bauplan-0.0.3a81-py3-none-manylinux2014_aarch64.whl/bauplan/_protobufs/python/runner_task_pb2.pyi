from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Mount(_message.Message):
    __slots__ = ["source_object_path", "source_object_id", "source_content", "target", "mode", "lifecycle"]
    SOURCE_OBJECT_PATH_FIELD_NUMBER: _ClassVar[int]
    SOURCE_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    LIFECYCLE_FIELD_NUMBER: _ClassVar[int]
    source_object_path: str
    source_object_id: str
    source_content: str
    target: str
    mode: str
    lifecycle: str
    def __init__(self, source_object_path: _Optional[str] = ..., source_object_id: _Optional[str] = ..., source_content: _Optional[str] = ..., target: _Optional[str] = ..., mode: _Optional[str] = ..., lifecycle: _Optional[str] = ...) -> None: ...

class Env(_message.Message):
    __slots__ = ["name", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class Port(_message.Message):
    __slots__ = ["port"]
    PORT_FIELD_NUMBER: _ClassVar[int]
    port: int
    def __init__(self, port: _Optional[int] = ...) -> None: ...

class LogGroup(_message.Message):
    __slots__ = ["id", "parent_id", "name"]
    ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    parent_id: str
    name: str
    def __init__(self, id: _Optional[str] = ..., parent_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class TaskInputModel(_message.Message):
    __slots__ = ["id", "source_task_id", "table_name", "file_format"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    FILE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    id: str
    source_task_id: str
    table_name: str
    file_format: str
    def __init__(self, id: _Optional[str] = ..., source_task_id: _Optional[str] = ..., table_name: _Optional[str] = ..., file_format: _Optional[str] = ...) -> None: ...

class TaskOutputModel(_message.Message):
    __slots__ = ["id", "source_task_id", "table_name", "file_format"]
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    FILE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    id: str
    source_task_id: str
    table_name: str
    file_format: str
    def __init__(self, id: _Optional[str] = ..., source_task_id: _Optional[str] = ..., table_name: _Optional[str] = ..., file_format: _Optional[str] = ...) -> None: ...

class TaskMetadata(_message.Message):
    __slots__ = ["level", "human_readable_task_type", "task_type", "function_name", "line_number", "file_name", "model_name"]
    class TaskLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        DAG: _ClassVar[TaskMetadata.TaskLevel]
        SYSTEM: _ClassVar[TaskMetadata.TaskLevel]
    DAG: TaskMetadata.TaskLevel
    SYSTEM: TaskMetadata.TaskLevel
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    HUMAN_READABLE_TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    LINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    level: TaskMetadata.TaskLevel
    human_readable_task_type: str
    task_type: str
    function_name: str
    line_number: int
    file_name: str
    model_name: str
    def __init__(self, level: _Optional[_Union[TaskMetadata.TaskLevel, str]] = ..., human_readable_task_type: _Optional[str] = ..., task_type: _Optional[str] = ..., function_name: _Optional[str] = ..., line_number: _Optional[int] = ..., file_name: _Optional[str] = ..., model_name: _Optional[str] = ...) -> None: ...

class TaskExitCode(_message.Message):
    __slots__ = ["code", "fatal", "description"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    FATAL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    code: int
    fatal: bool
    description: str
    def __init__(self, code: _Optional[int] = ..., fatal: bool = ..., description: _Optional[str] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ["type", "region", "bucket_name", "object_key", "hash", "name", "image_id", "image_name", "input_model_ids", "model_name", "input_data", "command", "mounts", "envs", "ports", "isolated_network", "can_invoce", "workdir", "network", "metadata", "input_models", "output_models"]
    class InputDataEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    BUCKET_NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_KEY_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_MODEL_IDS_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    INPUT_DATA_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    MOUNTS_FIELD_NUMBER: _ClassVar[int]
    ENVS_FIELD_NUMBER: _ClassVar[int]
    PORTS_FIELD_NUMBER: _ClassVar[int]
    ISOLATED_NETWORK_FIELD_NUMBER: _ClassVar[int]
    CAN_INVOCE_FIELD_NUMBER: _ClassVar[int]
    WORKDIR_FIELD_NUMBER: _ClassVar[int]
    NETWORK_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    INPUT_MODELS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_MODELS_FIELD_NUMBER: _ClassVar[int]
    type: str
    region: str
    bucket_name: str
    object_key: str
    hash: str
    name: str
    image_id: str
    image_name: str
    input_model_ids: _containers.RepeatedScalarFieldContainer[str]
    model_name: str
    input_data: _containers.ScalarMap[str, str]
    command: _containers.RepeatedScalarFieldContainer[str]
    mounts: _containers.RepeatedCompositeFieldContainer[Mount]
    envs: _containers.RepeatedCompositeFieldContainer[Env]
    ports: _containers.RepeatedCompositeFieldContainer[Port]
    isolated_network: bool
    can_invoce: _containers.RepeatedScalarFieldContainer[str]
    workdir: str
    network: str
    metadata: TaskMetadata
    input_models: _containers.RepeatedCompositeFieldContainer[TaskInputModel]
    output_models: _containers.RepeatedCompositeFieldContainer[TaskOutputModel]
    def __init__(self, type: _Optional[str] = ..., region: _Optional[str] = ..., bucket_name: _Optional[str] = ..., object_key: _Optional[str] = ..., hash: _Optional[str] = ..., name: _Optional[str] = ..., image_id: _Optional[str] = ..., image_name: _Optional[str] = ..., input_model_ids: _Optional[_Iterable[str]] = ..., model_name: _Optional[str] = ..., input_data: _Optional[_Mapping[str, str]] = ..., command: _Optional[_Iterable[str]] = ..., mounts: _Optional[_Iterable[_Union[Mount, _Mapping]]] = ..., envs: _Optional[_Iterable[_Union[Env, _Mapping]]] = ..., ports: _Optional[_Iterable[_Union[Port, _Mapping]]] = ..., isolated_network: bool = ..., can_invoce: _Optional[_Iterable[str]] = ..., workdir: _Optional[str] = ..., network: _Optional[str] = ..., metadata: _Optional[_Union[TaskMetadata, _Mapping]] = ..., input_models: _Optional[_Iterable[_Union[TaskInputModel, _Mapping]]] = ..., output_models: _Optional[_Iterable[_Union[TaskOutputModel, _Mapping]]] = ...) -> None: ...
