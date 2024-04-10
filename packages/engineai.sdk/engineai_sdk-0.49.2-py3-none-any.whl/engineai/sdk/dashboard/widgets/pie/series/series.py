"""Spec for Pie Series."""
import warnings
from typing import Optional
from typing import Union

import pandas as pd
from beartype import beartype

from engineai.sdk.dashboard.formatting.number import NumberFormatting
from engineai.sdk.dashboard.styling.color import Palette
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.widgets.components.charts.typing import TooltipItem
from engineai.sdk.dashboard.widgets.components.charts.typing import TooltipItems

from .base import BaseSeries
from .styling import SeriesStyling


class Series(BaseSeries):
    """Spec for Pie Series."""

    _API_TYPE = "PieWidgetChartSeriesStandardInput"
    _INPUT_KEY = "standard"

    @beartype
    def __init__(
        self,
        *,
        name: TemplatedStringItem = "Series",
        category_column: TemplatedStringItem = "category",
        data_column: TemplatedStringItem = "value",
        formatting: Optional[NumberFormatting] = None,
        styling: Optional[Union[Palette, SeriesStyling]] = None,
        tooltips: Optional[TooltipItems] = None,
    ):
        """Construct spec for Pie Series.

        Args:
            name: name for the Pie series.
            category_column: name of column in pandas dataframe(s) that has category
                info within the pie.
            data_column: name of column in pandas dataframe(s) that has pie data.
            formatting: spec for number formatting.
            styling: spec for pie series styling.
            tooltips: tooltip items to be displayed at Series level.

        Examples:
            ??? example "Customise Pie Widget series (e.g. changing data column)"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import pie
                data = pd.DataFrame(
                    {
                        "name": ["X", "Y"],
                        "volume": [10, 20],
                    },
                )
                dashboard = Dashboard(
                    content=pie.Pie(
                        data=data,
                        series=pie.Series(
                            category_column="name",
                            data_column="volume",
                        )
                    )
                )
                ```
        """
        super().__init__(
            name=name,
            category_column=category_column,
            data_column=data_column,
            formatting=formatting,
            styling=styling,
            tooltips=tooltips,
        )

    def validate(
        self,
        *,
        data: pd.DataFrame,
    ) -> None:
        """Validates Pie Series Widget and the inner components specs."""
        self._validate_field(
            data=data,
            field="category_column",
            item=self._category_column,
        )
        super().validate(data=data)

    def add_tooltips(self, *tooltips: TooltipItem) -> "Series":
        """Add tooltip item(s) to the series.

        Args:
            tooltips: item(s) to be added to the series.

        Returns:
            Series: reference to this widget to facilitate
                inline manipulation
        """
        warnings.warn(
            "`add_tooltips` is deprecated. Use `tooltips` in constructor, instead.",
            DeprecationWarning,
        )
        self._tooltip_items.extend(tooltips)
        return self
