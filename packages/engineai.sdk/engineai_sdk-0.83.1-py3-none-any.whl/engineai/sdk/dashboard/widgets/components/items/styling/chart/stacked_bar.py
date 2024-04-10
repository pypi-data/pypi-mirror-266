"""Spec for Widget Stacked Bar Chart Styling."""
from typing import Any
from typing import Dict
from typing import Optional

from engineai.sdk.dashboard.styling.color.typing import ColorSpec
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from ..base import BaseItemStyling


class StackedBarChartItemStyling(BaseItemStyling):
    """Spec for styling used by Stacked Bar Chart Item."""

    _API_TYPE = "SparkChartStackedBarStylingInput"

    def __init__(
        self,
        *,
        data_column: Optional[TemplatedStringItem] = None,
        color_spec: Optional[ColorSpec] = None,
        show_total_value: bool = False
    ):
        """Construct spec for the StackedBarChartItemStyling class.

        Args:
            data_column (Optional[str]): styling data key.
            color_spec (Optional[ColorSpec]): specs for color.
            show_total_value (bool): whether to show total value.
        """
        super().__init__(data_column=data_column, color_spec=color_spec)
        self.__show_total_value = show_total_value

    def _build_extra_inputs(self) -> Dict[str, Any]:
        return {"showTotalOnTooltip": self.__show_total_value}
