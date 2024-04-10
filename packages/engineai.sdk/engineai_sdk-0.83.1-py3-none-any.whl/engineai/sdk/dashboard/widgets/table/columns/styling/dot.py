"""Specification for styling a column with an arrow next to value."""
from typing import Optional
from typing import Union

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.styling import color
from engineai.sdk.dashboard.styling.color.typing import ColorSpec

from .base import TableColumnStylingBase


class DotStyling(TableColumnStylingBase):
    """Specification for styling a column with a colored dot left to the value."""

    _API_TYPE = "TableColumnStylingDotInput"

    @type_check
    def __init__(
        self,
        *,
        color_spec: Optional[ColorSpec] = None,
        data_column: Optional[Union[str, WidgetField]] = None,
    ):
        """Construct for DotStyling class.

        Args:
            data_column: id of column which values are used to determine behavior of
                color of dot. Optional if color_spec is a single color.
            color_spec: spec for color of dot.
        """
        super().__init__(
            color_spec=color_spec
            if color_spec is not None
            else color.Palette.MINT_GREEN,
            data_column=data_column,
        )
