"""Helper class to connect to Dashboard API and obtain base types."""

import json
import logging
import os
import uuid
from datetime import datetime as dt
from typing import Any
from typing import Dict
from typing import Optional

import jwt
import requests
import urllib3
from jwt.exceptions import PyJWTError
from requests.adapters import CaseInsensitiveDict
from requests.adapters import HTTPAdapter

from engineai.sdk.internal.authentication.utils import authenticate
from engineai.sdk.internal.graphql_dataclasses.exceptions import UnauthenticatedError
from engineai.sdk.internal.graphql_dataclasses.types import APITypes

from .exceptions import APIServerError
from .exceptions import APIUrlNotFound

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").propagate = False


class APIClient:
    """Class to generalize the API client."""

    def __init__(self, *, max_retries: int = 3) -> None:
        """Create connector to an API instance.

        Args:
            max_retries (int): maximum number of requests retries
        """
        self.__url = self._set_url()
        self.__token = self._get_token()
        APITypes().set_types(
            url=self.__url,
            request_headers={"Authorization": f"Bearer {self.__token}"},
        )
        self.__session = self.__initialize_session(max_retries=max_retries)

    @property
    def url(self) -> str:
        """Get address of dashboard API."""
        return self.__url

    @property
    def token(self) -> str:
        """Get token of dashboard API."""
        return self.__token

    @staticmethod
    def _set_url() -> str:
        """Set the URL of the API."""
        if os.environ.get("DASHBOARD_API_URL") is not None:
            return os.environ["DASHBOARD_API_URL"]
        else:
            raise APIUrlNotFound()

    @staticmethod
    def __initialize_session(max_retries: int = 3) -> requests.Session:
        """Creates a HTTP/HTTPS session and returns."""
        retries = urllib3.Retry(
            total=max_retries, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    @staticmethod
    def _is_valid_token(token: str) -> bool:
        try:
            information = jwt.decode(token, options={"verify_signature": False})
        except PyJWTError:
            return False
        else:
            if "exp" not in information:
                return False

            return dt.fromtimestamp(float(information.get("exp", 0))) > dt.now()

    def _get_token(self) -> str:
        """Set auth token."""
        # TODO: this is currently a workaround in order to be able to get a token
        # from the environment in a remote resource (i.e: a POD), that will
        # run a Dashboard and it won't be able to use Auth0's "Device Authorization
        # Flow". Ideally, for these cases, we use the "Client Credentials Flow"
        # (Machine to Machine), by sending a client secret, so that a token can be
        # obtained without a user having to authenticate in the web browser.
        # For more information, refer to:
        # https://auth0.com/docs/get-started/authentication-and-authorization-flow
        if "DASHBOARD_API_TOKEN" in os.environ:
            token = os.environ["DASHBOARD_API_TOKEN"]
        else:
            token = authenticate(self._set_url(), force_authentication=False)
            os.environ["DASHBOARD_API_TOKEN"] = token

        return token

    def _request(
        self, *, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Do a graphql request."""
        data = json.dumps(
            {"query": query, "variables": variables if variables is not None else {}}
        )
        headers: CaseInsensitiveDict = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {self.__token}"
        headers["x-request-id"] = str(uuid.uuid4())

        try:
            res = self.__session.post(self.__url, data=data, headers=headers)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise APIServerError(
                request_id=headers["x-request-id"], error=str(e.response.content)
            ) from requests.exceptions.RequestException

        errors = res.json().get("errors")
        if errors:
            error_extensions = errors[0].get("extensions")
            if (
                error_extensions is not None
                and error_extensions.get("code") == "UNAUTHENTICATED"
            ):
                raise UnauthenticatedError()

            raise APIServerError(
                request_id=headers["x-request-id"],
                error=errors[0].get("message"),
                error_code=error_extensions.get("code"),
            )
        return res.json()
