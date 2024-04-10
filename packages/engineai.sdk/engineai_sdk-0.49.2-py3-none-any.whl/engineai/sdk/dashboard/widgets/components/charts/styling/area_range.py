"""Spec to style an area range series."""
from typing import Optional

from beartype import beartype

from engineai.sdk.dashboard.styling.color.typing import ColorSpec
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .base import BaseChartSeriesStyling
from .enums import MarkerSymbol


class AreaRangeSeriesStyling(BaseChartSeriesStyling):
    """Spec to style an area range series."""

    _API_TYPE = "ChartAreaRangeSeriesStylingInput"

    @beartype
    def __init__(
        self,
        *,
        color_spec: ColorSpec,
        data_column: Optional[TemplatedStringItem] = None,
        marker_symbol: MarkerSymbol = MarkerSymbol.CIRCLE,
    ):
        """Construct style spec for area range series.

        Args:
            color_spec: spec for coloring area range.
            data_column: name of column in pandas dataframe(s) used for color spec if
                a gradient is used. Optional for single colors.
            marker_symbol: symbol for marker in tooltips and legends.

        Raises:
            ChartStylingMissingDataColumnError: if color_spec is
                ColorDiscreteMap/ColorGradient and data_column
                has not been specified
        """
        super().__init__(
            color_spec=color_spec, data_column=data_column, marker_symbol=marker_symbol
        )
