"""Spec for a Fluid Row item."""

from typing import Any
from typing import Union

from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.search.search import Search
from engineai.sdk.dashboard.widgets.select.select import Select
from engineai.sdk.dashboard.widgets.toggle.toggle import Toggle

DashboardFluidRowItem = Union[Select, Toggle, Search]


def build_fluid_item(item: DashboardFluidRowItem) -> Any:
    """Method implemented by all factories to generate Input spec.

    Args:
        item (DashboardFluidRowItem): Fluid row item spec.

    Returns:
        Input object for Dashboard API
    """
    return generate_input(
        "DashboardFluidRowItemUnionInput",
        widget=_build_fluid_widget_item(item),
    )


def _build_fluid_widget_item(item: DashboardFluidRowItem) -> Any:
    return generate_input(
        "DashboardFluidRowItemWidgetInput",
        widgetId=item.widget_id,
        dependencies=item.build_datastore_dependencies(),
        title=None,
        widgetType=_build_widget_input(item),
    )


def _build_widget_input(item: DashboardFluidRowItem) -> Any:
    return generate_input(
        "DashboardFluidRowItemWidgetUnionInput",
        **{_get_input_key(item): item.build_widget_input()},
    )


def _get_input_key(item: DashboardFluidRowItem) -> str:
    if isinstance(item, Select):
        result = "select"
    elif isinstance(item, Toggle):
        result = "toggle"
    elif isinstance(item, Search):
        result = "search"
    else:
        raise NotImplementedError(
            f"Build for Fluid Row Item with class "
            f"{item.__class__.__name__} not implemented."
        )
    return result
