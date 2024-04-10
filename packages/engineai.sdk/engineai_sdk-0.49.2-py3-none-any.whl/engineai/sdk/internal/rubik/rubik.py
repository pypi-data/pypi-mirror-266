"""Rubik module."""
import concurrent.futures
import logging
import os
import queue
from pathlib import Path
from time import perf_counter_ns
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Final
from typing import Iterable
from typing import Iterator
from typing import KeysView
from typing import List
from typing import Mapping
from typing import MutableMapping
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union
from typing import cast
from typing import overload

import brotli
import fsspec
from azure.storage.blob import ContentSettings
from pandas import DataFrame

from engineai.sdk.internal.rubik.serialization import default_deserialize
from engineai.sdk.internal.rubik.serialization import default_serialize

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem

_COMPRESSION_MIN_LENGTH: Final[int] = 1_000  # 1Kb
_THREAD_POOL_MAX_WORKERS: Final[int] = 8
_DATA_EXT: Final[str] = ".json"
_SCHEMA_EXT: Final[str] = ".schema" + _DATA_EXT

_VT_co = TypeVar("_VT_co", covariant=True)
DataT = Union[
    bool,
    int,
    float,
    str,
    List[Any],
    Dict[str, Any],
    DataFrame,
]
"""Type representing possible data values."""

logger = logging.getLogger(__name__)


class ThreadPoolExecutorWithQueueSizeLimit(concurrent.futures.ThreadPoolExecutor):
    """`ThreadPoolExecutorWithQueueSizeLimit` class."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes a `ThreadPoolExecutorWithQueueSizeLimit` instance."""
        super().__init__(*args, **kwargs)
        self._work_queue = cast("queue.SimpleQueue[Any]", queue.Queue(maxsize=50))


class RubikKeysViewStartsWith(KeysView[str]):
    """KeysView implementation with support for starts_with."""

    _mapping: "Rubik"
    _starts_with: str

    def __init__(self, mapping: "Rubik", starts_with: str) -> None:
        """Instantiates a `RubikKeysViewStartsWith` object."""
        super().__init__(mapping)
        self._starts_with = starts_with

    def __len__(self) -> int:
        return sum(1 for _ in self.__iter__())

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        return key in self.__iter__()

    def __iter__(self) -> Iterator[str]:
        base_path_len = len(str(Path(self._mapping.fs_mapper.root))) + 1

        def _walk(base_path: str, starts_with: str) -> Iterable[str]:
            for path, dirs, files in self._mapping.fs_mapper.fs.walk(
                base_path, maxdepth=1
            ):
                base_key = path[base_path_len:]

                for dir_ in dirs:
                    key = os.path.join(base_key, dir_)
                    if key.startswith(starts_with[0 : len(key)]):
                        yield from _walk(f"{path}/{dir_}", starts_with)

                for file in files:
                    if file.endswith(_SCHEMA_EXT):
                        continue

                    key = os.path.join(base_key, file)[: -len(_DATA_EXT)]
                    if key.startswith(starts_with):
                        yield key

        yield from _walk(self._mapping._base_path, self._starts_with)


class Rubik(MutableMapping[str, DataT]):
    """The `Rubik` class."""

    __executor: Optional[ThreadPoolExecutorWithQueueSizeLimit]
    _base_path: str
    _protocol: str
    _fs_mapper: fsspec.mapping.FSMap

    def __init__(
        self,
        base_path: str,
        protocol: str,
        storage_options: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Instantiates a `Rubik` object.

        Args:
            base_path (str): The rubik's base path.
            protocol (str): A protocol.
            storage_options (Dict[str, Any]): Backend parameters.
        """
        self.__executor = None
        self._base_path = base_path
        self._protocol = protocol

        default_options = {
            "create": True,
            "skip_instance_cache": True,
            "use_listings_cache": False,
        }
        storage_options = storage_options or {}
        self._fs_mapper = fsspec.get_mapper(
            f"{protocol}://{base_path}",
            **{**default_options, **storage_options},
        )

    @property
    def fs_mapper(self) -> fsspec.mapping.FSMap:
        """The rubik's fs mapper.

        Returns:
            fsspec.mapping.FSMap: A fs mapper.
        """
        return self._fs_mapper

    def __read_schema(self, key: str, /) -> Optional[bytes]:
        try:
            return self._read(key + _SCHEMA_EXT)
        except KeyError:
            return None

    def __getitem__(self, key: str, /) -> DataT:
        serialized_value = self._read(key + _DATA_EXT)
        value: DataT = default_deserialize(
            serialized_value,
            schema=lambda: self.__read_schema(key),
        )
        return value

    def __setitem__(self, key: str, value: Optional[DataT], /) -> None:
        serialized_value, serialized_schema = default_serialize(value)
        if isinstance(value, list):
            try:
                self.__delitem__(key + _SCHEMA_EXT)
            except KeyError:
                pass

        self._write(key + _DATA_EXT, serialized_value)

        if serialized_schema is not None:
            self._write(key + _SCHEMA_EXT, serialized_schema)

    def __delitem__(self, key: str, /) -> None:
        self._fs_mapper.__delitem__(key + _DATA_EXT)
        try:
            self.__delitem__(key + _SCHEMA_EXT)
        except KeyError:
            pass

    def __iter__(self) -> Iterator[str]:
        return (x[: -len(_DATA_EXT)] for x in self._fs_mapper.__iter__())

    def __len__(self) -> int:
        return cast(int, self._fs_mapper.__len__())

    def __contains__(self, key: object, /) -> bool:
        return cast(
            bool,
            self._fs_mapper.__contains__(self._fs_mapper._key_to_str(key) + _DATA_EXT),
        )

    def __del__(self) -> None:
        if self.__executor is not None:
            self.__executor.shutdown()

    def __repr__(self) -> str:
        return (
            "<"
            f"{self.__class__.__name__} ("
            f"base_path={self.base_path},"
            f"protocol={self._protocol}"
            ")>"
        )

    @property
    def _executor(self) -> ThreadPoolExecutorWithQueueSizeLimit:
        if self.__executor is None:
            self.__executor = ThreadPoolExecutorWithQueueSizeLimit(
                max_workers=_THREAD_POOL_MAX_WORKERS,
                thread_name_prefix="rubik_ops",
            )

        return self.__executor

    @property
    def base_path(self) -> str:
        """The rubik's base path.

        Returns:
            str: A path like object.
        """
        return self._base_path

    @property
    def protocol(self) -> str:
        """The rubik's protocol.

        Returns:
            str: A protocol.
        """
        return self._protocol

    def _read(self, path: str) -> bytes:
        t_start = perf_counter_ns()
        try:
            f = self._fs_mapper.fs.open(self._base_path + "/" + path)
        except FileNotFoundError as err:
            raise KeyError from err

        value: bytes = f.read()
        if (
            self._protocol == "abfs"
            # _details attr only available in abfs protocol
            and f._details["content_settings"][  # pylint: disable=W0212
                "content_encoding"
            ]
            == "br"
        ):
            value = brotli.decompress(value)

        size = len(value)
        t_elapsed = (perf_counter_ns() - t_start) * 1e-6

        logger.info(
            "Read operation finished: (base_path='%s', path='%s', size='%s')",
            self._base_path,
            path,
            size,
            extra={
                "function": "_read",
                "base_path": self._base_path,
                "path": path,
                "size": size,
                "elapsed": t_elapsed,
            },
        )

        return value

    def _write(self, path: str, data: bytes) -> None:
        t_start = perf_counter_ns()
        size = len(data)
        kwargs = {}
        if self._protocol == "abfs" and len(data) >= _COMPRESSION_MIN_LENGTH:
            data = brotli.compress(data, quality=1)
            content_settings = ContentSettings(
                content_type="application/json",
                content_encoding="br",
            )
            kwargs.update({"content_settings": content_settings})

        if len(directory := path.rsplit("/", maxsplit=1)) > 1:
            self._fs_mapper.fs.makedirs(
                os.path.join(self.base_path, directory[0]),
                exist_ok=True,
            )

        self._fs_mapper.fs.write_bytes(
            f"{self.base_path}/{path}",
            data,
            overwrite=True,
            **kwargs,
        )
        t_elapsed = (perf_counter_ns() - t_start) * 1e-6

        logger.info(
            "Write operation finished: (base_path='%s', path='%s', size='%s')",
            self._base_path,
            path,
            size,
            extra={
                "function": "_write",
                "path": path,
                "size": size,
                "elapsed": t_elapsed,
            },
        )

    def clear(self) -> None:
        """Remove all items from current rubik instance and its backend."""
        futures = []
        for path, dirs, files in self._fs_mapper.fs.walk(
            self._fs_mapper.root, maxdepth=1
        ):
            for dir_ in dirs:
                futures.append(
                    self._executor.submit(
                        self._fs_mapper.fs.rm,
                        os.path.join(path, dir_),
                        recursive=True,
                    )
                )
            for file in files:
                futures.append(
                    self._executor.submit(
                        self._fs_mapper.fs.rm,
                        os.path.join(path, file),
                        recursive=True,
                    )
                )
        concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)

    @overload
    def keys(self) -> KeysView[str]:
        ...

    @overload
    def keys(self, starts_with: Optional[str]) -> KeysView[str]:
        ...

    def keys(self, starts_with: Optional[str] = None) -> KeysView[str]:
        """A list of keys.

        Args:
            starts_with (Optional[str]): Lists keys only with the same starting path.
                Defaults to `None`.

        Returns:
            Iterable[str]: An iterable of keys.
        """
        if starts_with is None:
            return super().keys()

        return RubikKeysViewStartsWith(self, starts_with)

    def getitems(
        self, keys: Iterable[str], /, default: Optional[_VT_co] = None
    ) -> Dict[str, Union[DataT, Optional[_VT_co]]]:
        """Returns a dict object containing the data for the respective given keys.

        Args:
            keys (Iterable[str]): A list of keys.
            default (Optional[Any]): The default to use if data is not found for a key.
                If not initialized and a key data is not found an exception will occur.
                Defaults to `missing`.

        Returns:
            Dict[str, DataT]: A dictionary containing the filtered keys and their data.
        """
        futures = {
            key: self._executor.submit(self.get, key, default)  # type: ignore[call-arg]
            for key in keys
        }
        return {k: f.result() for k, f in futures.items()}

    @overload
    def update(
        self, other: "SupportsKeysAndGetItem[str, DataT]", /, **kwargs: DataT
    ) -> None:
        ...

    @overload
    def update(self, other: Iterable[Tuple[str, DataT]], /, **kwargs: DataT) -> None:
        ...

    @overload
    def update(self, /, **kwargs: DataT) -> None:
        ...

    def update(
        self,
        other: Union[
            "SupportsKeysAndGetItem[str, DataT]", Iterable[Tuple[str, DataT]]
        ] = (),
        /,
        **kwargs: DataT,
    ) -> None:
        """Updates current instance key-values pairs.

        Args:
            other (Union[SupportsKeysAndGetItem[str, DataT], Mapping[str, DataT]):
                A mapping like object.
            kwargs (DataT): Keyword arguments to write as key-value pairs.
        """
        futures = []

        if isinstance(other, Mapping):
            for key in other:
                futures.append(
                    self._executor.submit(
                        self.__setitem__,
                        key,
                        other[key],
                    )
                )
        elif hasattr(other, "keys") and hasattr(other, "__getitem__"):
            for key in other.keys():
                futures.append(
                    self._executor.submit(
                        self.__setitem__,
                        key,
                        other[key],
                    )
                )
        else:
            for key, value in other:
                futures.append(
                    self._executor.submit(
                        self.__setitem__,
                        key,
                        value,
                    )
                )

        for key, value in kwargs.items():
            futures.append(
                self._executor.submit(
                    self.__setitem__,
                    key,
                    value,
                )
            )
        concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)

    def copy_from(self, other: "Rubik", /, starts_with: Optional[str] = None) -> None:
        """Copies `other` items into current rubik's instance.

        Args:
            other (Rubik): A rubik object.
            starts_with (Optional[str]): Copies data only with the same starting path.
                Defaults to `None`.
        """

        def _set_other_item(other: "Rubik", key: str) -> None:
            self[key] = other[key]

        futures = [
            self._executor.submit(_set_other_item, other, key)
            for key in other.keys(starts_with)
        ]
        concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
