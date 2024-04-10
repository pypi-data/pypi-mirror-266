"""Class to manage component's data and dependencies."""
import re
from copy import copy
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union
from typing import cast

import pandas as pd
from typing_extensions import Unpack

from engineai.sdk.dashboard.abstract.selectable_widgets import AbstractSelectWidget
from engineai.sdk.dashboard.abstract.typing import PrepareParams
from engineai.sdk.dashboard.dependencies import WidgetSelectDependency
from engineai.sdk.dashboard.links import RouteLink
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.widgets.exceptions import WidgetTemplateStringWidgetNotFound

from ...abstract.interface import DependencyInterface
from ...dependencies.datastore import DashboardStorage
from ..decorator import DataSource
from ..decorator import OperationItem
from .interface import DependencyManagerInterface
from .interface import StaticDataType

WidgetDataType = Union[DataSource, StaticDataType]

RouteDataType = Union[DataSource, pd.DataFrame]


class DependencyManager(AbstractFactoryLinkItemsHandler, DependencyManagerInterface):
    """Class to manage component's data and dependencies."""

    def __init__(
        self,
        data: Optional[Union[WidgetDataType, RouteDataType]] = None,
        base_path: Optional[str] = None,
    ) -> None:
        """Constructor to manage components data.

        Args:
            data: data for the widget.
                Can be a pandas dataframe or a dictionary depending on the widget type,
                or Storage object if the data is to be retrieved from a storage.
            base_path: data base path.
        """
        super().__init__()
        self.__dependencies: Set[DependencyInterface] = set()
        self._data = self.__set_data(data=data, base_path=base_path)

    def __set_data(
        self,
        data: Optional[Union[WidgetDataType, RouteDataType]],
        base_path: Optional[str] = None,
    ) -> Optional[DataSource]:
        if data is None:
            return None
        data = (
            data
            if isinstance(data, DataSource)
            else DataSource(data, base_path=base_path)
        )
        data.component = self
        return data

    @property
    def data(self) -> Set[DataSource]:
        """Returns data of widget.

        Returns:
            WidgetDataType: data of widget
        """
        return self.get_data_sources()

    def _prepare_dependencies(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepares dependencies for widget."""
        page_id = re.sub(r"\W+", "", kwargs["page"].path)
        self.__set_internal_data_field()
        self.__set_template_links_widgets(
            **kwargs,
        )
        self.__set_storage()
        self.__prepare_template_dependencies()
        self.__prepare_route_dependencies()
        self.__prepare_widget_fields()
        self.__prepare_widget_dependencies(page_id)

    def store_data(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Stores data in widget.

        Args:
            kwargs (dict): keyword arguments
        """
        for data_source in self.get_data_sources():
            data_source(
                storage=kwargs["storage"],
                write_keys=kwargs["write"],
            )

    def build_datastore_dependencies(self) -> List[Any]:
        """Build datastore dependencies."""
        return [dependency.build() for dependency in self.__dependencies]

    def __prepare_widget_dependencies(self, page_id: str) -> None:
        for dependency in self.__dependencies:
            if (
                isinstance(dependency, WidgetSelectDependency)
                and page_id
                and not dependency.widget_id.endswith(page_id)
            ):
                dependency.widget_id = f"{dependency.widget_id}_{page_id}"

    def __prepare_widget_fields(self) -> None:
        for widget_field in self.get_widget_fields():
            dependency = widget_field.link_component.select_dependency()
            self.__dependencies.add(cast(WidgetSelectDependency, dependency))

    def __prepare_template_dependencies(self) -> None:
        for template_link in self.get_template_links():
            if template_link.is_widget_field():
                dependency = template_link.component.select_dependency(
                    dependency_id=template_link.widget_id
                )

                self.__dependencies.add(
                    cast(
                        WidgetSelectDependency,
                        dependency,
                    )
                )
            elif template_link.is_route_link():
                route_link = template_link.route_link
                self.__dependencies.add(route_link.dependency)

    def __prepare_route_dependencies(self) -> None:
        for route_link in self.get_route_links():
            self.__dependencies.add(route_link.dependency)

    def __set_internal_data_field(self) -> None:
        for internal_data_field in self.get_internal_data_fields():
            if internal_data_field.dependency_id == "":
                internal_data_field.set_dependency_id(dependency_id=self.dependency_id)

    def __set_template_links_widgets(
        self,
        **kwargs: Unpack[PrepareParams],
    ) -> None:
        dashboard_slug = kwargs["dashboard_slug"]
        selectable_widgets: Dict[str, AbstractSelectWidget] = kwargs[
            "selectable_widgets"
        ]
        for template_link in self.get_template_links():
            if template_link.is_widget_field():
                if template_link.widget_id not in selectable_widgets:
                    raise WidgetTemplateStringWidgetNotFound(
                        slug=dashboard_slug,
                        widget_id=self.data_id,
                        template_widget_id=template_link.widget_id,
                    )
                template_link.component = cast(
                    AbstractSelectWidget,
                    selectable_widgets.get(template_link.widget_id),
                )
            elif template_link.is_route_link():
                template_link.component = kwargs["page"].route

    def __set_storage(self) -> None:
        """Sets the data storage based on widget dependency id(s)."""
        for data_source in self.get_data_sources():
            self.__add_link_dependencies(data_source=data_source)
            self.__dependencies.add(
                DashboardStorage(
                    dependency_id=data_source.component.dependency_id,
                    series_id=self.__generate_series_id(data_source),
                    operations=data_source.operations,
                )
            )
            if data_source.operations is not None:
                self.__add_operations_dependencies(
                    operations=data_source.operations,
                )

    @staticmethod
    def __generate_series_id(data_source: DataSource) -> str:
        if len(data_source.args) > 0:
            store_id_templates: List[str] = [str(link) for link in data_source.args]

            series_id = (
                store_id_templates[0]
                if len(store_id_templates) == 1
                else data_source.separator.join(store_id_templates)
            )
            return f"{data_source.base_path}/{series_id}"
        else:
            return data_source.base_path

    def __add_link_dependencies(self, data_source: DataSource) -> None:
        for link in data_source.args:
            if isinstance(link, WidgetField):
                dependency = cast(
                    WidgetSelectDependency, link.link_component.select_dependency()
                )
                self.__dependencies.add(dependency)

            elif isinstance(link, RouteLink):
                new_link = copy(link)
                new_link.dependency.path = data_source.base_path
                self.__dependencies.add(new_link.dependency)

    def __add_operations_dependencies(
        self,
        operations: List[OperationItem],
    ) -> None:
        for operation in operations:
            for dependency in operation.dependencies:
                self.__dependencies.add(dependency)
