# pylint: disable=missing-function-docstring, missing-class-docstring, missing-module-docstring

from typing import List, Generator, Iterator

import pytest
from fixpoint_sdk.lib.iterwrapper import IterWrapper


def yielder() -> Generator[int, None, None]:
    yield from range(4)


class MyIterWrapper:
    ints: List[int]
    finished: bool
    _iterator: IterWrapper[int]

    def __init__(self) -> None:
        self.ints = []
        self.finished = False

        self._iterator = IterWrapper(
            yielder(),
            on_iter=self.on_iter,
            on_finish=self.on_finish,
            on_error=self.on_error,
        )

    def on_iter(self, val: int) -> None:
        self.ints.append(val)

    def on_finish(self) -> None:
        self.finished = True

    def on_error(self, e: Exception) -> None:
        raise e

    def __next__(self) -> int:
        return self._iterator.__next__()

    def __iter__(self) -> Iterator[int]:
        return self

    @property
    def yieldit(self) -> Iterator[int]:
        # pylint: disable=use-yield-from
        for val in self:
            yield val


def test_plain_iter() -> None:
    myiter = MyIterWrapper()
    vals = []
    for val in myiter:
        vals.append(val)
    assert_iter_correct(vals, myiter)


def test_inner_iter() -> None:
    myiter = MyIterWrapper()
    vals = []
    for val in myiter.yieldit:
        vals.append(val)
    assert_iter_correct(vals, myiter)


def test_intermixed_iterator() -> None:
    myiter = MyIterWrapper()
    vals = []
    vals.append(next(myiter))
    vals.append(next(myiter))
    vals.append(next(myiter.yieldit))
    vals.append(next(myiter))
    assert myiter.finished is False
    with pytest.raises(StopIteration):
        next(myiter)
    assert_iter_correct(vals, myiter)


def assert_iter_correct(vals: List[int], myiter: MyIterWrapper) -> None:
    assert vals == [0, 1, 2, 3]
    assert myiter.ints == [0, 1, 2, 3]
    assert myiter.finished is True
