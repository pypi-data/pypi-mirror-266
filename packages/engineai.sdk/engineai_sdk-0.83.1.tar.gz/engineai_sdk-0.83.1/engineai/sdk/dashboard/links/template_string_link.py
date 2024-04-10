"""Class that represents one of the possible Links after being stringify."""
from typing import Any
from typing import Optional
from typing import Union

from ..abstract.selectable_widgets import AbstractSelectWidget
from ..interface import RouteInterface
from .route_link import RouteLink


class TemplateStringLink:
    """Class that represents one of the possible Links after being stringify."""

    def __init__(self, template: str) -> None:
        """Construct for TemplateStringLink class.

        Args:
            template (str): String representing the link associated.
        """
        self.__route_field: Optional[str] = self._extract_field(
            template, "__ROUTE__.0."
        )
        self.__widget_id: Optional[str] = self._extract_widget_id(template)
        self.__component: Optional[Union[AbstractSelectWidget, RouteInterface]] = None

    @staticmethod
    def _extract_field(template: str, prefix: str) -> Optional[str]:
        return template.replace(prefix, "") if prefix in template else None

    @staticmethod
    def _extract_widget_id(template: str) -> Optional[str]:
        return (
            template.split(".")[0]
            if "__QUERY__" not in template and "__ROUTE__" not in template
            else None
        )

    @property
    def widget_id(self) -> str:
        """Returns Widget Id."""
        if self.__widget_id is None:
            raise ValueError("No Widget ID set.")
        return self.__widget_id

    @widget_id.setter
    def widget_id(self, widget_id: str) -> None:
        """Sets new Widget Id."""
        self.__widget_id = widget_id

    @property
    def component(self) -> Any:
        """Returns Widget."""
        if self.__component is None:
            raise ValueError("No SelectWidget nor Route set.")
        return self.__component

    @component.setter
    def component(self, component: Union[AbstractSelectWidget, RouteInterface]) -> None:
        """Sets Widget."""
        self.__component = component

    @property
    def route_link(self) -> RouteLink:
        """Returns Dashboard Route Link."""
        if self.__route_field is None:
            raise ValueError("No Dashboard Route Link set.")
        return RouteLink(field=self.__route_field, route=self.component)

    def is_widget_field(self) -> bool:
        """Returns if the TemplateStringLink is a WidgetField."""
        return self.__widget_id is not None

    def is_route_link(self) -> bool:
        """Returns if the TemplateStringLink is a DashboardRouteLink."""
        return self.__route_field is not None
