"""Spec fot Text Styling Font."""
from typing import Optional

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.styling.color.spec import ColorSpec
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from ..base import BaseItemStyling


class TextStylingChip(BaseItemStyling):
    """Spec for Text Chip Styling Class."""

    _API_TYPE = "TextStylingChipInput"

    @type_check
    def __init__(
        self,
        *,
        color_spec: Optional[ColorSpec] = None,
        data_column: Optional[TemplatedStringItem] = None,
    ):
        """Construct spec for Text Chip Styling.

        Args:
            color_spec (Optional[ColorSpec]): specs for color.
            data_column (Optional[TemplatedStringItem]): styling value key.
        """
        super().__init__(data_column=data_column, color_spec=color_spec)
