"""Spec for dynamic scale for y axis."""

from typing import Any

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input


class AxisScaleDynamic(AbstractFactory):
    """Spec for dynamic scale for y axis.

    Axis extremes are calculated dynamically to minimize the amount of dead space
        in a chart.
    """

    @beartype
    def __init__(self, *, tick_amount: int = 3):
        """Construct dynamic scale for y axis.

        Args:
            tick_amount: number of ticks beyond min and max.
        """
        super().__init__()
        self.__tick_amount = tick_amount

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "ChartNumericAxisScaleDynamicInput", tickAmount=self.__tick_amount
        )
