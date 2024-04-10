"""Spec for the layout Card Header."""

from typing import Optional

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from ..components.header import BaseHeader
from .chip import CardChip


class CardHeader(BaseHeader):
    """Spec for the layout Card Header."""

    @type_check
    def __init__(
        self,
        *chips: CardChip,
        title: Optional[TemplatedStringItem] = None,
    ):
        """Construct Header in card layout.

        Args:
            chips: chips to be added to the card header.
            title: Card title.

        Examples:
            ??? example "Create a Card layout with a title"
                ```py linenums="1"
                # Add Header to a Card
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
                    content=layout.Card(
                        content=pie.Pie(data=data),
                        header=layout.CardHeader(title="Header Title")
                    )
                )
                ```
        """
        super().__init__(*chips, title=title)


Header = CardHeader  # retro
