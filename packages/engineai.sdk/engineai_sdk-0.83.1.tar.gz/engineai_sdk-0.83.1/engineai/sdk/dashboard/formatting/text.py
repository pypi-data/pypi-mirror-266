"""Formatting spec for text."""

from typing import Any
from typing import Optional

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input


class TextFormatting(AbstractFactory):
    """Spec to format text."""

    def __init__(self, *, max_characters: int = 30, split: Optional[str] = None):
        """Spec to format text.

        Args:
            max_characters (int): number of characters to show before text is trimmed.
                If len(text) > max_characters, text is trimmed to max_characters and
                ... are added and full text shown on hover.
                Defaults to 30.
            split (Optional[str]): split character to determine first word.
                After split character, ... are added and full text shown on hover.
                Defaults to None.
        """
        super().__init__()
        self.__max_characters = max_characters
        self.__split = split

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "TextFormattingInput",
            maxCharacters=self.__max_characters,
            split=self.__split,
        )
