"""Spec for scale for y axis with only positive values."""

from typing import Any
from typing import Optional

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input


class AxisScalePositive(AbstractFactory):
    """Spec for scale for y axis with only negative values.

    Assumes min value of chart to be fixed at 0.

    """

    @beartype
    def __init__(
        self, *, max_value: Optional[int] = None, intermediate_tick_amount: int = 3
    ):
        """Construct positive scale spec.

        Args:
            max_value: fixed maximum value for axis.
                Defaults to None (max value calculated dynamically)
            intermediate_tick_amount: number of extra ticks between extremes.
        """
        super().__init__()
        self.__max_value = max_value
        self.__intermediate_tick_amount = intermediate_tick_amount

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "ChartNumericAxisScalePositiveInput",
            max=self.__build_max_value(),
            tickAmount=self.__intermediate_tick_amount,
        )

    def __build_max_value(
        self,
    ) -> Any:
        return generate_input(
            "ChartNumericAxisScaleMaxInput",
            max=self.__max_value,
        )
