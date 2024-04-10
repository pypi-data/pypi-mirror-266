"""Spec for defining dependencies with a widget."""
from typing import Any
from typing import List
from typing import Optional

from engineai.sdk.dashboard.base import DependencyInterface
from engineai.sdk.dashboard.interface import OperationInterface as OperationItem
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

from .header import HttpHeader


class HttpDependency(DependencyInterface):
    """Specs base for defining the Widget Dependency."""

    _INPUT_KEY = "http"

    def __init__(
        self,
        *,
        path: TemplatedStringItem,
        host: str,
        headers: Optional[List[HttpHeader]] = None,
        operations: Optional[List[OperationItem]] = None,
    ):
        """Creates dependency with a widget.

        Args:
            path: path to the data.
            host: host of the data.
            headers: headers for the request.
            operations: operations to be performed on the data.

        Note: Only `application/json` are supported for `Content-Type` header.
        """
        super().__init__()
        self.__path = path
        self.__host = host
        self.__headers = headers
        self.__operations = operations
        self.__dependency_id = ""

    @property
    def dependency_id(self) -> str:
        """Return Dependency ID."""
        if self.__dependency_id == "":
            raise NotImplementedError("Dependency ID not set.")
        return self.__dependency_id

    @dependency_id.setter
    def dependency_id(self, dependency_id: str) -> None:
        """Set Dependency ID."""
        self.__dependency_id = dependency_id

    @property
    def operations(self) -> Optional[List[OperationItem]]:
        """Returns operations to be performed on the data."""
        return self.__operations

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Any: Input object for Dashboard API
        """
        return generate_input(
            "HttpDependencyInput",
            name=self.dependency_id,
            path=build_templated_strings(items=self.__path),
            host=self.__host,
            headers=[header.build() for header in self.__headers]
            if self.__headers is not None
            else None,
            operations=[operation.build() for operation in self.__operations]
            if self.__operations is not None
            else None,
        )
