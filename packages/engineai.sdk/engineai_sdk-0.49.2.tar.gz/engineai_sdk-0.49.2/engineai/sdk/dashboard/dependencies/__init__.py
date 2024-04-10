"""Specs for dependencies."""
from .datastore import DashboardStorage
from .route import RouteDependency
from .widget import WidgetSelectDependency

__all__ = [
    # .datastore
    "DashboardStorage",
    # .widget
    "WidgetSelectDependency",
    # .route
    "RouteDependency",
]
