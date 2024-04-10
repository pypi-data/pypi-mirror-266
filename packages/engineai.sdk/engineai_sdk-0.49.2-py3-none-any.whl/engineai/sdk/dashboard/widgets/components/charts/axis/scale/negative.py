"""Spec for scale for y axis with only negative values."""

from typing import Any
from typing import Optional

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input


class AxisScaleNegative(AbstractFactory):
    """Spec for scale for y axis with only negative values.

    Assumes max value of chart to be fixed at 0.

    """

    @beartype
    def __init__(
        self, *, min_value: Optional[int] = None, intermediate_tick_amount: int = 3
    ):
        """Construct positive scale spec.

        Args:
            min_value: fixed minimum value for axis.
                Defaults to None (min value calculated dynamically)
            intermediate_tick_amount: number of extra ticks between extremes.
        """
        super().__init__()
        self.__min_value = min_value
        self.__intermediate_tick_amount = intermediate_tick_amount

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "ChartNumericAxisScaleNegativeInput",
            min=self.__build_min_value(),
            tickAmount=self.__intermediate_tick_amount,
        )

    def __build_min_value(
        self,
    ) -> Any:
        return generate_input(
            "ChartNumericAxisScaleMinInput",
            min=self.__min_value,
        )
