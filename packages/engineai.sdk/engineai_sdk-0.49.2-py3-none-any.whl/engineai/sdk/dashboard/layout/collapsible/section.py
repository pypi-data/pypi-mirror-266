"""Spec for a Collapsible Section in a dashboard grid layout."""

from typing import Any
from typing import List
from typing import Optional
from typing import Union

from beartype import beartype
from typing_extensions import Unpack

from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem
from engineai.sdk.dashboard.abstract.typing import PrepareParams
from engineai.sdk.dashboard.dependencies.route import CollapsibleSectionRouteDependency
from engineai.sdk.dashboard.dependencies.widget import (
    CollapsibleSectionSelectDependency,
)
from engineai.sdk.dashboard.interface import CollapsibleInterface
from engineai.sdk.dashboard.interface import WidgetInterface as Widget
from engineai.sdk.dashboard.layout.build_item import build_item
from engineai.sdk.dashboard.layout.exceptions import ElementHeightNotDefinedError
from engineai.sdk.dashboard.layout.grid import Grid
from engineai.sdk.dashboard.layout.typings import LayoutItem
from engineai.sdk.dashboard.utils import generate_input

from .header import CollapsibleSectionHeader


class CollapsibleSection(CollapsibleInterface):
    """Spec for a Collapsible Section in a dashboard layout."""

    _INPUT_KEY = "collapsible"

    @beartype
    def __init__(
        self,
        *,
        content: Union[LayoutItem, List[LayoutItem]],
        header: Optional[Union[str, CollapsibleSectionHeader]] = None,
        expanded: bool = True,
    ) -> None:
        """Construct Collapsible Section in dashboard layout.

        CollapsibleSection is only supported in the root level in each Page.

        Args:
            content: content within the Section. One of Widget, Card, Grid,
                SelectableSection.
            header: Header specifications. By default the CollapsibleSection does
                not have title
            expanded: Whether the section is expanded or not.

        Examples:
            ??? example "Create a Collapsible Section layout and add a widget"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                from engineai.sdk.dashboard import layout

                data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )

                Dashboard(content=layout.CollapsibleSection(
                    content=maps.Geo(data=data))
                )
                ```

            ??? example "Create a Collapsible Section layout with multiple Widgets"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                from engineai.sdk.dashboard import layout

                data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )

                Dashboard(
                    content=layout.CollapsibleSection(content=[
                        maps.Geo(data=data),
                        maps.Geo(data=data)
                    ])
                )
                ```

        """
        super().__init__()
        self.__header = self._set_header(header)
        self.__content = self.__set_content(content)
        self.__height: Optional[Union[float, int]] = None
        self.__expanded = expanded

    @property
    def force_height(self) -> bool:
        """Get if the Section has a forced height."""
        return False

    @staticmethod
    def __set_content(
        content: Union[LayoutItem, List[LayoutItem]],
    ) -> LayoutItem:
        # pylint: disable=C0415
        """Sets content for Section."""
        return Grid(*content) if isinstance(content, list) else content

    @property
    def height(self) -> Union[float, int]:
        """Returns height required by Section based on underlying item height.

        Returns:
            Union[float, int]: height required by Section
        """
        if self.__height is None:
            raise ElementHeightNotDefinedError()
        return self.__height

    @property
    def has_custom_heights(self) -> bool:
        """Returns if the Item has custom heights in its inner components."""
        return (
            False
            if isinstance(self.__content, Widget)
            else self.__content.has_custom_heights
        )

    @property
    def dependencies(
        self,
    ) -> List[
        Union[CollapsibleSectionSelectDependency, CollapsibleSectionRouteDependency]
    ]:
        """Returns the Section underlying item."""
        return self.__header.dependencies

    def _set_header(
        self, header: Optional[Union[str, CollapsibleSectionHeader]]
    ) -> CollapsibleSectionHeader:
        if header is None:
            return CollapsibleSectionHeader()
        elif isinstance(header, str):
            return CollapsibleSectionHeader(title=header)
        else:
            return header

    def items(self) -> List[AbstractLayoutItem]:
        """Returns list of grid items that need to be inserted individually."""
        return self.__content.items()

    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare Section.

        Args:
            **kwargs (Unpack[PrepareParams]): keyword arguments
        """
        self.__content.prepare(**kwargs)

    def prepare_heights(self, row_height: Optional[Union[float, int]] = None) -> None:
        """Prepare Selectable Layout heights."""
        if not isinstance(self.__content, Widget):
            self.__content.prepare_heights(row_height=row_height)

        self.__height = row_height or self.__content.height

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "DashboardCollapsibleCardInput",
            item=build_item(self.__content),
            height=self.height,
            header=self.__header.build(),
            expanded=self.__expanded,
            dependencies=[dependency.build() for dependency in self.dependencies],
        )
