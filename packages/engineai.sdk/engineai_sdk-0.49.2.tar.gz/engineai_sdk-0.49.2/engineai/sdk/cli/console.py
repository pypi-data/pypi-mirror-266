"""Cli main file."""
import sys
from pathlib import Path
from typing import Optional
from warnings import filterwarnings

import click
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning

from engineai.sdk.internal.authentication.auth0 import DEFAULT_URL
from engineai.sdk.internal.authentication.utils import MalformedURLError
from engineai.sdk.internal.authentication.utils import URLNotSupportedError
from engineai.sdk.internal.authentication.utils import add_url_into_env_file
from engineai.sdk.internal.authentication.utils import authenticate
from engineai.sdk.internal.authentication.utils import get_url

from ..internal.graphql_dataclasses.exceptions import UnauthenticatedError
from .generator import ProjectAlreadyExistsError
from .generator import generate_template
from .generator import remove_temporary_files
from .utils import run_env

filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)

URL_HELP = (
    "URL of the EngineAI Platform API. Skipping option in the "
    "event you are using DASHBOARD_API_URL environment variable. "
    f"Default: {DEFAULT_URL}"
)

DASHBOARD_CREATED_MSG = (
    "\nDashboard created! To publish your dashboard, navigate to "
    "`{}` folder and run `engineai dashboard publish` to publish.\n"
)


@click.group()
def process() -> None:
    """Platform SDK Command Line Interface."""


@process.command()
@click.option(
    "-u",
    "--url",
    type=str,
    default=None,
    help=URL_HELP,
)
def login(
    url: Optional[str] = None,
) -> None:
    """Log in the EngineAI API Authentication System."""
    try:
        url = get_url(url)
        add_url_into_env_file(url=url)
        authenticate(url, force_authentication=True)
    except (MalformedURLError, URLNotSupportedError) as e:
        sys.stdout.write(f"\n{e}\n")
        sys.exit(1)


@process.group(name="dashboard", invoke_without_command=False)
def dashboard() -> None:
    """Dashboard commands."""


@dashboard.command()
def tutorial() -> None:
    """Create a simple and functional dashboard."""
    try:
        generate_template(dashboard_slug="new_dashboard", tutorial=True)
        sys.stdout.write(DASHBOARD_CREATED_MSG.format("new_dashboard"))
    except ProjectAlreadyExistsError:
        sys.stdout.write(
            "\nDashboard already exists and has tutorial data! "
            "Please, remove it first or use another slug.\n"
        )
    finally:
        remove_temporary_files()


@dashboard.command()
def init() -> None:
    """Create a simple and functional dashboard."""
    try:
        slug = click.prompt(
            "Name your project", default="new_dashboard", type=str, show_default=True
        )

        generate_template(dashboard_slug=slug, tutorial=False)
        sys.stdout.write(DASHBOARD_CREATED_MSG.format(slug))
    except ProjectAlreadyExistsError:
        sys.stdout.write(
            "\nDashboard already exists! Please, remove it first or use another slug.\n"
        )
    finally:
        remove_temporary_files()


@dashboard.command()
@click.option(
    "-f",
    "--filename",
    type=str,
    default="main.py",
    help=("Overwrite default Dashboard file directory."),
)
@click.option(
    "-u",
    "--url",
    type=str,
    default=None,
    help=URL_HELP,
)
@click.option(
    "--skip-data",
    type=bool,
    is_flag=True,
    default=False,
    help=(
        "Skip the data processing and validation. Can only be used after "
        "the first complete run. It is useful to increase the dashboard performance."
    ),
)
@click.option(
    "--skip-browser",
    type=bool,
    is_flag=True,
    default=False,
    help=("Skip the browser opening after the dashboard is published."),
)
def publish(
    url: str,
    skip_data: bool,
    skip_browser: bool,
    filename: Optional[str] = None,
) -> None:
    """Log in the user and publish a dashboard into Dashboard API."""
    try:
        add_url_into_env_file(url=get_url(url))
        run_env(Path(filename).resolve(), skip_data, skip_browser)
    except (MalformedURLError, URLNotSupportedError, UnauthenticatedError) as e:
        sys.stdout.write(f"\n{e}\n")
        sys.exit(1)
