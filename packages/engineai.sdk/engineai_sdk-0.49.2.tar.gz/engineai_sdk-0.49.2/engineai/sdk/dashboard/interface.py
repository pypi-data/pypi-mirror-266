"""Specs for Layout Package Interfaces."""
from typing import List

from engineai.sdk.dashboard.abstract.interface import DependencyInterface
from engineai.sdk.dashboard.abstract.layout import AbstractLayoutItem


class CardInterface(AbstractLayoutItem):
    """Specs for Card Interface."""


class CollapsibleInterface(AbstractLayoutItem):
    """Specs for Card Interface."""


class GridInterface(AbstractLayoutItem):
    """Specs for Grid Interface."""


class SelectableInterface(AbstractLayoutItem):
    """Specs for Selectable Interface."""


class WidgetInterface:
    """Interface for Widget instance."""


class RouteInterface:
    """Specs for Route Interface."""


class OperationInterface:
    """Specs for Operation Interface."""

    @property
    def dependencies(self) -> List[DependencyInterface]:
        """Returns operation id."""
        return []
