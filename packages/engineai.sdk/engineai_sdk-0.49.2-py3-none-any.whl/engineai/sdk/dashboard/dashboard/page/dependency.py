"""Specs for Dashboard Route Datastore Dependency."""

from typing import Any

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input


class RouteDatastoreDependency(AbstractFactory):
    """Specs for Dashboard Route Datastore Dependency."""

    @beartype
    def __init__(
        self,
        *,
        dependency_id: str,
        path: str,
        query_parameter: str,
    ) -> None:
        """Construct for DashboardRouteDatastoreDependency class.

        Args:
            dependency_id (str): Dependency ID.
            path (str): Datastore path.
            query_parameter (str): query parameter to select the series.
        """
        self.__dependency_id = dependency_id
        self.__query_parameter = query_parameter
        self.__path = path
        self.__dashboard_slug: str = ""

    def prepare(self, dashboard_slug: str) -> None:
        """Prepare route."""
        self.__dashboard_slug = dashboard_slug

    @property
    def store_id(self) -> str:
        """Returns store_id associated with dependency.

        Returns:
            str: store id
        """
        return self.__dashboard_slug.replace("_", "-")

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "DashboardPageUrlQueryApiDependencyInput",
            name=self.__dependency_id,
            storeId=self.store_id,
            seriesIdPrefix=self.__path,
            seriesIdQueryKey=self.__query_parameter,
        )
