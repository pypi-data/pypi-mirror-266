from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import timedelta
from functools import cache
from typing import NoReturn
from urllib.request import (
    AbstractHTTPHandler,
    BaseHandler,
    OpenerDirector,
    Request,
    build_opener,
)

from atoti_core import fetch_json, get_env_flag

from .event import Event

_TELEMETRY_SERVICE_URL = "https://telemetry.atoti.io/events"
_TEST_TELEMETRY_ENV_VAR_NAME = "_ATOTI_TEST_TELEMETRY"
_TIMEOUT = timedelta(seconds=5)


@cache
def _get_executor() -> Executor:
    # Sending events in the background to not bother the user.
    return ThreadPoolExecutor(max_workers=1)


class _TestHandler(AbstractHTTPHandler):
    def _handle_request(self, request: Request) -> NoReturn:
        assert isinstance(request.data, bytes)
        print(request.data.decode("utf8"))  # noqa: T201
        raise AssertionError("This handler cancels the request.")

    http_request = _handle_request
    https_request = _handle_request


@cache
def _get_opener_director() -> OpenerDirector:
    handlers: list[BaseHandler] = []

    # Branching off at the last moment to keep the test behavior as close as possible to the regular one.
    if get_env_flag(_TEST_TELEMETRY_ENV_VAR_NAME):
        handlers.append(_TestHandler())

    return build_opener(*handlers)


def send_event(event: Event, /) -> None:
    body = {"events": [event]}

    executor = _get_executor()
    opener_director = _get_opener_director()

    def _send_event() -> None:
        fetch_json(
            _TELEMETRY_SERVICE_URL,
            body=body,
            opener_director=opener_director,
            timeout=_TIMEOUT,
        )

    executor.submit(_send_event)
