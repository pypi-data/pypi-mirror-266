"""Code for wrapping iterators."""

from typing import Callable, Generic, Iterator, TypeVar


_T = TypeVar("_T")


class IterWrapper(Generic[_T]):
    """Wraps an iterator with callbacks."""

    _iterator: Iterator[_T]
    _on_iter: Callable[[_T], None]
    _on_finish: Callable[[], None]
    _on_error: Callable[[Exception], None]

    def __init__(
        self,
        iterator: Iterator[_T],
        *,
        on_iter: Callable[[_T], None],
        on_finish: Callable[[], None],
        on_error: Callable[[Exception], None],
    ):
        self._iterator = iterator
        self._on_iter = on_iter
        self._on_finish = on_finish
        self._on_error = on_error

    def __next__(self) -> _T:
        try:
            val = self._iterator.__next__()
            self._on_iter(val)
            return val
        except StopIteration:
            self._on_finish()
            raise
        except Exception as e:
            self._on_error(e)
            raise

    def __iter__(self) -> Iterator[_T]:
        return self
