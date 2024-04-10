"""Base Package Utils."""
import sys
from typing import Any
from typing import Optional
from uuid import UUID

from tqdm.auto import tqdm

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


def generate_progressbar(
    progress_bar: bool = True, additional: bool = False, **kwargs: Any
) -> tqdm:
    """Progress bar wrapper method.

    Args:
        progress_bar (bool): include progress bar in the logs.
        additional (bool, optional): adds additional information to the progress bar.
    """
    return tqdm(
        bar_format="Progress: "
        + (
            "{percentage:3.0f}%|{bar:20}| "
            + ("Processed Widgets: " if additional else "")
            + " {n_fmt}/{total_fmt}  {bar:-20b} {desc}"
            if progress_bar
            else "{desc:40} ------- [ Elapsed: {elapsed}] -------"
        ),
        **kwargs,
        leave=True,
        file=sys.stdout,
    )
