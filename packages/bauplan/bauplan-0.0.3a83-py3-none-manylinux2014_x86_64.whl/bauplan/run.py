import io
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import grpc
import pkg_resources

from ._common import (
    get_commander_and_metadata,
)
from ._protobufs.bauplan_pb2 import (
    RunnerInfo,
    RunnerInfoType,
    RunnerLog,
    TaskLifecycleEvent,
    TaskLifecycleType,
    TriggerRunRequest,
)

JOB_STATUS_FAILED = 'FAILED'
JOB_STATUS_SUCCESS = 'SUCCESS'
JOB_STATUS_CANCELLED = 'CANCELLED'


class RunState:
    """
    RunState tracks information about what happened during the course of a Bauplan
    job run (executed DAG).

    It represents the state of a run, including job ID, task lifecycle events, user logs,
    task start and stop times, failed nonfatal task descriptions, project directory,
    job status, and failed fatal task description.
    """

    job_id: str
    task_lifecycle_events: List[TaskLifecycleEvent]
    user_logs: List[RunnerLog]
    tasks_started: Dict[str, datetime]
    tasks_stopped: Dict[str, datetime]
    failed_nonfatal_task_descriptions: Dict[str, bool]
    project_dir: str
    job_status: Optional[str]
    failed_fatal_task_description: Optional[str]

    def __init__(
        self,
        job_id: str,
        project_dir: str,
    ) -> None:
        self.job_id = job_id
        self.task_lifecycle_events = []
        self.user_logs = []
        self.tasks_started = {}
        self.tasks_stopped = {}
        self.failed_nonfatal_task_descriptions = {}
        self.project_dir = project_dir
        self.job_status = None
        self.failed_fatal_task_description = None


def run(
    project_dir: str,
    id: Optional[str] = None,
    materialize: Optional[str] = None,
    output: Optional[str] = None,
    branch_prefix: Optional[str] = None,
    args: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Union[str, int, float, bool]]] = None,
) -> RunState:
    """
    Run a Bauplan project and return the state of the run. This is the equivalent of
    running through the CLI the ``bauplan run`` command.

    :param project_dir: The directory of the project (where the ``bauplan_project.yml`` file is located).
    :param id: The ID of the run (optional). This can be used to re-run a previous run, e.g., on a different branch.
    :param materialize: The materialization mode (optional).
    :param output: The output directory (optional).
    :param branch_prefix: The branch prefix (optional).
    :param args: Additional arguments (optional).
    :param parameters: Parameters for templating into SQL or Python models.
    :return: The state of the run.
    """
    if parameters is None:
        parameters = {}
    trigger_run_request = _create_trigger_run_request(
        project_dir, id, materialize, branch_prefix, args, parameters
    )
    client, metadata = get_commander_and_metadata()
    job_id = client.TriggerRun(trigger_run_request, metadata=metadata)
    log_stream: grpc.Call = client.SubscribeLogs(job_id, metadata=metadata)
    run_state = _create_run_state(job_id, project_dir)
    _process_logs(log_stream, run_state)
    return run_state


def _upload_files(
    project_dir: str, temp_dir: str, parameters: Dict[str, Union[str, int, float, bool]]
) -> List[str]:
    upload_files = []

    for file in os.listdir(project_dir):
        if file.endswith(('.py', '.sql', 'requirements.txt', 'bauplan_project.yml')):
            src_path = os.path.join(project_dir, file)
            dst_path = os.path.join(temp_dir, file)
            shutil.copy(src_path, dst_path)
            upload_files.append(dst_path)

    if 'bauplan_project.yml' not in [os.path.basename(file) for file in upload_files]:
        raise Exception('bauplan_project.yml not found in project directory.')

    parameter_entries = [f"    '{key}': {_python_code_str(value)}," for key, value in parameters.items()]
    parameter_entries_str = '\n'.join(parameter_entries)
    internal_py_content = f"""
_user_params = {{
{parameter_entries_str}
}}
"""

    internal_py_path = os.path.join(temp_dir, '_internal.py')
    with open(internal_py_path, 'w') as internal_py_file:
        internal_py_file.write(internal_py_content)

    upload_files.append(internal_py_path)

    return upload_files


def _create_trigger_run_request(
    project_dir: str,
    id: str,
    materialize: Optional[str],
    branch_prefix: Optional[str],
    args: Optional[Dict[str, Any]],
    parameters: Dict[str, Union[str, int, float, bool]],
) -> TriggerRunRequest:
    trigger_run_request = TriggerRunRequest(
        module_version=pkg_resources.get_distribution('bauplan').version,
        args=args or {},
    )
    if id:
        trigger_run_request.run_id = id
    if materialize:
        branch_name = materialize
        if branch_prefix and not branch_name.startswith(branch_prefix):
            branch_name = f'{branch_prefix}.{branch_name}'
        trigger_run_request.args['write-branch'] = branch_name

    with tempfile.TemporaryDirectory() as temp_dir:
        upload_files = _upload_files(project_dir, temp_dir, parameters)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in upload_files:
                zipf.write(file, os.path.basename(file))

    trigger_run_request.zip_file = zip_buffer.getvalue()
    trigger_run_request.client_hostname = os.uname().nodename

    return trigger_run_request


def _python_code_str(value: Any) -> str:
    if isinstance(value, str):
        return f"'{value}'"
    if isinstance(value, bool):
        return str(value)
    return repr(value)


def _create_run_state(job_id: str, project_dir: str) -> RunState:
    return RunState(
        job_id=job_id,
        project_dir=project_dir,
    )


def _process_logs(log_stream: grpc.Call, run_state: RunState) -> None:
    for log in log_stream:
        if os.getenv('BPLN_DEBUG'):
            print(log)
        if _handle_log(log, run_state):
            break


def _handle_log(log: RunnerInfo, run_state: RunState) -> bool:
    if log.info_type == RunnerInfoType.JOB_COMPLETE:
        run_state.job_status = JOB_STATUS_SUCCESS
        return True
    if log.info_type == RunnerInfoType.JOB_RUNNER_TELEMETRY:
        lifecycle_event = log.task_lifecycle_event
        run_state.task_lifecycle_events.append(lifecycle_event)
        task_description = lifecycle_event.task_description
        lifecycle_type = lifecycle_event.lifecycle_type
        if lifecycle_type == TaskLifecycleType.TASK_STARTED:
            run_state.tasks_started[task_description] = datetime.now()
        if (
            lifecycle_type == TaskLifecycleType.TASK_FINISHED_SUCCESS
            and lifecycle_event.task_metadata.task_type != 'PIP_INSTALL'
        ):
            run_state.tasks_stopped[task_description] = datetime.now()
        if lifecycle_type == TaskLifecycleType.TASK_FINISHED_FAILURE:
            run_state.failed_fatal_task_description = task_description
            run_state.job_status = JOB_STATUS_FAILED
            return True
        else:  # noqa: RET505
            # TODO: Hitting some proto issues with TASK_FINISHED_FAILURE_NONFATAL,
            # need to fix some day (something weird happening)
            run_state.failed_nonfatal_task_descriptions[task_description] = True
    elif log.info_type == RunnerInfoType.JOB_USER_LOG:
        if log.runner_log:
            run_state.user_logs.append(log.runner_log)
    return False
