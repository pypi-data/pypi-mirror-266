"""Spec fot Text Styling Font."""
from typing import Any
from typing import Optional

from beartype import beartype

from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

from ..base import BaseItemStyling


class TextStylingCountryFlag(BaseItemStyling):
    """Spec for Text Country Flag Styling Class."""

    _API_TYPE = "TextStylingCountryFlagInput"

    @beartype
    def __init__(
        self,
        *,
        left: bool = True,
        data_column: Optional[TemplatedStringItem] = None,
    ):
        """Construct spec for Text Country Flag Styling.

        Args:
            data_column (Optional[TemplatedStringItem]): styling value key.
            left (bool): whether to put flag to the left (True) or
                right (False) of column value.
        """
        super().__init__(data_column=data_column, color_spec=None)
        self.__left = left

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            self._api_type,
            left=self.__left,
            valueKey=build_templated_strings(items=self.column),
        )
