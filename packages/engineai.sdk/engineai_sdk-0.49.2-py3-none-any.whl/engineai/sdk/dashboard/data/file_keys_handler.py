"""Spec for a file handler that will store the keys of the widgets options in a file."""
import os
import shutil
from pathlib import Path
from typing import Any
from typing import Iterable

_TEMP_DIR = ".tmpkeys"
_SPECIAL_CHAR = "@"


class DataKeysWriter:
    """Class that stores the keys of the widgets options in a file."""

    def __init__(self, path: str, write_keys: bool, separator: str = "/") -> None:
        """Constructor for the DataKeysWriter Class."""
        Path(_TEMP_DIR).mkdir(parents=True, exist_ok=True)
        self.__fs: Any
        self.__separator = separator
        self.__write_keys = write_keys
        self.__path = Path(_TEMP_DIR) / _process_path(path, separator)

    def __enter__(self) -> "DataKeysWriter":
        if self.__write_keys:
            if os.path.exists(self.__path):
                os.remove(self.__path)
            self.__fs = open(self.__path, "a+", encoding="utf-8")
        return self

    def write(self, data: Any) -> None:
        """Write an option key in the file."""
        if self.__write_keys:
            line = ""

            if data is not None:
                try:
                    line = f"{''.join(tuple(map(str, *data)))}"
                except TypeError:
                    line = f"{f'{self.__separator}'.join(tuple(map(str, data)))}"

                self.__fs.write(f"{line}\n")

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.__write_keys:
            self.__fs.close()
            if os.stat(self.__path).st_size == 0:
                os.remove(self.__path)


class DataKeysReader:
    """Class that reads the keys of the widgets options from a file."""

    @staticmethod
    def keys(path: str, separator: str = "/") -> Iterable[str]:
        """Get the keys from the file."""
        if separator != path[-1]:
            yield path
        else:
            p = Path(_TEMP_DIR) / _process_path(path, separator)
            with open(p, "r", encoding="utf-8") as fs:
                for line in iter(fs.readline, ""):
                    yield path + line.strip()

    @staticmethod
    def delete() -> None:
        """Delete the temporary directory."""
        if os.path.exists(_TEMP_DIR):
            shutil.rmtree(_TEMP_DIR)


def _process_path(path: str, separator: str = "/") -> str:
    p = path if not path.endswith(separator) else path[:-1]
    return f"{p.replace(separator, _SPECIAL_CHAR)}.txt"
