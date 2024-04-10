"""Specification for staked bar chart columns in Table widget."""

from typing import Any
from typing import List
from typing import Optional
from typing import Union

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.formatting import NumberFormatting
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input

from ...styling.stacked_bar import StackedBarStyling
from .base import ChartColumn


class StackedBarColumn(ChartColumn):
    """Specifications for StackedBarColumn class."""

    _ITEM_ID_TYPE: str = "STACKED_BAR"

    @type_check
    def __init__(
        self,
        *,
        data_column: Union[str, WidgetField],
        data_key: Union[str, WidgetField],
        label: Optional[Union[str, GenericLink]] = None,
        styling: StackedBarStyling,
        label_key: Optional[str] = None,
        formatting: Optional[NumberFormatting] = None,
        hiding_priority: int = 0,
        tooltip_text: Optional[List[TemplatedStringItem]] = None,
        min_width: Optional[int] = None,
        sortable: bool = True,
        display_total_value: bool = True,
        optional: bool = False,
    ):
        """Class StackedBarColumn is used as stack bar column for the Table Widget.

        Args:
            data_column: name of column in pandas dataframe(s) used for this widget.
            data_key: key in object that contains the value for the stack bar chart.
            label_key: key in object that contains the label for the stack bar chart.
            label: label to be displayed for this column.
            formatting: formatting spec.
            styling: styling spec for stacked chart.
            hiding_priority: columns with lower hiding_priority are hidden first
                if not all data can be shown.
            tooltip_text: info text to explain column. Each element of list is
                displayed as a separate paragraph.
            min_width: min width of the column in pixels.
            sortable: determines if column can be sorted.
            display_total_value: display total value after stacked bars chart.
            optional: flag to make the column optional if there is no Data for that
                columns.

        Examples:
            ??? example "Create a Table widget with StackedBarColumn"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import table
                data = pd.DataFrame(
                    {
                        "stacked_data": [
                            {"key": 10, "category": 1},
                            {"key": 10, "category": 2},
                        ],
                    },
                )

                color_spec = color.DiscreteMap(
                        color.DiscreteMapValueItem(
                            value=1, color=color.Palette.MINT_GREEN
                        ),
                        color.DiscreteMapValueItem(
                            value=2, color=color.Palette.SUNSET_ORANGE
                        ),
                    ),
                )

                Dashboard(
                    content=table.Table(
                        data=data,
                        columns=[
                            table.StackedBarColumn(
                                data_column="stacked_data",
                                data_key="key",
                                styling=table.StackedBarStyling(
                                    data_column="category",
                                    color_spec=color_spec,
                            ),
                        ],
                    )
                )
                ```
        """
        super().__init__(
            data_column=data_column,
            data_key=data_key,
            styling=styling,
            label=label,
            hiding_priority=hiding_priority,
            tooltip_text=tooltip_text,
            min_width=min_width,
            reference_line=None,
            optional=optional,
        )
        self.__formatting = formatting if formatting else NumberFormatting()
        self.__sortable = sortable
        self.__display_total_value = display_total_value
        self.__label_key = label_key

    def _build_column(self) -> Any:
        return generate_input(
            "TableColumnTypeInput",
            stackedBarColumn=generate_input(
                "TableStackedBarColumnInput",
                formatting=self.__formatting.build(),
                styling=self._build_styling(),
                valueKey=build_templated_strings(items=self.data_key),
                labelKey=build_templated_strings(items=self.__label_key),
                sortable=self.__sortable,
                displayTotalValue=self.__display_total_value,
                optional=self._optional,
            ),
        )
