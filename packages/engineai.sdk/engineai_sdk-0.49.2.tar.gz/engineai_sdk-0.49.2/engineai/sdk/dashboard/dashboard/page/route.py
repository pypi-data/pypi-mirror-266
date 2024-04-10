"""Specs for dashboard Route."""
from typing import Any
from typing import Mapping

import pandas as pd
from beartype import beartype

from engineai.sdk.dashboard.dashboard.page.dependency import RouteDatastoreDependency
from engineai.sdk.dashboard.data.manager.manager import DependencyManager
from engineai.sdk.dashboard.data.manager.manager import RouteDataType
from engineai.sdk.dashboard.interface import RouteInterface
from engineai.sdk.dashboard.links import RouteLink
from engineai.sdk.dashboard.selected import Selected


class _Selected(Selected["Route", RouteLink, "Route"]):
    """Route Selected property configuration."""


class Route(DependencyManager, RouteInterface):
    """Specs for dashboard Route."""

    _DEPENDENCY_ID = "__ROUTE__"

    @beartype
    def __init__(
        self,
        data: RouteDataType,
        *,
        query_parameter: str,
    ) -> None:
        """Constructor for dashboard Route.

        Args:
            data (RouteDataType): data for the widget. Can be a
                pandas dataframe or Storage object if the data is to be retrieved
                from a storage.
            query_parameter (str): parameter that will be used to apply url queries.
        """
        super().__init__(data=data, base_path="route")
        self.__query_parameter = query_parameter
        self.__dependency: RouteDatastoreDependency = RouteDatastoreDependency(
            query_parameter=query_parameter,
            path=self._data.base_path + self._data.separator,
            dependency_id=self.dependency_id,
        )
        self.selected = _Selected(component=self)

    @property
    def data_id(self) -> str:
        """Returns data id."""
        return "route"

    @property
    def query_parameter(self) -> str:
        """Query parameter."""
        return self.__query_parameter

    def prepare(self, dashboard_slug: str) -> None:
        """Prepare page routing."""
        self.__dependency.prepare(dashboard_slug=dashboard_slug)

    def validate(self, data: pd.DataFrame, **_: Any) -> None:
        """Page routing has no validations to do."""

    def build(self) -> Mapping[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return {"dependency": self.__dependency.build()}
