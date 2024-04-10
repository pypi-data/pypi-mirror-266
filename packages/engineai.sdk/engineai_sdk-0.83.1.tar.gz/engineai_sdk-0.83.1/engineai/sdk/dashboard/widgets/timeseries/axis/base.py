"""Specs for a Base Timeseries chart."""

from typing import Any
from typing import Mapping
from typing import Optional

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.utils import generate_input


class TimeseriesBaseAxis(AbstractFactoryLinkItemsHandler):
    """Specs for a Base Timeseries chart."""

    _API_TYPE: Optional[str] = None

    @type_check
    def __init__(
        self,
        *,
        enable_crosshair: bool = False,
    ) -> None:
        """Construct TimeseriesBaseAxis.

        Args:
            enable_crosshair: whether to enable crosshair that follows either
                the mouse pointer or the hovered point.
        """
        super().__init__()
        self.__enable_crosshair = enable_crosshair

    @property
    def _api_type(self) -> str:
        """Returns API type argument value.

        All Timeseries Axis must now have the _API_TYPE defined.
        """
        if self._API_TYPE is None:
            raise NotImplementedError(
                f"Class {self.__class__.__name__}._API_TYPE not defined."
            )
        return self._API_TYPE

    def _build_axis(self) -> Mapping[str, Any]:
        """Method that generates the input for a specific axis."""
        return {}

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API.
        """
        return generate_input(
            self._api_type,
            **self._build_axis(),
            enableCrosshair=self.__enable_crosshair,
            bands=[],
            lines=[],
        )
