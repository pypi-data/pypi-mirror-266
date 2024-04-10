"""app command for engineai CLI."""
from typing import List

import click
import inquirer
from rich.console import Console
from rich.table import Table

from engineai.sdk.cli.utils import set_env_var
from engineai.sdk.cli.utils import write_console
from engineai.sdk.dashboard.clients.api import DashboardAPI
from engineai.sdk.dashboard.clients.exceptions import APIServerError
from engineai.sdk.internal.graphql_dataclasses.exceptions import UnauthenticatedError


def _get_apps() -> List:
    api = DashboardAPI()
    try:
        apps = api.list_my_apps()
    except (APIServerError, UnauthenticatedError) as e:
        write_console(f"{e}\n", 1)
    return apps


def _check_empty_apps(apps: List) -> None:
    if apps == []:
        write_console("No apps found\n", 1)


def _set_app_using_argument(app_id: str, apps: List) -> None:
    if app_id:
        if app_id not in [app.get("appId") for app in apps]:
            write_console(f"Invalid app `{app_id}`\n", 1)
        set_env_var("APP_ID", app_id)
        write_console(f"Current app set to {app_id}\n", 0)


def _set_app_via_cli(apps: List) -> None:
    app_list = [
        inquirer.List(
            "app_id",
            message="Select an app",
            choices=[app.get("appId") for app in apps],
        )
    ]
    answer = inquirer.prompt(app_list)
    set_env_var("APP_ID", answer.get("app_id"))
    write_console(f"Current app set to {answer.get('app_id')}\n")


def _show_apps(apps: List) -> None:
    """Show table for apps.

    Args:
        apps: apps object list.
    """
    if apps:
        console = Console()
        table = Table(
            title="Apps",
            show_header=False,
            show_edge=True,
        )
        for current_app in apps:
            table.add_row(current_app.get("appId"))
        console.print(table)
    else:
        write_console("No apps found\n", 0)


@click.group(name="app", invoke_without_command=False)
def app() -> None:
    """App commands."""


@app.command()
def ls() -> None:
    """List all apps."""
    api = DashboardAPI()
    try:
        apps = api.list_my_apps()
        _show_apps(apps)
    except (APIServerError, UnauthenticatedError) as e:
        write_console(f"{e}\n", 1)


@app.command()
@click.option(
    "-a",
    "--app-id",
    required=False,
    type=str,
    help="App to be set in .env file.",
)
def use(app_id: str) -> None:
    """Set the current app."""
    apps = _get_apps()
    _check_empty_apps(apps)

    _set_app_using_argument(app_id, apps)
    _set_app_via_cli(apps)
