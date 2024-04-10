"""Spec for scale for y axis with only positive and negative values."""

from typing import Any
from typing import Optional

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.components.charts.exceptions import (
    ChartScaleSymmetricValueError,
)


class AxisScaleSymmetric(AbstractFactory):
    """Spec for scale for y axis with only positive and negative values.

    Extremes determined by max(abs(data)) and 0 added as the middle tick.

    """

    @beartype
    def __init__(
        self,
        *,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        intermediate_tick_amount: int = 1,
        strict: Optional[bool] = None
    ):
        """Construct symmetric y axis scale.

        Args:
            min_value (Optional[int]): fixed minimum value for axis.
                Defaults to None (calculated dynamically).
            max_value (Optional[int]): fixed maximum value for axis.
                Defaults to None (calculated dynamically).
            intermediate_tick_amount (int): number of ticks between min-mid and
                between mid and max.
                Defaults to 1 (axis with five ticks)
            strict (bool): Strict the Symmetry between the min and max value.
                Defaults to True.
        """
        super().__init__()
        if min_value is not None and max_value is not None and strict is not None:
            raise ChartScaleSymmetricValueError(class_name=self.__class__.__name__)
        self.__min_value = min_value
        self.__max_value = max_value
        self.__intermediate_tick_amount = intermediate_tick_amount
        self.__strict = strict

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "ChartNumericAxisScaleSymmetricalInput",
            min=self.__build_min_value(),
            max=self.__build_max_value(),
            intermediateTickAmount=self.__intermediate_tick_amount,
            strict=self.__strict if self.__strict is not None else True,
        )

    def __build_min_value(
        self,
    ) -> Any:
        return generate_input(
            "ChartNumericAxisScaleMinInput",
            min=self.__min_value,
        )

    def __build_max_value(
        self,
    ) -> Any:
        return generate_input(
            "ChartNumericAxisScaleMaxInput",
            max=self.__max_value,
        )
