"""Specs for extra elements for tooltip of timeseries chart and series."""
from typing import List
from typing import Union

from engineai.sdk.dashboard.widgets.components.charts.tooltip import CategoryTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import DatetimeTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import NumberTooltipItem
from engineai.sdk.dashboard.widgets.components.charts.tooltip import TextTooltipItem

TooltipItem = Union[
    CategoryTooltipItem,
    DatetimeTooltipItem,
    NumberTooltipItem,
    TextTooltipItem,
]

TooltipItems = Union[TooltipItem, List[TooltipItem]]
