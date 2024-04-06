"""Utilities for debugging."""

from dataclasses import dataclass
import functools
import os
import typing
from typing import Callable, TypeVar
from typing_extensions import ParamSpec

from .logging import logger


def _is_debug_mode() -> bool:
    debugmode = os.environ.get("DEBUG", "off").lower()
    return debugmode in ["on", "true", "1"]


def dprint(*args: typing.Any, **kwargs: typing.Any) -> None:
    """Prints only if debug mode is on."""
    if not _is_debug_mode():
        return
    logger.debug(*args, **kwargs)


P = ParamSpec("P")
T = TypeVar("T")


class FnIODict(typing.TypedDict):
    """A dictionary representation of a function call."""

    name: str
    args: typing.List[str]
    kwargs: typing.Dict[str, str]
    output: str


@dataclass
class FnIO:
    """Store the text representation of a function call."""

    name: str
    args: typing.List[str]
    kwargs: typing.Dict[str, str]
    output: str

    def to_dict(self) -> FnIODict:
        """Converts the object to a dictionary."""
        return {
            "name": self.name,
            "args": self.args,
            "kwargs": self.kwargs,
            "output": self.output,
        }

    def log(self) -> None:
        """Prints a text representation of the FnIO object."""
        logger.info(self.to_dict())


def debug_log_function_io(func: Callable[P, T]) -> Callable[P, T]:
    """Logs the input and output of a function, only if debug mode is on."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if not _is_debug_mode():
            return func(*args, **kwargs)
        return _log_fn_io(func, *args, **kwargs)

    return wrapper


def log_function_io(func: Callable[P, T]) -> Callable[P, T]:
    """Logs the input and output of a function."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return _log_fn_io(func, *args, **kwargs)

    return wrapper


def _log_fn_io(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    args_repr = [repr(a) for a in args]
    kwargs_repr = {k: repr(v) for k, v in kwargs.items()}
    out = func(*args, **kwargs)
    out_repr = repr(out)
    fnio = FnIO(name=func.__name__, args=args_repr, kwargs=kwargs_repr, output=out_repr)
    fnio.log()
    return out
