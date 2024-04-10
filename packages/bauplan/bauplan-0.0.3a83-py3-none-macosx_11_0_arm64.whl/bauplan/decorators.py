"""

Bauplan functions are normal Python functions enriched by a few key decorators.
This module contains the decorators used to define Bauplan models, expectations and
Python environments, with examples of how to use them.

"""

import functools
from typing import Any, Callable, Dict, List, Optional


def model(
    name: Optional[str] = None,
    columns: Optional[List[str]] = None,
    materialize: Optional[bool] = None,
    internet_access: Optional[bool] = None,
) -> Callable:
    """
    A model is a function from one (or more) dataframe-like object(s)
    to another dataframe-like object: it is used to define a transformation in a
    pipeline. Models are chained together implicitly by using them as inputs to
    their children. A Python model needs a Python environment to run, which is defined
    using the `python` decorator, e.g.:

    .. code-block:: python

        @bauplan.model(
            columns=['*'],
            materialize=False
        )
        @bauplan.python('3.11')
        def source_scan(
            data=bauplan.Model(
                'iot_kaggle',
                columns=['*'],
                filter="motion='false'"
            )
        ):
            # your code here
            return data


    :param name: the name of the model (e.g. 'users'); if missing the function name is used.
    :param columns: the columns of the output dataframe after the model runs (e.g. ['id', 'name', 'email']). Use ['*'] as a wildcard.
    :param materialize: whether the model should be materialized.
    :param internet_access: whether the model requires internet access.
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return f(*args, **kwargs)

        return wrapper

    return decorator


def expectation() -> Callable:
    """
    An expectation is a function from one (or more) dataframe-like object(s) to a boolean: it
    is commonly used to perform data validation and data quality checks when running a pipeline.
    Expectations takes as input the table(s) they are validating and return a boolean indicating
    whether the expectation is met or not. A Python expectation needs a Python environment to run,
    which is defined using the `python` decorator, e.g.:

    .. code-block:: python

        @bauplan.expectation()
        @bauplan.python('3.10')
        def test_joined_dataset(
            data=bauplan.Model(
                'join_dataset',
                columns=['anomaly']
            )
        ):
            # your data validation code here
            return expect_column_no_nulls(data, 'anomaly')

    :param f: The function to decorate.
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return f(*args, **kwargs)

        return wrapper

    return decorator


def synthetic_model(
    name: str,
    columns: List[str],
) -> Callable:
    """
    Define a Bauplan Synthetic Model.

    :meta private:

    :param name: The name of the model. Defaults to the function name.
    :param columns: The columns of the synthetic model (e.g. ``['id', 'name', 'email']``).
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return f(*args, **kwargs)

        return wrapper

    return decorator


def python(
    version: Optional[str] = None,
    pip: Optional[Dict[str, str]] = None,
) -> Callable:
    """
    Define a Python environment for a Bauplan function (e.g. a model or expectation). It is used to
    specify directly in code the configuration of the Python environment required to run the function, i.e.
    the Python version and the Python packages required.

    :param version: The python version for the interpreter (e.g. ``'3.11'``).
    :param pip: A dictionary of dependencies (and versions) required by the function (e.g. ``{'requests': '2.26.0'}``).
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return f(*args, **kwargs)

        return wrapper

    return decorator
