from __future__ import annotations

from contextvars import ContextVar
from types import TracebackType
from typing import Optional, Protocol

_transaction_id_context: ContextVar[Optional[int]] = ContextVar(
    "_transaction_id", default=None
)


def is_inside_transaction() -> bool:
    return _transaction_id_context.get() is not None


class _Start(Protocol):
    def __call__(self, *, scenario_name: str, is_user_initiated: bool) -> int: ...


class _End(Protocol):
    def __call__(self, transaction_id: int, /, *, has_succeeded: bool) -> None: ...


class Transaction:
    _scenario_name: str
    _start: _Start
    _end: _End
    _is_user_initiated: bool = True

    def __init__(
        self,
        scenario_name: str,
        *,
        start: _Start,
        end: _End,
        is_user_initiated: bool = True,
    ):
        self._scenario_name = scenario_name
        self._start = start
        self._end = end
        self._is_user_initiated = is_user_initiated

    def __enter__(self) -> None:
        transaction_id = self._start(
            scenario_name=self._scenario_name, is_user_initiated=self._is_user_initiated
        )
        _transaction_id_context.set(transaction_id)

    def __exit__(  # pylint: disable=too-many-positional-parameters
        self,
        exception_type: Optional[type[BaseException]],
        exception_value: Optional[BaseException],
        exception_traceback: Optional[TracebackType],
    ) -> None:
        transaction_id = _transaction_id_context.get()
        _transaction_id_context.set(None)
        assert transaction_id is not None, "Cannot end transaction without ID."
        self._end(transaction_id, has_succeeded=exception_value is None)
