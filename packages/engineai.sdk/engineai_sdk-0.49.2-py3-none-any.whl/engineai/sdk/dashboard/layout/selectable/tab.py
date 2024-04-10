"""Specs for Tab and TabSection."""

from typing import Any
from typing import List
from typing import Optional
from typing import Union

from beartype import beartype

from engineai.sdk.dashboard.layout.build_item import build_item
from engineai.sdk.dashboard.layout.typings import LayoutItem
from engineai.sdk.dashboard.links.widget_field import WidgetField
from engineai.sdk.dashboard.styling.icons import Icons
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

from .base import SelectableItem
from .base import SelectableSection


class Tab(SelectableItem):
    """Specs for tab in a tab section."""

    @beartype
    def __init__(
        self,
        *,
        label: TemplatedStringItem,
        content: Union[LayoutItem, List[LayoutItem]],
        icon: Optional[Union[Icons, WidgetField]] = None,
        default_selected: bool = False,
    ):
        """Construct tab for tab section dashboard vertical grid layout.

        Args:
            label: label to be displayed in tab.
            content: item to be added in tab.
            icon: tab icon.
            default_selected: set tab as default selected.
        """
        super().__init__(
            label=label, content=content, default_selected=default_selected
        )
        self.__icon = icon

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec."""
        return generate_input(
            "DashboardGridTabSectionOptionInput",
            label=build_templated_strings(items=self.label),
            item=build_item(self.item),
            icon=build_templated_strings(
                items=self.__icon.value
                if isinstance(self.__icon, Icons)
                else self.__icon
            )
            if self.__icon is not None
            else None,
            preSelected=self.default_selected,
        )


class TabSection(SelectableSection):
    """Spec for tab section in the layout."""

    _API_TYPE = "tabSection"
    _INPUT_KEY = "tabSection"

    @beartype
    def __init__(
        self,
        *tabs: Tab,
    ):
        """Construct for TabSection class.

        Args:
            tabs: tabs to be added to tab section.

        Examples:
            ??? example "Create a TabSection with different tabs"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import maps
                from engineai.sdk.dashboard.layout import TabSection
                from engineai.sdk.dashboard.layout import Tab
                from engineai.sdk.dashboard.layout import Grid
                from engineai.sdk.dashboard.layout import Row

                data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )

                tab_1 = Tab(label="One Widget", content=maps.Geo(data=data))
                tab_2 = Tab(
                    label="Multiple Widgets",
                    content=[maps.Geo(data=data), maps.Geo(data=data)]
                )
                tab_3 = Tab(
                    label="Multiple Widgets - Different Layout",
                    content=Grid(Row(maps.Geo(data=data), maps.Geo(data=data)))
                )

                Dashboard(content=TabSection(tab_1, tab_2, tab_3))
                ```
        """
        super().__init__()
        self._add_items(*tabs)

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "DashboardGridTabSectionInput",
            options=[tab.build() for tab in self._items],
        )
