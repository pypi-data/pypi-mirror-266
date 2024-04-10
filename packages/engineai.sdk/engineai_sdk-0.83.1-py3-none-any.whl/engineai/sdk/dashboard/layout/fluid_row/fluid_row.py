"""Spec for a fluid row in a dashboard vertical grid layout."""

from typing import Any
from typing import Iterable
from typing import List
from typing import Optional
from typing import Union

from typing_extensions import Unpack

from engineai.sdk.dashboard.abstract.typing import PrepareParams
from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.enum.align import (
    FluidHorizontalAlignment as HorizontalAlignment,
)
from engineai.sdk.dashboard.enum.align import VerticalAlignment
from engineai.sdk.dashboard.utils import generate_input

from ..exceptions import ElementHeightNotDefinedError
from .items_build import DashboardFluidRowItem
from .items_build import build_fluid_item


class FluidRow(AbstractFactory):
    """Spec for a fluid row in a dashboard vertical grid layout."""

    def __init__(
        self,
        *items: DashboardFluidRowItem,
        vertical_alignment: VerticalAlignment = VerticalAlignment.TOP,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
    ) -> None:
        """Construct fluid row in dashboard vertical grid layout.

        Args:
            items: item within the FluidRow. One of Select, Toggle.
            vertical_alignment: Fluid Row vertical alignment option.
                `TOP`, `MIDDLE` or `BOTTOM`, available.
            horizontal_alignment: Fluid Row horizontal alignment option.
                `LEFT`, `CENTER`, `RIGHT` or `STRETCH` available.

        Examples:
            ??? example "Create Fluid Row with widget"
                ```py linenums="1"
                import pandas as pd

                from engineai.sdk.dashboard import dashboard
                from engineai.sdk.dashboard import layout
                from engineai.sdk.dashboard.widgets import select

                data = pd.DataFrame({"id": [1, 2, 3]})

                dashboard.Dashboard(
                    content=layout.Grid(
                        layout.FluidRow(select.Select(data))
                    )
                )
                ```

            ??? example "Create FluidRow with multiple Widgets"
                ```py linenums="1"
                import pandas as pd

                from engineai.sdk.dashboard import dashboard
                from engineai.sdk.dashboard import layout
                from engineai.sdk.dashboard.widgets import select
                from engineai.sdk.dashboard.widgets import toggle

                data = pd.DataFrame({"id": [1, 2, 3]})

                dashboard.Dashboard(
                    content=layout.Grid(
                        layout.FluidRow(
                            select.Select(data),
                            toggle.Toggle(data),
                        )
                    )
                )
                ```

            ??? example "Create FluidRow with left alignment"
                ```py linenums="1"
                import pandas as pd

                from engineai.sdk.dashboard import dashboard
                from engineai.sdk.dashboard import layout
                from engineai.sdk.dashboard.enum import align
                from engineai.sdk.dashboard.widgets import select
                from engineai.sdk.dashboard.widgets import toggle

                data = pd.DataFrame({"id": [1, 2, 3]})

                dashboard.Dashboard(
                    content=layout.Grid(
                        layout.FluidRow(
                            select.Select(data),
                            toggle.Toggle(data),
                            horizontal_alignment=align.FluidHorizontalAlignment.LEFT,
                        )
                    )
                )
                ```
        """
        super().__init__()
        self.__items: List[DashboardFluidRowItem] = []
        self.__set_items(*items)
        self.__height: Optional[Union[float, int]] = None
        self.__vertical_alignment = vertical_alignment.value
        self.__horizontal_alignment = horizontal_alignment.value

    def __set_items(self, *items: DashboardFluidRowItem) -> None:
        """Set items for fluid row."""
        for item in items:
            self.__items.append(item)

    def prepare_heights(self) -> None:
        """Prepare fluid row heights."""
        self.__height = float(max(item.height for item in self.__items))

    @property
    def force_height(self) -> bool:
        """Get if the Row has a forced height from the ."""
        return True

    @property
    def height(self) -> Union[float, int]:
        """Get row height."""
        if self.__height is None:
            raise ElementHeightNotDefinedError()
        return self.__height

    def items(self) -> Iterable[DashboardFluidRowItem]:
        """Return items associated."""
        return self.__items

    @property
    def widgets(self) -> List[DashboardFluidRowItem]:
        """Returns list of widgets in dashboard grid row layout.

        Returns:
            List[Widget]: list of widget
        """
        return self.__items

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "DashboardFluidRowInput",
            height=self.__height,
            items=[build_fluid_item(item=item) for item in self.__items],
            verticalAlign=self.__vertical_alignment,
            horizontalAlign=self.__horizontal_alignment,
        )

    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare row."""
        for item in self.__items:
            item.prepare(**kwargs)
