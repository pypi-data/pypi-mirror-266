"""Specs for category item for a tooltip."""

from typing import Optional
from typing import Union

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.formatting import MapperFormatting
from engineai.sdk.dashboard.templated_string import DataField
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from .base import BaseTooltipItem


class CategoryTooltipItem(BaseTooltipItem):
    """Specs for category tooltip item."""

    _API_TYPE = "TooltipCategoricalItemInput"

    @type_check
    def __init__(
        self,
        *,
        data_column: TemplatedStringItem,
        formatting: MapperFormatting,
        label: Optional[Union[str, DataField]] = None,
    ):
        """Construct category tooltip item.

        Args:
            data_column (TemplatedStringItem): name of column in pandas dataframe(s)
                used for the value of the tooltip item.
            formatting (MapperFormatting): tooltip formatting spec.
            label (Optional[Union[str, DataField]]): label to be used for tooltip item,
                it can be either a string or a DataField object.
        """
        super().__init__(
            data_column=data_column,
            formatting=formatting,
            label=label,
        )
