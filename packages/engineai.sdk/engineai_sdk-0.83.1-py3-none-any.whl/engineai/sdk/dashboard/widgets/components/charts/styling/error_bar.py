"""Spec to style a column series."""
from typing import Optional

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.styling.color.typing import ColorSpec
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .base import BaseChartSeriesStyling
from .enums import MarkerSymbol


class ErrorBarSeriesStyling(BaseChartSeriesStyling):
    """Spec to style error bar series."""

    _API_TYPE = "ChartErrorBarSeriesStylingInput"

    @type_check
    def __init__(
        self,
        *,
        color_spec: ColorSpec,
        data_column: Optional[TemplatedStringItem] = None,
        marker_symbol: MarkerSymbol = MarkerSymbol.SQUARE,
    ):
        """Construct style spec for error bar series.

        Args:
            color_spec: spec for coloring columns.
            data_column: name of column in pandas dataframe(s) used for color spec if
                a gradient is used. Optional for single colors.
            marker_symbol: symbol for marker in tooltips and legends.

        Raises:
            ChartStylingMissingDataColumnError: if a data_column is not defined when
                color_spec is a ColorDiscreteMap or ColorGradient
        """
        super().__init__(
            color_spec=color_spec, data_column=data_column, marker_symbol=marker_symbol
        )
