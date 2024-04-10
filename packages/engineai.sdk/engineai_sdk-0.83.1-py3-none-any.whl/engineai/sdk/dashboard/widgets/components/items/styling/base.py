"""Spec for Base Item Styling class."""

import warnings
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union
from typing import cast

import pandas as pd

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.exceptions import ImproperlyConfiguredError
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.styling.color import Palette
from engineai.sdk.dashboard.styling.color import Single
from engineai.sdk.dashboard.styling.color.spec import build_color_spec
from engineai.sdk.dashboard.styling.color.typing import ColorSpec
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

from .exceptions import ItemStylingValidationError


class BaseItemStyling(AbstractFactoryLinkItemsHandler):
    """Spec for Number Styling Base class."""

    _API_TYPE: Optional[str] = None

    @type_check
    def __init__(
        self,
        *,
        color_spec: Optional[ColorSpec] = None,
        data_column: Optional[TemplatedStringItem] = None,
    ):
        """Construct for BaseItemStyling class.

        Args:
            color_spec (Optional[ColorSpec]): specs for color.
            data_column (Optional[TemplatedStringItem]): styling value key.
        """
        super().__init__()

        self.__data_column = data_column
        self.__color_spec = color_spec or Palette.AQUA_GREEN

        self.__verify_column_is_not_used()

    def prepare(
        self, data_column: Optional[Union[str, TemplatedStringItem, GenericLink]]
    ) -> None:
        """Prepare data column."""
        if self.__data_column is None:
            self.__data_column = data_column

    def __verify_column_is_not_used(self) -> None:
        if (
            self.__color_spec is not None
            and self.__data_column is not None
            and isinstance(self.__color_spec, (Single, Palette))
        ):
            warnings.warn(
                f"class variable with value = {self.__data_column} is not used if "
                f"`color_spec` is Single or Palette.",
                UserWarning,
            )

    def _build_extra_inputs(self) -> Dict[str, Any]:
        return {}

    @property
    def _api_type(self) -> str:
        """Get API TYPE value."""
        if self._API_TYPE is None:
            raise ImproperlyConfiguredError(
                f"Class {self.__class__.__name__} does not have the "
                f"`_api_type` configured. Please set "
                f"{self.__class__.__name__}._API_TYPE or change the "
                f"{self.__class__.__name__}._api_type property."
            )
        return self._API_TYPE

    @property
    def column(
        self,
    ) -> Optional[TemplatedStringItem]:
        """Return Data Column."""
        return self.__data_column

    @column.setter
    def column(
        self,
        column: TemplatedStringItem,
    ) -> None:
        self.__data_column = column

    def __contains_key(self, data: Union[pd.DataFrame, Dict[str, Any]]) -> bool:
        if isinstance(data, pd.DataFrame):
            return self.__data_column in cast(pd.DataFrame, data).columns
        return self.__data_column in cast(Dict[str, Any], data).keys()

    def validate(
        self,
        *,
        data: Union[pd.DataFrame, Dict[str, Any]],
        column_name: str,
    ) -> None:
        """Validate if dataframe that will be used for column contains required columns.

        Args:
            data (Union[DataFrame, Dict[str, Any]]): pandas dataframe or Dict which
                will be used for Number.
            column_name (str): column name in data.

        """
        if self.__data_column is None or isinstance(
            self.__color_spec, (Single, Palette)
        ):
            return

        if not self.__contains_key(data=data):
            raise ItemStylingValidationError(
                class_name=self.__class__.__name__,
                column_value=str(self.__data_column),
                column_name=column_name,
            )

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            self._api_type,
            colorSpec=build_color_spec(spec=self.__color_spec)
            if self.__color_spec
            else self.__color_spec,
            valueKey=build_templated_strings(items=self.__data_column),
            **self._build_extra_inputs(),
        )
