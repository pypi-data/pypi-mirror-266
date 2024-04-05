# Copyright 2023 Iguazio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""The API client used to communicate with the Iguazio backend."""
import base64
import copy
import logging
import os
import typing
from http import HTTPStatus

import httpx
import inflection
import semver

import igz_mgmt.common
import igz_mgmt.constants
import igz_mgmt.logger


class _BaseHTTPClient:
    def __init__(
        self,
        parent_logger: igz_mgmt.logger.Logger,
        api_url: str,
        *,
        timeout: int = 60,
        retries: int = 3,
    ) -> None:
        super().__init__()
        self._logger = parent_logger.get_child("httpc")
        self._transport = httpx.HTTPTransport(verify=False, retries=retries)
        self._cookies = httpx.Cookies()
        self._headers = {
            igz_mgmt.constants._RequestHeaders.content_type_header: "application/json"
        }
        self._session = httpx.Client(
            base_url=api_url,
            timeout=timeout,
            mounts={
                "http://": self._transport,
                "https://": self._transport,
            },
            cookies=self._cookies,
        )
        self._api_url = api_url

    def post(self, path, error_message: str = "", **kwargs) -> httpx.Response:
        return self._send_request("POST", path, error_message, **kwargs)

    def get(self, path, error_message: str = "", **kwargs) -> httpx.Response:
        return self._send_request("GET", path, error_message, **kwargs)

    def delete(self, path, error_message: str = "", **kwargs) -> httpx.Response:
        ignore_status_codes = []
        if kwargs.pop("ignore_missing", False):
            ignore_status_codes.append(HTTPStatus.NOT_FOUND)
        return self._send_request(
            "DELETE",
            path,
            error_message,
            ignore_status_codes=ignore_status_codes,
            **kwargs,
        )

    def put(self, path, error_message: str = "", **kwargs) -> httpx.Response:
        return self._send_request("PUT", path, error_message, **kwargs)

    def close(self):
        self._session.close()

    def _send_request(
        self, method, path, error_message: str, **kwargs
    ) -> httpx.Response:
        endpoint = f"api/{path.lstrip('/')}"

        if kwargs.get("timeout") is None:
            kwargs["timeout"] = 60

        self._logger.debug_with(
            "Sending request", method=method, endpoint=endpoint, **kwargs
        )
        headers = copy.deepcopy(self._headers)
        headers.update(kwargs.pop("headers", {}))

        # setting the cookie jar to the session
        # this is mostly needed for first request onwards, but it's not harmful to set it every time
        self._session.cookies.update(self._cookies)
        ignore_status_codes = kwargs.pop("ignore_status_codes", [])
        response = self._session.request(method, endpoint, headers=headers, **kwargs)
        ctx = self._resolve_ctx_from_response(response)

        # updating the cookies jar with server-response
        self._cookies.update(response.cookies)

        self._logger.debug_with(
            "Received response", status_code=response.status_code, ctx=ctx
        )
        if response.is_error and response.status_code not in ignore_status_codes:
            log_kwargs = copy.deepcopy(kwargs)
            log_kwargs.update({"method": method, "path": path})
            if response.content:
                errors = self._resolve_errors_from_response(response)
                if errors:
                    error_message = f"{error_message}: {str(errors)}"
                    log_kwargs.update({"ctx": ctx, "errors": errors})
                else:
                    log_kwargs.update({"response_content": response.content})

            self._logger.warn_with("Request failed", **log_kwargs)

            # reraise with a custom error message to avoid the default one which
            # is not very customizable and friendly
            raise httpx.HTTPStatusError(
                error_message, request=response.request, response=response
            )

        return response

    @staticmethod
    def _resolve_ctx_from_response(response: httpx.Response):
        try:
            return response.json().get("meta", {}).get("ctx")
        except Exception:
            return None

    @staticmethod
    def _resolve_errors_from_response(response):
        try:
            return response.json().get("errors", [])
        except Exception:
            return None


class APIClient:
    """Client protocol to communicate with the Iguazio system.

    Args:
        endpoint (str, optional): system endpoint.
        timeout (int, optional): protocol timeout.
        retries (int, optional): number of retries for a request before failing.
        username (str, optional): username to log in the system.
        password (str, optional): password to log in the system.
        access_key (str, optional): control plane access key for the Iguazio system.
    """

    __DEFAULT_EXTERNAL_VERSION_NUMBER = "3.4.2"

    def __init__(
        self,
        *,
        endpoint: str = "",
        timeout: int = 60,
        retries: int = 3,
        username: str = "",
        password: str = "",
        access_key: str = "",
        logger: typing.Optional[logging.Logger] = None,
    ):
        if password and access_key:
            raise ValueError("Must provide either password or access key")

        if not username and not access_key:
            username = os.getenv("V3IO_USERNAME")
        if password and not username:
            raise ValueError("Must provide username when providing password")

        if not password and not access_key:
            access_key = os.getenv("V3IO_ACCESS_KEY")

        self._logger = igz_mgmt.get_or_create_logger(
            level="INFO", name="apic", logger=logger
        )

        # enriched once authenticated
        self._tenant_id: typing.Optional[str] = None

        self._client = _BaseHTTPClient(
            self._logger,
            igz_mgmt.common.helpers.get_endpoint(endpoint, default_scheme="https"),
            timeout=timeout,
            retries=retries,
        )

        self._version = None
        self._authenticated = False
        self._username = username
        self._password = password
        if access_key:
            self._set_auth(username=username, access_key=access_key)
            self._authenticated = True

    def close(self):
        """Closes the client connection."""
        self._client.close()

    def login(self, *, username: str = "", password: str = ""):
        """Authenticates to the API server using username and password.

        Args:
            username (str): The username to log in with.
            password (str): The password to log in with.
        """
        username = username or self._username
        password = password or self._password

        # validate both username and password are provided
        if not (username and password):
            raise ValueError("Username and password must be provided")

        self._login(username, password)

        self._authenticated = True
        self._username = username
        self._password = password
        self._logger.info("Successfully logged in")

    def with_access_key(self, access_key: str):
        """Sets the access key to be used for authentication.

        Args:
            access_key (str): The new access key.

        Returns:
            APIClient: The client protocol.
        """
        self._set_auth(access_key=access_key)
        self._authenticated = True
        return self

    def create(self, resource_name: str, attributes, relationships=None, **kwargs):
        """Creates a new resource.

        Args:
            resource_name (str): The resource name.
            attributes: The resource attributes.
            relationships (optional): The resource relationships. None by default.
            **kwargs: additional arguments to pass to the request.
        """
        response = self._client.post(
            inflection.pluralize(resource_name),
            f"Failed to create {resource_name}".strip(),
            json=self._compile_api_request(resource_name, attributes, relationships),
            **kwargs,
        )
        return response.json()

    def update(
        self, resource_name: str, resource_id, attributes, relationships=None, **kwargs
    ):
        """Updates an existing resource.

        Args:
            resource_name (str): The resource name.
            resource_id: The resource ID
            attributes: The resource attributes.
            relationships (optional): The resource relationships. None by default.
            **kwargs: additional arguments to pass to the request.
        """
        path = f"{inflection.pluralize(resource_name)}"
        if resource_id:
            path = f"{path}/{resource_id}"
        return self._client.put(
            path,
            f"Failed to update {resource_name} {resource_id}".strip(),
            json=self._compile_api_request(resource_name, attributes, relationships),
            **kwargs,
        )

    def delete(self, resource_name: str, resource_id, **kwargs):
        """Deletes an existing resource.

        Args:
            resource_name (str): The resource name.
            resource_id: The resource ID
            **kwargs: additional arguments to pass to the request.
        """
        return self._client.delete(
            f"{inflection.pluralize(resource_name)}/{resource_id}",
            f"Failed to delete {resource_name} {resource_id}".strip(),
            **kwargs,
        )

    def delete_by_attribute(
        self, resource_name: str, attribute_name: str, attribute_value: str, **kwargs
    ):
        """Deletes an existing resource by resource attribute.

        Args:
            resource_name (str): The resource name.
            attribute_name (str): The identifying attribute in the resource to be deleted.
            attribute_value (str): The value of the resource attribute to delete by.
            **kwargs: additional arguments to pass to the request.
        """
        attributes = {attribute_name: attribute_value}
        return self._client.delete(
            f"{inflection.pluralize(resource_name)}",
            f"Failed to delete {resource_name} by {attribute_name}:{attribute_value}".strip(),
            json=self._compile_api_request(resource_name, attributes),
            **kwargs,
        )

    def detail(self, resource_name: str, resource_id, **kwargs):
        """Gets an existing single resource.

        Args:
            resource_name (str): The resource name.
            resource_id: The resource ID to delete
            **kwargs: additional arguments to pass to the request.
        """
        response = self._client.get(
            f"{inflection.pluralize(resource_name)}/{resource_id}",
            f"Failed to get {resource_name} {resource_id}".strip(),
            **kwargs,
        )
        return response.json()

    def list(self, resource_name: str, **kwargs):
        """Lists existing resources.

        Args:
            resource_name (str): The resource name.
            **kwargs: additional arguments to pass to the request.
        """
        response = self._client.get(
            inflection.pluralize(resource_name),
            f"Failed to list {inflection.pluralize(resource_name)}".strip(),
            **kwargs,
        )
        return response.json()

    def request(self, method, path, **kwargs):
        """Executes a raw request.

        Args:
            method: The request method.
            path: The request path.
            **kwargs: additional arguments to pass to the request.
        """
        response = self._client._send_request(
            method, path, "Failed to execute request", **kwargs
        )
        return response.json()

    @staticmethod
    def _compile_api_request(data_type, attributes, relationships=None):
        return {
            "data": {
                "type": data_type,
                "attributes": attributes,
                "relationships": relationships if relationships else {},
            },
        }

    def _login(self, username: str, password: str):
        self._logger.debug_with("Authenticating", username=username)
        response = self._client.post(
            "/sessions",
            "Authentication failed",
            json=self._compile_api_request(
                data_type="session",
                attributes={
                    "username": username,
                    "password": password,
                    "plane": igz_mgmt.constants.SessionPlanes.control.value,
                },
            ),
        )
        self._set_auth(username=username, session=response.cookies.get("session"))

    def _set_auth(self, username: str = "", access_key: str = "", session: str = ""):
        if access_key and session:
            raise ValueError("Cannot set both access_key and session")
        self._client._cookies.set(
            "session",
            f'j:{{"sid": "{access_key}"}}' if access_key else session,
        )

        if access_key and username:
            encoded_auth = f"{username}:{access_key}"
            base64_encoded_auth = base64.b64encode(encoded_auth.encode("utf-8")).decode(
                "utf-8"
            )
            self._client._headers[
                igz_mgmt.constants._RequestHeaders.authorization_header
            ] = f"Basic {base64_encoded_auth}"

        self._version = self._get_external_versions()
        self._session_verification()

    def _try_resolve_external_version(self, node):
        try:
            # get external version via tunnel
            response = self._client.get(
                "/tunnel/{0}.version.0/external_versions/{0}".format(node),
                "Failed to get external version from node {0}".format(node),
                timeout=10,
            )
            version = (
                response.json().get("data", {}).get("attributes", {}).get("external")
            )
            return semver.VersionInfo.parse(version).finalize_version()
        except Exception as exc:
            self._logger.debug_with(str(exc) or repr(exc))
            return None

    def _get_external_versions(self):
        # try to iterate over 3 nodes
        for node in ["igz0", "igz1", "igz2"]:
            external_version = self._try_resolve_external_version(node)
            if external_version:
                return external_version

        # if got here, something is off
        self._logger.info(
            "Failed to resolve auto detect iguazio external version, use `client.version = x.y.z` for explicitness"
        )

        # oldest supported GA version
        return self.__DEFAULT_EXTERNAL_VERSION_NUMBER

    def _session_verification(self):
        response = self.request("POST", "/sessions/verifications/planes/any/internal")
        response_attributes = response.get("data", {}).get("attributes", {})
        self._tenant_id = (
            response_attributes.get("context", {})
            .get("authentication", {})
            .get("tenant_id")
        )
        self._username = response_attributes.get("username", self._username)

    @property
    def tenant_id(self) -> str:
        """Authenticated session tenant id.

        Returns:
            tenant id
        """
        if not self._authenticated:
            raise RuntimeError("Must .login() first")
        return self._tenant_id

    @property
    def username(self) -> str:
        """Authenticated username.

        Returns:
            username
        """
        if not self._authenticated:
            raise RuntimeError("Must .login() first")
        return self._username

    @property
    def version(self) -> semver.VersionInfo:
        """Iguazio system version info.

        Returns:
            semver.VersionInfo: Iguazio version
        """
        return self._version

    @version.setter
    def version(self, value: semver.VersionInfo):
        """Change Iguazio system version info.

        Args:
            value (semver.VersionInfo): Iguazio version
        """
        self._version = value
