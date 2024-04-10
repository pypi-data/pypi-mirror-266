"""Specs for Position and Region."""
import enum


class LegendPosition(enum.Enum):
    """Options for positions of Map legend.

    Attributes:
        TOP: Legend is placed on the top of the map.
        LEFT: Legend is placed on the left side of the map.
        RIGHT: Legend is placed on the right side of the map.
        BOTTOM: Legend is placed on the bottom of the map.
    """

    TOP = "TOP"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BOTTOM = "BOTTOM"


class Region(enum.Enum):
    """Options for region.

    Attributes:
        WORLD: World region.
        EUROPE: Europe region.
        USA: USA region.
        NORTH_AMERICA: North America region.
    """

    WORLD = "WORLD"
    EUROPE = "EUROPE"
    USA = "USA"
    NORTH_AMERICA = "NORTH_AMERICA"
