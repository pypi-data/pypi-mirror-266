"""Specs for text item for a tooltip."""

from typing import Optional
from typing import Union

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.formatting import TextFormatting
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .base import BaseTooltipItem


class TextTooltipItem(BaseTooltipItem):
    """Specs for text item for a tooltip."""

    _API_TYPE = "TooltipTextItemInput"

    @type_check
    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        formatting: Optional[TextFormatting] = None,
        label: Optional[Union[str, DataField]] = None,
    ):
        """Construct text tooltip item.

        Args:
            data_column (TemplatedStringItem): name of column in pandas dataframe(s)
                used for the value of the tooltip item.
            formatting (Optional[TextFormatting]): tooltip formatting spec.
                Defaults to TextFormatting(max_characters=30).
            label (Optional[Union[str, DataField]]): label to be used for tooltip item,
                it can be either a string or a DataField object.
        """
        super().__init__(
            data_column=data_column,
            formatting=formatting if formatting is not None else TextFormatting(),
            label=label,
        )
