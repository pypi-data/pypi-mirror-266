"""Spec for Pie Widget."""
import warnings
from typing import Any
from typing import List
from typing import Optional
from typing import Union

import pandas as pd
from beartype import beartype
from pandas.api.types import is_datetime64_dtype
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_object_dtype
from pandas.api.types import is_string_dtype

from engineai.sdk.dashboard.data import DataSource
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.chart_utils import TooltipItem
from engineai.sdk.dashboard.widgets.chart_utils import get_object_columns_tooltip
from engineai.sdk.dashboard.widgets.components.charts.tooltip.datetime import (
    DatetimeTooltipItem,
)
from engineai.sdk.dashboard.widgets.components.charts.tooltip.number import (
    NumberTooltipItem,
)
from engineai.sdk.dashboard.widgets.components.charts.tooltip.text import (
    TextTooltipItem,
)
from engineai.sdk.dashboard.widgets.components.charts.typing import TooltipItems

from ..base import Widget
from ..base import WidgetTitleType
from .chart import Chart
from .legend import LegendPosition
from .legend import build_legend
from .series.series import Series
from .series.typings import ChartSeries


class Pie(Widget):
    """Spec for Pie Widget."""

    _WIDGET_API_TYPE = "pie"
    _DEPENDENCY_ID = "__PIE_DATA_DEPENDENCY__"

    @beartype
    def __init__(
        self,
        data: Union[DataSource, pd.DataFrame],
        *,
        series: Optional[ChartSeries] = None,
        legend_position: LegendPosition = LegendPosition.BOTTOM,
        widget_id: Optional[str] = None,
        title: Optional[WidgetTitleType] = None,
        tooltips: Optional[TooltipItems] = None,
    ):
        """Construct spec for the Pie Widget.

        Args:
            data: data for the widget. Can be a pandas dataframe or DataStorage object
                if the data is to be retrieved from a storage.
            widget_id: unique widget id in a dashboard.
            title: title of widget can be either a string (fixed value) or determined
                by a value from another widget using a WidgetLink.
            series: Pie Series spec class.
            legend_position: position of the legend within the pie.
            tooltips: tooltip items to be displayed at Chart level.

        Examples:
            ??? example "Create a minimal Pie Widget"
                ```py linenums="1"
                import pandas as pd

                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import pie

                data = pd.DataFrame(
                    {
                        "category": ["A", "B"],
                        "value": [1, 2],
                        "tooltip": ["X", "Y"],
                    },
                )

                dashboard = Dashboard(content=pie.Pie(data))
                ```


            ??? example "Set the legend position to right"
                ```py linenums="13"
                dashboard = Dashboard(
                    content=pie.Pie(
                        data=data,
                        legend_position=pie.LegendPosition.RIGHT,
                    )
                )
                ```
        """
        super().__init__(widget_id=widget_id, data=data)
        self._legend_position = legend_position

        self._chart = Chart(
            series=series or Series(),
            tooltips=self._auto_generate_tooltips(
                data=data, series=series, tooltips=tooltips
            ),
        )
        self._title = title

    def _auto_generate_tooltips(
        self,
        data: Union[DataSource, pd.DataFrame],
        series: Optional[ChartSeries],
        tooltips: Optional[TooltipItems] = None,
    ) -> List[TooltipItem]:
        if tooltips is not None:
            return tooltips if isinstance(tooltips, list) else [tooltips]

        if series is not None:
            return []

        return self.__get_data_tooltips(data=data)

    @staticmethod
    def __get_data_tooltips(data: Union[DataSource, pd.DataFrame]) -> List[TooltipItem]:
        tooltips: List[TooltipItem] = []

        if isinstance(data, pd.DataFrame):
            aux_data = data.drop(["category", "value"], axis=1)
            for column_name in aux_data.columns:
                if is_numeric_dtype(aux_data[column_name]):
                    tooltips.append(NumberTooltipItem(data_column=str(column_name)))
                elif is_datetime64_dtype(aux_data[column_name]):
                    tooltips.append(DatetimeTooltipItem(data_column=str(column_name)))
                elif is_string_dtype(aux_data[column_name]):
                    tooltips.append(TextTooltipItem(data_column=str(column_name)))
                elif is_object_dtype(aux_data[column_name]):
                    tooltip_item = get_object_columns_tooltip(
                        column_data=aux_data[column_name], column_name=str(column_name)
                    )
                    if tooltip_item is not None:
                        tooltips.append(tooltip_item)

        return tooltips

    def add_tooltips(self, *tooltips: TooltipItem) -> "Pie":
        """Add tooltip item(s) to Pie Widget.

        Args:
            tooltips: item(s) to be added to the Pie Widget.

        Returns:
            Pie: reference to this widget to facilitate
                inline manipulation
        """
        warnings.warn(
            "`add_tooltips` is deprecated. Use `tooltips` in constructor, instead.",
            DeprecationWarning,
        )
        self._chart.add_tooltips(*tooltips)
        return self

    def validate(self, data: pd.DataFrame, **kwargs: Any) -> None:
        """Validates Pie Widget and the inner components specs."""
        self._chart.validate(data=data)

    def _prepare(self, **kwargs: object) -> None:
        """Method for each Widget prepare before building."""
        self._chart.prepare(self.dependency_id, kwargs.get("json_data", None))

    def _build_widget_input(self) -> Any:
        """Builds spec for dashboard API."""
        return generate_input(
            "PieWidgetInput",
            title=build_templated_strings(items=self._title) if self._title else None,
            chart=self._chart.build(),
            legend=build_legend(self._legend_position),
        )

    def build_widget_input(self) -> Any:
        """Method to access the build from outside the class."""
        return self._build_widget_input()
