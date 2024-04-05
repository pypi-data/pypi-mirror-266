from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet

from atoti_core import DelegateMutableMapping
from atoti_query._internal import AuthenticationType
from typing_extensions import override

from ._java_api import JavaApi

_BASIC_AUTHENTICATION_TYPE: AuthenticationType = "BASIC"
_REDACTED_PASSWORD = "**REDACTED**"  # noqa: S105


class BasicCredentials(DelegateMutableMapping[str, str]):
    def __init__(self, *, java_api: JavaApi) -> None:
        super().__init__()

        self._java_api = java_api

    @override
    def _get_underlying(self) -> dict[str, str]:
        return {
            username: _REDACTED_PASSWORD
            for username in self._java_api._enterprise_api().getUsers(
                _BASIC_AUTHENTICATION_TYPE
            )
        }

    @override
    def _update(self, other: Mapping[str, str], /) -> None:
        usernames = set(self.keys())

        for username, password in other.items():
            if username in usernames:
                self._java_api._enterprise_api().updateUserPassword(
                    username, password, _BASIC_AUTHENTICATION_TYPE
                )
            else:
                self._java_api._enterprise_api().createUser(
                    username,
                    password,
                    _BASIC_AUTHENTICATION_TYPE,
                )

    @override
    def _delete_keys(self, keys: AbstractSet[str], /) -> None:
        for username in keys:
            self._java_api._enterprise_api().deleteUser(
                username, _BASIC_AUTHENTICATION_TYPE
            )
