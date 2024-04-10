"""Inspect a graphql schema."""
import builtins
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from urllib.parse import urlparse

import requests
import toposort

from engineai.sdk.internal.graphql_dataclasses.exceptions import UnauthenticatedError

query = """
query schema {
    __schema {
        queryType {
            name
        }
        types {
            kind
            name
            description
            fields {
                name
                description
                type {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                            }
                        }
                    }
                }
            }
            interfaces {
                kind
                name
            }
            enumValues {
                name
                description
            }
            inputFields {
                name
                description
                type {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                            }
                        }
                    }
                }
            }
        }
    }
}
"""


def topological_sort(types: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    deps = toposort.toposort_flatten(
        {
            type_.get("name"): {
                interface.get("name") for interface in type_.get("interfaces") or []
            }
            for type_ in types
        }
    )

    return [
        next(type_ for type_ in types if type_.get("name") == type_name)
        for type_name in deps
    ]


def fetch_graphql_types(
    url: str, request_headers: Optional[Mapping[str, str]] = None
) -> List[Dict[str, Any]]:
    """Fetches types from a graphql endpoint."""
    if not urlparse(url).netloc:
        raise ValueError(
            f"URL ({url if url else 'empty'}) is malformed. Please use the default "
            "or insert a valid one."
        )

    res = requests.post(url, headers=request_headers, json={"query": query}, timeout=10)

    content = res.json()
    errors = content.get("errors")

    if errors:
        error_extensions = errors[0].get("extensions")
        if (
            error_extensions is not None
            and error_extensions.get("code") == "UNAUTHENTICATED"
        ):
            raise UnauthenticatedError()

        raise builtins.Exception(errors)

    data = content.get("data")
    types = data.get("__schema", {}).get("types", [])

    return topological_sort(types)


__all__ = ["fetch_graphql_types"]
