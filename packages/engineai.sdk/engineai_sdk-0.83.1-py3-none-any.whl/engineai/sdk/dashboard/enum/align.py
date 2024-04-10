"""Dashboard Alignment Enums."""
import enum


class HorizontalAlignment(enum.Enum):
    """Horizontal Alignment keys.

    Attributes:
        LEFT (str): Left alignment.
        CENTER (str): Center alignment.
        RIGHT (str): Right alignment.
    """

    LEFT = "LEFT"
    CENTER = "CENTER"
    RIGHT = "RIGHT"


class FluidHorizontalAlignment(enum.Enum):
    """Horizontal Alignment keys.

    Attributes:
        LEFT (str): Left alignment.
        CENTER (str): Center alignment.
        RIGHT (str): Right alignment.
        STRETCH (str): Stretch alignment.
    """

    LEFT = "LEFT"
    CENTER = "CENTER"
    RIGHT = "RIGHT"
    STRETCH = "STRETCH"


class VerticalAlignment(enum.Enum):
    """Vertical alignment keys.

    Attributes:
        TOP (str): Top alignment.
        MIDDLE (str): Middle alignment.
        BOTTOM (str): Bottom alignment.
    """

    TOP = "TOP"
    MIDDLE = "MIDDLE"
    BOTTOM = "BOTTOM"
