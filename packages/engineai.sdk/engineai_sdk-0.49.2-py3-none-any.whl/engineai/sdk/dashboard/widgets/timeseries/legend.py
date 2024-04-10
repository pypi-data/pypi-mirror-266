"""Spec for legend of a timeseries widget."""
from typing import Any

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.enum.legend_position import LegendPosition
from engineai.sdk.dashboard.utils import generate_input


class Legend(AbstractFactory):
    """Spec for legend of a timeseries widget."""

    @beartype
    def __init__(self, *, position: LegendPosition = LegendPosition.BOTTOM):
        """Construct a legend for a timeseries widget.

        Args:
            position: location of position relative to data, charts.
        """
        super().__init__()
        self.__position = position

    @property
    def position(self) -> LegendPosition:
        """Returns the current Legend Position."""
        return self.__position

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "TimeseriesWidgetLegendInput", position=self.__position.value
        )
