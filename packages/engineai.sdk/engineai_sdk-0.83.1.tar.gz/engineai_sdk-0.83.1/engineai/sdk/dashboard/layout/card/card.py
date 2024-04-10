"""Spec for a Card in a dashboard  grid layout."""

from typing import Any
from typing import List
from typing import Optional
from typing import Union

from typing_extensions import Unpack

from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem
from engineai.sdk.dashboard.abstract.typing import PrepareParams
from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.interface import CardInterface
from engineai.sdk.dashboard.interface import WidgetInterface as Widget
from engineai.sdk.dashboard.layout.build_item import build_item
from engineai.sdk.dashboard.layout.exceptions import ElementHeightNotDefinedError
from engineai.sdk.dashboard.layout.typings import LayoutItem
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.utils import generate_input

from ...base import DependencyInterface
from .header import CardHeader


class Card(CardInterface):
    """Spec for a Card in a dashboard layout."""

    _INPUT_KEY = "card"

    @type_check
    def __init__(
        self,
        *,
        content: Union[LayoutItem, List[LayoutItem]],
        header: Optional[Union[TemplatedStringItem, CardHeader]] = None,
    ) -> None:
        """Construct Card in dashboard layout.

        Args:
            content: content within the Card. One of Widget, Card, Grid,
                SelectableSection.
            header: Header card spec. Defaults to None, i.e. a card without title.

        Examples:
            ??? example "Create a Card layout and add a widget"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                from engineai.sdk.dashboard.layout import Card

                data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )

                Dashboard(content=Card(content=maps.Geo(data=data)))
                ```

            ??? example "Create a Card layout with multiple Widgets"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                from engineai.sdk.dashboard.layout import Card

                data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )

                Dashboard(
                    content=Card(content=[maps.Geo(data=data), maps.Geo(data=data)])
                )
                ```
        """
        super().__init__()
        self.__header = self._set_header(header)
        self.__content = self.__set_content(content)
        self.__height: Optional[Union[float, int]] = None

    @staticmethod
    def __set_content(
        content: Union[LayoutItem, List[LayoutItem]],
    ) -> LayoutItem:
        # pylint: disable=C0415
        """Sets content for Card."""
        from engineai.sdk.dashboard.layout.grid import Grid

        return Grid(*content) if isinstance(content, list) else content

    @property
    def height(self) -> Union[float, int]:
        """Returns height required by Card based on height required by underlying item.

        Returns:
            Union[float, int]: height required by Card
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

    def _set_header(
        self, header: Optional[Union[TemplatedStringItem, CardHeader]]
    ) -> CardHeader:
        if header is None:
            return CardHeader()
        elif isinstance(header, CardHeader):
            return header
        else:
            return CardHeader(title=header)

    def items(self) -> List[AbstractLayoutItem]:
        """Returns list of grid items that need to be inserted individually."""
        return self.__content.items()

    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare card.

        Args:
            **kwargs (Unpack[PrepareParams]): keyword arguments
        """
        self.__content.prepare(**kwargs)

    def prepare_heights(self, row_height: Optional[Union[float, int]] = None) -> None:
        """Prepare Selectable Layout heights."""
        if not isinstance(self.__content, Widget):
            self.__content.prepare_heights(row_height=row_height)

        self.__height = row_height or self.__content.height

    def __build_dependencies(self) -> List[Any]:
        """Build dependencies for Card."""
        dependencies = []
        for dependency in self.__header.dependencies:
            dependencies.append(self.__build_dependency(dependency))
        return dependencies

    @staticmethod
    def __build_dependency(dependency: DependencyInterface) -> Any:
        return generate_input(
            "DashboardGridCardDependencyUnionInput",
            **{dependency.input_key: dependency.build()},
        )

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "DashboardGridCardInput",
            item=build_item(self.__content),
            header=self.__header.build(),
            dependencies=self.__build_dependencies(),
        )
