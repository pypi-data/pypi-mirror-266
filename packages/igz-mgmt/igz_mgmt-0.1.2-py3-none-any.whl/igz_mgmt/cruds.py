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
"""This module represents CRUD operations.

Using a CRUD-like HTTP client, we can: get, list, create, update, and delete resources,
and trigger operations against the Iguazio System.
"""

import abc
import http
import typing

import httpx
import inflection
import pydantic

import igz_mgmt.client
import igz_mgmt.exceptions


class ResourceListPagingQueryParams(pydantic.BaseModel):
    """List paging query params."""

    number: int = pydantic.Field(0, ge=0)
    size: int = pydantic.Field(50, ge=0)


class _CrudFactory:
    @staticmethod
    def create(crud_type: str) -> "_BaseCrud":
        if crud_type == "user":
            return _UserCrud
        elif crud_type == "user_group":
            return _UserGroupCrud
        elif crud_type == "access_key":
            return _AccessKeyCrud
        elif crud_type == "job":
            return _JobCrud
        elif crud_type == "app_services_manifest":
            return _AppServicesManifestCrud
        elif crud_type == "project":
            return _ProjectCrud
        elif crud_type == "event":
            return _EventCrud
        elif crud_type == "audit_event":
            return _AuditEventCrud
        elif crud_type == "communication_event":
            return _CommunicationEventCrud
        elif crud_type == "authorization_role":
            return _AuthorizationRoleCrud
        else:
            raise Exception("Unknown type")


class _BaseCrud(abc.ABC):
    __ALLOW_GET_DETAIL__ = True

    @classmethod
    def create(
        cls,
        http_client: igz_mgmt.client.APIClient,
        attributes,
        relationships=None,
        **kwargs,
    ):
        return http_client.create(cls.type(), attributes, relationships, **kwargs)

    @classmethod
    def get(cls, http_client: igz_mgmt.client.APIClient, resource_id, **kwargs):
        # we do it for endpoints that don't really support get detail thought
        # they behave like they do (e.g. app services manifests)
        if not cls.__ALLOW_GET_DETAIL__:
            response_list = cls.list(http_client)
            return response_list[0]

        # get detail
        try:
            return http_client.detail(cls.type(), resource_id, **kwargs)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == http.HTTPStatus.NOT_FOUND:
                raise igz_mgmt.exceptions.ResourceNotFoundException(
                    cls.type(), resource_id
                ) from exc
            raise exc

    @classmethod
    def list(
        cls,
        http_client: igz_mgmt.client.APIClient,
        filter_by: typing.Optional[typing.Mapping[str, str]] = None,
        sort_by: typing.Optional[typing.List[str]] = None,
        paging: typing.Optional[ResourceListPagingQueryParams] = None,
        include: typing.Optional[typing.List[str]] = None,
    ):
        params = {}
        if filter_by:
            for key, value in filter_by.items():
                params[f"filter[{key}]"] = value
        if include:
            params["include"] = ",".join(include)
        if sort_by:
            params["sort"] = ",".join(sort_by)
        if paging:
            for key, value in paging.dict().items():
                params[f"page[{key}]"] = value

            # currently not needed. it simply returns the total number of items.
            # might be needed when we will add a dedicated pagination function
            # params["count"] = "records"
        return http_client.list(cls.type(), params=params)

    @classmethod
    def update(
        cls,
        http_client: igz_mgmt.client.APIClient,
        resource_id,
        attributes,
        relationships=None,
        **kwargs,
    ):
        return http_client.update(
            cls.type(), resource_id, attributes, relationships, **kwargs
        )

    @classmethod
    def delete(
        cls,
        http_client: igz_mgmt.client.APIClient,
        resource_id,
        ignore_missing: bool = False,
    ) -> typing.Optional[str]:
        response = http_client.delete(
            cls.type(), resource_id, ignore_missing=ignore_missing
        )

        # check if response is a job of "deletion_response" type
        if response.status_code == http.HTTPStatus.ACCEPTED:
            response_body = response.json()
            if response_body.get("data", {}).get("type", "") == "deletion_response":
                # there might be jobs handling the deletion, return the job id
                jobs_data = (
                    response_body.get("data", {})
                    .get("relationships", {})
                    .get("jobs", {})
                    .get("data", [])
                )
                if jobs_data:
                    return jobs_data[0].get("id", None)

    @classmethod
    def get_custom(cls, http_client: igz_mgmt.client.APIClient, path, **kwargs):
        return http_client.request("GET", path, **kwargs)

    @classmethod
    def post_custom(cls, http_client: igz_mgmt.client.APIClient, path, **kwargs):
        return http_client.request("POST", path, **kwargs)

    @classmethod
    def type(cls):
        return inflection.underscore(cls.__name__.strip("_")).replace("_crud", "")


class _UserCrud(_BaseCrud):
    pass


class _UserGroupCrud(_BaseCrud):
    pass


class _AccessKeyCrud(_BaseCrud):
    pass


class _JobCrud(_BaseCrud):
    pass


class _AppServicesManifestCrud(_BaseCrud):
    __ALLOW_GET_DETAIL__ = False


class _ProjectCrud(_BaseCrud):
    pass


class _EventCrud(_BaseCrud):
    pass


class _AuditEventCrud(_BaseCrud):
    pass


class _CommunicationEventCrud(_BaseCrud):
    pass


class _AuthorizationRoleCrud(_BaseCrud):
    pass
