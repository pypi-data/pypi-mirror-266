import sys

if sys.version_info[:2] >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from .classes import Model
from .decorators import (
    expectation,
    model,
    python,
    synthetic_model,
)
from .parameters import Parameter
from .store import load_obj, save_obj

__version__ = metadata.version(__package__ or 'bauplan')

del metadata

__all__ = [
    'Model',
    'Parameter',
    '__version__',
    'expectation',
    'load_obj',
    'model',
    'python',
    'query',
    'query_to_arrow',
    'query_to_file',
    'query_to_generator',
    'query_to_pandas',
    'run',
    'save_obj',
    'standard_expectations',
    'synthetic_model',
]
