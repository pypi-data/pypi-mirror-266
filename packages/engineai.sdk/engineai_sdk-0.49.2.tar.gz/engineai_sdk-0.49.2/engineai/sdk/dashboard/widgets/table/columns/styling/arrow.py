"""Specifications for styling a column with an arrow next to value."""
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from beartype import beartype

from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.styling import color
from engineai.sdk.dashboard.styling.color.typing import ColorSpec

from .base import TableColumnStylingBase


class ArrowStyling(TableColumnStylingBase):
    """Specification for styling a column with an arrow next to value."""

    _API_TYPE = "TableColumnStylingArrowInput"

    @beartype
    def __init__(
        self,
        *,
        data_column: Optional[Union[str, WidgetField]] = None,
        mid: Union[float, int] = 0,
        color_spec: Optional[ColorSpec] = None,
    ):
        """Construct for ArrowStyling class.

        Args:
            data_column: id of column which values are used to determine behavior of
                arrow. By default, will use values of column to which styling is
                applied.
            mid: value that determines when arrow flips up/down.
            color_spec: spec for color of arrows. By default, used the
                PositiveNegativeDiscreteMap.
        """
        super().__init__(
            color_spec=color_spec
            if color_spec
            else color.PositiveNegativeDiscreteMap(),
            data_column=data_column,
        )
        self.__mid = mid

    def _build_extra_inputs(self) -> Dict[str, Any]:
        return {"mid": self.__mid}
