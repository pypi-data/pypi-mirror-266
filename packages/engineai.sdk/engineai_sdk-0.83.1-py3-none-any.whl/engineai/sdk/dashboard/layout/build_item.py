"""Spec to build different nested Grid items."""

from typing import Any

from engineai.sdk.dashboard.utils import generate_input


def build_item(item: Any) -> Any:
    """Builds spec for dashboard API.

    Args:
        item (Any): item spec

    Returns:
        Input object for Dashboard API
    """
    return generate_input(
        "DashboardGridNestedItemUnionInput", **{item.input_key: item.build()}
    )
