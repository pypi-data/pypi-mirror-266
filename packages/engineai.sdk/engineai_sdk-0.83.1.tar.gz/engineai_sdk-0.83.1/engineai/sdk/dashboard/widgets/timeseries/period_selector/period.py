"""Spec to build different periods supported by period selector."""

from typing import Any
from typing import Dict
from typing import Union

from engineai.sdk.dashboard.utils import generate_input

from .custom_period import CustomPeriod
from .standard import Period

PeriodType = Union[Period, CustomPeriod]


def build_timeseries_period(period: PeriodType) -> Any:
    """Builds spec for dashboard API.

    Returns:
        Input object for Dashboard API
    """
    return generate_input(
        "TimeseriesWidgetPeriodInput",
        **_get_input(period),
    )


def _get_input(period: PeriodType) -> Dict[str, Any]:
    if isinstance(period, Period):
        return {
            "standard": generate_input(
                "TimeseriesWidgetStandardPeriodInput",
                period=period.value,
            )
        }
    elif isinstance(period, CustomPeriod):
        return {"custom": period.build()}

    else:
        raise TypeError(
            f"period needs to be of Period, CustomPeriod. " f"{type(period)} provided"
        )
