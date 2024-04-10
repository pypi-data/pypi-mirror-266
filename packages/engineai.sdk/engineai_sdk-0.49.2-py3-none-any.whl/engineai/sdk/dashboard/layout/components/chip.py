"""Spec for the layout chip component."""

from typing import Any
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar
from typing import Union
from typing import get_args

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.dependencies.route import CardRouteDependency
from engineai.sdk.dashboard.dependencies.route import CollapsibleSectionRouteDependency
from engineai.sdk.dashboard.dependencies.widget import CardSelectDependency
from engineai.sdk.dashboard.dependencies.widget import (
    CollapsibleSectionSelectDependency,
)
from engineai.sdk.dashboard.layout.components.label import build_context_label
from engineai.sdk.dashboard.links import RouteLink
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

SelectDependencyType = TypeVar(
    "SelectDependencyType", CardSelectDependency, CollapsibleSectionSelectDependency
)

RouteDependencyType = TypeVar(
    "RouteDependencyType", CardRouteDependency, CollapsibleSectionRouteDependency
)


class BaseChip(AbstractFactory, Generic[SelectDependencyType, RouteDependencyType]):
    """Spec for the layout chip component.

    This component is used in Card and CollapsibleSection components.
    """

    @beartype
    def __init__(
        self,
        *,
        label: Union[str, GenericLink],
        tooltip_text: Optional[List[TemplatedStringItem]] = None,
        separator: str = "-",
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        """Constructor for BaseChip.

        Args:
            label: Header label value. Can assume a static label or a single
                GenericLink.
            tooltip_text: informational pop up text. Each element of list is displayed
                as a separate paragraph. Can only use this option if the `label` is
                set.
            separator: label separator in case of a List of WidgetLinks
            prefix: prefix value to use in before each label.
            suffix: suffix value to use in after each label.
        """
        super().__init__()
        self.__tooltip_text = tooltip_text or []
        self.__label = label
        self.__separator = separator
        self.__prefix = prefix
        self.__suffix = suffix
        self.__set_dependencies_class()

    @classmethod
    def __set_dependencies_class(cls) -> None:
        """Set dependencies class."""
        # This was a trick found at
        # https://stackoverflow.com/questions/57706180/generict-base-class-how-to-get-type-of-t-from-within-instance
        # With this we can access cls and get those classes that were defined in the
        # Generic class.

        # The zero here points to the current generic data. If, in the future, we have
        # to change the parents class, we need to make sure that this index is correct.
        cls._SelectDependencyType, cls._RouteDependencyType = get_args(
            cls.__orig_bases__[0]
        )

    @classmethod
    # TODO: Add page dependency
    def _generate_label_dependency(
        cls,
        label: GenericLink,
    ) -> Union[SelectDependencyType, RouteDependencyType]:
        if isinstance(label, WidgetField):
            return cls._SelectDependencyType(
                dependency_id=label.dependency.dependency_id,
                widget_id=label.dependency.widget_id,
            )

        return cls._RouteDependencyType(
            dependency_id=label.dependency.dependency_id,
            field=label.field,
        )

    @property
    def dependencies(self) -> List[Union[SelectDependencyType, RouteDependencyType]]:
        """Method to generate the dependencies list from the elements of this class."""
        return (
            [
                self._generate_label_dependency(
                    label=self.__label,
                )
            ]
            if isinstance(self.__label, (WidgetField, RouteLink))
            else []
        )

    def build(self) -> Any:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "DashboardGridCardHeaderContextInput",
            label=build_context_label(
                label=self.__label,
                separator=self.__separator,
                prefix=self.__prefix,
                suffix=self.__suffix,
            ),
            tooltipText=[
                build_templated_strings(items=tooltip)
                for tooltip in self.__tooltip_text
            ],
        )
