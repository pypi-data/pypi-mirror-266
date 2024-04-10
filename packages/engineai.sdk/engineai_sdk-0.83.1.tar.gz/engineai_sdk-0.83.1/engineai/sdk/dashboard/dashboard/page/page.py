"""DashboardPage spec."""
from typing import Any
from typing import Final
from typing import List
from typing import Optional
from typing import Union

from typing_extensions import Unpack

from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem
from engineai.sdk.dashboard.abstract.selectable_widgets import AbstractSelectWidget
from engineai.sdk.dashboard.abstract.typing import PrepareParams
from engineai.sdk.dashboard.dashboard.exceptions import (
    DashboardDuplicatedWidgetIdsError,
)
from engineai.sdk.dashboard.dashboard.typings import DashboardContent
from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.interface import CollapsibleInterface
from engineai.sdk.dashboard.interface import WidgetInterface as Widget
from engineai.sdk.dashboard.layout.card.card import Card
from engineai.sdk.dashboard.layout.grid import Grid
from engineai.sdk.dashboard.layout.selectable.base import SelectableSection
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

from ...base import DependencyInterface
from ...links import RouteLink
from .dependency import RouteDatastoreDependency
from .root import RootGrid
from .route import Route

ROW_HEIGHT_PIXELS: Final[int] = 100


class Page:
    """Dashboard Page spec."""

    @type_check
    def __init__(
        self,
        *,
        name: TemplatedStringItem,
        content: DashboardContent,
        route: Optional[Route] = None,
        path: str = "/",
    ):
        """Page class constructor.

        Args:
            name: Dashboard name to be displayed. Defaults to slug
                title case.
            content: Dashboard content.
            route: Specs for Page routing.
            path: page endpoint path.
        """
        self.__name = name
        self.__generate_content(content)
        self.__path = path
        self.__dashboard_slug = ""
        self.__route = route

    @property
    def widgets(self) -> List[Widget]:
        """Get page widgets."""
        return [w for w in self._items() if isinstance(w, Widget)]

    @property
    def route(self) -> Optional[Route]:
        """Get page route."""
        return self.__route

    @property
    def path(self) -> str:
        """Returns page path."""
        return self.__path

    def _items(self) -> List[AbstractLayoutItem]:
        """Returns list of grid items that need to be inserted individually.

        Returns:
            List[DashboardVerticalGridItem]: list of grid items in layout
        """
        return self.__grid.items()

    def __generate_content(self, content: DashboardContent) -> None:
        self.__grid: RootGrid
        if isinstance(
            content, (Grid, Widget, SelectableSection, Card, CollapsibleInterface)
        ):
            self.__grid = RootGrid(content)
        elif isinstance(content, list):
            self.__grid = RootGrid(*content)
        else:
            raise NotImplementedError(
                f"Page content of type {type(content)} is not supported."
            )

    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare layout for building."""
        self.__dashboard_slug = kwargs["dashboard_slug"]
        kwargs["selectable_widgets"] = {
            w.widget_id: w for w in self._items() if isinstance(w, AbstractSelectWidget)
        }
        kwargs["page"] = self
        self.__grid.prepare_heights()
        self.__grid.prepare(**kwargs)

        if self.__route is not None:
            self.__route.prepare(**kwargs)

    def validate(self) -> None:
        """Validates layout spec."""
        dashboard_widget_ids = [
            w.widget_id for w in self._items() if isinstance(w, Widget)
        ]

        duplicated_widget_ids = []
        for widget_id in set(dashboard_widget_ids):
            if dashboard_widget_ids.count(widget_id) > 1:
                duplicated_widget_ids.append(widget_id)
        if duplicated_widget_ids:
            raise DashboardDuplicatedWidgetIdsError(
                slug=self.__dashboard_slug, widget_ids=duplicated_widget_ids
            )

    def _build_content(self) -> Any:
        return {
            "grid": generate_input(
                "DashboardPageContentGridInput",
                rowHeightPixels=ROW_HEIGHT_PIXELS,
                rootGrid=self.__grid.build(),
            )
        }

    def __build_dependencies(self) -> Any:
        dependencies = set()
        if self.__route is not None:
            for dependency in self.__route.dependency:
                dependencies.add(dependency)

        if not isinstance(self.__name, (str, RouteLink)):
            dependencies.add(self.__name.dependency)

        return [self.__build_dependency(dependency) for dependency in dependencies]

    @staticmethod
    def __build_dependency(
        dependency: Union[RouteDatastoreDependency, DependencyInterface]
    ) -> Any:
        return generate_input(
            "DashboardPageDependencyUnionInput",
            **{dependency.input_key: dependency.build()},
        )

    def build(self) -> Any:
        """Builds spec for Dashboard Page."""
        return generate_input(
            "DashboardPageInput",
            path=self.__path,
            name=build_templated_strings(items=self.__name),
            content=self._build_content(),
            selectable=False,
            searchable=False,
            controlBar=None,
            entities=[],
            dependencies=self.__build_dependencies(),
        )
