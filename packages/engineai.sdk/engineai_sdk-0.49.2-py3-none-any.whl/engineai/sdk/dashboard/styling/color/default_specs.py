"""Specs for default color specs."""
import sys

from engineai.sdk.dashboard.styling.color.palette import sequential_palette

from .discrete_map import DiscreteMap
from .discrete_map import DiscreteMapIntervalItem
from .discrete_map import DiscreteMapValueItem
from .gradient import Gradient
from .gradient import GradientItem
from .single import Palette
from .single import Single


class PositiveNegativeDiscreteMap(DiscreteMap):
    """Template DiscreteMap for Positive/Negative Numbers."""

    def __init__(self) -> None:
        """Creates template DiscreteMap for Positive/Negative Numbers."""
        super().__init__(
            DiscreteMapIntervalItem(
                color=Palette.RUBI_RED,
                min_value=-sys.maxsize,
                max_value=0,
                exclude_max=True,
            ),
            DiscreteMapValueItem(value=0, color=Palette.COCONUT_GREY),
            DiscreteMapIntervalItem(
                color=Palette.OCEAN_BLUE,
                min_value=0,
                max_value=sys.maxsize,
                exclude_min=True,
            ),
        )


class SequentialColorGradient(Gradient):
    """Sequential discrete map."""

    def __init__(self) -> None:
        """Creates template Sequential Color Map spec."""
        super().__init__(
            GradientItem(
                color=Single(color=sequential_palette(index=5)),
                value=0,
            ),
            GradientItem(
                color=Single(color=sequential_palette(index=4)),
                value=1 / 5,
            ),
            GradientItem(
                color=Single(color=sequential_palette(index=3)),
                value=2 / 5,
            ),
            GradientItem(
                color=Single(color=sequential_palette(index=2)),
                value=0.5,
            ),
            GradientItem(
                color=Single(color=sequential_palette(index=1)),
                value=4 / 5,
            ),
            GradientItem(
                color=Single(color=sequential_palette(index=0)),
                value=1,
            ),
            steps=5,
        )


class ScoreColorDiscreteMap(DiscreteMap):
    """Score Color Discrete Map."""

    SCORE_COLORS = [
        Palette.RUBI_RED,
        Palette.SUNSET_ORANGE,
        Palette.BANANA_YELLOW,
        Palette.BABY_BLUE,
        Palette.OCEAN_BLUE,
    ]
    SCORE_SUP_VALUES = [2.0, 4.0, 6.0, 8.0, 10.0]
    SCORE_INF_VALUES = [0.0] + SCORE_SUP_VALUES[:-1]

    def __init__(self) -> None:
        """Creates template Score Color Discrete Map spec."""
        super().__init__(
            *(
                DiscreteMapIntervalItem(
                    min_value=min_val,
                    max_value=max_val,
                    color=color_val,
                    exclude_min=False,
                    exclude_max=idx < len(self.SCORE_COLORS) - 1,
                )
                for idx, (min_val, max_val, color_val) in enumerate(
                    zip(self.SCORE_INF_VALUES, self.SCORE_SUP_VALUES, self.SCORE_COLORS)
                )
            )
        )
