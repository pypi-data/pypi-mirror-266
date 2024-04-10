"""Specification for text columns."""

from typing import Any
from typing import List
from typing import Optional
from typing import Union

import pandas as pd
from beartype import beartype

from engineai.sdk.dashboard.formatting import NumberFormatting
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.styling.color import Palette
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.table.enums import HorizontalAlignment

from ..styling.arrow import ArrowStyling
from ..styling.cell import CellStyling
from ..styling.color_bar import ColorBarStyling
from ..styling.country_flag import CountryFlagStyling
from ..styling.dot import DotStyling
from ..styling.font import FontStyling
from ..styling.split_bar import SplitBarStyling
from ..styling.utils import build_styling_input
from .base import Column

NumberColumnStyling = Union[
    ArrowStyling,
    CellStyling,
    ColorBarStyling,
    CountryFlagStyling,
    DotStyling,
    FontStyling,
    SplitBarStyling,
]


class NumberColumn(Column):
    """Specifications for NumberColumn class."""

    _ITEM_ID_TYPE: str = "NUMBER"

    @beartype
    def __init__(
        self,
        *,
        data_column: Union[str, WidgetField],
        label: Optional[Union[str, GenericLink]] = None,
        formatting: Optional[NumberFormatting] = None,
        styling: Optional[Union[Palette, NumberColumnStyling]] = None,
        align: Optional[HorizontalAlignment] = None,
        hiding_priority: int = 0,
        tooltip_text: Optional[List[TemplatedStringItem]] = None,
        min_width: Optional[int] = None,
        sortable: bool = True,
        optional: bool = False,
    ):
        """Class NumberColumn is used as number column for the Table Widget.

        Args:
            data_column: name of column in pandas dataframe(s) used for this widget.
            label: label to be displayed for this column.
            formatting: formatting spec.
            styling: styling spec for column. One of TableColumnStylingCell,
                TableColumnStylingCountryFlag or TableColumnStylingDot.
            align: column align. By default, it is set to the Right and when using Cell
                or Bar styling, otherwise it is set to the center.
            hiding_priority: columns with lower hiding_priority are hidden first
                if not all data can be shown.
            tooltip_text: info text to explain column. Each element of list is
                displayed as a separate paragraph.
            min_width: min width of the column in pixels.
            sortable: determines if column can be sorted.
            optional: flag to make the column optional if there is no Data for that
                columns.

        Examples:
            ??? example "Create a Table widget with NumberColumn"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import table
                data = pd.DataFrame(
                    {
                        "number": [2],
                    },
                )
                Dashboard(
                    content=table.Table(
                        data=data,
                        columns=[
                            table.NumberColumn(
                                data_column="number",
                                ),
                            ),
                        ],
                    )
                )
                ```
        """
        super().__init__(
            data_column=data_column,
            label=label,
            hiding_priority=hiding_priority,
            tooltip_text=tooltip_text,
            min_width=min_width,
            optional=optional,
        )
        self.__styling = (
            CellStyling(color_spec=styling) if isinstance(styling, Palette) else styling
        )
        self.__align = self.__get_alignment(align)
        self.__sortable = sortable
        self.__formatting = formatting if formatting else NumberFormatting()

    def __get_alignment(
        self, align: Optional[HorizontalAlignment]
    ) -> HorizontalAlignment:
        if align is not None:
            return align
        elif isinstance(
            self.__styling, (CellStyling, ColorBarStyling, SplitBarStyling)
        ):
            return HorizontalAlignment.CENTER
        else:
            return HorizontalAlignment.RIGHT

    def prepare(self) -> None:
        """Prepare data column."""
        if self.__styling is not None:
            self.__styling.prepare(self._data_column)

    def _custom_validation(self, *, data: pd.DataFrame) -> None:
        """Custom validation for each columns to implement.

        Args:
            data: pandas dataframe which will be used for table.
        """
        if self.__styling is not None:
            self.__styling.validate(data=data)

    def _build_styling(self) -> Any:
        column_styling_spec = None
        if self.__styling is not None:
            column_styling_spec = generate_input(
                "TableNumberColumnStylingInput",
                **build_styling_input(
                    data_column=self.data_column, styling=self.__styling
                ),
            )
        return column_styling_spec

    def _build_column(self) -> Any:
        return generate_input(
            "TableColumnTypeInput",
            numberColumn=generate_input(
                "TableNumberColumnInput",
                formatting=self.__formatting.build(),
                align=self.__align.value,
                sortable=self.__sortable,
                styling=self._build_styling(),
                optional=self._optional,
            ),
        )
