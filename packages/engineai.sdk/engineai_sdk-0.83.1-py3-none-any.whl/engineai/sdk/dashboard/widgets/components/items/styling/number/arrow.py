"""Spec fot Number Styling Arrow."""

from typing import Any
from typing import Optional

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.styling.color.divergent import Divergent
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

from ..base import BaseItemStyling


class NumberStylingArrow(BaseItemStyling):
    """Spec for Number Arrow Styling class."""

    _API_TYPE: str = "NumberStylingArrowInput"

    @type_check
    def __init__(
        self,
        *,
        data_column: Optional[TemplatedStringItem] = None,
        color_divergent: Divergent,
    ):
        """Construct spec Number Arrow Styling.

        Args:
            color_divergent (ColorDivergent): specs for color.
            data_column (TemplatedStringItem): styling value key.
        """
        super().__init__(
            data_column=data_column,
        )
        self.__color_divergent = color_divergent

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            self._api_type,
            divergentPalette=self.__color_divergent.build(),
            valueKey=build_templated_strings(items=self.column),
        )
