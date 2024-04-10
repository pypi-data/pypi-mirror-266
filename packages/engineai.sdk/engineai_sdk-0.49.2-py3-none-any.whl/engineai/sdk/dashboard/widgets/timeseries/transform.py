"""Spec for legend of a timeseries widget."""
from typing import Any
from typing import Optional
from typing import Union

from beartype import beartype

from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.utils import generate_input

from .enums import TransformChoices
from .exceptions import TimeseriesTransformScalarRequiredError


class Transform(AbstractFactoryLinkItemsHandler):
    """Spec for transforms of a timeseries series."""

    @beartype
    def __init__(
        self,
        *,
        transform: TransformChoices,
        scalar: Optional[Union[float, int]] = None,
    ):
        """Construct a transform for a timeseries widget.

        Args:
            transform: transform to apply to series data.
            scalar: Applies scalar value to data. Only applies when using the
                following transformations ADD, SUBTRACT, DIVIDE and MULTIPLY.
        """
        super().__init__()
        if (
            transform
            in [
                TransformChoices.ADD,
                TransformChoices.DIVIDE,
                TransformChoices.MULTIPLY,
                TransformChoices.SUBTRACT,
            ]
        ) and scalar is None:
            raise TimeseriesTransformScalarRequiredError(transformation=transform.value)

        self._transform = transform
        self._scalar = scalar

    def build(self) -> Any:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return generate_input(
            "SeriesTransform", transform=self._transform.value, scalar=self._scalar
        )
