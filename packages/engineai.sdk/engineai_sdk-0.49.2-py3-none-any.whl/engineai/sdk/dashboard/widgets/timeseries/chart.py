"""Spec for charts in a Timeseries widget."""

from typing import Any
from typing import Optional
from typing import Union

import pandas as pd
from beartype import beartype

from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.components.charts.tooltip.item import (
    build_tooltip_item,
)

from ..components.charts.typing import TooltipItems
from ..utils import get_tooltips
from .axis.x_axis import XAxis
from .axis.y_axis.build_y_axis import YAxisSpec
from .axis.y_axis.build_y_axis import build_timeseries_y_axis
from .axis.y_axis.y_axis import YAxis
from .axis.y_axis.y_axis_mirror import MirrorYAxis
from .exceptions import TimeseriesChartBothAxisNotDefinedError
from .exceptions import TimeseriesDifferentAxisTypeError
from .exceptions import TimeseriesHeightUnitWrongDefinitionError
from .exceptions import TimeseriesHeightWrongDefinitionError
from .exceptions import TimeseriesWrongSeriesAxisError
from .series.base import TimeseriesBaseSeries
from .series.typing import TimeseriesSeries


class Chart(AbstractFactoryLinkItemsHandler):
    """Spec for charts in a Timeseries widget."""

    _HEIGHT_TIMESERIES_CHART_TITLE = 0.19
    __height: float  # Added here to use property logic for all entries

    @beartype
    def __init__(
        self,
        *,
        left_y_axis: Optional[Union[YAxisSpec, TimeseriesSeries]] = None,
        height_percentage: Optional[Union[float, int]] = None,
        height: Union[float, int] = 3,
        x_axis: Optional[XAxis] = None,
        right_y_axis: Optional[Union[YAxisSpec, TimeseriesSeries]] = None,
        title: Optional[Union[str, WidgetField]] = None,
        area_series_stacked: bool = False,
        tooltips: Optional[TooltipItems] = None,
    ):
        """Construct a chart for a timeseries widget.

        Args:
            x_axis: spec for x axis or the specific date column that must be used for
                the x axis.
            left_y_axis: spec for left y axis. If `TimeseriesSeries` added directly,
                a `YAxis` will be used as the default axis spec.
            right_y_axis: spec for right y axis (optional). If `TimeseriesSeries`
                added directly, a `YAxis` will be used as the default axis spec.
            title: title of chart can be either a string (fixed value) or determined
                by a value from another widget using a WidgetField.
            height_percentage: percentage of height occupied by chart.
                The height_percentage of all charts in a timeseries widgets has to
                sum to 1.
            height: height value for the chart in units of 100px. Values range from 2
                to 10 units.
            area_series_stacked: enable stacking for all area series in this chart.
            tooltips: tooltip items to be displayed at Chart level.
        """
        super().__init__()
        self.__x_axis: XAxis = x_axis or XAxis()
        self.__height_percentage = height_percentage
        self.__title = title
        self.__extra_tooltip_items = get_tooltips(tooltips)
        self.__area_series_stacked = area_series_stacked
        self.height = height

        self.__set_chart_axis(left_y_axis, right_y_axis)
        self._date_column: TemplatedStringItem = " "

    def __set_chart_axis(
        self,
        left_y_axis: Optional[Union[YAxisSpec, TimeseriesSeries]] = None,
        right_y_axis: Optional[Union[YAxisSpec, TimeseriesSeries]] = None,
    ) -> None:
        self.__validate_axis_position(left_y_axis)

        self.__left_y_axis = (
            left_y_axis
            if isinstance(left_y_axis, (YAxis, MirrorYAxis))
            else YAxis().add_series(left_y_axis)
            if left_y_axis is not None
            else None
        )

        self.__right_y_axis = (
            right_y_axis
            if isinstance(right_y_axis, (YAxis, MirrorYAxis))
            else YAxis().add_series(right_y_axis)
            if right_y_axis is not None
            else None
        )

        self.__validate_axis()

    def __validate_axis(
        self,
    ) -> None:
        if self.__left_y_axis is None and self.__right_y_axis is None:
            raise TimeseriesChartBothAxisNotDefinedError()

        if self.__left_y_axis is not None and self.__right_y_axis is not None:
            self.__both_axis_same_type()

    def __both_axis_same_type(
        self,
    ) -> None:
        if (
            isinstance(self.__left_y_axis, MirrorYAxis)
            and not isinstance(self.__right_y_axis, MirrorYAxis)
            or isinstance(self.__left_y_axis, YAxis)
            and not isinstance(self.__right_y_axis, YAxis)
        ):
            raise TimeseriesDifferentAxisTypeError()

    @staticmethod
    def __validate_axis_position(
        series: Optional[Union[YAxisSpec, TimeseriesSeries]] = None
    ) -> None:
        if (
            series is not None
            and isinstance(series, TimeseriesBaseSeries)
            and series.is_right_axis
        ):
            raise TimeseriesWrongSeriesAxisError()

    @property
    def height(self) -> Union[float, int]:
        """Get chart height based on the `height` value plus a title buffer."""
        return self.__height + (
            self._HEIGHT_TIMESERIES_CHART_TITLE if self.__title else 0
        )

    @height.setter
    def height(self, height: Union[float, int]) -> None:
        if 2 > height > 10:
            raise TimeseriesHeightWrongDefinitionError()
        if height % 1 not in [0, 0.5]:
            raise TimeseriesHeightUnitWrongDefinitionError()
        self.__height = height

    @property
    def height_percentage(self) -> Optional[Union[float, int]]:
        """Returns height percentage occupied by this chart.

        Returns:
            Optional[Union[float, int]]: height percentage.
        """
        return self.__height_percentage

    @height_percentage.setter
    def height_percentage(self, height_percentage: Union[float, int]) -> None:
        """Set Height Percentage."""
        self.__height_percentage = height_percentage

    def prepare(self, date_column: TemplatedStringItem) -> None:
        """Method that prepares the spec to be built."""
        self._date_column = date_column
        if self.__left_y_axis is not None:
            self.__left_y_axis.prepare(date_column)

        if self.__right_y_axis is not None:
            self.__right_y_axis.prepare(
                date_column,
                offset=len(self.__left_y_axis) if self.__left_y_axis else 0,
            )

    def validate(
        self,
        *,
        data: pd.DataFrame,
    ) -> None:
        """Validate if chart has all dataframe columns and axis dependencies.

        Args:
            data: pandas dataframe which will be used for table.
        """
        # validate tooltip
        for item in self.__extra_tooltip_items:
            item.validate(data=data)

        # validate each axis
        if self.__left_y_axis is not None:
            self.__left_y_axis.validate(
                data=data,
            )
        if self.__right_y_axis is not None:
            self.__right_y_axis.validate(
                data=data,
            )

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API.
        """
        return generate_input(
            "TimeseriesWidgetChartInput",
            xAxis=self.__x_axis.build(),
            yAxisLeft=[build_timeseries_y_axis(axis=self.__left_y_axis)]
            if self.__left_y_axis is not None
            else [],
            yAxisRight=[build_timeseries_y_axis(axis=self.__right_y_axis)]
            if self.__right_y_axis is not None
            else [],
            title=build_templated_strings(items=self.__title) if self.__title else None,
            heightPercentage=self.height_percentage,
            **self.__build_tooltip(),
            enableAreaStacking=self.__area_series_stacked,
        )

    def __build_tooltip(self) -> Any:
        tooltip_spec = None
        if len(self.__extra_tooltip_items) > 0:
            tooltip_spec = generate_input(
                "TimeseriesWidgetChartTooltipInput",
                xAxisKey=build_templated_strings(items=self._date_column),
                items=[
                    build_tooltip_item(item=item) for item in self.__extra_tooltip_items
                ],
            )
        return {"tooltip": tooltip_spec}
