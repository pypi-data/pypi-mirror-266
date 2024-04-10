"""Spec for Gradients."""

from typing import Any
from typing import Union

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.styling.color.palette import Palette
from engineai.sdk.dashboard.utils import generate_input

from .single import Single


class GradientItem(AbstractFactory):
    """Item of a color gradient."""

    @type_check
    def __init__(
        self,
        *,
        value: Union[float, int],
        color: Union[Palette, Single],
    ):
        """Item of a Color Gradient.

        Args:
            value: initial value of interval with color.
            color: color applied to interval (Palette)
                or color itself (Single).
        """
        super().__init__()
        self.__color = color if isinstance(color, Single) else Single(color=color)
        self.__value = value

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "GradientItemInput", color=self.__color.build(), value=self.__value
        )


class Gradient(AbstractFactory):
    """Gradient of transition between colors."""

    @type_check
    def __init__(self, *items: GradientItem, steps: int = 10):
        """Color Gradient spec.

        This class is used to create a gradient of colors using

        Args:
            items: map between color and intervals.
            steps: number of intermediate colors between gradient items.
                Defaults to 10.

        Examples:
            ??? example "Create a gradient with 3 colors"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.styling import color
                from engineai.sdk.dashboard.widgets import timeseries
                from engineai.sdk.dashboard.dashboard import Dashboard
                # Create the color schema
                gradient_color = color.Gradient(
                    color.GradientItem(value=0, color=color.Palette.RUBI_RED),
                    color.GradientItem(value=2.5, color=color.Palette.GRASS_GREEN),
                    color.GradientItem(value=5, color=color.Palette.BABY_BLUE)
                )
                # Create the timeseries and apply the color schema
                data = pd.DataFrame(
                    {
                        "value": [10, 20, 30, 10, 20, 30, 10, 20, 30, 10],
                        "color": [0, 1, 2, 0, 1, 2, 0, 1, 2, 0],
                    },
                    index=pd.date_range("2020-01-01", "2020-01-10"),
                )
                ts = timeseries.Timeseries(
                    data
                ).set_series(
                    timeseries.LineSeries(
                        data_column="value",
                        styling=timeseries.LineSeriesStyling(
                            color_spec=gradient_color,
                            data_column="color",
                        )
                    )
                )
                Dashboard(content=ts)
                ```
        """
        super().__init__()
        self.__items = items
        self.__steps = steps

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "ColorGradientInput",
            colorMap=[item.build() for item in self.__items],
            nSteps=self.__steps,
        )
