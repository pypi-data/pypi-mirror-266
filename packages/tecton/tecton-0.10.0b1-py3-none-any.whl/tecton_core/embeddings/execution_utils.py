from __future__ import annotations

import sys
import traceback
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Mapping
from typing import Union

import pyarrow as pa
import pyarrow.parquet


if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

if sys.version_info >= (3, 10):
    from typing import Concatenate
    from typing import ParamSpec
else:
    from typing_extensions import Concatenate
    from typing_extensions import ParamSpec


# NOTE [ Python Traceback Reference Cycle Problem ]
#
# When using sys.exc_info(), it is important to **not** store the exc_info[2],
# which is the traceback, because otherwise you will run into the traceback
# reference cycle problem, i.e., the traceback holding reference to the frame,
# and the frame (which holds reference to all the object in its temporary scope)
# holding reference the traceback.
#  https://github.com/python/cpython/issues/75188


class KeyErrorMessage(str):
    r"""str subclass that returns itself in repr"""

    def __repr__(self):
        return self


class ExceptionWrapper:
    """Wraps an exception and traceback for exception handling in a multi-threaded execution setting."""

    def __init__(self, exc_info=None, where="in background"):
        # It is important that we don't store exc_info, see
        # NOTE [ Python Traceback Reference Cycle Problem ]
        if exc_info is None:
            exc_info = sys.exc_info()
        self.exc_type = exc_info[0]
        self.exc_msg = "".join(traceback.format_exception(*exc_info))
        self.where = where

    def reraise(self):
        r"""Reraises the wrapped exception in the current thread"""
        # Format a message such as: "Caught ValueError in DataLoader worker
        # process 2. Original Traceback:", followed by the traceback.
        msg = f"Caught {self.exc_type.__name__} {self.where}.\nOriginal {self.exc_msg}"
        if self.exc_type == KeyError:
            # KeyError calls repr() on its argument (usually a dict key). This
            # makes stack traces unreadable. It will not be changed in Python
            # (https://github.com/python/cpython/issues/46903), so we work around it.
            msg = KeyErrorMessage(msg)
        elif getattr(self.exc_type, "message", None):
            # Some exceptions have first argument as non-str but explicitly
            # have message field
            raise self.exc_type(message=msg)
        try:
            exception = self.exc_type(msg)
        except TypeError:
            # If the exception takes multiple arguments, don't try to
            # instantiate since we don't know how to
            raise RuntimeError(msg) from None
        raise exception


Item = Union[pa.RecordBatch, ExceptionWrapper]
P = ParamSpec("P")
PreprocessorCallable = Callable[Concatenate[Item, P], Iterable[Item]]
ModelCallable = Callable[Concatenate[Item, P], Item]


def data_preprocessor_one_step(item: Item, func: PreprocessorCallable, func_kwargs: P.kwargs) -> Iterable[Item]:
    if isinstance(item, ExceptionWrapper):
        return (item,)

    try:
        return func(item, **func_kwargs)
    except Exception:
        return (ExceptionWrapper(where="in data preprocessor"),)


def model_inference_one_step(item: Item, func: ModelCallable, func_kwargs: P.kwargs) -> Item:
    if isinstance(item, ExceptionWrapper):
        return item

    try:
        return func(item, **func_kwargs)
    except Exception:
        return ExceptionWrapper(where="in model inference")


class FuncConfig(Protocol):
    def load(self) -> FuncConfig: ...

    def kwargs(self) -> Mapping[str, Any]: ...
