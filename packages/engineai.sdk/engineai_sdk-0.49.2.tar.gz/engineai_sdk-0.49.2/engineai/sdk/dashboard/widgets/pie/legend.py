"""Spec for Legend position and respective build."""
import enum
from typing import Any

from engineai.sdk.dashboard.utils import generate_input


class LegendPosition(enum.Enum):
    """Spec for Legend Position.

    Attributes:
        RIGHT: Legend is placed on the right side of the chart.
        BOTTOM: Legend is placed on the bottom of the chart.
        NEXT_TO_DATA: Legend is placed next to the data.
    """

    RIGHT = "RIGHT"
    BOTTOM = "BOTTOM"
    NEXT_TO_DATA = "NEXT_TO_DATA"


def build_legend(legend: LegendPosition) -> Any:
    """Builds spec for dashboard API.

    Returns:
        Input object for Dashboard API
    """
    return generate_input(
        "PieWidgetLegendInput",
        position=legend.value,
    )
