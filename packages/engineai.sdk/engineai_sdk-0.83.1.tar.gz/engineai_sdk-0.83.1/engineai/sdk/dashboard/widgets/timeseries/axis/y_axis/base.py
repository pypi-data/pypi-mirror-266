"""Specs for y axis of a Timeseries chart."""

from abc import abstractmethod
from typing import Any
from typing import List
from typing import Mapping
from typing import Optional
from typing import Set
from typing import Union

import pandas as pd

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.formatting import AxisNumberFormatting
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.components.charts.axis.scale import AxisScale
from engineai.sdk.dashboard.widgets.components.charts.axis.scale import AxisScaleDynamic
from engineai.sdk.dashboard.widgets.components.charts.axis.scale import build_axis_scale
from engineai.sdk.dashboard.widgets.components.charts.exceptions import (
    ChartSeriesNameAlreadyExistsError,
)

from ...exceptions import TimeseriesAxisEmptyDefinitionError
from ...series.typing import TimeseriesSeries
from ..base import TimeseriesBaseAxis


class BaseTimeseriesYAxis(TimeseriesBaseAxis):
    """Specs for y axis of a Timeseries chart."""

    @type_check
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
                Defaults to None.
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
        super().__init__(enable_crosshair=enable_crosshair)

        self.__formatting = (
            formatting if formatting is not None else AxisNumberFormatting()
        )

        self.__title = title
        self.__scale = scale if scale else AxisScaleDynamic()

        # used for getting a color from the index of each bands
        self.__series_names: Set[str] = set()

    def validate(
        self,
        *,
        data: pd.DataFrame,
    ) -> None:
        """Validate if dataframe has the required columns and dependencies for axis.

        Args:
            data (pd.DataFrame): pandas dataframe which will be used for table.

        Raises:
            ChartDependencyNotFoundError: when `datastore_id` does not exists on
                current datastores
        """
        self._validate_series(
            data=data,
        )
        self.__formatting.validate(data=data)

    @abstractmethod
    def _validate_series(
        self,
        *,
        data: pd.DataFrame,
    ) -> None:
        """Validate timeseries y axis series."""

    def _add_series(
        self, current_series: List[TimeseriesSeries], *series: TimeseriesSeries
    ) -> "BaseTimeseriesYAxis":
        """Auxiliary method to add series to top y axis.

        Returns:
            YAxis: reference to this axis to facilitate inline manipulation.

        Raises:
            TimeseriesAxisEmptyDefinitionError: when no series data are added
            ChartSeriesNameAlreadyExistsError: when series have duplicated names
        """
        if len(series) == 0:
            raise TimeseriesAxisEmptyDefinitionError()

        for element in series:
            if element.name in current_series:
                raise ChartSeriesNameAlreadyExistsError(
                    class_name=self.__class__.__name__,
                    series_name=element.name,
                )
            if isinstance(element.name, str):
                self.__series_names.add(str(element.name))

        current_series.extend(series)

        return self

    @abstractmethod
    def prepare(self, date_column: TemplatedStringItem, offset: int = 0) -> None:
        """Prepare layout for building."""

    @abstractmethod
    def _build_extra_y_axis(self) -> Mapping[str, Any]:
        """Method that generates the input for a specific y axis."""

    def _build_axis(self) -> Mapping[str, Any]:
        """Method that generates the input for a specific axis."""
        return {
            "formatting": self.__formatting.build()
            if self.__formatting is not None
            else None,
            "title": build_templated_strings(
                items=self.__title if self.__title else ""
            ),
            "scale": build_axis_scale(scale=self.__scale),
            **self._build_extra_y_axis(),
        }
