"""Map resources."""
from .enums import LegendPosition
from .enums import Region
from .geo.geo import Geo
from .series.numeric import NumericSeries
from .series.styling import SeriesStyling

__all__ = [
    # .geo
    "Geo",
    "Region",
    # .position
    "LegendPosition",
    # .series
    "NumericSeries",
    # .styling
    "SeriesStyling",
]
