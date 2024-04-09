from typing import Any, Dict

from ._common import (
    get_commander_and_metadata,
)
from ._protobufs.bauplan_pb2 import (
    DeleteBranchRequest,
    GetBranchesRequest,
    GetBranchRequest,
    GetTableRequest,
)


def get_branches() -> Dict[str, Any]:
    """
    Get the branches from the server.

    :return: A dictionary containing the branches.
    """
    client, metadata = get_commander_and_metadata()

    response = client.GetBranches(GetBranchesRequest(), metadata=metadata)
    return response.data.branches


def get_branch(branch_name: str) -> Dict[str, Any]:
    """
    Get the branch with the specified name.

    :param branch_name: The name of the branch to retrieve.
    :return: A dictionary containing the branch data.
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


def get_table(branch_name: str, table_name: str) -> Dict[str, Any]:
    """
    Get the table data for a given branch and table name.

    :param branch_name: The name of the branch to get tables from.
    :param table_name: The table name to retrieve.
    :return: A dictionary containing the table data.
    """
    client, metadata = get_commander_and_metadata()

    response = client.GetTable(
        GetTableRequest(branch_name=branch_name, table_name=table_name),
        metadata=metadata,
    )
    return response.data.entry.fields
