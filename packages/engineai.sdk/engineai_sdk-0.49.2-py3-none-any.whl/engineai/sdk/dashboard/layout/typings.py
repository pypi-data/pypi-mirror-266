"""Typings for layout modules."""
from typing import Union

from engineai.sdk.dashboard.interface import CardInterface as Card
from engineai.sdk.dashboard.interface import GridInterface as Grid
from engineai.sdk.dashboard.interface import SelectableInterface as SelectableSection
from engineai.sdk.dashboard.interface import WidgetInterface as Widget

LayoutItem = Union[Widget, Card, Grid, SelectableSection]
