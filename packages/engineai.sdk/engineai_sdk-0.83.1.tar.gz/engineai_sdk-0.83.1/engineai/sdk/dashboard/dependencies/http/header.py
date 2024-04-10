"""Specs for defining an Http Header."""
from typing import Any

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input


class HttpHeader(AbstractFactory):
    """Specs for defining an Http Header."""

    def __init__(self, key: str, value: str) -> None:
        """Constructor for HttpHeader class.

        Args:
            key: key of the header.
            value: value of the header.

        Note: Only `application/json` are supported for `Content-Type` header.
        """
        self.__key = key
        self.__value = value

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "HttpHeaderUnionInput",
            header=generate_input(
                "HttpHeaderInput", key=self.__key, value=self.__value
            ),
        )
