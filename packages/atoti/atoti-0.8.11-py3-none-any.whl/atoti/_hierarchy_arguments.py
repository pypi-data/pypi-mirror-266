from collections.abc import Mapping
from dataclasses import dataclass

from atoti_core import HierarchyIdentifier, keyword_only_dataclass

from ._level_arguments import LevelArguments


@keyword_only_dataclass
@dataclass(frozen=True)
class HierarchyArguments:
    identifier: HierarchyIdentifier
    levels_arguments: Mapping[str, LevelArguments]
    slicing: bool
    visible: bool
    virtual: bool
    dimension_default: bool
