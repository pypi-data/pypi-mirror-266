"""Spec for navigator of a timeseries widget."""

from typing import Any
from typing import Optional

import pandas as pd
from beartype import beartype

from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.base import WidgetTitleType

from .exceptions import TimeseriesNavigatorEmptyDefinitionError
from .series.typing import TimeseriesSeries


class Navigator(AbstractFactoryLinkItemsHandler):
    """Spec for navigator of a timeseries widget."""

    @beartype
    def __init__(
        self, *series: TimeseriesSeries, title: Optional[WidgetTitleType] = None
    ) -> None:
        """Construct a navigator for a timeseries widget.

        Args:
            title: title to be added to navigator
            series: series to be added to navigator

        Examples:
            ??? examples "Create a minimal timeseries widget with a navigator"
                ```python linenums="1"
                import pandas as pd

                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import timeseries

                data = pd.DataFrame(
                    {
                        "value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    },
                    index=pd.date_range("2020-01-01", "2020-01-10"),
                )

                ts = timeseries.Timeseries(
                    data=data,
                    navigator=timeseries.Navigator(
                        timeseries.ColumnSeries(data_column="value")
                    )
                )
                Dashboard(content=ts)
                ```
        """
        super().__init__()

        if len(series) == 0:
            raise TimeseriesNavigatorEmptyDefinitionError()

        self.__series = series
        self.__title = title

    def prepare(self, date_column: TemplatedStringItem) -> None:
        """Method that prepares the spec to be build."""
        for index, series in enumerate(self.__series):
            series.prepare(date_column, index=index)

    def validate(self, *, data: pd.DataFrame) -> None:
        """Validate if dataframe that will be used for column contains required columns.

        Args:
            data: pandas dataframe which will be used for table

        """
        for series in self.__series:
            series.validate(data=data)

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        series_spec = []
        for series in self.__series:
            series_spec.append(series.build())
        return generate_input(
            "TimeseriesWidgetNavigatorInput",
            series=series_spec,
            title=build_templated_strings(items=self.__title),
        )
