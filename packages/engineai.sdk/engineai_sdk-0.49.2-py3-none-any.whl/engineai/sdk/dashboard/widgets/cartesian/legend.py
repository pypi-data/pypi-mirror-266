"""Spec for legend of a categorical widget."""
from typing import Any

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.enum.legend_position import LegendPosition
from engineai.sdk.dashboard.utils import generate_input


class Legend(AbstractFactory):
    """Spec for legend of a categorical widget.

    Args:
        position: location of position relative to data, charts.
    """

    @beartype
    def __init__(self, *, position: LegendPosition = LegendPosition.BOTTOM):
        """Construct a legend for a categorical widget."""
        super().__init__()
        self.__position = position

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "ContinuousCartesianWidgetLegendInput", position=self.__position.value
        )
