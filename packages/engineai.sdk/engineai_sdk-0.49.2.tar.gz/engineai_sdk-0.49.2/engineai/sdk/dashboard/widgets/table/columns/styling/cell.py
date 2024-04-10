"""Specification for styling a column with an arrow next to value."""
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from beartype import beartype

from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.styling.color.typing import ColorSpec

from .base import TableColumnStylingBase


class CellStyling(TableColumnStylingBase):
    """Specification for styling a column with an arrow next to value."""

    _API_TYPE = "TableColumnStylingCellInput"

    @beartype
    def __init__(
        self,
        *,
        color_spec: ColorSpec,
        data_column: Optional[Union[str, WidgetField]] = None,
        percentage_fill: Optional[Union[float, int]] = 1,
    ):
        """Construct for CellStyling class.

        Args:
            data_column: id of column which values are used to determine behavior of
                arrow. By default, will use values of column to which styling is
                applied.
            percentage_fill: how much of the cell should the color
                fill. Default to 1, meaning the whole cell
            color_spec: spec for color of arrows.
        """
        super().__init__(color_spec=color_spec, data_column=data_column)
        self.__percentage_fill = percentage_fill

    def _build_extra_inputs(self) -> Dict[str, Any]:
        return {"percentageFill": self.__percentage_fill}
