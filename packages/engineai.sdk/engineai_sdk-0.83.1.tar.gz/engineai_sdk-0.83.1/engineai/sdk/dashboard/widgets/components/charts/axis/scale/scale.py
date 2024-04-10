"""Spec to build different scales supported by y axis."""

from typing import Any

from engineai.sdk.dashboard.utils import generate_input

from .dynamic import AxisScaleDynamic
from .negative import AxisScaleNegative
from .positive import AxisScalePositive
from .symmetric import AxisScaleSymmetric
from .typing import AxisScale


def build_axis_scale(scale: AxisScale) -> Any:
    """Builds spec for dashboard API.

    Returns:
        Input object for Dashboard API
    """
    return generate_input(
        "ChartNumericAxisScaleInput", **{_get_input_key(scale): scale.build()}
    )


def _get_input_key(scale: AxisScale) -> str:
    if isinstance(scale, AxisScaleDynamic):
        return "dynamic"
    elif isinstance(scale, AxisScaleSymmetric):
        return "symmetrical"
    elif isinstance(scale, AxisScalePositive):
        return "positive"
    elif isinstance(scale, AxisScaleNegative):
        return "negative"
    else:
        raise TypeError(
            "AxisScale requires one of AxisScaleDynamic, "
            "AxisScaleDynamic, AxisScalePositive, "
            "AxisScaleNegative"
        )
