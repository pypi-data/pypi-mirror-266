"""Specification for Country Column in Table widget."""
import enum
from typing import Any
from typing import List
from typing import Optional
from typing import Union

import pandas as pd
from beartype import beartype

from engineai.sdk.dashboard.formatting import TextFormatting
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.typing import GenericLink
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.table.enums import HorizontalAlignment

from ..styling.country_flag import CountryFlagStyling
from ..styling.utils import build_styling_input
from .base import Column


class FlagPositions(enum.Enum):
    """Country Column Flag Position Options.

    Attributes:
        LEFT: Flag at the left of the country name.
        RIGHT: Flag at the right of the country name.
        HIDDEN: Flag is hidden.
    """

    LEFT: bool = True
    RIGHT: bool = False
    HIDDEN: None = None


class CountryColumn(Column):
    """Specifications for CountryColumn class."""

    _ITEM_ID_TYPE: str = "COUNTRY"

    @beartype
    def __init__(
        self,
        *,
        data_column: Union[str, WidgetField],
        label: Optional[Union[str, GenericLink]] = None,
        formatting: Optional[TextFormatting] = None,
        flag_position: FlagPositions = FlagPositions.LEFT,
        align: HorizontalAlignment = HorizontalAlignment.LEFT,
        hiding_priority: int = 0,
        tooltip_text: Optional[List[TemplatedStringItem]] = None,
        min_width: Optional[int] = None,
        sortable: bool = False,
        optional: bool = False,
    ):
        """Class CountryColumn is used as Country information column for Table Widget.

        Args:
            data_column: name of column in pandas dataframe(s) used for this widget.
                Data in this column should be ISO 3166-1 alpha-2 country codes.
            label: label to be displayed for this column.
            flag_position: position of country flag.
            formatting: text formatting spec.
            align: column alignment.
            hiding_priority: columns with lower hiding_priority are hidden first
                if not all data can be shown.
            tooltip_text: info text to explain column. Each element of list is
                displayed as a separate paragraph.
            min_width: min width of the column in pixels.
            sortable: determines if column can be sorted.
            optional: flag to make the column optional if there is no Data for that
                columns.

        Examples:
            ??? example "Create a Table widget with Country Column"
                ```py linenums="1"
                import pandas as pd
                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import table
                data = pd.DataFrame(
                    {
                        "country_code": ["US", "CA", "MX"],
                    },
                )
                Dashboard(
                    content=table.Table(
                        data=data,
                        columns=[
                            table.CountryColumn(
                                data_column="country_code",
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
        self.__align = align
        self.__styling = (
            None
            if flag_position == FlagPositions.HIDDEN
            else CountryFlagStyling(data_column=data_column, left=flag_position.value)
        )
        self.__sortable = sortable
        self.__formatting = formatting if formatting else TextFormatting()

    def _custom_validation(self, *, data: pd.DataFrame) -> None:
        pass

    def _build_styling(self) -> Any:
        column_styling = None
        if self.__styling:
            column_styling = generate_input(
                "TableCountryColumnStylingInput",
                **build_styling_input(
                    data_column=self.data_column, styling=self.__styling
                ),
            )
        return column_styling

    def _build_column(self) -> Any:
        return generate_input(
            "TableColumnTypeInput",
            countryColumn=generate_input(
                "TableCountryColumnInput",
                sortable=self.__sortable,
                formatting=self.__formatting.build(),
                align=self.__align.value,
                styling=self._build_styling(),
                optional=self._optional,
            ),
        )
