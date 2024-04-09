import json
import os
from datetime import datetime
from typing import Any, Dict, Generator, Optional

import grpc
import pyarrow.flight

from ._common import (
    get_commander_and_metadata,
)
from ._protobufs.bauplan_pb2 import TriggerRunRequest


def query(
    query: str,
    max_rows: int = 10,
    no_cache: bool = False,
    branch: str = 'main',
    args: Optional[Dict[str, Any]] = None,
) -> Optional[pyarrow.flight.FlightStreamReader]:
    """
    Execute a Bauplan query and return the results as a FlightStreamReader.

    :param query: The Bauplan query to execute.
    :param max_rows: The maximum number of rows to return (default: ``10``).
    :param no_cache: Whether to disable caching for the query (default: ``False``).
    :param branch: The branch to read from (default: 'main').
    :param args: Additional arguments to pass to the query (default: None).
    :return: The ``FlightStreamReader`` containing the query results, or None if no results found.
    """

    trigger_run_request: TriggerRunRequest = TriggerRunRequest(
        module_version='0.0.1',
        args=args or {},
        query_for_flight=query,
        is_flight_query=True,
    )

    if no_cache:
        trigger_run_request.args['runner-cache'] = 'off'

    if branch:
        trigger_run_request.args['read-branch'] = branch

    client, metadata = get_commander_and_metadata()

    job_id: TriggerRunRequest = client.TriggerRun(trigger_run_request, metadata=metadata)

    log_stream: grpc.Call = client.SubscribeLogs(job_id, metadata=metadata)

    flight_endpoint: Optional[str] = None
    for log in log_stream:
        if os.getenv('BPLN_DEBUG'):
            print(log)
        if log.task_lifecycle_event.flight_endpoint:
            flight_endpoint = log.task_lifecycle_event.flight_endpoint
            break

    if not flight_endpoint:
        return None

    flight_client: pyarrow.flight.FlightClient = pyarrow.flight.FlightClient('grpc://' + flight_endpoint)
    options: pyarrow.flight.FlightCallOptions = pyarrow.flight.FlightCallOptions(
        headers=[(b'authorization', 'Bearer my_special_token'.encode())]
    )
    ticket: pyarrow.flight.Ticket = (
        next(
            flight_client.list_flights(
                options=options,
            )
        )
        .endpoints[0]
        .ticket
    )
    reader: pyarrow.flight.FlightStreamReader = flight_client.do_get(
        ticket,
        options=options,
    )
    return reader


def query_to_arrow(*args: Any, **kwargs: Any) -> pyarrow.Table:
    """
    Execute a Bauplan query and return the results as a ``pyarrow.Table``.

    :param args: Arguments to pass to the query function.
    :param kwargs: Keyword arguments to pass to the query function.
    :return: The query results as a ``pyarrow.Table``.
    """
    reader: pyarrow.flight.FlightStreamReader = query(*args, **kwargs)
    if reader is None:
        raise ValueError('No results found')
    return reader.read_all()


def query_to_generator(*args: Any, **kwargs: Any) -> Generator[Dict[str, Any], None, None]:
    """
    Execute a Bauplan query and return the results as a generator of dictionaries.

    :param args: Arguments to pass to the query function.
    :param kwargs: Keyword arguments to pass to the query function.
    :yield: A dictionary representing a row of query results.
    """
    reader: pyarrow.flight.FlightStreamReader = query(*args, **kwargs)
    if reader is None:
        raise ValueError('No results found')
    while True:
        try:
            if reader is None:
                raise ValueError('No results found')
            chunk: Optional[pyarrow.lib.RecordBatch] = reader.read_chunk()
            if chunk is not None:
                batch: pyarrow.lib.RecordBatch = chunk.data
                schema: pyarrow.lib.Schema = batch.schema
                for i in range(batch.num_rows):
                    yield row_to_dict(batch, i, schema)
            else:
                break
        except StopIteration:
            break


def row_to_dict(
    batch: pyarrow.lib.RecordBatch,
    row_index: int,
    schema: pyarrow.lib.Schema,
) -> Dict[str, Any]:
    """
    Convert a row of a ``pyarrow.RecordBatch`` to a dictionary.

    :param batch: The ``pyarrow.RecordBatch`` containing the row.
    :param row_index: The index of the row to convert.
    :param schema: The schema of the ``RecordBatch``.
    :return: A dictionary representing the row.
    """
    row: Dict[str, Any] = {}
    for j, name in enumerate(schema.names):
        column: pyarrow.lib.ChunkedArray = batch.column(j)
        value = column[row_index].as_py()
        if isinstance(value, datetime):
            value = value.isoformat()
        row[name] = value
    return row


def query_to_file(filename: str, *args: Any, **kwargs: Any) -> None:
    """
    Execute a Bauplan query and write the results to a file.

    :param filename: The name of the file to write the results to.
    :param args: Arguments to pass to the query function.
    :param kwargs: Keyword arguments to pass to the query function.
    """
    if filename.endswith('.json'):
        with open(filename, 'w') as outfile:
            outfile.write('[\n')
            first_row: bool = True
            for row in query_to_generator(*args, **kwargs):
                if not first_row:
                    outfile.write(',\n')
                    first_row = False
                outfile.write(json.dumps(row))
            outfile.write('\n]')
    else:
        raise ValueError('Only .json extension is supported for filename')
