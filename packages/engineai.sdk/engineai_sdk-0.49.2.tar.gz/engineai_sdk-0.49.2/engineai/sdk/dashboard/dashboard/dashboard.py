"""Spec for a Dashboard."""
import logging
import os
import re
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from typing import Union
from typing import cast
from warnings import filterwarnings

from beartype import beartype
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from environs import Env

from engineai.sdk.dashboard.dashboard.typings import DashboardContent
from engineai.sdk.dashboard.utils import generate_input
from engineai.sdk.internal.rubik import Rubik

from ..abstract.typing import PrepareParams
from ..clients import DashboardAPI
from ..clients.exceptions import APIServerError
from .enums import DashboardStatus
from .exceptions import DashboardCreateRunError
from .exceptions import DashboardDuplicatedPathsError
from .exceptions import DashboardEmptyContentError
from .exceptions import DashboardInvalidSlugError
from .exceptions import DashboardNoDashboardFoundError
from .exceptions import DashboardSkipDataCannotCreateRunError
from .exit_handler import ExitHandler
from .graph import Graph
from .page.page import Page
from .version.version import DashboardVersion

filterwarnings("ignore", category=BeartypeDecorHintPep585DeprecationWarning)

logging.getLogger("azure").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


env = Env()


@dataclass
class APIResponse:
    """API response."""

    url: str
    has_connection_string: bool
    version: str
    run: str


class Dashboard:
    """Dashboard class."""

    @beartype
    def __init__(
        self,
        *,
        slug: str = "new_dashboard",
        content: Union[List[Page], DashboardContent],
        app_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        last_available_data: Optional[Union[datetime, List[str]]] = None,
        status: Optional[DashboardStatus] = None,
        version: Optional[str] = None,
        create_run: bool = False,
        skip_data: bool = False,
        activate: bool = True,
        auto_upgrade: Optional[bool] = None,
    ):
        """Construct for Dashboard class.

        Args:
            slug: unique identifier for dashboard.
            content: Dashboard content.
            app_id: App id where the dashboard will be published.
                For development purposes the app_id can be set as environment variable
                as APP_ID.
            name: Dashboard name to be displayed. Defaults to slug
                title case.
            description: Dashboard description. Markdown compliant
                string.
            last_available_data: Last available
                data for dashboard.
            status: Dashboard status.
            version: Dashboard version. By default, is None, can also be set
                using environment variable DASHBOARD_VERSION.
            create_run: create run for dashboard. If true the API will create a run,
                if false the API will pick the active run, if there isn't one it will
                be created as none.
            skip_data: skip data processing. If True the publish process will
                only update the dashboard layout, if False the publish process will
                update the data and the layout.
            activate: flag to activate the dashboard after a successful publish.
            auto_upgrade: auto upgrade dashboard version. If true the API will
                automatically upgrade the dashboard version to the published version.
        """
        self.__api_client = DashboardAPI()
        self.__slug: str = self._set_slug(slug)
        self.__name: str = name or slug.replace("_", " ").title()
        self.__pages = self.__generate_content(content=content)
        self.__skip_data = skip_data or env.bool("SKIP_DATA", False)
        self.__container_name: str
        self._set_activate(activate=activate, auto_upgrade=auto_upgrade)

        if self.__skip_data and create_run:
            raise DashboardSkipDataCannotCreateRunError()

        if create_run and version is None:
            raise DashboardCreateRunError()

        self.__version = (
            DashboardVersion(
                slug=self.__slug,
                last_available_data=last_available_data,
                status=status,
                version=version,
                create_run=create_run,
            )
            if version
            else None
        )

        self.__description = description
        self.__rubik: Optional[Rubik] = None
        self.__api_connection_string: Optional[str] = None
        self.__skip_open_dashboard = env.bool("SKIP_OPEN_DASHBOARD", True)
        self.__app_id = self._set_app_id(app_id)
        self.__publish()

    def _set_activate(
        self,
        activate: bool,
        auto_upgrade: Optional[bool] = None,
    ) -> None:
        if auto_upgrade is not None:
            warnings.warn(
                "Dashboard `auto_upgrade`flag is deprecated and it will be removed "
                "in the next major version. Please use `activate` instead.",
                DeprecationWarning,
            )

        self.__activate = (
            auto_upgrade if auto_upgrade is not None and auto_upgrade else activate
        )

    @staticmethod
    def _set_slug(slug: str) -> str:
        """Set a new dashboard slug."""
        pattern = re.compile("^[a-z0-9-_]+$")

        if pattern.search(slug) is None or slug[-1] == "_":
            raise DashboardInvalidSlugError(slug=slug)

        return slug

    @staticmethod
    def _set_app_id(app_id: Optional[str]) -> Optional[str]:
        """Set app id."""
        if (internal_app_id := os.environ.get("APP_ID")) is not None:
            return internal_app_id  # for internal use only
        return app_id

    def __generate_content(
        self, content: Union[List[Page], DashboardContent]
    ) -> List[Page]:
        if isinstance(content, List) and len(content) == 0:
            raise DashboardEmptyContentError()

        if isinstance(content, List) and all(
            isinstance(item, Page) for item in content
        ):
            return cast(List[Page], content)
        else:
            return [Page(name=self.__name, content=cast(DashboardContent, content))]

    def __publish(self) -> None:
        self.__validate_dashboard_exists()
        self.__prepare()
        self.__validate_pages()

        sys.stdout.write("\nBuilding and sending layout to the API...⏳")

        self.__set_exit_handler(self.__set_api_variables())

    def __set_api_variables(self) -> APIResponse:
        data, has_connection_string = self.__api_client.add_dashboard(
            dashboard=self.__build()
        )
        version = data["version"]
        run = data["run"]

        if has_connection_string:
            self.__api_connection_string = data["storage"]["blob"]["connectionString"]
            self.__container_name = (
                data["storage"]["blob"]["containerName"]
                + "/"
                + data["storage"]["blob"]["path"]
            )
            sys.stdout.write("\nLayout sent successfully ✅\n")

        return APIResponse(
            url=data["url"],
            has_connection_string=has_connection_string,
            version=version,
            run=run,
        )

    def __set_exit_handler(self, api_response: APIResponse) -> None:
        with ExitHandler(
            url=self.__api_client.url,
            name=self.__name,
            url_path=api_response.url,
            skip_open_dashboard=self.__skip_open_dashboard,
            activate=self.__activate,
        ):
            self.__store_data(api_response.has_connection_string)
            self.__activate_dashboard(
                version=api_response.version,
                run=api_response.run,
            )

    def __validate_pages(self) -> None:
        paths = set()
        for page in self.__pages:
            if page.path not in paths:
                paths.add(page.path)
            else:
                raise DashboardDuplicatedPathsError(page.path)
            page.validate()

    def __validate_dashboard_exists(self) -> None:
        if self.__skip_data:
            try:
                self.__api_client.get_dashboard(
                    dashboard_slug=self.__slug.replace("_", "-"),
                    app_id=self.__app_id,
                    version=None if self.__version is None else self.__version.version,
                )
            except APIServerError as e:
                raise DashboardNoDashboardFoundError(
                    slug=self.__slug,
                    app_id=self.__app_id,
                    version=None if self.__version is None else self.__version.version,
                ) from e

    def __prepare(self) -> None:
        kwargs: PrepareParams = {
            "dashboard_slug": self.__slug,
        }
        if self.__version:
            self.__version.prepare(**kwargs)
        for page in self.__pages:
            page.prepare(**kwargs)

    def key_value_storage(self) -> Rubik:
        """Returns Dashboard default storage."""
        if self.__rubik is None:
            self.__rubik = self.__create_storage_instance()
        return self.__rubik

    def __create_storage_instance(self) -> Rubik:
        return Rubik(
            base_path=self.__container_name,
            protocol="abfs",
            storage_options={
                "connection_string": self.__api_connection_string,
                "create": False,
            },
        )

    def __store_data(self, has_connection_string: bool) -> None:
        if has_connection_string and not self.__skip_data:
            kwargs: PrepareParams = {
                "dashboard_slug": self.__slug,
            }
            if has_connection_string:
                kwargs.update({"storage": self.key_value_storage()})
            widgets = []
            routes = []
            for page in self.__pages:
                routes.append(page.route)
                widgets.append(page.widgets)
            sys.stdout.write("\nPreparing to store data..⏳\n")
            Graph(widgets=widgets, routes=routes, **kwargs)

    def __activate_dashboard(self, version: str, run: str) -> None:
        if self.__activate:
            self.__api_client.activate_dashboard(
                dashboard_slug=self.__slug.replace("_", "-"),
                version=version,
                run=run,
            )

    def __build(self) -> Any:
        """Builds spec for dashboard API."""
        return generate_input(
            "DashboardInput",
            name=self.__name,
            slug=self.__slug.replace("_", "-"),
            description=self.__description,
            version=self.__version.build() if self.__version else None,
            activate=False,
            pages=[page.build() for page in self.__pages],
            appId=self.__app_id,
        )
