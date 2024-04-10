"""Chart Series Custom Entity."""

from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.dashboard.widgets.components.charts.series.entities.base import Entity


class CustomEntity(Entity):
    """Custom entity spec."""

    _INPUT_KEY = "standard"

    def __init__(self, name: TemplatedStringItem):
        """Construct custom entity.

        Args:
            name: name for custom entity.
        """
        super().__init__()
        self.__name = name

    def _build_entity(self):
        return generate_input(
            "ChartSeriesStandardEntityInput",
            name=build_templated_strings(items=self.__name),
        )
