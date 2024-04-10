"""Spec for Search Widget Result Column Style."""

from typing import Any
from typing import Optional

import pandas as pd

from engineai.sdk.dashboard.styling.color.discrete_map import DiscreteMap
from engineai.sdk.dashboard.styling.color.gradient import Gradient
from engineai.sdk.dashboard.styling.color.palette import Palette
from engineai.sdk.dashboard.styling.color.spec import build_color_spec
from engineai.sdk.dashboard.styling.color.typing import ColorSpec
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

from ...exceptions import SearchStylingMissingDataColumnError
from ...exceptions import SearchValidateNoDataColumnError


class ResultColumnStyling:
    """Spec for Search Widget Result Column Style."""

    _API_TYPE: Optional[str] = None

    def __init__(
        self,
        *,
        color_spec: Optional[ColorSpec] = None,
        data_column: Optional[TemplatedStringItem] = None,
    ):
        """Construct for Search Widget Result Column Style.

        Args:
            color_spec: Spec for coloring columns.
            data_column: Name of column in pandas
                dataframe(s) used for color spec if a gradient is used. Optional for
                single colors.
        """
        super().__init__()
        if (
            color_spec is not None
            and isinstance(color_spec, (DiscreteMap, Gradient))
            and data_column is None
        ):
            raise SearchStylingMissingDataColumnError()
        self.__color_spec = color_spec or Palette.AQUA_GREEN
        self.__data_column = data_column

    @property
    def _api_type(self) -> str:
        """Returns styling API type argument value.

        All Select Layout Items must now have the _API_TYPE defined.
        """
        if self._API_TYPE is None:
            raise NotImplementedError(
                f"Class {self.__class__.__name__}._API_TYPE not defined."
            )
        return self._API_TYPE

    def validate(
        self,
        *,
        data: pd.DataFrame,
    ) -> None:
        """Validate if data has the right columns.

        Args:
            data: pandas dataframe which will be used for table.

        Raises:
            SearchValidateNoDataColumnError: if data does not contain data_column
        """
        if (
            isinstance(self.__data_column, str)
            and self.__data_column not in data.columns
        ):
            raise SearchValidateNoDataColumnError(data_column=self.__data_column)

        # TODO: Validate abstractLinks if used (widgetField, f.e)

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            self._api_type,
            chip=generate_input(
                "SearchWidgetResultColumnChipStylingInput",
                colorSpec=build_color_spec(spec=self.__color_spec)
                if self.__color_spec
                else None,
                dataKey=build_templated_strings(items=self.__data_column),
            ),
        )
