"""Specs for y axis of a Timeseries chart."""

from typing import Any
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union
from typing import cast

import pandas as pd
from beartype import beartype

from engineai.sdk.dashboard.formatting import AxisNumberFormatting
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.widgets.components.charts.axis.scale import AxisScale

from ...series.typing import TimeseriesSeries
from .base import BaseTimeseriesYAxis


class MirrorYAxis(BaseTimeseriesYAxis):
    """Specs for mirror y axis of a Timeseries chart."""

    _API_TYPE = "TimeseriesWidgetChartMirrorYAxisInput"

    @beartype
    def __init__(
        self,
        *,
        formatting: Optional[AxisNumberFormatting] = None,
        title: Union[str, WidgetField] = "",
        enable_crosshair: bool = False,
        scale: Optional[AxisScale] = None,
    ):
        """Construct y axis for a Timeseries chart.

        Args:
            formatting (Optional[AxisNumberFormatting]): formatting spec for axis
                labels.
                Defaults to None (Base AxisFormatting).
            title (Union[str, WidgetField]): axis title.
                Defaults to empty string.
            enable_crosshair (bool): whether to enable crosshair that follows either
                the mouse pointer or the hovered point.
                Defaults to False.
            scale (Optional[YAxisScale]): y axis scale, one of
                AxisScaleSymmetric, AxisScaleDynamic,
                AxisScalePositive, AxisScaleNegative.
                Defaults to AxisScaleSymmetric.
        """
        super().__init__(
            formatting=formatting,
            title=title,
            enable_crosshair=enable_crosshair,
            scale=scale,
        )
        self.__top_series: List[TimeseriesSeries] = []
        self.__bottom_series: List[TimeseriesSeries] = []

    def __len__(self) -> int:
        """Get number of series for this axis."""
        return len(self.__top_series) + len(self.__bottom_series)

    def _validate_series(self, *, data: pd.DataFrame) -> None:
        """Validate timeseries y axis series."""
        for series in self.__top_series:
            series.validate(data=data)
        for series in self.__bottom_series:
            series.validate(data=data)

    def add_top_series(self, *series: TimeseriesSeries) -> "MirrorYAxis":
        """Add series to top y axis.

        Returns:
            MirrorYAxis: reference to this axis to facilitate inline manipulation.

        Raises:
            TimeseriesAxisEmptyDefinitionError: when no series data are added
            ChartSeriesNameAlreadyExistsError: when series have duplicated names
        """
        return cast(MirrorYAxis, self._add_series(self.__top_series, *series))

    def add_bottom_series(self, *series: TimeseriesSeries) -> "MirrorYAxis":
        """Add series to top y axis.

        Returns:
            MirrorYAxis: reference to this axis to facilitate inline manipulation.

        Raises:
            TimeseriesAxisEmptyDefinitionError: when no series data are added
            ChartSeriesNameAlreadyExistsError: when series have duplicated names
        """
        return cast(MirrorYAxis, self._add_series(self.__bottom_series, *series))

    def prepare(self, date_column: TemplatedStringItem, offset: int = 0) -> None:
        """Prepare layout for building."""
        for index, element in enumerate(self.__top_series):
            element.prepare(
                date_column=date_column,
                index=index + offset,
            )

        for index, element in enumerate(self.__bottom_series):
            element.prepare(
                date_column=date_column,
                index=index + offset,
            )

    def _build_extra_y_axis(self) -> Mapping[str, Any]:
        """Method that generates the input for a specific y axis."""
        return {
            "topSeries": [series.build() for series in self.__top_series],
            "bottomSeries": [series.build() for series in self.__bottom_series],
        }
