"""Spec for the layout Collapsible Section Header."""

from typing import Optional

from beartype import beartype

from engineai.sdk.dashboard.dependencies.route import CollapsibleSectionRouteDependency
from engineai.sdk.dashboard.dependencies.widget import (
    CollapsibleSectionSelectDependency,
)

from ..components.header import BaseHeader
from .chip import CollapsibleSectionChip


class CollapsibleSectionHeader(
    BaseHeader[CollapsibleSectionSelectDependency, CollapsibleSectionRouteDependency]
):
    """Spec for the layout Collapsible Section Header."""

    @beartype
    def __init__(
        self,
        *chips: CollapsibleSectionChip,
        title: Optional[str] = None,
    ):
        """Construct Header for Collapsible Section layout.

        Args:
            chips: chips to be added to the collapsible section header.
            title: Collapsible Section title.

        Examples:
            ??? example "Create a Collapsible Section layout with a title"
                ```py linenums="1"
                # Add Header to a Collapsible Section
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import pie
                from engineai.sdk.dashboard import layout

                data = pd.DataFrame(
                   {
                       "category": ["A", "B"],
                       "value": [1, 2],
                   },
                )

                Dashboard(
                    content=layout.CollapsibleSection(
                        content=pie.Pie(data=data),
                        header=layout.CollapsibleSectionHeader(title="Header Title")
                    )
                )
                ```
        """
        super().__init__(*chips, title=title)

    def has_title(self) -> bool:
        """Method to validate if header has title."""
        return self.__title is not None
