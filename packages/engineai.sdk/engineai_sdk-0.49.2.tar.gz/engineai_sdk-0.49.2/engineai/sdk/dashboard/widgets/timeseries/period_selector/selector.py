"""Spec for period selector of a timeseries widget."""

from typing import Any
from typing import List
from typing import Optional

from beartype import beartype

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.utils import generate_input

from ..exceptions import TimeseriesPeriodSelectorHiddenPeriodsError
from ..exceptions import TimeseriesPeriodSelectorNoAvailableDefaultOptionError
from .custom_period import CustomPeriod
from .period import PeriodType
from .period import build_timeseries_period
from .standard import Period


class PeriodSelector(AbstractFactory):
    """Spec for period selector of a timeseries widget."""

    @beartype
    def __init__(
        self,
        *periods: PeriodType,
        default_selection: Optional[int] = None,
        visible: bool = True,
    ) -> None:
        """Construct period selector.

        Args:
            periods: specs for periods added into timeseries widget
                period selector component.
            default_selection: choose which period selector to be the default.
            visible: flag that makes the period selector visible.
                If False, all periods added and default selection will be ignored.

        Raises:
            TimeseriesPeriodSelectorEmptyDefinitionError: when `periods` is empty.
            TimeseriesPeriodSelectorNoAvailableDefaultOptionError: when the
                desired default selection element does not exist

        Examples:
            ??? example "Create a minimal timeseries widget with a selector"
                ```python linenums="1"
                import pandas as pd

                from engineai.sdk.dashboard.dashboard import Dashboard
                from engineai.sdk.dashboard.widgets import timeseries

                data = pd.DataFrame(
                    {
                        "value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    },
                    index=pd.date_range("2020-01-01", "2020-01-10"),
                )
                ts = timeseries.Timeseries(
                    data=data,
                    period_selector=timeseries.PeriodSelector(
                        timeseries.Period.W1,
                        timeseries.Period.M1,
                        timeseries.Period.ALL,
                        default_selection=1,
                    )
                )
                Dashboard(content=ts)
                ```
        """
        super().__init__()
        self.__validate(*periods, visible=visible)
        self.__selected: str
        self.__option = default_selection
        self.__visible = visible

        self.__set_periods(*periods)
        self.__set_default_selection(self.__option)

    def __validate(self, *periods: PeriodType, visible: bool) -> None:
        if len(periods) > 0 and not visible:
            raise TimeseriesPeriodSelectorHiddenPeriodsError()

    def __set_periods(self, *periods: PeriodType) -> None:
        if self.__visible:
            default: List[PeriodType] = [  # Short Term Periods
                Period.M1,
                Period.YTD,
                Period.Y1,
                Period.Y5,
                Period.ALL,
            ]

            self.__periods: List[PeriodType] = (
                default if len(periods) == 0 else list(periods)
            )
            if self.__option is None:
                self.__set_default_selection(3 if self.__periods == default else 1)
        else:
            self.__periods = []
            self.__selected = ""

    def __set_default_selection(self, option: Optional[int] = None) -> None:
        if self.__visible:
            if option is not None:
                if len(self.__periods) < option or option <= 0:
                    raise TimeseriesPeriodSelectorNoAvailableDefaultOptionError(
                        len(self.__periods), option
                    )
                self.__selected = self.__periods[option - 1].label

    def prepare(self) -> None:
        """Validate Period Selector specs.

        Raises:
            TimeseriesPeriodSelectorDuplicatedLabelsError: when two periods have the
                same label
            TimeseriesPeriodSelectorUnorderedPeriodsError: when added periods are not
                ordered in a timeline way
        """
        self._custom_periods_prepare()

    def _custom_periods_prepare(self):
        custom_periods = [
            period for period in self.__periods if isinstance(period, CustomPeriod)
        ]

        if len(custom_periods) == 1:
            custom_periods[0].prepare("Custom Period")
        else:
            for i in range(0, len(custom_periods)):
                custom_periods[i].prepare("Period " + str(i + 1))

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "TimeseriesWidgetPeriodSelectorInput",
            periods=[
                build_timeseries_period(period=period) for period in self.__periods
            ]
            if self.__periods
            else [],
            selected=self.__selected,
            isDatePickerVisible=self.__visible,
        )
