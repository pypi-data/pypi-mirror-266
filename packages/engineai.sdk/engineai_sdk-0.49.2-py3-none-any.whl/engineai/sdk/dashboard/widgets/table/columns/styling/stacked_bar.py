"""Specification for styling the stacked bar column."""

from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from beartype import beartype

from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.styling.color import DiscreteMap
from engineai.sdk.dashboard.styling.color.spec import build_color_spec

from .base import TableSparklineColumnStylingBase


class StackedBarStyling(TableSparklineColumnStylingBase):
    """Specification for styling a Stack Bar chart table column."""

    _API_TYPE = "SparkChartStackedBarStylingInput"

    @beartype
    def __init__(
        self,
        *,
        color_spec: DiscreteMap,
        data_column: Optional[Union[str, WidgetField]] = None,
        show_total_on_tooltip: bool = False
    ):
        """Construct for StackedBarStyling class.

        Args:
            data_column: id of column which values are used for chart.
            color_spec: spec for discrete color map of stacked bar column chart.
            show_total_on_tooltip: show stacked bar total on tooltip.
        """
        super().__init__(
            data_column=data_column,
            color_spec=color_spec,
        )
        self.__show_total_on_tooltip = show_total_on_tooltip

    def _build_color_spec(self) -> Dict[str, Any]:
        return (
            {
                "colorSpec": build_color_spec(spec=self.color_spec),
                "showTotalOnTooltip": self.__show_total_on_tooltip,
            }
            if self.color_spec is not None
            else {}
        )
