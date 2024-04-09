from typing import Any


# Exceptions raised during loading of object
class UserObjectKeyNotExistsError(Exception):
    pass


class MismatchedPythonVersionsError(Exception):
    pass


# Exceptions raised during saving object
class UserObjectWithKeyExistsError(Exception):
    pass


class ObjectTooBigError(Exception):
    pass


class ObjectCannotBeSerializedError(Exception):
    pass


class UnhandledRuntimeError(Exception):
    pass


def load_obj(key: str) -> Any:
    from ._runtime_private._store import load_obj

    try:
        return load_obj(key)
    except Exception as e:
        if e.__class__.__name__ == 'UserObjectWithKeyExistsError':
            raise UserObjectKeyNotExistsError(str(e)) from e

        if e.__class__.__name__ == 'MismatchedPythonVersionsError':
            raise MismatchedPythonVersionsError(str(e)) from e

        raise UnhandledRuntimeError(str(e)) from e


def save_obj(key: str, obj: Any) -> None:
    from ._runtime_private._store import save_obj

    try:
        save_obj(key, obj)
    except Exception as e:
        if e.__class__.__name__ == 'ObjectTooBigError':
            raise ObjectTooBigError(str(e)) from e

        if e.__class__.__name__ == 'ObjectCannotBeSerializedError':
            raise ObjectCannotBeSerializedError(str(e)) from e

        if e.__class__.__name__ == 'UserObjectWithKeyExistsError':
            raise UserObjectWithKeyExistsError(str(e)) from e

        raise UnhandledRuntimeError(str(e)) from e
