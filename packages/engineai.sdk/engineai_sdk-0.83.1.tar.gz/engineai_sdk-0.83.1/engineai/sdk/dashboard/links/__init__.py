"""Spec for Common Links spec used across the packages."""
from .route_link import RouteLink
from .url import UrlQueryDependency
from .widget_field import WidgetField

__all__ = [
    "WidgetField",
    "RouteLink",
    "UrlQueryDependency",
]
