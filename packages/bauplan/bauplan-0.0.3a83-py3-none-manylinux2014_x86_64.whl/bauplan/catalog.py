from typing import Any, List

from ._common import (
    get_commander_and_metadata,
)
from ._protobufs.bauplan_pb2 import (
    Branch,
    DeleteBranchRequest,
    GetBranchesRequest,
    GetBranchRequest,
    GetTableRequest,
    TableField,
)


def get_branches() -> List[Branch]:
    """
    Get the available data branches in the Bauplan catalog.

    .. code-block:: python

        from bauplan.catalog import get_branches
        branch_names = [branch.name for branch in get_branches()]

    :return: a list of branches, each having "name", "hash", "user", "data_name"
    """
    client, metadata = get_commander_and_metadata()

    response = client.GetBranches(GetBranchesRequest(), metadata=metadata)
    return response.data.branches


def get_branch(branch_name: str) -> List[Any]:
    """
    Get the tables and views in the target branch.

    .. code-block:: python

        from bauplan.catalog import get_branch
        # retrieve only the tables as tuples of (name, kind)
        tables = [(b.name, b.kind) for b in get_branch('main') if b.kind == 'TABLE']

    :param branch_name: The name of the branch to retrieve.
    :return: A list of tables, each having "name", "kind" (e.g. TABLE)
    """
    client, metadata = get_commander_and_metadata()

    response = client.GetBranch(GetBranchRequest(branch_name=branch_name), metadata=metadata)
    return response.data.entries


def delete_branch(branch_name: str) -> None:
    """
    Delete a branch.

    :param branch_name: The name of the branch to delete.
    """
    client, metadata = get_commander_and_metadata()

    client.DeleteBranch(DeleteBranchRequest(branch_name=branch_name), metadata=metadata)


def get_table(branch_name: str, table_name: str) -> list[TableField]:
    """
    Get the table metadata for a table in the target branch.

    .. code-block:: python

        from bauplan.catalog import get_table
        # get the fields and metadata for the taxi_zones table in the main branch
        cnt_f = get_table(branch_name='main', table_name='taxi_zones')
        # loop through the fields and print their name, required, and type
        for c in cnt_f:
            print(c.name, c.required, c.type)

    :param branch_name: The name of the branch to get the table from.
    :param table_name: The name of the table to retrieve.
    :return: a list of fields, each having "name", "required", "type"
    """
    client, metadata = get_commander_and_metadata()

    response = client.GetTable(
        GetTableRequest(branch_name=branch_name, table_name=table_name),
        metadata=metadata,
    )
    return response.data.entry.fields
