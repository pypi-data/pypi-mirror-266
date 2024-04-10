"""Base Package Utils."""
import sys
import threading
from typing import Any
from typing import Optional
from urllib.parse import urlparse
from uuid import UUID

from engineai.sdk.internal.graphql_dataclasses.types import APITypes

if sys.platform == "darwin":
    from pathlib import Path

    import pync


def generate_input(input_type: str, default_class: Any = None, **kwargs: Any) -> Any:
    """Method to abstract the APITypes call."""
    return APITypes().get(input_type, default_class, **kwargs)


def notify(dashboard_name: str, dashboard_url: Optional[str], exc_value: Any) -> None:
    """Notify the user that the dashboard run is over.

    Args:
        dashboard_name (str): dashboard name.
        dashboard_url (Optional[str]): dashboard url.
        exc_value (Any): exception value, if any.
    """
    if sys.platform == "darwin":
        base_path = Path(__file__).parent.absolute()
        open_link = {"open": dashboard_url} if dashboard_url is not None else {}
        message = "Dashboard Successfully Published." + (
            " Click to open Dashboard" if dashboard_url is not None else ""
        )
        pync.notify(
            message=message
            if exc_value is None
            else "An Error Occurred While Publishing Dashboard",
            title=f"EngineAI - {dashboard_name}",
            contentImage=f"{base_path}/assets/engineai_logo.png",
            **open_link,
        )


def is_uuid(uuid_str: str, version: int = 4) -> bool:
    """Validates if uuid_str is a valid uuid within a certain version.

    Args:
        uuid_str (str): uuid string.
        version (int, optional): uuid version of uuid_str.

    Returns:
        bool: whether uuid_str is a uuid or not.
    """
    try:
        uuid_obj = UUID(uuid_str, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_str


def _validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_valid_url(url: str) -> None:
    """Check if the url is valid."""
    if not _validate_url(url):
        raise ValueError(f"Invalid URL: {url}")


class ProgressBar:
    """Class that handles a custom progress bar."""

    def __init__(self, total: int = -1, length: int = 50) -> None:
        """Constructor for ProgressBar."""
        self.total = total
        self.length = length
        self.lock = threading.Lock()
        self.counter = 0

    def write(self, message: str, flush: bool = True) -> None:
        """Write a message to stdout."""
        with self.lock:
            sys.stdout.write(f"\n{message}\n\n")
            if flush:
                sys.stdout.flush()

    def update(self) -> None:
        """Iterates the progress bar."""
        self.counter += 1
        progress = self.counter / self.total
        with self.lock:
            bar_format = (
                "\nProgress: [{:<" + str(self.length) + "}] {}%  Data Sources: {}/{}"
            )
            bar_output = bar_format.format(
                "=" * int(self.length * progress),
                int(progress * 100),
                self.counter,
                self.total,
            )
            sys.stdout.write("\r" + bar_output)
            sys.stdout.flush()

    def finish(self, message="Done!") -> None:
        """Writes the final message to stdout."""
        with self.lock:
            sys.stdout.flush()
            sys.stdout.write(f"{message}\n")
