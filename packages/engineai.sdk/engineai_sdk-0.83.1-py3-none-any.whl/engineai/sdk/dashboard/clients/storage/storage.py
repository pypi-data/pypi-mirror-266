"""Storage module."""
import logging
import uuid
from dataclasses import dataclass
from time import perf_counter_ns
from typing import Any
from typing import Dict
from typing import Final
from typing import List
from typing import MutableMapping
from typing import Optional
from typing import Union

import brotli
import requests
from pandas import DataFrame
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from engineai.sdk.dashboard.clients.storage.serialization import default_serialize

from .exceptions import StorageError

_COMPRESSION_MIN_LENGTH: Final[int] = 1_000  # 1Kb

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


@dataclass
class StorageConfig:
    """Storage configuration."""

    base_path: str
    headers: Optional[Dict[str, str]] = None


class Storage(MutableMapping[str, DataT]):
    """The `Storage` class."""

    _base_path: str

    def __init__(
        self,
        base_path: str,
        **kwargs: Any,
    ) -> None:
        """Instantiates a `Storage` object.

        Args:
            base_path: Path where the data will be stored.
            headers: Headers to use for the data storage
                when using `http` or `https` protocol.
        """
        self._headers = self.__set_headers(kwargs.get("headers", None))
        self._base_path: str = base_path
        self._session = self._create_session()

    def __delitem__(self, key: str, /) -> None:
        raise NotImplementedError

    def __iter__(self) -> Any:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    @property
    def headers(self) -> Dict[str, Dict[str, str]]:
        """The Storage's headers.

        Returns:
            Dict[str, str]: A dictionary of headers.
        """
        return {
            "headers": {
                "x-request-id": str(uuid.uuid4()),
                **self._headers.copy(),
            }
        }

    def __set_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        if headers is None:
            return {}
        return headers

    def __getitem__(self, key: str, /) -> DataT:
        raise NotImplementedError

    def __setitem__(self, key: str, value: Optional[DataT], /) -> None:
        serialized_value, _ = default_serialize(value)

        self._write(key, serialized_value)

    def __repr__(self) -> str:
        return "<" f"{self.__class__.__name__} (" f"base_path={self.base_path}," ")>"

    @property
    def base_path(self) -> str:
        """The Storage's base path.

        Returns:
            str: A path like object.
        """
        return self._base_path

    def _write(self, path: str, data: bytes) -> None:
        t_start = perf_counter_ns()
        size = len(data)
        headers = self.headers

        if size >= _COMPRESSION_MIN_LENGTH:
            data = brotli.compress(data, quality=1)
            headers["headers"].update({"Content-Encoding": "br"})

        try:
            res = self._session.put(
                self._base_path + path,
                data=data,
                timeout=180,
                headers=headers["headers"],
            )

            res.raise_for_status()

            with open(".storage.txt", mode="a+", encoding="utf-8") as f:
                f.write(self._base_path + path + "\n")

        except requests.exceptions.RequestException as e:
            raise StorageError(
                self._base_path + path,
                e.response.status_code if e.response is not None else None,
            ) from e

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

    def _create_session(self) -> requests.Session:
        """Create a session."""
        session = requests.Session()
        retry = Retry(
            total=10,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def close(self) -> None:
        """Close the session."""
        self._session.close()
