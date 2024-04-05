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
"""Below are classes which do not have a corresponding resource in the API but represent operations.

Some endpoints within the management API are considered “operations”,
which means that the response may not represent a resource.
Some operations are long-living, which means a background job is created whereas the response will hold its id.
"""
import json
import typing

import igz_mgmt.client
import igz_mgmt.constants
import igz_mgmt.exceptions
import igz_mgmt.resources
import igz_mgmt.schemas.app_services


class ClusterConfigurations(object):
    """Cluster configuration operations."""

    @classmethod
    def reload(
        cls,
        http_client: igz_mgmt.client.APIClient,
        config_type: igz_mgmt.constants.ConfigTypes,
    ):
        """Cluster configuration reload.

        Args:
            http_client (APIClient): The client to use.
            config_type (ConfigTypes): The configuration type.
        """
        response = http_client.request(
            "POST", f"configurations/{config_type.value}/reloads"
        )
        job_id = response["data"]["id"]
        igz_mgmt.Job.wait_for_completion(http_client, job_id, timeout=360)


class ManualEvents(object):
    """Manual event operations."""

    @classmethod
    def emit(
        cls,
        http_client: igz_mgmt.client.APIClient,
        event: igz_mgmt.resources.Event,
        audit_tenant_id: typing.Optional[str] = None,
        **kwargs,
    ):
        """Emits a manual event.

        This operation requires system-admin role permissions.

        Args:
            http_client (APIClient): The client to use.
            event (ManualEventSchema): The event to emit.
            audit_tenant_id: The assigned tenant id for auditing events (required for audit events).
            kwargs: Additional arguments to pass to the request.
        """
        # we do not want to send the type in the request body as it is part of the manual event request
        event.type = None

        # set the audit tenant id on relationships
        if audit_tenant_id:
            event.relationships = (
                {} if event.relationships is None else event.relationships
            )
            event.relationships.setdefault("audit_tenant", {}).setdefault("data", {})
            event.relationships["audit_tenant"]["data"] = {
                "type": "tenant",
                "id": audit_tenant_id,
            }

        # empty out relationships as it is not part of the attributes
        relationships = event.relationships.copy() if event.relationships else {}
        event.relationships = None

        try:
            http_client.request(
                "POST",
                "manual_events",
                json={
                    "data": {
                        "type": "event",
                        "relationships": relationships,
                        "attributes": event.dict(exclude_none=True),
                    },
                },
                **kwargs,
            )
        except json.JSONDecodeError:
            # endpoint is not json on old igz versions
            pass


class AppServices(object):
    """Syntactic sugar to AppServicesManifest class."""

    @classmethod
    def get(
        cls,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
    ) -> typing.Optional[igz_mgmt.schemas.app_services.AppServiceBase]:
        """Gets the app service that matches the given spec name.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): The name of the app service spec.

        Returns:
            AppServiceBase, optional: The app service instance that matches the given spec name.
        """
        app_services_manifest = igz_mgmt.resources.AppServicesManifest.get(http_client)
        return app_services_manifest.resolve_service(app_service_spec_name)

    @classmethod
    def create_or_update(
        cls,
        http_client: igz_mgmt.client.APIClient,
        app_service: typing.Union[
            igz_mgmt.schemas.app_services.AppServiceSpec,
            igz_mgmt.schemas.app_services.AppServiceBase,
        ],
        wait_for_completion=True,
    ) -> typing.Optional[igz_mgmt.resources.Job]:
        """Creates or updates an app service.

        Args:
            http_client (APIClient): The client to use.
            app_service (AppServiceSpec or AppServiceBase): app service to create or update.
            wait_for_completion (bool): Whether to wait for the job to complete.

        Returns:
            Job, optional: The job that was created or None if wait_for_completion is False
        """
        app_services_manifest = igz_mgmt.resources.AppServicesManifest.get(http_client)
        return app_services_manifest.create_or_update(
            http_client, app_service, wait_for_completion
        )

    @classmethod
    def restart(
        cls,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
        wait_for_completion=True,
    ) -> typing.Optional[igz_mgmt.resources.Job]:
        """Restarts an app service.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): Name of the app service to restart.
            wait_for_completion (bool): Whether to wait for the job to complete.

        Returns:
            Job, optional: The job that was created or None if wait_for_completion is False
        """
        app_services_manifest = igz_mgmt.resources.AppServicesManifest.get(http_client)
        return app_services_manifest.restart(
            http_client, app_service_spec_name, wait_for_completion
        )

    @classmethod
    def remove(
        cls,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
        wait_for_completion=True,
    ) -> typing.Optional[igz_mgmt.resources.Job]:
        """Removes an app service.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): Name of the app service to remove.
            wait_for_completion (bool): Whether to wait for the job to complete.

        Returns:
            Job, optional: The job that was created or None if wait_for_completion is False
        """
        app_services_manifest = igz_mgmt.resources.AppServicesManifest.get(http_client)
        return app_services_manifest.remove_service(
            http_client, app_service_spec_name, wait_for_completion
        )

    @classmethod
    def enable(
        cls,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
        wait_for_completion=True,
    ) -> typing.Optional[igz_mgmt.resources.Job]:
        """Enables an app service.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): Name of the app service to enable.
            wait_for_completion (bool): Whether to wait for the job to complete.

        Returns:
            Job, optional: The job that was created or None if wait_for_completion is False
        """
        return cls._change_service_state(
            http_client,
            app_service_spec_name,
            igz_mgmt.constants.AppServiceDesiredStates.ready,
            wait_for_completion,
        )

    @classmethod
    def disable(
        cls,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
        wait_for_completion=True,
    ) -> typing.Optional[igz_mgmt.resources.Job]:
        """Disables an app service.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): Name of the app service to disable.
            wait_for_completion (bool): Whether to wait for the job to complete.

        Returns:
            Job, optional: The job that was created or None if wait_for_completion is False
        """
        return cls._change_service_state(
            http_client,
            app_service_spec_name,
            igz_mgmt.constants.AppServiceDesiredStates.disabled,
            wait_for_completion,
        )

    @classmethod
    def scale_from_zero(
        cls,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
        wait_for_completion=True,
    ) -> typing.Optional[igz_mgmt.resources.Job]:
        """Scales an app service from zero.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): Name of the app service to scale from zero.
            wait_for_completion (bool): Whether to wait for the job to complete.

        Returns:
            Job, optional: The job that was created or None if wait_for_completion is False
        """
        app_services_manifest = igz_mgmt.resources.AppServicesManifest.get(http_client)
        return app_services_manifest.scale_from_zero(
            http_client, app_service_spec_name, wait_for_completion
        )

    @classmethod
    def _change_service_state(
        cls,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
        service_state: igz_mgmt.constants.AppServiceDesiredStates,
        wait_for_completion=True,
    ):
        """Changes an app service desired state.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): Name of the app service.
            service_state (AppServiceDesiredStates): App service state
            wait_for_completion (bool): Whether to wait for the job to complete.

        Returns:
            Job, optional: The job that was created or None if wait_for_completion is False

        Raises:
            AppServiceNotExistsException: If app service not exists
        """
        app_services_manifest = igz_mgmt.resources.AppServicesManifest.get(http_client)
        app_service_base = app_services_manifest.resolve_service(app_service_spec_name)
        if not app_service_base:
            raise igz_mgmt.exceptions.AppServiceNotExistsException(
                name=app_service_spec_name
            )
        app_service_base.spec.desired_state = service_state
        return app_services_manifest.create_or_update(
            http_client, app_service_base, wait_for_completion
        )
