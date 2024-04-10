"""Specs for chart toolbar."""

from typing import Any

from engineai.sdk.dashboard.utils import generate_input


def build_chart_toolbar(enable: bool) -> Any:
    """Build chart toolbar method."""
    return generate_input("WidgetContinuousChartToolbarInput", disabled=not enable)
