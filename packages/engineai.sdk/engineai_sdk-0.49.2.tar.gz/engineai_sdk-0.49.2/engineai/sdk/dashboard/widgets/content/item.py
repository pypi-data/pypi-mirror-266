"""Spec for ContentItem class."""

from typing import Any
from typing import Union

from engineai.sdk.dashboard.utils import generate_input

from .markdown import MarkdownItem

ContentItem = Union[MarkdownItem]


def build_content_item(item: ContentItem) -> Any:
    """Builds item for Content Widget.

    Args:
        item (ContentItem): Item to build.

    Returns:
        Input object for Dashboard API
    """
    if isinstance(item, MarkdownItem):
        return generate_input("ContentWidgetItemInput", markdown=item.build())
    else:
        raise TypeError("Content `item` needs to be MarkdownItem.")
