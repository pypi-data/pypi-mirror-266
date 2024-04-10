"""Spec to build different series supported by Map widget."""

from typing import Any

from engineai.sdk.dashboard.utils import generate_input

from .numeric import NumericSeries

MapSeries = NumericSeries


def build_map_series(series: MapSeries) -> Any:
    """Builds spec for dashboard API.

    Args:
        series: series spec

    Returns:
        Input object for Dashboard API
    """
    if isinstance(series, NumericSeries):
        return generate_input("MapWidgetSeriesInput", numeric=series.build())
    else:
        raise TypeError(
            "MapSeries requires one of MapWidgetNumericSeries, ",
        )
