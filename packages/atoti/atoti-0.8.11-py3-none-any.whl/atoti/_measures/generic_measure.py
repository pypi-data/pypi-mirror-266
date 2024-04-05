from collections.abc import Sequence
from typing import Optional

from atoti_core import MeasureIdentifier
from typing_extensions import override

from .._java_api import JavaApi
from .._measure_description import MeasureDescription
from .._measure_metadata import MeasureMetadata
from .utils import convert_measure_args


class GenericMeasure(MeasureDescription):
    """Generic implementation of a MeasureDescription."""

    _plugin_key: str
    _args: Sequence[object]

    def __init__(self, plugin_key: str, /, *args: object):
        """Create the measure.

        Args:
            plugin_key: The plugin key of the Java implementation.
            args: The arguments used to create the measure.
                They are directly forwarded to the Java code, except for the ``Measure``
                arguments that are first created on the Java side and replaced by their name.
        """
        self._plugin_key = plugin_key
        self._args = args

    @override
    def _do_distil(
        self,
        identifier: Optional[MeasureIdentifier] = None,
        /,
        *,
        cube_name: str,
        java_api: JavaApi,
        measure_metadata: Optional[MeasureMetadata] = None,
    ) -> MeasureIdentifier:
        return java_api.create_measure(
            identifier,
            self._plugin_key,
            *convert_measure_args(
                java_api=java_api, cube_name=cube_name, args=self._args
            ),
            cube_name=cube_name,
            measure_metadata=measure_metadata,
        )
