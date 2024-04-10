"""Spec for defining a dependency with a widget."""

from typing import Any
from typing import Generator
from typing import Optional
from typing import Tuple

from engineai.sdk.dashboard.abstract.interface import DependencyInterface
from engineai.sdk.dashboard.utils import generate_input


class BaseRouteDependency(DependencyInterface):
    """Spec for defining a dependency with a datastore."""

    API_DEPENDENCY_INPUT: Optional[str] = None

    def __init__(self, *, dependency_id: str, field: str):
        """Creates dependency with a series in a datastore.

        Args:
            dependency_id (str): id of dependency (to be used in other dependencies)
            field (str): field ID inside the datastore.
        """
        self.__dependency_id = dependency_id
        self.__field_id = field
        self.__path: str = ""

    def __iter__(self) -> Generator[Tuple[str, str], None, None]:
        yield "field_id", self.__field_id

    def __hash__(self) -> int:
        return hash(self.__dependency_id)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and (
            self.dependency_id == other.dependency_id
        )

    @property
    def api_dependency_input(self) -> str:
        """Return the API input to cast in api types during build."""
        if self.API_DEPENDENCY_INPUT is None:
            raise NotImplementedError(
                f"Class {self.__class__.__name__}.API_DEPENDENCY_INPUT not defined."
            )
        return self.API_DEPENDENCY_INPUT

    @property
    def path(self) -> str:
        """Get Datastore Path."""
        return self.__path

    @path.setter
    def path(self, path: str) -> None:
        """Set Datastore Path."""
        self.__path = path

    @property
    def dependency_id(self) -> str:
        """Get Dependency ID."""
        return self.__dependency_id

    @property
    def field_id(self) -> str:
        """Get Field ID."""
        return self.__field_id

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Any: Input object for Dashboard API
        """
        return generate_input(
            self.api_dependency_input,
            dashboardPage=generate_input(
                "DashboardPageVariableDependencyInput",
                name=self.__dependency_id,
            ),
        )


class RouteDependency(BaseRouteDependency):
    """Spec for defining a dependency with a datastore."""

    API_DEPENDENCY_INPUT = "WidgetOwnedDependencyUnionInput"


class CardRouteDependency(BaseRouteDependency):
    """Spec for defining a dependency with a datastore."""

    API_DEPENDENCY_INPUT = "DashboardGridCardDependencyUnionInput"


class CollapsibleSectionRouteDependency(CardRouteDependency):
    """Spec for defining a dependency with a datastore."""

    API_DEPENDENCY_INPUT = "DashboardCollapsibleCardDependencyUnionInput"
