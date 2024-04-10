"""Specification for styling a column with an icon to a value."""
from typing import Any
from typing import Dict
from typing import Union

from beartype import beartype

from engineai.sdk.dashboard.links import WidgetField

from .base import TableColumnStylingBase


class IconStyling(TableColumnStylingBase):
    """Specification for styling a column with an icon to a value."""

    _API_TYPE = "TableColumnStylingIconInput"

    @beartype
    def __init__(
        self,
        *,
        data_column: Union[str, WidgetField],
        left: bool = True,
    ):
        """Construct for IconStyling class.

        Args:
            data_column: id of column which values are used to determine behavior of
                arrow.
                By default, will use values of column to which styling is applied.
            left: whether to put icon to the left (True) or right (False) of column
                value.
        """
        super().__init__(data_column=data_column, color_spec=None)
        self.__left = left

    def _build_extra_inputs(self) -> Dict[str, Any]:
        return {"left": self.__left}
