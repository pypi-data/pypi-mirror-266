"""Helper class to connect to Dashboard API and obtain base types."""

import logging
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional

from engineai.sdk.dashboard.clients.activate_dashboard import ActivateDashboard
from engineai.sdk.internal.clients import APIClient

from .exceptions import DashboardAPINoVersionFoundError

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").propagate = False


@dataclass
class DashboardResponse:
    """API response."""

    url_path: str
    dashboard_id: str
    version: Optional[str]
    run: Optional[str]
    app_id: Optional[str]
    dashboard_slug: str


class DashboardAPI(APIClient):
    """Dashboard API Connector and Types."""

    def publish_dashboard(
        self, dashboard: Dict[Any, Any]
    ) -> Optional[DashboardResponse]:
        """Publish a Dashboard."""
        content = self._request(
            query="""
                mutation PublishDashboard ($input: DashboardInput!) {
                    publishDashboard(input: $input) {
                        run
                        id
                        version
                        url
                        appId
                        warnings {
                            message
                        }
                    }
                }
            """,
            variables={"input": dashboard},
        )

        data = content.get("data", {}).get("publishDashboard", {})

        if data is None:
            return None

        return DashboardResponse(
            url_path=data.get("url"),
            dashboard_id=data.get("id"),
            version=data.get("version", None),
            run=data.get("run", None),
            app_id=data.get("appId"),
            dashboard_slug=dashboard.get("slug", "").replace(" ", "-"),
        )

    def get_dashboard(
        self, dashboard_slug: str, app_id: Optional[str], version: Optional[str]
    ) -> None:
        """Get a dashboard."""
        return self._request(
            query="""query Dashboard($slug: String, $appId: String!, $version: String) {
                dashboard(slug: $slug, appId: $appId, version: $version) {
                    name
                }
            }""",
            variables={
                "slug": dashboard_slug,
                "appId": app_id,
                "version": version or "none",
            },
        )

    def get_dashboard_by_slug(
        self, dashboard_slug: str, version: str, run: str, app_id: Optional[str]
    ) -> Any:
        """Get a dashboard."""
        return (
            self._request(
                query="""
        query Query($slug: String!, $appId: String!, $version: String, $run: String) {
            dashboard(slug: $slug, appId: $appId, version: $version, run: $run) {
                id
            }
        }""",
                variables={
                    "slug": dashboard_slug,
                    "appId": app_id,
                    "version": version,
                    "run": run,
                },
            )
            .get("data", {})
            .get("dashboard", {})
            .get("id", "")
        )

    def list_my_apps(self) -> List:
        """List user's apps."""
        return (
            self._request(
                query="""
                query Apps {
                    myApps {
                        apps {
                            appId
                        }
                    }
                }"""
            )
            .get("data", {})
            .get("myApps", {})
            .get("apps", [])
        )

    def list_my_dashboards(self, app_id: str) -> List:
        """List user's dashboards."""
        return (
            self._request(
                query="""
                query Apps($appId: String!) {
                    app(appId: $appId) {
                        dashboards {
                            name
                            slug
                        }
                    }
                }""",
                variables={"appId": app_id},
            )
            .get("data", {})
            .get("app", {})
            .get("dashboards", [])
        )

    def list_dashboard_versions(self, app_id: str, dashboard_slug: str) -> Generator:
        """List dashboard versions."""
        dashboard_versions = self._get_dashboard_versions(app_id, dashboard_slug)
        for dashboard_version in dashboard_versions:
            yield dashboard_version

    def list_dashboard_runs(
        self, app_id: str, dashboard_slug: str, version: str
    ) -> Generator:
        """List dashboard version runs."""
        dashboard_versions = self._get_dashboard_versions(app_id, dashboard_slug)
        for dashboard_version in dashboard_versions:
            if dashboard_version.get("version") == version:
                for run in dashboard_version.get("runs", []):
                    yield run
                break

    def activate_dashboard(self, activate_dashboard: ActivateDashboard) -> None:
        """Activate a dashboard."""
        activate_dashboard_spec = activate_dashboard.build().to_dict()

        return self._request(
            query="""
                mutation ActivateDashboard($input: ActivateDashboardInput!) {
                    activateDashboard(input: $input)
                }""",
            variables={"input": activate_dashboard_spec},
        )

    def activate_dashboard_by_slug(
        self,
        app_id: str,
        slug: str,
        version: str,
        run: str,
        activate_version: bool = True,
    ) -> None:
        """Activate a dashboard."""
        dashboard_id = self.get_dashboard_by_slug(slug, version, run, app_id)
        activate_dashboard_spec = (
            ActivateDashboard(
                dashboard_id=dashboard_id,
                version=version,
                run=run,
                activate_version=activate_version,
            )
            .build()
            .to_dict()
        )

        return self._request(
            query="""
                mutation ActivateDashboard($input: ActivateDashboardInput!) {
                    activateDashboard(input: $input)
                }""",
            variables={"input": activate_dashboard_spec},
        )

    def _get_dashboard_versions(self, app_id: str, dashboard_slug: str) -> List:
        dashboard_versions = (
            self._request(
                query="""
                query DashboardVersions($appId: String!, $slug: String!) {
                    dashboardVersions(appId: $appId, slug: $slug) {
                        version
                        active
                        runs {
                            slug
                            active
                        }
                    }
                }""",
                variables={"appId": app_id, "slug": dashboard_slug},
            )
            .get("data", {})
            .get("dashboardVersions", [])
        )
        return dashboard_versions or []

    def _get_api_version(self) -> str:
        content = self._request(query="query Version {version { tag } }")

        if not self._version_content_valid(content):
            raise DashboardAPINoVersionFoundError()

        return str(content.get("data").get("version").get("tag").replace("v", ""))

    @staticmethod
    def _version_content_valid(content: Dict[str, Any]) -> bool:
        return (
            "data" in content
            and "version" in content.get("data", {})
            and "tag" in content.get("data", {}).get("version", {})
        )
