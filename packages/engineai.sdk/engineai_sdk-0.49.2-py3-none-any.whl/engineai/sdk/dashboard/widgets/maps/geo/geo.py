"""Spec for Map Geo widget."""

from typing import Any
from typing import Optional
from typing import Union

import pandas as pd
from beartype import beartype

from engineai.sdk.dashboard.data import DataSource
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.components.charts.typing import TooltipItems
from engineai.sdk.dashboard.widgets.maps.enums import LegendPosition
from engineai.sdk.dashboard.widgets.maps.enums import Region

from ...base import WidgetTitleType
from ..series.series import MapSeries
from .base import BaseMapGeo


class Geo(BaseMapGeo[pd.DataFrame]):
    """Spec for MapGeo widget."""

    @beartype
    def __init__(
        self,
        data: Union[DataSource, pd.DataFrame],
        *,
        series: Optional[MapSeries] = None,
        region_column: str = "region",
        widget_id: Optional[str] = None,
        title: Optional[WidgetTitleType] = None,
        legend_position: LegendPosition = LegendPosition.BOTTOM,
        region: Region = Region.WORLD,
        tooltips: Optional[TooltipItems] = None,
    ):
        """Construct spec for the Map Geo widget.

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
            ??? example "Create a minimal Map widget"
                ```python linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                data = pd.DataFrame(
                    data=[
                        {"region": "PT", "value": 10, "tooltip": "A"},
                        {"region": "GB", "value": 100, "tooltip": "B"},
                    ]
                )
                Dashboard(content=maps.Geo(data=data))
                ```
        """
        super().__init__(
            data=data,
            series=series,
            region_column=region_column,
            widget_id=widget_id,
            title=title,
            legend_position=legend_position,
            region=region,
            tooltips=tooltips,
        )

    def _build_widget_input(self) -> Any:
        """Method to build map widget."""
        return generate_input(
            "MapGeoWidgetInput",
            title=build_templated_strings(items=self._title) if self._title else None,
            colorAxis=self._build_color_axis(),  # not being used by API for now.
            legend=self._legend_position.build(),
            series=self._build_series(),
            region=self._region.value,
            tooltip=self._build_tooltips(),
        )

    def _build_color_axis(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "MapWidgetColorAxisInput", position=LegendPosition.BOTTOM.value
        )

    def validate(self, data: pd.DataFrame, **kwargs: Any) -> None:
        """Validates widget spec.

        Args:
            data: pandas DataFrame where
                the data is present.

        Raises:
            TooltipItemColumnNotFoundError: if column(s) of tooltip(s) were not found
            MapColumnDataNotFoundError: if column(s) supposed to contain data were not
                found.
        """
        self._validate_map_data(data=data)
        self._validate_series(data=data)
