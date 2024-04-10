"""Spec for SingleColor class."""

from typing import Any

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input

from .palette import Palette


class Single(AbstractFactory):
    """Creates a class for a single color."""

    @beartype
    def __init__(self, color: Palette):
        """Construct method for ColorSingle class.

        Args:
            color: a color from Palette.
        """
        super().__init__()
        self.__color = color.color

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "ColorSingleInput",
            customColor=self.__color,
        )
