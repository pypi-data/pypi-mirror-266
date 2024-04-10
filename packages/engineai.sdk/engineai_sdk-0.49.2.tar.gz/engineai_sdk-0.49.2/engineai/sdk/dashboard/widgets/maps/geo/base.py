"""Spec for Base Map Geo class."""
from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar
from typing import Union

import pandas as pd
from beartype import beartype
from pandas.api.types import is_datetime64_dtype
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_object_dtype
from pandas.api.types import is_string_dtype

from engineai.sdk.dashboard.data.decorator import DataSource
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.chart_utils import get_object_columns_tooltip
from engineai.sdk.dashboard.widgets.components.charts.tooltip.datetime import (
    DatetimeTooltipItem,
)
from engineai.sdk.dashboard.widgets.components.charts.tooltip.item import (
    build_tooltip_item,
)
from engineai.sdk.dashboard.widgets.components.charts.tooltip.number import (
    NumberTooltipItem,
)
from engineai.sdk.dashboard.widgets.components.charts.tooltip.text import (
    TextTooltipItem,
)
from engineai.sdk.dashboard.widgets.components.charts.typing import TooltipItems
from engineai.sdk.dashboard.widgets.maps.enums import LegendPosition
from engineai.sdk.dashboard.widgets.maps.enums import Region
from engineai.sdk.dashboard.widgets.maps.exceptions import MapColumnDataNotFoundError
from engineai.sdk.dashboard.widgets.maps.legend import Legend
from engineai.sdk.dashboard.widgets.maps.series.numeric import NumericSeries

from ...base import Widget
from ...base import WidgetTitleType
from ...utils import build_data
from ...utils import get_tooltips
from ..series.series import MapSeries
from ..series.series import build_map_series

T = TypeVar("T", pd.DataFrame, Dict[str, Any])


class BaseMapGeo(Generic[T], Widget):
    """Spec for Base MapGeo widget."""

    _WIDGET_API_TYPE = "mapGeo"
    _DEPENDENCY_ID = "__MAP_GEO_DATA_DEPENDENCY__"

    @beartype
    def __init__(
        self,
        data: Union[DataSource, T],
        *,
        series: Optional[MapSeries] = None,
        region_column: str = "region",
        widget_id: Optional[str] = None,
        title: Optional[WidgetTitleType] = None,
        legend_position: LegendPosition = LegendPosition.BOTTOM,
        region: Region = Region.WORLD,
        tooltips: Optional[TooltipItems] = None,
    ):
        """Construct spec for the Base Map Geo class.

        Args:
            data: data source for the widget.
            series: Series to be added to y axis.
            region_column: key to match region code in DS.
            widget_id: unique widget id in a dashboard.
            title: title of widget can be either a string (fixed value) or determined
                by a value from another widget using a WidgetField.
            legend_position: location of position relative to data, maps.
            region: sets the region os the Map.
            tooltips: tooltip items to be displayed at Chart level.

        Examples:
            >>> # Create a minimal map widget
            >>> import pandas as pd
            >>> from engineai.sdk.dashboard.dashboard import Dashboard
            >>> from engineai.sdk.dashboard.widgets import maps
            >>> data = pd.DataFrame(
            ...     data=[
            ...         {"region": "PT", "value": 10, "tooltip": "A"},
            ...         {"region": "GB", "value": 100, "tooltip": "B"},
            ...     ]
            ... )
            >>> Dashboard(content=maps.Geo(data=data))
        """
        super().__init__(data=data, widget_id=widget_id)
        self._title = title
        self._legend_position = Legend(position=legend_position)
        self._series: List[MapSeries] = [series] if series else [NumericSeries()]
        self._region = region
        self._region_column = region_column
        self._extra_tooltip_items = get_tooltips(tooltips)
        self._auto_generate_tooltips(
            data=data, series=series, region_column=region_column
        )
        self._json_data = None

    def _prepare(self, **kwargs: object) -> None:
        for num, series in enumerate(self._series):
            series.prepare(
                num,
                self._region_column,
                self.dependency_id,
                kwargs.get("json_data", None),
            )
        self._json_data = kwargs.get("json_data", None)

    def _validate_map_data(self, data: T) -> None:
        """Validates data for map widget spec."""
        iterable = iter([data]) if isinstance(data, pd.DataFrame) else data.values()
        for value in iterable:
            if (
                isinstance(value, pd.DataFrame)
                and self._region_column not in value.columns
            ):
                raise MapColumnDataNotFoundError(column_data=self._region_column)

            if self._extra_tooltip_items and isinstance(value, pd.DataFrame):
                for tooltips in self._extra_tooltip_items:
                    tooltips.validate(data=value)

    def _validate_series(self, data: T) -> None:
        """Validates styling for map series spec."""
        if isinstance(data, pd.DataFrame):
            for series in self._series:
                series.validate(data=data)

    def _build_series(self) -> Any:
        """Builds series spec."""
        series_spec = []
        for series in self._series:
            series_spec.append(build_map_series(series=series))
        return series_spec

    def _build_tooltips(self) -> Any:
        """Builds tooltip spec."""
        if self._extra_tooltip_items:
            return generate_input(
                "MapWidgetTooltipInput",
                regionKey=self._region_column,
                data=build_data(path=self.dependency_id, json_data=self._json_data),
                items=[
                    build_tooltip_item(item=tooltip)
                    for tooltip in self._extra_tooltip_items
                ]
                if self._extra_tooltip_items
                else [],
            )
        return None

    def _auto_generate_tooltips(
        self,
        data: Union[DataSource, T],
        series: Optional[MapSeries],
        region_column: str,
    ) -> None:
        if series is not None or region_column != "region":
            return
        if isinstance(data, pd.DataFrame):
            self._validate_map_data(data)
            self._validate_series(data)
            aux_data = data.drop(["region", "value"], axis=1)
            for column_name in aux_data.columns:
                if is_numeric_dtype(aux_data[column_name]):
                    self._extra_tooltip_items.append(
                        NumberTooltipItem(data_column=str(column_name))
                    )
                elif is_datetime64_dtype(aux_data[column_name]):
                    self._extra_tooltip_items.append(
                        DatetimeTooltipItem(data_column=str(column_name))
                    )
                elif is_string_dtype(aux_data[column_name]):
                    self._extra_tooltip_items.append(
                        TextTooltipItem(data_column=str(column_name))
                    )
                elif is_object_dtype(aux_data[column_name]):
                    tooltip_item = get_object_columns_tooltip(
                        column_data=aux_data[column_name], column_name=str(column_name)
                    )
                    if tooltip_item is not None:
                        self._extra_tooltip_items.append(tooltip_item)
