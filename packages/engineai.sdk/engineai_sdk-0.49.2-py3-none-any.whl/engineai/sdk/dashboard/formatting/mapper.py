"""Formatting spec for Key/Value."""

from typing import Any
from typing import Mapping

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input


class MapperFormatting(AbstractFactory):
    """Factory class to map a column with ordinal numbers to text."""

    def __init__(self, *, mapping: Mapping[int, str]):
        """Spec to format numbers that represent categories.

        Args:
            mapping (Mapping[int, str]): mapping between number and text label.
        """
        super().__init__()
        self.__mapping = mapping

    @property
    def mapping(self) -> Mapping[int, str]:
        """Returns formatting mapping between integer numbers and labels.

        Returns:
            Mapping[int, str]: formatting mapping
        """
        return self.__mapping

    def _build_mapping(self) -> Any:
        return [
            generate_input("KeyValueInput", key=str(key), value=self.__mapping[key])
            for key in self.__mapping
        ]

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return generate_input("MapperFormattingInput", mapping=self._build_mapping())
