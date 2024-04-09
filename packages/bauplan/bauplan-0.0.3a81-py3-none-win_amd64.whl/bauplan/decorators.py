import functools
from typing import Any, Callable, Dict, List, Optional


def model(
    name: Optional[str] = None,
    columns: Optional[List[str]] = None,
    materialize: Optional[bool] = None,
    internet_access: Optional[bool] = None,
) -> Callable:
    """
    A Bauplan model is a dataframe-like object representing a "step" in a
    DAG/pipeline. It can be used as inputs and outputs to other steps.

    :param name: the name of the model (e.g. 'users'); if missing the function name is used
    :param columns: the columns of the model (e.g. ['id', 'name', 'email'])
    :param materialize: whether the model should be materialized
    :param internet_access: whether the model requires internet access
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return f(*args, **kwargs)

        return wrapper

    return decorator


def expectation() -> Callable:
    """
    Define a Bauplan Expecation. Expectations are used to validate the data
    in a model.

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
    Define a Bauplan Expecation.

    :param version: The python version required to run the model (e.g. ``'3.11'``).
    :param pip: A list of python dependencies to install into the model function (e.g. ``{'requests': '2.26.0'}``).
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return f(*args, **kwargs)

        return wrapper

    return decorator
