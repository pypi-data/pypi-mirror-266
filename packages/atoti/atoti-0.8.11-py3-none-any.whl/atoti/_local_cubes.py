from collections.abc import Mapping, Set as AbstractSet
from typing import Any, Protocol, TypeVar

from atoti_core import BaseCubes, DelegateMutableMapping
from typing_extensions import override

from ._local_cube import LocalCube

_LocalCube_co = TypeVar(
    "_LocalCube_co", bound="LocalCube[Any, Any, Any]", covariant=True
)


class _DeleteCube(Protocol):
    def __call__(self, cube_name: str, /) -> None: ...


class _GetCube(Protocol[_LocalCube_co]):
    def __call__(self, cube_name: str, /) -> _LocalCube_co: ...


class _GetCubes(Protocol[_LocalCube_co]):
    def __call__(self) -> Mapping[str, _LocalCube_co]: ...


class LocalCubes(  # type: ignore[type-var]
    DelegateMutableMapping[
        str,
        _LocalCube_co,  # pyright: ignore[reportInvalidTypeArguments]
    ],
    BaseCubes[_LocalCube_co],
):
    def __init__(
        self,
        *,
        delete_cube: _DeleteCube,
        get_cube: _GetCube[_LocalCube_co],
        get_cubes: _GetCubes[_LocalCube_co],
    ) -> None:
        super().__init__()

        self._delete_cube = delete_cube
        self._get_cube = get_cube
        self._get_cubes = get_cubes

    @override
    def _update(
        self,
        other: Mapping[str, _LocalCube_co],
        /,
    ) -> None:
        raise AssertionError("Use `Session.create_cube()` to create a cube.")

    @override
    def __getitem__(self, key: str, /) -> _LocalCube_co:
        return self._get_cube(key)

    @override
    def _get_underlying(self) -> dict[str, _LocalCube_co]:
        return {**self._get_cubes()}

    @override
    def _delete_keys(self, keys: AbstractSet[str], /) -> None:
        for key in keys:
            self._delete_cube(key)
