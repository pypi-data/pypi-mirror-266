"""Class that manages the Dashboard status updates."""
import atexit
import sys
import webbrowser
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from urllib.parse import urljoin

from ..utils import notify

PLATFORM_URL: Dict[str, str] = {
    "https://api.engineai.dev": "https://platform.engineai.dev",
    "https://api.engineai.review": "https://platform.engineai.review",
    "https://api.engineai.com": "https://platform.engineai.com",
}


class ExitHandler:
    """Class that manages the at exit handlers."""

    def __init__(
        self,
        url_path: str,
        name: str,
        url: Optional[str],
        datastores_publishing: bool = False,
        skip_open_dashboard: bool = True,
        activate: bool = True,
    ) -> None:
        """Constructor for exit handlers Class.

        Args:
            url_path: dashboard slug.
            name: dashboard name.
            url: dashboard url.
            datastores_publishing: flag to show the datastores publishing.
            skip_open_dashboard: flag to skip the open dashboard.
            activate: flag to activate the dashboard.
        """
        self.__url = self.__set_url(url_path, url)
        self.__dashboard_name = name
        self.__datastores_publishing = datastores_publishing
        self.__skip_open_dashboard = skip_open_dashboard
        self.__activate = activate

    def __set_url(self, url_path: str, url: Optional[str]) -> Optional[str]:
        """Set the url of the dashboard."""
        return f"{PLATFORM_URL.get(url)}{url_path}" if url is not None else None

    def __enter__(self) -> "ExitHandler":
        if self.__datastores_publishing:
            sys.stdout.write("\nUploading Datastores into Blob..⏳\n")
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if exc_value is None:
            register_at_end(
                show_published_url,
                self.__url,
                self.__skip_open_dashboard,
                self.__activate,
            )
        else:
            atexit.unregister(show_published_url)
        register_at_end(notify, self.__dashboard_name, self.__url, exc_value)


def show_published_url(
    dashboard_url: Optional[str], skip_open_dashboard: bool, activate: bool
) -> None:
    """Notify the user when the run ends."""
    if (
        dashboard_url is not None
        and urljoin(dashboard_url, "/")[:-1] in PLATFORM_URL.values()
    ):
        if activate:
            sys.stdout.write(
                f"\n✅ Dashboard Successfully Published at: {dashboard_url} ✅\n"
            )
            if not skip_open_dashboard:
                webbrowser.open(dashboard_url)
        else:
            sys.stdout.write("\nDashboard Successfully Published but not active.\n")


def register_at_end(func: Callable[..., Any], *args: object) -> None:
    """Method that resets the at exit functions.

    Args:
        func (Callable[..., Any]): function that will be updated at exit.
    """
    atexit.unregister(func)
    atexit.register(func, *args)
