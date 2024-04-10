"""Generate dataclasses and enum types from a graphql endpoint using introspection."""
import os

from .types import APITypes
from .types import generate_types

__all__ = ["generate_types", "APITypes"]

GRAPHQL_DATACLASSES_URL = os.environ.get("GRAPHQL_DATACLASSES_URL")
if GRAPHQL_DATACLASSES_URL:
    for name, type_ in generate_types(GRAPHQL_DATACLASSES_URL).items():
        globals()[name] = type_
        __all__.append(name)
