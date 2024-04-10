"""Specs for dateitem item for a tooltip."""

from typing import Optional
from typing import Union

from beartype import beartype

from engineai.sdk.dashboard.formatting import DateTimeFormatting
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .base import BaseTooltipItem


class DatetimeTooltipItem(BaseTooltipItem):
    """Specs for datetime item for a tooltip."""

    _API_TYPE = "TooltipDateTimeItemInput"

    @beartype
    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        formatting: Optional[DateTimeFormatting] = None,
        label: Optional[Union[str, DataField]] = None,
    ):
        """Construct datetime tooltip item.

        Args:
            data_column (TemplatedStringItem): name of column in pandas dataframe(s)
                used for the value of the tooltip item.
            formatting (DateTimeFormatting): tooltip formatting spec
                Defaults to DateTimeFormatting for Dates (i.e. not include HH:MM).
            label (Optional[Union[str, DataField]]): label to be used for tooltip item,
                it can be either a string or a DataField object.
        """
        super().__init__(
            data_column=data_column,
            formatting=formatting if formatting is not None else DateTimeFormatting(),
            label=label,
        )
