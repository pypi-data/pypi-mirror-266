"""Spec for the layout Card Header Labels Context."""

from typing import List
from typing import Optional
from typing import Union

from beartype import beartype

from engineai.sdk.dashboard.dependencies.route import CardRouteDependency
from engineai.sdk.dashboard.dependencies.widget import CardSelectDependency
from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from ..components.chip import BaseChip


class CardChip(BaseChip[CardSelectDependency, CardRouteDependency]):
    """Spec for the layout Card Header chip."""

    @beartype
    def __init__(
        self,
        *,
        label: Union[str, GenericLink],
        tooltip_text: Optional[List[TemplatedStringItem]] = None,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        """Construct CardHeaderContext in Layout Card Header.

        Args:
            label: Card Header label value. Can assume a static label or a single
                GenericLink.
            tooltip_text: informational pop up text. Each element of list is displayed
                as a separate paragraph. Can only use this option if the `label` is
                set.
            prefix: prefix value to use in before each label.
            suffix: suffix value to use in after each label.

        Examples:
            ??? example "Create a Card with multiple chips."
                ```py linenums="1"
                # Using a Chip with a static label and a Chip with a Toggle widget.
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard import layout
                from engineai.sdk.dashboard.widgets import toggle
                from engineai.sdk.dashboard.widgets import maps

                data = pd.DataFrame(
                    data=[
                        {"id": 1, "label": "Option 1"},
                        {"id": 2, "label": "Option 2"}
                    ]
                )
                toggle_widget = toggle.Toggle(data=data)

                chip = layout.CardChip(label="Chip 1")
                linked_chip = layout.CardChip(label=toggle_widget.selected.label)

                map_data = pd.DataFrame(
                   data=[{"region": "PT", "value": 10}, {"region": "GB", "value": 100}]
                )
                Dashboard(
                    content=[
                       toggle_widget,
                       layout.Card(
                            content=maps.Geo(data=map_data),
                            header=layout.CardHeader(chip, linked_chip)
                        )
                    ]
                )
                ```

        """
        super().__init__(
            label=label,
            tooltip_text=tooltip_text,
            prefix=prefix,
            suffix=suffix,
        )


Chip = CardChip  # retro
