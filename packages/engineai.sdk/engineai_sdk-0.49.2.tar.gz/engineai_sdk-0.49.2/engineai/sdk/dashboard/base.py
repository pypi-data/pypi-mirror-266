"""Top-level package for Dashboard factories."""
import logging
from abc import ABC
from abc import abstractmethod
from typing import Any

logger = logging.getLogger(__name__)

HEIGHT_ROUND_VALUE = 2


class AbstractFactory(ABC):
    """Abstract Class implemented by all factories."""

    @abstractmethod
    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """


class AbstractLink:
    """Abstract class to implement links."""

    def __str__(self) -> str:
        return self._generate_templated_string()

    @property
    def link_component(self) -> Any:
        """Return link component.

        Widget for WidgetField
        Route for RouteLink
        """

    @abstractmethod
    def _generate_templated_string(self, *, selection: int = 0) -> str:
        """Generates template string to be used in dependency."""
