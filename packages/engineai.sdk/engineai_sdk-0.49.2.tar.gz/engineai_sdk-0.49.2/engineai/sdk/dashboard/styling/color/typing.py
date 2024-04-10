"""Specs for color typing."""
from typing import Union

from engineai.sdk.dashboard.styling.color.palette import Palette

from .discrete_map import DiscreteMap
from .gradient import Gradient
from .single import Single

ColorSpec = Union[Palette, Single, Gradient, DiscreteMap]
