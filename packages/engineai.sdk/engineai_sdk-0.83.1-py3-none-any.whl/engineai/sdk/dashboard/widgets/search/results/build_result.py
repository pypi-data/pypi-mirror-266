"""Specs for build Search result."""

from typing import Any

from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.search.results.number import ResultNumberItem
from engineai.sdk.dashboard.widgets.search.results.text import ResultTextItem

from .typing import ResultItemType


def build_search_result(item: ResultItemType) -> Any:
    """Builds spec for dashboard API.

    Args:
        item: item spec

    Returns:
        Input object for Dashboard API
    """
    return generate_input(
        "SearchWidgetResultColumnUnionInput", **{_get_input_key(item): item.build()}
    )


def _get_input_key(item: ResultItemType) -> str:
    if isinstance(item, ResultNumberItem):
        return "number"
    elif isinstance(item, ResultTextItem):
        return "text"
    else:
        raise TypeError("item needs to be one of ResultTextItem, ResultNumberItem.")
