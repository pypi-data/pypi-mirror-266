"""Spec for defining dependencies with a widget."""

from engineai.sdk.dashboard.abstract.widget_dependencies import AbstractWidgetDependency


class WidgetSelectDependency(AbstractWidgetDependency):
    """Spec for defining a dependency with a widget."""

    API_DEPENDENCY_INPUT = "WidgetOwnedDependencyUnionInput"

    def __init__(self, *, dependency_id: str, widget_id: str):
        """Creates dependency with a widget.

        Args:
            dependency_id (str): id of dependency (to be used in other dependencies)
            widget_id (str): id of widget to associate dependency with
        """
        super().__init__(
            dependency_id=dependency_id, widget_id=widget_id, path="selected"
        )


class CardSelectDependency(AbstractWidgetDependency):
    """Spec for defining a dependency with a card."""

    API_DEPENDENCY_INPUT = "DashboardGridCardDependencyUnionInput"

    def __init__(self, *, dependency_id: str, widget_id: str):
        """Creates dependency with a widget.

        Args:
            dependency_id (str): id of dependency (to be used in other dependencies)
            widget_id (str): id of widget to associate dependency with
        """
        super().__init__(
            dependency_id=dependency_id, widget_id=widget_id, path="selected"
        )


class CollapsibleSectionSelectDependency(CardSelectDependency):
    """Spec for defining a dependency with a row."""

    API_DEPENDENCY_INPUT = "DashboardCollapsibleCardDependencyUnionInput"
