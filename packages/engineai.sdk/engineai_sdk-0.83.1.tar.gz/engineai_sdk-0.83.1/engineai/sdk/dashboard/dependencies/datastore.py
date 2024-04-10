"""Spec for defining a dependency with a widget."""

from typing import Any
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from engineai.sdk.dashboard.base import DependencyInterface
from engineai.sdk.dashboard.interface import OperationInterface as OperationItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input


class BaseStorage(DependencyInterface):
    """Spec for defining a dependency with a datastore."""

    _API_TYPE: Optional[str] = None

    def __init__(
        self,
        *,
        dependency_id: str,
        series_id: str,
        operations: Optional[List[OperationItem]] = None,
    ):
        """Creates dependency with a series in a datastore.

        Args:
            dependency_id: id of dependency (to be used in other dependencies)
            series_id: id of series in datastore.
                Defaults to empty string.
            operations: list of operations to be applied to data.
        """
        super().__init__()
        self.__dependency_id = dependency_id
        self.__series_id = series_id
        self.__operations = operations or []

    def __iter__(self) -> Generator[Tuple[str, str], None, None]:
        yield "dependency_id", self.__dependency_id
        yield "series_id", self.__series_id

    def __hash__(self) -> int:
        return hash(f"{self.__dependency_id}_{self.__series_id}")

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, type(self))
            and self.__series_id == other.series_id
            and self.__dependency_id == other.dependency_id
        )

    @property
    def dependency_id(self) -> str:
        """Returns dependency id.

        Returns:
            str: dependency
        """
        return self.__dependency_id

    @property
    def series_id(self) -> str:
        """Returns series id.

        Returns:
            str: series id
        """
        return self.__series_id

    @property
    def api_type(self) -> str:
        """Returns API type.

        Returns:
            str: API type
        """
        if self._API_TYPE is None:
            raise NotImplementedError(
                f"Class {self.__class__.__name__}._API_TYPE not defined."
            )
        return self._API_TYPE

    def prepare(self, route_dependency_id: str) -> None:
        """Prepare dependency."""
        if len(route_dependency_id) > 0:
            self.__series_id = f"{self.__series_id}/{{{{{route_dependency_id}}}}}"

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Any: Input object for Dashboard API
        """
        return generate_input(
            self.api_type,
            fileName=build_templated_strings(items=self.__series_id),
            name=self.__dependency_id,
            operations=[operation.build() for operation in self.__operations],
        )


class DashboardBlobStorage(BaseStorage):
    """Spec for defining a dependency with a datastore."""

    _INPUT_KEY = "dashboardSelfBlobStore"
    _API_TYPE = "DashboardStoreSelfBlobDependencyInput"


class DashboardFileShareStorage(BaseStorage):
    """Spec for defining a dependency with a datastore."""

    _INPUT_KEY = "azureFileShareSelfStorage"
    _API_TYPE = "AzureFileShareStorageSelfDependencyInput"


DashboardStorage = Union[DashboardBlobStorage, DashboardFileShareStorage]
