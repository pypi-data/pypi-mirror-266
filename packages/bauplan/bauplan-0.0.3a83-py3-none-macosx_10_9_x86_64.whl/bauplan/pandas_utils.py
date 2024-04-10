"""
The Bauplan module does not come with pandas, but it can be used with pandas
workflows if pandas is installed.

This module provides a few utility functions that can be used to run SQL queries against
a Bauplan instance, and to visualize the results in a Python notebook through a magic cell syntax.
"""

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable

import pyarrow

if TYPE_CHECKING:
    from pandas import DataFrame

from .query import query

"""
_INTERNALNOTE: if you add a function here, you must also wrap it with the pandas_import_checker
decorator to make sure we gracefully handle the case where pandas is not installed.
"""

# Utility decorator ####


class MissingPandasError(Exception):
    """
    :meta private:
    """

    def __init__(self) -> None:
        super().__init__('Pandas is not installed. Please do `pip3 install pandas` to resolve this error.')


class MissingMagicCellError(Exception):
    """
    :meta private:
    """

    def __init__(self) -> None:
        super().__init__(
            '`from IPython.core.magic import register_cell_magic` failed: are you in a Python notebook context? You can do `pip3 install jupyterlab` to resolve this error.'
        )


def pandas_import_checker(f: Callable) -> Callable:
    """
    Decorator checks if pandas is installed before running the function.

    The user may have already pandas installed, so we don't bundle it
    with our SDK - however, if they don't have it, we should let them know
    that conversion to pandas object will not work!

    :meta private:
    """

    @wraps(f)
    def wrapped(*args, **kwargs) -> Any:
        # try import pandas first
        try:
            import pandas  # noqa
        except ModuleNotFoundError:
            raise MissingPandasError from None
        # if pandas can be imported, run the function
        return f(*args, **kwargs)

    return wrapped


def magic_cell_import_checker(f: Callable) -> Callable:
    """
    Decorator replace the proper magic cell import with a dummy function if the magic cell
    import failed at import time.

    :meta private:
    """

    @wraps(f)
    def wrapped(*args, **kwargs) -> None:
        raise MissingMagicCellError from None

    return wrapped


# Pandas-specific functions ####


@pandas_import_checker
def query_to_pandas(*args, **kwargs) -> 'DataFrame':
    """
    Run a SQL query on Bauplan and return the results as a pandas DataFrame.

    .. code-block:: python

        from bauplan.pandas_utils import query_to_pandas
        # run a query over the main branch and return the results as a DataFrame
        df = query_to_pandas('SELECT c1 FROM my_table', branch='main')

    :param args: The arguments to pass to the query function.
    :param kwargs: The keyword arguments to pass to the query function.
    :return: A pandas DataFrame object containing the results of the query.
    """
    reader: pyarrow.flight.FlightStreamReader = query(*args, **kwargs)
    if reader is None:
        raise ValueError('No results found')
    return reader.read_pandas()


# Notebook-specific functions ####


def in_notebook() -> bool:
    """
    Return True if we are in a notebook context, False otherwise.

    From: https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook

    :meta private:
    """
    try:
        from IPython import get_ipython

        if 'IPKernelApp' not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


# we try and import the magic cell first
try:
    # check if we are in a notebook context
    if not in_notebook():
        raise ModuleNotFoundError

    from IPython.core.magic import register_cell_magic

except ModuleNotFoundError:
    # if it fails, we replace the magic cell import with a dummy function
    register_cell_magic = magic_cell_import_checker


@register_cell_magic
def bauplan_sql(line: int, cell: str) -> 'DataFrame':
    """
    This function is a magic cell that allows users to run SQL queries on Bauplan
    directly in a Python notebook cell - optionally, the branch can be specified
    next to the magic command, e.g.:

    .. code-block:: sql

        %%bauplan_sql main

        SELECT c1 FROM t2 WHERE f=1

    The result of the query will be returned as a pandas DataFrame object, which gets
    nicely visualized in a Python notebook by default.

    This function is not intended to be called directly, but rather used as a magic cell.

    """

    target_branch = line if line is not None else 'main'
    query = cell.strip()
    return query_to_pandas(query, branch=target_branch).head()
