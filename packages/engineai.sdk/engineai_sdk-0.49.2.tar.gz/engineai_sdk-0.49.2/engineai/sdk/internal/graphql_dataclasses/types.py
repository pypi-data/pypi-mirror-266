"""Generate types from a graphql schema."""
import builtins
import dataclasses
import enum
import itertools
import keyword
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Union
from typing import cast

import dataclasses_json

from engineai.sdk.internal.graphql_dataclasses.schema import fetch_graphql_types


class DotDict(Dict[Any, Any]):
    __getattr__ = dict.get


def create_field_type(type_: Any, nullable: bool = True) -> Any:  # noqa: C901
    kind = type_.get("kind")
    name = type_.get("name")
    of_type = type_.get("ofType")

    result = Any

    if kind == "NON_NULL":
        result = create_field_type(of_type, nullable=False)

    if nullable:
        result = Optional[create_field_type(type_, nullable=False)]

    if kind == "LIST":
        result = List[create_field_type(of_type)]  # type: ignore

    if kind == "SCALAR":
        if name == "JSON":
            result = Any
        if name == "Int":
            result = int
        if name == "Float":
            result = float
        if name == "String":
            result = str
        if name == "Boolean":
            result = bool
        if name == "ID":
            result = str

    return result


def _get_default(field: Dict[str, Any]) -> Dict[str, Any]:
    return (
        {"default_factory": list}
        if field.get("type", {}).get("kind") == "LIST"
        else {"default": field.get("default", None)}
    )


def create_field(field: Any) -> Any:
    name = field.get("name")
    metadata = None
    if keyword.iskeyword(name):
        metadata = dataclasses_json.config(field_name=name)
        name = name + "_"
    type_ = create_field_type(field.get("type"))

    new_field = dataclasses.field(metadata=metadata, default=None)
    type_str = str(type_)
    if "NoneType" in type_str:
        new_field = dataclasses.field(**_get_default(field), metadata=metadata)

    return (name, type_, new_field)


def simplify_bases(bases: List[type]) -> List[type]:
    for t1, t2 in itertools.permutations(bases, 2):
        if issubclass(t1, t2):
            bases.remove(t2)
    return bases


class Singleton(type):
    """Define an unique object instance."""

    def __init__(cls, name: Any, bases: Any, attrs: Any) -> None:
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class APITypes(metaclass=Singleton):
    """Class that contains Dashboard API supported types."""

    _API_TYPES = None

    def set_types(
        self,
        url: str,
        request_headers: Optional[Mapping[str, str]] = None,
        include_typenames: bool = False,
        json: bool = True,
    ) -> None:
        """Fetches dashboard api types.

        Args:
            url (str): dashboard api url.
            request_headers (Optional[Mapping[str, str]]): headers that should be
                added to the request.
                Defaults to None.
            include_typenames (bool): flag that defines if the result should have the
                type names.
                Defaults to False.
            json (bool): flag that defines if the result uses JSON formatting.
                Defaults to True.
        """
        if self._API_TYPES is None:
            self._API_TYPES = generate_types(
                url,
                request_headers,
                include_typenames,
                json,
            )

    def get(self, input_type: str, default_class: Any = None, **kwargs: Any) -> Any:
        """Define the structure for a specific input.

        Args:
            input_type (str): input type to build.
            default_class (Any): Class to init in the event of not having the type
                inside the types dictionary.

        Raises:
            ValueError: if types were not fetched.

        Returns:
            Any: input build.
        """
        if self._API_TYPES is None:
            if default_class is None:
                raise ValueError("Types were not fetched yet and no default class set.")

            return default_class(**kwargs)

        if input_type not in self._API_TYPES:
            if default_class is None:
                raise TypeError(f"No input for {input_type=} and no default class set.")

            return default_class(**kwargs)

        input_type_build = cast(type, self._API_TYPES[input_type])

        return input_type_build(**kwargs)


def generate_types(
    url: str,
    request_headers: Optional[Mapping[str, str]] = None,
    include_typenames: bool = False,
    json: bool = True,
) -> Mapping[str, Union[type, enum.Enum]]:
    """Generates dataclasses and enums from a graphql endpoint."""
    types: Dict[str, Union[type, enum.Enum]] = DotDict()
    for type_ in fetch_graphql_types(url, request_headers):
        kind = type_.get("kind")
        name = type_.get("name") or ""
        fields = type_.get("fields") or type_.get("inputFields") or []
        interfaces = type_.get("interfaces") or []

        if name == "Query" or name == "Mutation" or (name and name.startswith("__")):
            continue

        if kind == "ENUM":
            enum_values = type_.get("enumValues")
            name = cast(str, name)
            types[name] = enum.Enum(
                name, {val.get("name"): val.get("name") for val in enum_values}
            )
            continue

        if kind == "INTERFACE":

            def init(self: Any) -> None:
                raise builtins.Exception(
                    f"'{self.__class__.__name__}' is an interface."
                )

            types[name] = type(name, (), {"__init__": init})
            continue

        if kind not in ("OBJECT", "INPUT_OBJECT"):
            continue

        if include_typenames:
            fields.append(
                {
                    "name": "__typename",
                    "default": name,
                    "type": {"kind": "SCALAR", "name": "String"},
                },
            )

        dataclass = dataclasses.make_dataclass(
            name,
            sorted(
                (create_field(field) for field in fields),
                key=lambda f: 0
                if f[2].default == dataclasses.MISSING  # type: ignore
                and f[2].default_factory == dataclasses.MISSING  # type: ignore
                else 1,
            ),
            bases=tuple(
                simplify_bases(
                    [
                        cast(type, types[interface.get("name")])
                        for interface in interfaces
                    ]
                )
            ),
        )

        if json:
            dataclass = dataclasses_json.dataclass_json(dataclass)

        types[name] = dataclass

    return types


__all__ = ["APITypes", "generate_types"]
