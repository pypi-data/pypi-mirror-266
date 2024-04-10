"""Typing for the dashboard SDK."""
from typing import Any
from typing import Dict
from typing import TypedDict

from typing_extensions import NotRequired

from engineai.sdk.internal.rubik import Rubik

from .selectable_widgets import AbstractSelectWidget


class PrepareParams(TypedDict):
    """Parameters for kwargs in prepare method."""

    # General
    dashboard_slug: str
    page: NotRequired[Any]
    storage: NotRequired[Rubik]
    selectable_widgets: NotRequired[Dict[str, AbstractSelectWidget]]
    write: NotRequired[bool]
