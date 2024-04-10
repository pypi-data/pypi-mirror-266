"""Spec for the layout Header component."""

from typing import Any
from typing import Generic
from typing import List
from typing import Optional
from typing import Union

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

from .chip import BaseChip
from .chip import RouteDependencyType
from .chip import SelectDependencyType


class BaseHeader(AbstractFactory, Generic[SelectDependencyType, RouteDependencyType]):
    """Spec for the layout Header component.

    This component is used in Card and CollapsibleSection components.
    """

    @beartype
    def __init__(
        self,
        *chips: BaseChip[SelectDependencyType, RouteDependencyType],
        title: Optional[str] = None,
    ):
        """Construct Header in layout.

        Args:
            chips: chips to be added to the header.
            title: Component title.
        """
        super().__init__()
        self.__title = title
        self.__chips = chips

    def has_title(self) -> bool:
        """Method to validate if header has title."""
        return self.__title is not None

    @property
    def dependencies(
        self,
    ) -> List[Union[SelectDependencyType, RouteDependencyType]]:
        """Method to generate the dependencies list from the elements of the class.

        Returns:
            List[CardSelectDependency]: List of dependencies.
        """
        dependencies_list = []
        for chip in self.__chips:
            dependencies_list.extend(chip.dependencies)
        return dependencies_list

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "DashboardGridCardHeaderInput",
            title=build_templated_strings(items=self.__title),
            context=[chip.build() for chip in self.__chips],
        )
