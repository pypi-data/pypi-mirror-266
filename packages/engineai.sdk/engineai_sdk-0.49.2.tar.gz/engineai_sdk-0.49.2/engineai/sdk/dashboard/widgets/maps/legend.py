"""Spec for legend of a Map Shape widget."""

from typing import Any

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.maps.enums import LegendPosition


class Legend(AbstractFactory):
    """Spec for legend of a Map widget."""

    @beartype
    def __init__(self, *, position: LegendPosition = LegendPosition.BOTTOM):
        """Construct a legend for a Map Shape widget.

        Args:
            position (Position): location of position
                relative to data, maps.
        """
        super().__init__()
        self.__position = position

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input("MapWidgetLegendInput", position=self.__position.value)
