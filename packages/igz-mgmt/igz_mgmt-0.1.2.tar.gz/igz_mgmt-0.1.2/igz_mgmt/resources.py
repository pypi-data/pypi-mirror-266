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
"""This module represents resources.

Most of the resources support all CRUD methods.
"""
import collections
import contextlib
import http
import json
import re
import time
import typing

import inflection
import pydantic.utils
import semver
from deprecated import deprecated

import igz_mgmt.client
import igz_mgmt.common.helpers
import igz_mgmt.constants
import igz_mgmt.cruds
import igz_mgmt.exceptions
import igz_mgmt.schemas
import igz_mgmt.schemas.app_services
import igz_mgmt.schemas.events


class ResourceBaseModel(pydantic.BaseModel):
    """Base model for all resources."""

    type: str
    id: typing.Optional[typing.Union[int, str]]
    relationships: typing.Optional[dict]
    included: typing.Optional[typing.List["ResourceBaseModel"]]
    _http_client: igz_mgmt.client.APIClient = None

    class Config:
        class _BaseGetter(pydantic.utils.GetterDict):
            def get(self, key: typing.Any, default: typing.Any = None) -> typing.Any:
                if key in ["id", "type"]:
                    return self._obj["data"][key]
                elif key == "relationships":
                    return self._obj["data"].get("relationships", {})
                elif key == "included":
                    return self._obj.get("included", [])
                elif key in self._obj["data"]["attributes"]:
                    return self._obj["data"]["attributes"][key]
                return default

        orm_mode = True
        use_enum_values = True
        underscore_attrs_are_private = True
        getter_dict = _BaseGetter

        # be forward compatible
        extra = "allow"

        validate_assignment = True

    def __getattribute__(self, item):
        value = super().__getattribute__(item)
        if item == "_http_client" and value is None:
            raise igz_mgmt.exceptions.ResourceNotInitializedError(
                self.__class__.__name__
            )

        return value

    @classmethod
    def from_orm_with_client(cls, http_client, *args, **kwargs):
        """Creates a new instance from an ORM object and init the http client."""
        instance = cls.from_orm(*args, **kwargs)
        instance._http_client = http_client
        return instance


class BaseResource(ResourceBaseModel):
    """Base resource contains common attributes and methods for resources in the system."""

    @classmethod
    def get(
        cls,
        http_client: igz_mgmt.client.APIClient,
        resource_id: typing.Union[int, str],
        include: typing.Optional[typing.List[str]] = None,
    ) -> "BaseResource":
        """Gets the resource record.

        Args:
            http_client (APIClient): The client to use.
            resource_id (int or str): Record id.
            include (typing.List[str], optional): Include related resources. None by default.

        Returns:
            BaseResource: The resource record.
        """
        params = {}
        if include:
            params["include"] = ",".join(include)
        resource = cls._get_crud().get(http_client, resource_id, params=params)
        return cls.from_orm_with_client(http_client, resource)

    @classmethod
    def list(
        cls,
        http_client: igz_mgmt.client.APIClient,
        filter_by: typing.Optional[typing.Mapping[str, str]] = None,
        sort_by: typing.Optional[typing.List[str]] = None,
        paging: typing.Optional[igz_mgmt.cruds.ResourceListPagingQueryParams] = None,
        include: typing.Optional[typing.List[str]] = None,
    ) -> typing.List["BaseResource"]:
        """Lists resource records.

        Args:
            http_client (APIClient): The client to use.
            filter_by (typing.Mapping[str, str], optional): Filter by field values. None by default.
            sort_by (typing.List[str], optional): Sort by field names. None by default.
            paging (ResourceListPagingQueryParams, optional): Allow to paginate resource by given records size.
            None by default.
            include (typing.List[str], optional): Include related resources. None by default.

        Returns:
            typing.List[BaseResource]: List of records for the specific resource.
        """
        list_resource = cls._get_crud().list(
            http_client, filter_by, sort_by, paging, include
        )
        return [
            cls.from_orm_with_client(
                http_client, {"data": item, "included": item.get("included", [])}
            )
            for item in list_resource["data"]
        ]

    def update(
        self, http_client: igz_mgmt.client.APIClient, relationships=None, **kwargs
    ) -> "BaseResource":
        """Updates resource record.

        Args:
            http_client (APIClient): The client to use.
            relationships (optional): The resource relationships. None by default.
            **kwargs: additional arguments to pass to the request.

        Returns:
            BaseResource: The updated record.
        """
        self._get_crud().update(
            http_client,
            self.id,
            attributes=self._fields_to_attributes(),
            relationships=relationships,
            **kwargs,
        )

        # TODO: build cls from response when BE will return the updated resource within the response body
        updated_resource = self.get(http_client, self.id)
        self.__dict__.update(updated_resource)
        self._http_client = http_client
        return self

    def delete(
        self,
        http_client: igz_mgmt.client.APIClient,
        ignore_missing: bool = False,
        wait_for_job_deletion: bool = True,
    ) -> typing.Optional["Job"]:
        """Deletes resource record.

        Args:
            http_client (APIClient): The client to use.
            ignore_missing (bool, optional): When True, don't raise an exception in case the record does not exist.
            False by default.
            wait_for_job_deletion (bool, optional): Whether to wait for the job to complete. True by default.

        Returns:
            Job, optional: the job that was created or None.
        """
        job_id = self._get_crud().delete(http_client, self.id, ignore_missing)
        if job_id:
            if wait_for_job_deletion:
                Job.wait_for_completion(
                    http_client, job_id, job_completion_retry_interval=10
                )
            return Job.get(http_client, job_id)

    @classmethod
    def _get_crud(cls) -> igz_mgmt.cruds._BaseCrud:
        return igz_mgmt.cruds._CrudFactory.create(
            inflection.underscore(cls.__fields__["type"].default)
        )

    @classmethod
    def _get_resource_by_name(
        cls, http_client: igz_mgmt.client.APIClient, filter_key, name, include=None
    ) -> "BaseResource":
        """Gets a resource by name, by listing all resource instances and filtering by name.

        If resource is not found, ResourceNotFoundException is raised
        """
        resources = cls.list(http_client, filter_by={filter_key: name})
        if not resources:
            raise igz_mgmt.exceptions.ResourceNotFoundException(
                cls.__fields__["type"].default, name
            )
        resource_id = resources[0].id

        # although we already have the resource, we need to get it again to get the relationships
        # passed in the include parameter
        return cls.get(http_client, resource_id, include=include)

    def _fields_to_attributes(self, exclude_unset=True):
        return self.dict(
            exclude={"type", "relationships", "id", "included"},
            exclude_none=True,
            exclude_unset=exclude_unset,
            by_alias=True,
        )


class ProjectMembershipResource(pydantic.BaseModel):
    """Base class for project membership resources."""

    def ensure_project_membership(
        self,
        http_client: igz_mgmt.client.APIClient,
        project_name: str,
        role: igz_mgmt.constants.ProjectAuthorizationRoles,
    ):
        """Ensures that the current object is a member of a project with a specific role.

        Args:
            http_client (APIClient): The client to use.
            project_name (str): The project name.
            role (ProjectAuthorizationRolesNames): The role name.
        """
        project = Project.get_by_name(http_client, project_name)
        return project.set_membership(
            http_client,
            self,
            role,
            add_member_mode=igz_mgmt.constants.AddMemberMode.override,
        )

    def remove_from_project(
        self, http_client: igz_mgmt.client.APIClient, project_name: str
    ):
        """Removes current object from a project.

        Args:
            http_client (APIClient): The client to use.
            project_name (str): The project name.
        """
        project = Project.get_by_name(http_client, project_name)
        return project.remove_member(http_client, self)


class User(BaseResource, ProjectMembershipResource):
    """User resource represents user in the system."""

    type: str = "user"
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    uid: int = 0
    created_at: str = ""
    data_access_mode: str = ""
    authentication_scheme: str = ""
    authentication_methods: typing.List[
        igz_mgmt.constants.UserAuthenticationMethods
    ] = []
    send_password_on_creation: bool = False
    assigned_policies: typing.List[igz_mgmt.constants.TenantManagementRoles] = []
    operational_status: str = igz_mgmt.constants.UserOperationalStatuses.up
    admin_status: str = igz_mgmt.constants.UserAdminStatuses.up
    password: pydantic.SecretStr = None
    phone_number: str = ""
    job_title: str = ""
    department: str = ""
    last_activity: str = ""

    @classmethod
    def create(
        cls,
        http_client: igz_mgmt.client.APIClient,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        password: str = None,
        uid: int = None,
        assigned_policies: typing.List[igz_mgmt.constants.TenantManagementRoles] = None,
        primary_group: typing.Union[str, "Group", None] = None,
        groups: typing.Union[typing.List[str], typing.List["Group"], None] = None,
        timeout: int = 30,
        wait_for_completion=True,
        phone_number: str = "",
        job_title: str = "",
        department: str = "",
        authentication_methods: igz_mgmt.constants.UserAuthenticationMethods = None,
    ) -> "User":
        """Creates a new User.

        Args:
            http_client (APIClient): The client to use.
            username (str): The user username.
            password (str, optional): The user password. None by default. (if not provided, an email is automatically
            sent to the user to set his password)
            assigned_policies (typing.List[TenantManagementRoles], optional): The assigned policies of the group.
            None by default.
            primary_group (str or Group or None): None by default.
            groups (typing.Union[typing.List[str], typing.List["Group"], None], optional): A list of group objects
            or group ids to add user to the groups. None by default.
            timeout (int, optional): The default is 30.
            wait_for_completion (bool): Whether to wait for the job to complete
            phone_number (str, optional): The user phone number.
            job_title (str, optional): The user job title.
            department (str, optional): The user department.
            authentication_methods (typing.List[UserAuthenticationMethods], optional): The authentication method
            type to log in with. None by default.

        Returns:
            User
        """
        assigned_policies = assigned_policies or [
            igz_mgmt.constants.TenantManagementRoles.developer.value,
            igz_mgmt.constants.TenantManagementRoles.application_read_only.value,
        ]
        attributes = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "assigned_policies": assigned_policies,
            "phone_number": phone_number,
            "job_title": job_title,
            "department": department,
        }
        if uid is not None:
            attributes["uid"] = uid
        if password is not None:
            attributes["password"] = password

        if authentication_methods is not None:
            # authentication_methods field exists only in version 3.5.5 and higher
            if http_client.version >= semver.VersionInfo.parse("3.5.5"):
                attributes["authentication_methods"] = authentication_methods
            else:
                http_client._logger.warn_with(
                    "The 'authentication_methods' field is only permitted in versions 3.5.5 and above - ignoring"
                )

        relationships = collections.defaultdict(dict)
        if primary_group:
            primary_group_id = (
                primary_group.id if isinstance(primary_group, Group) else primary_group
            )
            relationships["primary_group"] = {
                "data": {
                    "type": "user_group",
                    "id": primary_group_id,
                },
            }

            # ensure primary group is in groups list
            if groups:
                primary_group_in_groups = False
                for group in groups:
                    group_id = group.id if isinstance(group, Group) else group
                    if primary_group_id == group_id:
                        primary_group_in_groups = True
                        break
                if not primary_group_in_groups:
                    groups += primary_group_id
            else:
                groups = [primary_group_id]

        if groups:
            for group in groups:
                relationships["user_groups"].setdefault("data", []).append(
                    {
                        "type": "user_group",
                        "id": group.id if isinstance(group, Group) else group,
                    }
                )

        created_resource = cls._get_crud().create(
            http_client,
            attributes=attributes,
            relationships=relationships,
        )

        # there might be jobs handling the creating
        jobs_data = (
            created_resource.get("data", {})
            .get("relationships", {})
            .get("jobs", {})
            .get("data", [])
        )
        if jobs_data and wait_for_completion:
            job_id = jobs_data[0].get("id", None)
            Job.wait_for_completion(
                http_client, job_id, job_completion_retry_interval=10
            )

        def _verify_user_is_operational(user_id):
            user_obj = User.get(http_client, user_id, include=["user_groups"])
            if not user_obj.is_operational(http_client):
                http_client._logger.warn_with("User is not yet operational, retrying")

                raise igz_mgmt.common.helpers.RetryUntilSuccessfulInProgressErrorMessage(
                    "Waiting for the user to be operational",
                )
            return user_obj

        user = cls.from_orm_with_client(http_client, created_resource)

        user = igz_mgmt.common.helpers.retry_until_successful(
            1,
            timeout,
            http_client._logger,
            True,
            _verify_user_is_operational,
            user_id=user.id,
        )
        return user

    def is_operational(self, http_client: igz_mgmt.client.APIClient):
        """Verify user is operational.

        Verifying that the user operational status is up and that the all_users group
        exists in the user_groups relationships.

        Args:
            http_client (APIClient): The client to use.

        Returns:
            bool: True if user is operational, False otherwise.
        """
        user = self.get(http_client, self.id)
        if user.operational_status == igz_mgmt.constants.UserOperationalStatuses.up:
            # check that all_users group exists in the user_groups relationships
            all_users_group = Group.get_by_name(http_client, "all_users")
            return user.in_group(http_client, all_users_group)
        return False

    @classmethod
    def get_by_username(
        cls, http_client: igz_mgmt.client.APIClient, username: str, include=None
    ) -> "User":
        """A convenience method to get a user by username.

        Args:
            http_client (APIClient): The client to use.
            username (str): The user username.
            include (optional): Include related resources. None by default.

        Returns:
            User: The user instance by username.

        Raises:
            ResourceNotFoundException: If user is not found
        """
        return cls._get_resource_by_name(
            http_client, "username", username, include=include
        )

    @classmethod
    def self(cls, http_client: igz_mgmt.client.APIClient) -> "User":
        """Gets the current user.

        Args:
            http_client (APIClient): The client to use.

        Returns:
            User: The current user instance.
        """
        user = cls._get_crud().get_custom(http_client, "self")
        return cls.from_orm_with_client(http_client, user)

    def in_group(
        self, http_client: igz_mgmt.client.APIClient, group: typing.Union[str, "Group"]
    ):
        """Checks if user is part of a group.

        Args:
            http_client (APIClient): The client to use.
            group (str or Group): The group id or group instance to check if user is part of it.

        Returns:
            bool: True if user is part of the group, False otherwise.
        """
        user = self.get(http_client, self.id, include=["user_groups"])
        group_id = group.id if isinstance(group, Group) else group
        if "user_groups" not in user.relationships:
            return False
        user_groups = [
            group["id"] for group in user.relationships["user_groups"]["data"]
        ]
        return group_id in user_groups

    def get_project_effective_role(
        self, http_client: igz_mgmt.client.APIClient, project_name: str
    ):
        """Gets the effective roles of the user in a project.

        Args:
            http_client (APIClient): The client to use.
            project_name (str): The project name.

        Returns:
            list: The effective roles of the user in the project.
        """
        project = Project.get_by_name(http_client, project_name)
        return project.get_user_effective_role(http_client, self)

    def add_to_group(
        self, http_client: igz_mgmt.client.APIClient, group: typing.Union[str, "Group"]
    ):
        """Adds a user to a group.

        1. get the user
        2. add the group to the user
        3. update the user

        Args:
            http_client (APIClient): The client to use.
            group (str or Group): The group id or group name or group instance to add user into it.
        """
        user = self.get(http_client, self.id, include=["user_groups"])
        if "user_groups" not in user.relationships:
            user.relationships["user_groups"] = {"data": []}

        group = Group._get_from_arg(http_client, group)
        if User._ensure_user_in_group(user, group.id):
            user.update(http_client, relationships=user.relationships)

    def remove_from_group(
        self,
        http_client: igz_mgmt.client.APIClient,
        group: typing.Union[str, "Group"],
        force=False,
    ):
        """Removes a user from a group.

        Args:
            http_client (APIClient): The client to use.
            group (str or Group): The group id or group name or group instance to remove user from it.
            force (bool): force (bool): Whether to force the removal of the user from the group (for example, from its
                                        primary group).
        """
        user = self.get(http_client, self.id, include=["user_groups"])
        group_id = Group._get_from_arg(http_client, group).id
        primary_group = self.get_primary_group(http_client)
        if primary_group and primary_group.id == group_id:
            if force:
                user.set_primary_group(http_client, "")
            else:
                raise igz_mgmt.exceptions.UserIsInPrimaryGroupError(self, primary_group)

        if "user_groups" in user.relationships:
            user.relationships["user_groups"]["data"] = [
                group
                for group in user.relationships["user_groups"]["data"]
                if group["id"] != group_id
            ]
            user.update(http_client, relationships=user.relationships)

    def get_primary_group(
        self, http_client: igz_mgmt.client.APIClient
    ) -> typing.Optional["Group"]:
        """Gets the primary group of a user.

        Args:
            http_client (APIClient): The client to use.

        Returns:
            Group: The primary group of the user.
        """
        user = self.get(http_client, self.id, include=["primary_group"])
        if "primary_group" in user.relationships:
            return Group.get(
                http_client, user.relationships["primary_group"]["data"]["id"]
            )

    def set_primary_group(
        self, http_client: igz_mgmt.client.APIClient, group: typing.Union[str, "Group"]
    ):
        """Sets the primary group of a user.

        Args:
            http_client (APIClient): The client to use.
            group (str or Group): The primary group id or group name or group instance.
        """
        group = Group._get_from_arg(http_client, group)
        group_id = group.id if isinstance(group, Group) else group

        # we need primary group
        user = self.get(http_client, self.id, include=["user_groups"])
        if "primary_group" not in user.relationships:
            user.relationships["primary_group"] = {"data": None}
        if "user_groups" not in user.relationships:
            user.relationships["user_groups"] = {"data": []}

        User._ensure_user_in_group(user, group_id)
        user.relationships["primary_group"]["data"] = {
            "id": group_id,
            "type": "user_group",
        }
        user.update(http_client, relationships=user.relationships)

    def disable(self, http_client: igz_mgmt.client.APIClient):
        """Disables the user instance.

        Args:
            http_client (APIClient): The client to use.
        """
        self.admin_status = igz_mgmt.constants.UserAdminStatuses.down
        return self.update(http_client)

    @classmethod
    @deprecated(reason="Use disable_user instead")
    def disable_by_username(cls, http_client: igz_mgmt.client.APIClient, username: str):
        """Disables the user by username.

        Args:
            http_client (APIClient): The client to use.
            username (str): The user username.
        """
        return cls.disable_user(http_client, username)

    @classmethod
    @deprecated(reason="Use disable_user instead")
    def disable_by_id(cls, http_client: igz_mgmt.client.APIClient, user_id: str):
        """Disables the user by user id.

        Args:
            http_client (APIClient): The client to use.
            user_id (str): The user id.
        """
        return cls.disable_user(http_client, user_id)

    @classmethod
    def disable_user(
        cls,
        http_client: igz_mgmt.client.APIClient,
        user: typing.Union[str, int, "User"],
    ):
        """Disables the user.

        Args:
            http_client (APIClient): The client to use.
            user (str or int or User): The user id, username or user instance.
        """
        user = cls._get_from_arg(http_client, user)
        return user.disable(http_client)

    def enable(self, http_client: igz_mgmt.client.APIClient):
        """Enables the user instance.

        Args:
            http_client (APIClient): The client to use.
        """
        self.admin_status = igz_mgmt.constants.UserAdminStatuses.up
        return self.update(http_client)

    @classmethod
    @deprecated(reason="Use enable_user instead")
    def enable_by_username(cls, http_client: igz_mgmt.client.APIClient, username: str):
        """Enables the user by username.

        Args:
            http_client (APIClient): The client to use.
            username (str): The user username.
        """
        return cls.enable_user(http_client, username)

    @classmethod
    @deprecated(reason="Use enable_user instead")
    def enable_by_id(cls, http_client: igz_mgmt.client.APIClient, user_id: str):
        """Enables the user by user id.

        Args:
            http_client (APIClient): The client to use.
            user_id (str): The user id.
        """
        return cls.enable_user(http_client, user_id)

    @classmethod
    def enable_user(
        cls,
        http_client: igz_mgmt.client.APIClient,
        user: typing.Union[str, int, "User"],
    ):
        """Enables the user.

        Args:
            http_client (APIClient): The client to use.
            user (str or int or User): The user id, username or user instance.
        """
        user = cls._get_from_arg(http_client, user)
        return user.enable(http_client)

    @classmethod
    def _get_from_arg(
        cls,
        http_client: igz_mgmt.client.APIClient,
        user: typing.Union[str, int, "User"],
    ):
        if isinstance(user, User):
            return user

        # check if we got a user id
        if igz_mgmt.common.helpers.is_uuid4(user):
            return cls.get(http_client, user)

        # here we assume that we want to get user by username
        return cls.get_by_username(http_client, user)

    @staticmethod
    def _ensure_user_in_group(user, group_id: str) -> bool:
        """Ensures that a user has a group in its relationships.

        e.g.:
        If group is not in user relationships, add it and return True
        Alternatively, if group is in user relationships, return False

        Returns:
            bool: True if the group was added to the user relationship, False otherwise.
        """
        if group_id not in [
            group["id"] for group in user.relationships["user_groups"]["data"]
        ]:
            user.relationships["user_groups"]["data"].append(
                {"id": group_id, "type": "user_group"}
            )
            return True

        return False


class Group(BaseResource, ProjectMembershipResource):
    """Group resource represents user group in the system."""

    type: str = "user_group"
    name: str = ""
    description: str = None
    data_access_mode: str = "enabled"
    gid: int = 0
    kind: str = "local"
    assigned_policies: typing.List[igz_mgmt.constants.TenantManagementRoles] = []
    system_provided: bool = False

    @classmethod
    def create(
        cls,
        http_client: igz_mgmt.client.APIClient,
        name: typing.Optional[str],
        assigned_policies: typing.Optional[
            typing.List[igz_mgmt.constants.TenantManagementRoles]
        ] = None,
        description: typing.Optional[str] = None,
        gid: typing.Optional[int] = None,
        users: typing.Optional[typing.List[typing.Union[int, str, User]]] = None,
    ) -> "Group":
        """Creates a new group.

        Args:
            http_client (APIClient): The client to use.
            name (str, optional): Group name.
            assigned_policies (typing.List[TenantManagementRoles], optional): The assigned policies of the group.
            None by default.
            description (str, optional): The description of the group. None by default.
            gid (int, optional): The gid of the group (leave empty for auto-assign). None by default.
            users (typing.List[typing.Union[int, str, User]], optional): A list of User objects or user ids
            to add to the group. None by default.

        Returns:
            Group
        """
        if not assigned_policies:
            assigned_policies = [
                igz_mgmt.constants.TenantManagementRoles.data.value,
                igz_mgmt.constants.TenantManagementRoles.application_admin.value,
            ]
        relationships = {}
        if users:
            relationships["users"] = {
                "data": [
                    {"id": user.id if isinstance(user, User) else user, "type": "user"}
                    for user in users
                ]
            }
        created_resource = cls._get_crud().create(
            http_client,
            attributes={
                "name": name,
                "description": description,
                "gid": gid,
                "assigned_policies": assigned_policies,
            },
            relationships=relationships,
        )
        return cls.from_orm_with_client(http_client, created_resource)

    @classmethod
    def get_by_name(
        cls, http_client: igz_mgmt.client.APIClient, name: str, include=None
    ) -> "Group":
        """A convenience method to get a group by name.

        Args:
            http_client (APIClient): The client to use.
            name (str): Group name.
            include (optional): Include related resources. None by default.

        Returns:
            Group: The group instance by group name.

        Raises:
            ResourceNotFoundException: If group is not found
        """
        return cls._get_resource_by_name(http_client, "name", name, include=include)

    def add_user(
        self,
        http_client: igz_mgmt.client.APIClient,
        user: typing.Union[str, int, "User"],
    ):
        """Adds a user to group.

        1. get the user
        2. add the group to the user
        3. update the group

        Args:
            http_client (APIClient): The client to use.
            user (str or int or User): The user id or username or user instance to add.
        """
        user = User._get_from_arg(http_client, user)
        user.add_to_group(http_client, self)
        self.__dict__.update(Group.get(http_client, self.id))

    def remove_user(
        self,
        http_client: igz_mgmt.client.APIClient,
        user: typing.Union[str, int, "User"],
        force=False,
    ):
        """Removes a user from group.

        Args:
            http_client (APIClient): The client to use.
            user (str ot int or User): The user id or username or user instance to remove.
            force (bool): force (bool): Whether to force the removal of the user from the group(for example, from its
                                        primary group).
        """
        user = User._get_from_arg(http_client, user)
        user.remove_from_group(http_client, self, force)
        self.__dict__.update(Group.get(http_client, self.id))

    @classmethod
    def _get_from_arg(
        cls,
        http_client: igz_mgmt.client.APIClient,
        group: typing.Union[str, int, "Group"],
    ):
        if not group:
            # in case group is None or empty string we want to return it (for example to unset primary group)
            return group

        if isinstance(group, Group):
            return group

        # check if we got a group id
        if igz_mgmt.common.helpers.is_uuid4(group):
            return cls.get(http_client, group)

        # here we assume that we want to get user by username
        return cls.get_by_name(http_client, group)


class AccessKey(BaseResource):
    """AccessKey resource represents access key in the system."""

    type: str = "access_key"
    tenant_id: str = ""
    ttl: int = 315360000  # 10 years
    created_at: str = ""
    updated_at: str = ""
    group_ids: typing.List[str] = []
    uid: int = 0
    gids: typing.List[int] = []
    expires_at: int = 0  # EPOCH
    interface_kind: str = "web"
    label: str = ""
    kind: str = "accessKey"
    planes: typing.List[
        igz_mgmt.constants.SessionPlanes
    ] = igz_mgmt.constants.SessionPlanes.all()

    @classmethod
    def create(
        cls,
        http_client: igz_mgmt.client.APIClient,
        planes: typing.List[
            igz_mgmt.constants.SessionPlanes
        ] = igz_mgmt.constants.SessionPlanes.all(),
        label: str = None,
    ) -> "AccessKey":
        """Creates a new access key.

        Args:
            http_client (APIClient): The client to use.
            planes (typing.List[SessionPlanes], optional): The planes of the access key.
            label (str, optional): The label of the access key.
        """
        created_resource = cls._get_crud().create(
            http_client,
            attributes={
                "planes": planes,
                "label": label,
            },
        )
        return cls.from_orm_with_client(http_client, created_resource)

    @classmethod
    def get_or_create(
        cls,
        http_client: igz_mgmt.client.APIClient,
        planes: typing.Optional[typing.List[igz_mgmt.constants.SessionPlanes]] = None,
        label: typing.Optional[str] = None,
    ) -> "AccessKey":
        """Get or create access key.

        If access key with the given planes exists, it will be returned.
        Otherwise, a new access key will be created.
        If no planes are given, all planes will be used.

        Args:
            http_client (APIClient): The client to use.
            planes (typing.List[SessionPlanes], optional): The planes of the access key.
            label (str, optional): The label of the access key.

        Returns:
            AccessKey: An existing or newly created access key.
        """
        if not planes:
            planes = igz_mgmt.constants.SessionPlanes.all()

        request_body = {
            "data": {
                "type": "access_key",
                "attributes": {},
            }
        }
        if not label:
            label = "for-sdk-mgmt"
        request_body["data"]["attributes"]["label"] = label
        if planes:
            request_body["data"]["attributes"]["planes"] = list(map(str, planes))
        response = cls._get_crud().post_custom(
            http_client, "/self/get_or_create_access_key", json=request_body
        )
        return cls.from_orm_with_client(http_client, response)


class Job(BaseResource):
    """Job is an abstraction for long-running operations in the API.

    Some operations, cannot be finished within a reasonable amount of time for a normal HTTP request.
    Job has a state, id and can be awaited on asynchronously.
    """

    type: str = "job"
    kind: str = ""
    params: str = ""
    max_total_execution_time: int = 3 * 60 * 60  # in seconds
    max_worker_execution_time: typing.Optional[int] = None  # in seconds
    delay: float = 0  # in seconds
    state: igz_mgmt.constants.JobStates = igz_mgmt.constants.JobStates.created
    result: str = ""
    created_at: str = ""
    on_success: typing.List[dict] = None
    on_failure: typing.List[dict] = None
    updated_at: str = ""
    handler: str = ""
    ctx_id: str = ""

    def delete(
        self, http_client: igz_mgmt.client.APIClient, **kwargs
    ) -> typing.Optional["Job"]:
        """This method is forbidden."""
        raise igz_mgmt.exceptions.ResourceDeleteException

    def update(self, http_client: igz_mgmt.client.APIClient, **kwargs):
        """This method is forbidden."""
        raise igz_mgmt.exceptions.ResourceUpdateException

    @staticmethod
    def wait_for_completion(
        http_client: igz_mgmt.client.APIClient,
        job_id: str,
        job_completion_retry_interval: float = 30,
        timeout: int = 3600,
    ):
        """Wait for a job to be finished.

        Args:
            http_client (APIClient): The client to use.
            job_id (str): The job id.
            job_completion_retry_interval (float, optional): The default is 30.
            timeout (int, optional): The default is 3600.
        """

        def _verify_job_in_terminal_state():
            try:
                job_obj = Job.get(http_client, job_id)
            except igz_mgmt.exceptions.ResourceNotFoundException as exc:
                http_client._logger.warn_with(
                    "Job not found, bail out",
                    job_id=job_id,
                )
                raise igz_mgmt.common.helpers.RetryUntilSuccessfulFatalError(
                    "Resource was not found", caused_by_exc=exc
                )
            if job_obj.state not in igz_mgmt.constants.JobStates.terminal_states():
                http_client._logger.info_with(
                    "Job is not in a terminal state yet, retrying",
                    current_state=job_obj.state,
                    job_id=job_id,
                )
                raise igz_mgmt.common.helpers.RetryUntilSuccessfulInProgressErrorMessage(
                    "Waiting for job completion",
                    variables={
                        "job_id": job_id,
                        "job_state": job_obj.state,
                    },
                )
            return job_obj

        http_client._logger.info_with("Waiting for job completion", job_id=job_id)
        job = igz_mgmt.common.helpers.retry_until_successful(
            job_completion_retry_interval,
            timeout,
            http_client._logger,
            True,
            _verify_job_in_terminal_state,
        )
        if job.state != igz_mgmt.constants.JobStates.completed:
            error_message = f"Job {job_id} failed with state: {job.state}"
            try:
                parsed_result = json.loads(job.result)
                error_message += f", message: {parsed_result['message']}"
                # status is optional
                if "status" in parsed_result:
                    status_code = int(parsed_result["status"])
                    error_message = f", status: {status_code}"

            except Exception:
                error_message += f", message: {job.result}"

            raise RuntimeError(error_message)
        http_client._logger.info_with("Job completed successfully", job_id=job_id)


class AppServicesManifest(BaseResource):
    """AppServicesManifest resource."""

    type: str = "app_services_manifest"
    cluster_name: str = ""
    tenant_name: str = ""
    tenant_id: str = ""
    app_services: typing.List[igz_mgmt.schemas.app_services.AppServiceBase] = []
    state: typing.Optional[igz_mgmt.constants.AppServicesManifestStates]
    last_error: typing.Optional[str]
    last_modification_job: str = ""
    apply_services_mode: typing.Optional[igz_mgmt.constants.ApplyServicesMode]
    running_modification_job: str = ""
    force_apply_all_mode: typing.Optional[igz_mgmt.constants.ForceApplyAllMode]

    _skip_apply: bool = False

    @staticmethod
    @contextlib.contextmanager
    def apply_services(
        http_client: igz_mgmt.client.APIClient,
        force_apply_all_mode: igz_mgmt.constants.ForceApplyAllMode = igz_mgmt.constants.ForceApplyAllMode.disabled,
    ) -> typing.ContextManager["AppServicesManifest"]:
        """A context manager to apply services with multiple changes at once.

        Args:
            http_client (APIClient): The client to use.
            force_apply_all_mode (ForceApplyAllMode, optional): Disabled by default.

        Returns:
            AppServicesManifest: The app service manifest instance.
        """
        app_services_manifest = AppServicesManifest.get(http_client)
        app_services_manifest._skip_apply = True
        try:
            yield app_services_manifest
        finally:
            app_services_manifest._apply(
                http_client,
                # writing it down here for explicitness
                wait_for_completion=True,
                force_apply_all_mode=force_apply_all_mode,
            )
            app_services_manifest._skip_apply = False

    def delete(
        self, http_client: igz_mgmt.client.APIClient, **kwargs
    ) -> typing.Optional[Job]:
        """This method is forbidden."""
        raise igz_mgmt.exceptions.ResourceDeleteException

    def update(self, http_client: igz_mgmt.client.APIClient, **kwargs):
        """This method is forbidden."""
        raise igz_mgmt.exceptions.ResourceUpdateException

    def list(self, http_client: igz_mgmt.client.APIClient, **kwargs):
        """This method is forbidden."""
        raise igz_mgmt.exceptions.ResourceListException

    @classmethod
    def get(
        cls, http_client: igz_mgmt.client.APIClient, **kwargs
    ) -> "AppServicesManifest":
        """Gets the app services manifest from the API.

        Args:
            http_client (APIClient): The client to use.
            **kwargs: Arbitrary keyword arguments (not in used).

        Returns:
            AppServicesManifest: The app service manifest instance.
        """
        resource = cls._get_crud().list(http_client)
        return [
            cls.from_orm_with_client(http_client, {"data": item})
            for item in resource["data"]
        ][0]

    def set_apply_mode(self, apply_mode: igz_mgmt.constants.ApplyServicesMode):
        """Sets the apply mode of the app services manifest.

        Args:
            apply_mode (ApplyServicesMode): apply services mode value.
        """
        self.apply_services_mode = apply_mode

    def resolve_service(
        self,
        app_service_spec_name: str,
    ) -> typing.Optional[igz_mgmt.schemas.app_services.AppServiceBase]:
        """Gets the app service that matches the given spec name.

        Args:
            app_service_spec_name (str): The name of the app service spec.

        Returns:
            AppServiceBase, optional: The app service instance that matches the given spec name.
        """
        for app_service in self.app_services:
            if app_service.spec.name == app_service_spec_name:
                return app_service
        return None

    def create_or_update(
        self,
        http_client: igz_mgmt.client.APIClient,
        app_service: typing.Union[
            igz_mgmt.schemas.app_services.AppServiceSpec,
            igz_mgmt.schemas.app_services.AppServiceBase,
        ],
        wait_for_completion=True,
    ) -> typing.Optional[Job]:
        """Creates or updates an app service.

        Args:
            http_client (APIClient): The client to use.
            app_service (AppServiceSpec or AppServiceBase): The app service to create or update
            wait_for_completion (bool): Whether to wait for the job to complete

        Returns:
            Job, optional: the job that was created or None if wait_for_completion is False.
        """
        app_service_spec = (
            app_service.spec
            if isinstance(app_service, igz_mgmt.schemas.app_services.AppServiceBase)
            else app_service
        )
        app_service_spec.mark_as_changed = True
        app_service_spec_obj = self.resolve_service(app_service_spec.name)
        if app_service_spec_obj:
            for position, service in enumerate(self.app_services):
                if service.spec.name == app_service_spec_obj.spec.name:
                    self.app_services[position].spec = app_service_spec
                    break
        else:
            self.app_services.append(
                igz_mgmt.schemas.app_services.AppServiceBase(spec=app_service_spec)
            )
        if not self._skip_apply:
            return self._apply(http_client, wait_for_completion)

    def restart(
        self,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
        wait_for_completion=True,
    ) -> typing.Optional[Job]:
        """Restarts an app service.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): Name of the app service to restart
            wait_for_completion (bool): Whether to wait for the job to complete

        Returns:
            Job, optional: the job that was created or None if wait_for_completion is False.
        """
        app_service_obj = self.resolve_service(app_service_spec_name)
        if not app_service_obj:
            raise igz_mgmt.exceptions.AppServiceNotExistsException(
                name=app_service_spec_name
            )
        for position, app_service in enumerate(self.app_services):
            if app_service.spec.name == app_service_obj.spec.name:
                self.app_services[position].spec.mark_for_restart = True
                break
        if not self._skip_apply:
            return self._apply(http_client, wait_for_completion)

    def remove_service(
        self,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
        wait_for_completion=True,
    ) -> typing.Optional[Job]:
        """Removes an app service.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): Name of the app service to remove
            wait_for_completion (bool): Whether to wait for the job to complete

        Returns:
            Job, optional: the job that was created or None if wait_for_completion is False.
        """
        app_service_obj = self.resolve_service(app_service_spec_name)
        if not app_service_obj:
            raise igz_mgmt.exceptions.AppServiceNotExistsException(
                name=app_service_spec_name
            )
        for position, app_service in enumerate(self.app_services):
            if app_service.spec.name == app_service_obj.spec.name:
                del self.app_services[position]
                break
        if not self._skip_apply:
            return self._apply(http_client, wait_for_completion)

    def scale_from_zero(
        self,
        http_client: igz_mgmt.client.APIClient,
        app_service_spec_name: str,
        wait_for_completion=True,
    ) -> typing.Optional[Job]:
        """Scales an app service from zero.

        Args:
            http_client (APIClient): The client to use.
            app_service_spec_name (str): Name of the app service to scale from zero
            wait_for_completion (bool): Whether to wait for the job to complete

        Returns:
            Job, optional: the job that was created or None if wait_for_completion is False.
        """
        app_service_obj = self.resolve_service(app_service_spec_name)
        if not app_service_obj:
            raise igz_mgmt.exceptions.AppServiceNotExistsException(
                name=app_service_spec_name
            )
        app_service_obj.spec.mark_as_changed = True
        app_service_obj.spec.desired_state = (
            igz_mgmt.constants.AppServiceDesiredStates.ready
        )
        for position, app_service in enumerate(self.app_services):
            if app_service.spec.name == app_service_obj.spec.name:
                self.app_services[position].spec = app_service_obj.spec
                break
        if not self._skip_apply:
            current_apply_mode = self.apply_services_mode

            # In 3.5.3, the ApplyServicesMode.scale_from_zero_only mode is deprecated.
            # because we can scale services from zero by using the mark_as_changed and desired_state fields
            if http_client.version >= semver.VersionInfo.parse("3.5.3"):
                self.set_apply_mode(
                    igz_mgmt.constants.ApplyServicesMode.service_owner_edit
                )
            else:
                self.set_apply_mode(
                    igz_mgmt.constants.ApplyServicesMode.scale_from_zero_only
                )
            apply_result = self._apply(http_client, wait_for_completion)

            # set to the previous apply mode
            self.set_apply_mode(current_apply_mode)
            return apply_result

    def _apply(
        self,
        http_client: igz_mgmt.client.APIClient,
        wait_for_completion=True,
        force_apply_all_mode=igz_mgmt.constants.ForceApplyAllMode.disabled,
    ) -> Job:
        """Apply the current state of the manifest to the API.

        Args:
            http_client (APIClient): The client to use.
            wait_for_completion (bool, optional): Whether to wait for the job to complete. True by default.
            force_apply_all_mode (ForceApplyAllMode, optional): Disabled by default.

        Returns:
            Job: the job that was created.
        """
        # TODO: handle errors
        self.force_apply_all_mode = force_apply_all_mode
        response = self._get_crud().update(
            http_client,
            None,
            # don't ignore unset fields
            attributes=self._fields_to_attributes(exclude_unset=False),
            relationships=self.relationships,
        )

        job_id = response.json().get("data", {}).get("id")
        if not wait_for_completion:
            return Job.get(http_client, job_id)

        # wait few seconds before checking job status
        time.sleep(5)
        apply_exc = None
        try:
            Job.wait_for_completion(
                http_client, job_id, job_completion_retry_interval=10
            )
        except Exception as exc:
            apply_exc = exc

        updated_resource = self.get(http_client)
        self.__dict__.update(updated_resource)
        if apply_exc:
            errors = []
            for service in updated_resource.app_services:
                if service.status.error_info and service.status.error_info.description:
                    errors.append(
                        f"Service {service.spec.name} failed due to {service.status.error_info.description}"
                    )
            if errors:
                raise RuntimeError(", ".join(errors)) from apply_exc
            else:
                raise apply_exc
        return Job.get(http_client, job_id)


class ProjectAuthorizationRole(BaseResource):
    """ProjectAuthorizationRole resource represents project authorization role in the system."""

    type: str = "project_authorization_role"
    name: igz_mgmt.constants.ProjectAuthorizationRoles
    users: typing.Optional[typing.List["User"]] = []
    groups: typing.Optional[typing.List["Group"]] = []
    project_id: str


class ProjectAuthorizationRoleSet(BaseResource):
    """ProjectAuthorizationRoleSet resource represents the set of authorization roles on a certain project."""

    type: str = "authorization_role"
    roles: typing.Optional[typing.Dict[str, ProjectAuthorizationRole]] = {}

    _skip_apply: bool = False
    _changes_detected: typing.List[bool] = []

    def get_roles(
        self, role: igz_mgmt.constants.ProjectAuthorizationRoles, member_kind
    ) -> typing.List[typing.Union["User", "Group"]]:
        """Get all members of a specific role.

        Args:
            role (igz_mgmt.constants.ProjectAuthorizationRoles): The role name.
            member_kind (str): The kind of member (users or groups).

        Returns:
            list: A list of members(instances of User/Group).
        """
        return getattr(self.roles.get(role, {}), member_kind)

    def add_member_to_role(
        self,
        http_client: igz_mgmt.client.APIClient,
        member: typing.Union[User, Group],
        role: igz_mgmt.constants.ProjectAuthorizationRoles,
        add_member_mode: igz_mgmt.constants.AddMemberMode = igz_mgmt.constants.AddMemberMode.fail_on_existing,
    ):
        """Add a member to a specific role.

        Args:
            http_client (igz_mgmt.client.APIClient): The client to use.
            member (typing.Union[User, Group]): The member to add.
            role (igz_mgmt.constants.ProjectAuthorizationRoles): The role name.
            add_member_mode (igz_mgmt.constants.AddMemberMode, optional): Add member mode, default: fail_on_existing
        """
        current_user_role = self.resolve_member_role(member)
        if current_user_role:
            if add_member_mode == igz_mgmt.constants.AddMemberMode.fail_on_existing:
                raise igz_mgmt.exceptions.MemberAlreadyExistsInProject(
                    member, current_user_role.name
                )
            elif add_member_mode == igz_mgmt.constants.AddMemberMode.best_effort:
                self._changes_detected.append(False)
                message = igz_mgmt.exceptions.MemberAlreadyExistsInProject(
                    member, current_user_role.name
                ).message
                http_client._logger.warn_with(
                    f"{message}.\nTo override, change add_member_mode to override."
                )
                return

        self._changes_detected.append(True)
        # we are in override mode here so we want to remove the member from the existing role
        self.remove_member(http_client, member)
        if member.type == "user":
            self.roles[role].users.append(member)
        else:
            self.roles[role].groups.append(member)
        self._apply(http_client)

    def add_members_to_role(
        self,
        http_client: igz_mgmt.client.APIClient,
        members: typing.List[typing.Union[User, Group]],
        role: igz_mgmt.constants.ProjectAuthorizationRoles,
        add_member_mode: igz_mgmt.constants.AddMemberMode = igz_mgmt.constants.AddMemberMode.fail_on_existing,
    ):
        """Add members to a specific role.

        Args:
            http_client (igz_mgmt.client.APIClient): The client to use.
            members (typing.List[typing.Union[User, Group]]): The members to add.
            role (igz_mgmt.constants.ProjectAuthorizationRoles): The role name.
            add_member_mode (igz_mgmt.constants.AddMemberMode, optional): Add member mode, default: fail_on_existing
        """
        for member in members:
            self.add_member_to_role(http_client, member, role, add_member_mode)
        self._apply(http_client)

    def remove_member(
        self, http_client: igz_mgmt.client.APIClient, member: typing.Union[User, Group]
    ):
        """Remove a member from the roles.

        Args:
            http_client (igz_mgmt.client.APIClient): The client to use.
            member (typing.Union[User, Group]): The member to delete.
        """
        role = self.resolve_member_role(member)
        if role:
            role_member_list = role.users if member.type == "user" else role.groups
            for index, role_member in enumerate(role_member_list):
                if role_member.id == member.id:
                    del role_member_list[index]
        self._apply(http_client)

    def remove_members(
        self,
        http_client: igz_mgmt.client.APIClient,
        members: typing.List[typing.Union[User, Group]],
    ):
        """Remove members.

        Args:
            http_client (igz_mgmt.client.APIClient): The client to use.
            members (typing.List[typing.Union[User, Group]]): The members to remove.
        """
        for member in members:
            self.remove_member(http_client, member)
        self._apply(http_client)

    def set_members(
        self,
        http_client: igz_mgmt.client.APIClient,
        members: typing.List[typing.Union[User, Group]],
        role: igz_mgmt.constants.ProjectAuthorizationRoles,
    ):
        """Overrides the existing role members with the given members.

        Args:
            http_client (igz_mgmt.client.APIClient): The client to use.
            members (typing.List[typing.Union[User, Group]]): The members to set.
            role (igz_mgmt.constants.ProjectAuthorizationRoles): The role name.
        """
        self.roles[role].groups = []
        self.roles[role].users = []
        self.add_members_to_role(
            http_client, members, role, igz_mgmt.constants.AddMemberMode.override
        )
        self._apply(http_client)

    def resolve_member_role(
        self, member: typing.Union[User, Group]
    ) -> typing.Optional["ProjectAuthorizationRole"]:
        """Find a member in the roles.

        Args:
            member (typing.Union[User, Group]): The member to find.

        Returns:
            ProjectAuthorizationRole: The role that the member belongs to.
        """
        for role in self.roles.values():
            relevant_members = role.users if member.type == "user" else role.groups
            for role_member in relevant_members:
                if role_member.id == member.id:
                    return role

    @contextlib.contextmanager
    def apply(
        self,
        http_client: igz_mgmt.client.APIClient,
        wait_for_job: bool = True,
        notify_by_email: bool = False,
    ) -> typing.ContextManager["ProjectAuthorizationRoleSet"]:
        """Apply the changes made to the roles.

        This function allows multiple membership changes with a single api call by context manager.
        It sets skip apply, yields itself for the context manager so user can run any function without applying,
        sets the value back and applies when context manager exists.

        Args:
            http_client (igz_mgmt.client.APIClient): The client to use.
            wait_for_job (bool, optional): Whether to wait for the job to finish. Defaults to True.
            notify_by_email (bool, optional): Whether to notify by email. Defaults to False.

        Yields:
            ProjectAuthorizationRoleSet: The updated role set.
        """
        self._skip_apply = True
        self._changes_detected = []
        yield self
        self._skip_apply = False
        self._apply(http_client, wait_for_job, notify_by_email)

    def _apply(
        self,
        http_client: igz_mgmt.client.APIClient,
        wait_for_job: bool = True,
        notify_by_email: bool = False,
    ) -> typing.Optional["Job"]:
        """Apply the changes made to the roles.

        we want to skip apply in those cases:
        1. _skip_apply is set to True:
            this is the case when we are in the context manager
        2. _changes_detected:
            _changes_detected contains a list of booleans, each boolean represents if there was change in the role.
            we want to skip apply only if _changes_detected is not empty and all the booleans are False.
            if _changes_detected is empty we want to apply because we want by default to apply the changes.
        """
        if self._skip_apply or (
            len(self._changes_detected) > 0 and not any(self._changes_detected)
        ):
            return

        request_body = {
            "data": {
                "attributes": {
                    "metadata": {
                        "project_ids": [
                            list(self.roles.values())[
                                0
                            ].project_id  # all share the same project id
                        ],
                        "notify_by_email": notify_by_email,
                    },
                    "requests": [
                        self._build_role_update_request_body(role)
                        for role in self.roles.values()
                    ],
                },
            }
        }
        response_body = self._get_crud().post_custom(
            http_client, "/async_transactions", json=request_body
        )
        job_id = response_body.get("data", {}).get("id", None)
        if wait_for_job:
            Job.wait_for_completion(
                http_client, job_id, job_completion_retry_interval=1
            )
        return Job.get(http_client, job_id)

    def _build_role_update_request_body(
        self, authorization_roles: ProjectAuthorizationRole
    ):
        request_body = {
            "method": "put",
            "resource": f"project_authorization_roles/{authorization_roles.id}",
            "body": {
                "data": {
                    "type": "project_authorization_role",
                    "attributes": {"name": authorization_roles.name},
                    "relationships": {
                        "project": {
                            "data": {
                                "type": "project",
                                "id": authorization_roles.project_id,
                            }
                        },
                        "principal_users": {
                            "data": self._build_membership_list(
                                authorization_roles.users
                            )
                        },
                        "principal_user_groups": {
                            "data": self._build_membership_list(
                                authorization_roles.groups
                            )
                        },
                    },
                }
            },
        }

        return request_body

    @staticmethod
    def _build_membership_list(memberships: typing.List[typing.Union["User", "Group"]]):
        return [
            {
                "id": membership.id,
                "type": membership.type,
            }
            for membership in memberships
        ]


class Project(BaseResource):
    """Project resource represents project in the system."""

    type: str = "project"
    name: str = ""
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    admin_status: str = igz_mgmt.constants.ProjectAdminStatuses.online
    operational_status: str = igz_mgmt.constants.ProjectOperationalStatuses.creating

    # e.g.: [{"name":"", "value":""}, ...]
    labels: typing.List[typing.Dict[str, str]] = []
    annotations: typing.List[typing.Dict[str, str]] = []

    # e.g.: [{"name":"", "value":""}, ...]
    # NOTE: Supported on Iguazio systems >= 3.5.5
    default_function_node_selector: typing.List[typing.Dict[str, str]] = []

    mlrun_project: str = ""
    nuclio_project: str = ""

    @pydantic.validator("default_function_node_selector")
    def default_function_node_selector_validator(cls, value):
        """Validate project default_function_node_selector field value."""
        cls._labels_validator("default_function_node_selector", value)
        return value

    @pydantic.validator("labels")
    def labels_validator(cls, value):
        """Validate project labels field value."""
        cls._labels_validator("labels", value)
        return value

    @pydantic.validator("annotations")
    def annotations_validator(cls, value):
        """Validate project annotations field value."""
        cls._labels_validator("annotations", value)
        return value

    @classmethod
    def create(
        cls,
        http_client: igz_mgmt.client.APIClient,
        name: str,
        description: str = "",
        labels: typing.List[typing.Dict[str, str]] = None,
        annotations: typing.List[typing.Dict[str, str]] = None,
        owner: typing.Union[str, "User", None] = None,
        wait_for_completion=True,
        default_function_node_selector: typing.List[typing.Dict[str, str]] = None,
    ) -> "Project":
        """Creates a new project.

        Args:
            http_client (APIClient): The client to use.
            name (str): The project name.
            description (str, optional): The project description.
            labels (typing.List[typing.Dict[str, str]], optional): The project labels.
            annotations (typing.List[typing.Dict[str, str]], optional): The project annotations.
            owner (str or User or None): The project owner. None by default
            wait_for_completion (bool): Whether to wait for the job to complete
            default_function_node_selector (typing.List[typing.Dict[str, str]], optional): The default node
            selectors to be used for functions in the project. (Supported on Iguazio systems >= 3.5.5)

        Returns:
            Project: The project instance.
        """
        attributes = {
            "name": name,
            "description": description,
        }

        if labels is not None:
            cls._labels_validator(field_name="labels", value=labels)
            attributes["labels"] = labels

        if annotations is not None:
            cls._labels_validator(field_name="annotations", value=annotations)
            attributes["annotations"] = annotations

        if default_function_node_selector is not None:
            cls._labels_validator(
                field_name="default_function_node_selector",
                value=default_function_node_selector,
            )
            attributes[
                "default_function_node_selector"
            ] = default_function_node_selector

        if http_client.version < semver.VersionInfo.parse("3.5.5"):
            attributes.pop("default_function_node_selector", None)
            if default_function_node_selector:
                http_client._logger.warn_with(
                    "default_function_node_selector is not supported on this Iguazio version, ignoring",
                    default_function_node_selector=default_function_node_selector,
                    iguazio_version=http_client.version.__str__(),
                )

        relationships = cls._fill_relationships(http_client, owner=owner)

        created_resource = cls._get_crud().create(
            http_client,
            attributes=attributes,
            relationships=relationships,
            headers=cls._resolve_project_header(),
        )

        # there might be jobs handling the creating
        job_id = (
            created_resource.get("data", {})
            .get("relationships", {})
            .get("last_job", {})
            .get("data", {})
            .get("id", None)
        )
        if job_id and wait_for_completion:
            Job.wait_for_completion(
                http_client, job_id, job_completion_retry_interval=10
            )
        return cls.from_orm_with_client(http_client, created_resource)

    def update(
        self, http_client: igz_mgmt.client.APIClient, relationships=None, **kwargs
    ) -> "BaseResource":
        """Updates project.

        Args:
            http_client (APIClient): The client to use.
            relationships (optional): The project relationships. None by default.
            **kwargs: additional arguments to pass to the request.

        Returns:
            BaseResource: The updated record.
        """
        return super().update(
            http_client,
            relationships=relationships,
            headers=self._resolve_project_header(),
            **kwargs,
        )

    def delete(
        self,
        http_client: igz_mgmt.client.APIClient,
        ignore_missing: bool = False,
        wait_for_job_deletion: bool = True,
        deletion_strategy: igz_mgmt.constants.ProjectDeletionStrategies = None,
    ) -> typing.Optional[Job]:
        """Deletes resource record.

        Args:
            http_client (APIClient): The client to use.
            ignore_missing (bool, optional): When True, don't raise an exception in case the record does not exist.
            False by default.
            wait_for_job_deletion (bool, optional): Whether to wait for the job to complete. True by default.
            deletion_strategy (ProjectDeletionStrategies, optional): The project deletion type. None by default

        Returns:
            Job, optional: the job that was created or None.
        """
        response = http_client.delete_by_attribute(
            self.type,
            "name",
            self.name,
            ignore_missing=ignore_missing,
            headers=self._resolve_project_header(deletion_strategy),
        )

        if response.status_code == http.HTTPStatus.ACCEPTED:
            response_body = response.json()
            job_id = response_body.get("data", {}).get("id", None)
            if job_id:
                if wait_for_job_deletion:
                    Job.wait_for_completion(
                        http_client, job_id, job_completion_retry_interval=10
                    )
                return Job.get(http_client, job_id)

    @classmethod
    def get_by_name(
        cls,
        http_client: igz_mgmt.client.APIClient,
        name: str,
        include: typing.Optional[typing.List[str]] = None,
    ) -> "Project":
        """A convenience method to get a project by name.

        Args:
            http_client (APIClient): The client to use.
            name (str): The project name.
            include (typing.List[str], optional): Include related resources (e.g. include=["tenant", "owner"]).
                None by default.

        Returns:
            Project: The project instance by name.

        Raises:
            ResourceNotFoundException: If project is not found
        """
        return cls._get_resource_by_name(http_client, "name", name, include=include)

    def get_owner(
        self, http_client: igz_mgmt.client.APIClient
    ) -> typing.Optional["User"]:
        """Returns the project owner.

        Args:
            http_client (APIClient): The client to use.

        Returns:
            User: The project owner.
        """
        project = self.get(http_client, self.id, include=["owner"])
        if not project.included:
            return
        return User.from_orm_with_client(
            http_client, {"data": project.included[0].dict()}
        )

    def set_owner(
        self, http_client: igz_mgmt.client.APIClient, owner: typing.Union[str, "User"]
    ):
        """Sets the owner of the project.

        Args:
            http_client (APIClient): The client to use.
            owner (str or User): The user id or user name or user instance.

        Returns:
            Project: The project instance.
        """
        relationships = self._fill_relationships(http_client, owner=owner)
        try:
            return self.update(http_client, relationships=relationships)
        except igz_mgmt.exceptions.ResourceNotFoundException:
            # we return None here because if we reach ResourceNotFoundException it means that current user have
            # no access to this project anymore
            return

    def get_user_effective_role(
        self, http_client: igz_mgmt.client.APIClient, user: typing.Union[str, "User"]
    ) -> typing.Optional[igz_mgmt.constants.ProjectAuthorizationRoles]:
        """Returns the effective role of the user.

        Args:
            http_client (APIClient): The client to use.
            user (str or User): The user id or username or user instance.

        Returns:
            str: The effective role of the user.
        """
        # in general case we should have _http_client set, but in case we don't we use the one passed
        client = self._http_client or http_client
        user = User._get_from_arg(client, user)

        authorization_roles = self._authorization_roles

        # first we try to resolve member role without checking in groups
        member_role = authorization_roles.resolve_member_role(user)
        if member_role:
            member_role = member_role.name
        # we try to resolve the role by checking in groups from high role to low
        for role in igz_mgmt.constants.ROLE_ORDER:
            current_role = authorization_roles.roles.get(role, None)
            if current_role:
                for group in current_role.groups:
                    if user.in_group(client, group):
                        member_role = igz_mgmt.common.helpers.get_highest_role(
                            current_role.name, member_role
                        )
        return member_role

    def get_viewer_users(self):
        """Returns the project viewer users."""
        return self._authorization_roles.get_roles(
            igz_mgmt.constants.ProjectAuthorizationRoles.viewer, "users"
        )

    def get_viewer_groups(self):
        """Returns the project viewer groups."""
        return self._authorization_roles.get_roles(
            igz_mgmt.constants.ProjectAuthorizationRoles.viewer, "groups"
        )

    def get_editor_users(self):
        """Returns the project editor users."""
        return self._authorization_roles.get_roles(
            igz_mgmt.constants.ProjectAuthorizationRoles.editor, "users"
        )

    def get_editor_groups(self):
        """Returns the project editor groups."""
        return self._authorization_roles.get_roles(
            igz_mgmt.constants.ProjectAuthorizationRoles.editor, "groups"
        )

    def get_admin_users(self):
        """Returns the project admin users."""
        return self._authorization_roles.get_roles(
            igz_mgmt.constants.ProjectAuthorizationRoles.admin, "users"
        )

    def get_admin_groups(self):
        """Returns the project admin groups."""
        return self._authorization_roles.get_roles(
            igz_mgmt.constants.ProjectAuthorizationRoles.admin, "groups"
        )

    def set_membership(
        self,
        http_client: igz_mgmt.client.APIClient,
        member: typing.Union["User", "Group", "ProjectMembershipResource"],
        role: igz_mgmt.constants.ProjectAuthorizationRoles,
        wait_for_job: bool = True,
        notify_by_email: bool = False,
        add_member_mode: igz_mgmt.constants.AddMemberMode = igz_mgmt.constants.AddMemberMode.fail_on_existing,
    ):
        """Adds a member to the project.

        Args:
            http_client (APIClient): The client to use.
            member (User or Group): User instance or Group instance.
            role (ProjectAuthorizationRolesTypes): The role name.
            wait_for_job (bool, optional): Wait for job completion. Defaults to True.
            notify_by_email (bool, optional): Notify by email. Defaults to False.
            add_member_mode (AddMemberModes, optional): Add member mode. Defaults to AddMemberModes.fail_on_existing.
        """
        with self._authorization_roles.apply(
            http_client, wait_for_job, notify_by_email
        ) as authorization_roles:
            authorization_roles.add_member_to_role(
                http_client, member, role, add_member_mode
            )

    def add_members(
        self,
        http_client: igz_mgmt.client.APIClient,
        members: typing.List[typing.Union["User", "Group"]],
        role: igz_mgmt.constants.ProjectAuthorizationRoles,
        wait_for_job: bool = True,
        notify_by_email: bool = False,
        add_member_mode: igz_mgmt.constants.AddMemberMode = igz_mgmt.constants.AddMemberMode.fail_on_existing,
    ):
        """Adds members to the project.

        Args:
            http_client (APIClient): The client to use.
            members (List[User or Group]): User instances or Group instances.
            role (ProjectAuthorizationRolesTypes): The role name.
            wait_for_job (bool, optional): Wait for job completion. Defaults to True.
            notify_by_email (bool, optional): Notify by email. Defaults to False.
            add_member_mode (AddMemberModes, optional): Add member mode. Defaults to AddMemberModes.fail_on_existing.
        """
        with self._authorization_roles.apply(
            http_client, wait_for_job, notify_by_email
        ) as authorization_roles:
            authorization_roles.add_members_to_role(
                http_client, members, role, add_member_mode
            )

    def set_members(
        self,
        http_client: igz_mgmt.client.APIClient,
        members: typing.List[typing.Union["User", "Group"]],
        role: igz_mgmt.constants.ProjectAuthorizationRoles,
        wait_for_job: bool = True,
        notify_by_email: bool = False,
        override: bool = False,
    ):
        """Overrides the existing role members with the given members.

        Args:
            http_client (APIClient): The client to use.
            members (List[User or Group]): User instances or Group instances.
            role (ProjectAuthorizationRolesTypes): The role name.
            wait_for_job (bool, optional): Wait for job completion. Defaults to True.
            notify_by_email (bool, optional): Notify by email. Defaults to False.
            override (bool, optional): Override existing members. Defaults to False.
        """
        # we want to raise exception only if the override is False and there are existing members
        if not override and len(
            self._authorization_roles.roles[role].users
            + self._authorization_roles.roles[role].groups
        ):
            raise RuntimeError(
                "This method overrides the existing members! if you want to run it pass override=True"
            )
        with self._authorization_roles.apply(
            http_client, wait_for_job, notify_by_email
        ) as authorization_roles:
            authorization_roles.set_members(http_client, members, role)

    def remove_member(
        self,
        http_client: igz_mgmt.client.APIClient,
        member: typing.Union["User", "Group", "ProjectMembershipResource"],
        wait_for_job: bool = True,
        notify_by_email: bool = False,
    ):
        """Removes a member from the project.

        Args:
            http_client (APIClient): The client to use.
            member (User or Group): User instance or Group instance.
            wait_for_job (bool, optional): Wait for job completion. Defaults to True.
            notify_by_email (bool, optional): Notify by email. Defaults to False.
        """
        with self._authorization_roles.apply(
            http_client, wait_for_job, notify_by_email
        ) as authorization_roles:
            authorization_roles.remove_member(http_client, member)

    def remove_members(
        self,
        http_client: igz_mgmt.client.APIClient,
        members: typing.List[typing.Union["User", "Group"]],
        wait_for_job: bool = True,
        notify_by_email: bool = False,
    ):
        """Removes members from the project.

        Args:
            http_client (APIClient): The client to use.
            members (List[User or Group]): User instances or Group instances.
            wait_for_job (bool, optional): Wait for job completion. Defaults to True.
            notify_by_email (bool, optional): Notify by email. Defaults to False.
        """
        with self._authorization_roles.apply(
            http_client, wait_for_job, notify_by_email
        ) as authorization_roles:
            authorization_roles.remove_members(http_client, members)

    def resolve_member_role(self, member: typing.Union["User", "Group"]):
        """Returns the member role.

        Args:
            member (User or Group): User instance or Group instance.

        Returns:
            ProjectAuthorizationRolesTypes: The member role.
        """
        return self._authorization_roles.resolve_member_role(member)

    @contextlib.contextmanager
    def apply_authorization_roles(
        self,
        http_client: igz_mgmt.client.APIClient,
        wait_for_job: bool = True,
        notify_by_email: bool = False,
    ) -> typing.ContextManager["ProjectAuthorizationRoleSet"]:
        """Returns a context manager that applies the authorization roles.

        Args:
            http_client (APIClient): The client to use.
            wait_for_job (bool, optional): Wait for job completion. Defaults to True.
            notify_by_email (bool, optional): Notify by email. Defaults to False.

        Yields:
            ProjectAuthorizationRoleSet: The project authorization roles.
        """
        authorization_roles = self._authorization_roles
        yield authorization_roles
        with authorization_roles.apply(
            http_client, wait_for_job, notify_by_email
        ) as authorization_roles:
            authorization_roles.apply(http_client, wait_for_job, notify_by_email)

    @classmethod
    def _get_from_arg(
        cls,
        http_client: igz_mgmt.client.APIClient,
        project: typing.Union[str, int, "Project"],
    ):
        if isinstance(project, Project):
            return project

        # check if we got a group id
        if cls._is_project_id(http_client.version, project):
            return Project.get(http_client, project)

        # here we assume that we want to get user by username
        return Project.get_by_name(http_client, project)

    @classmethod
    def _is_project_id(
        cls, iguazio_system_version: semver.VersionInfo, project_id: str
    ):
        if iguazio_system_version >= semver.VersionInfo.parse("3.5.4"):
            project_pattern = r"[\w.-]+@[\w.-]+"
            return re.match(project_pattern, project_id) is not None
        return igz_mgmt.common.helpers.is_uuid4(project_id)

    @property
    def _authorization_roles(self):
        """Returns the project authorization roles."""
        project = self.get(
            self._http_client,
            self.id,
            include=[
                "project_authorization_roles.principal_users",
                "project_authorization_roles.principal_user_groups",
            ],
        )

        memberships = self._build_membership_dict(project)
        return self._build_project_authorization_role_set(project, memberships)

    def _build_membership_dict(self, project):
        member_resource_classes = {
            "user": User,
            "user_group": Group,
        }
        memberships = {}
        for included_resource in project.included:
            if included_resource.type not in member_resource_classes:
                continue
            memberships[included_resource.id] = member_resource_classes[
                included_resource.type
            ].from_orm_with_client(
                self._http_client, {"data": included_resource.dict()}
            )
        return memberships

    def _build_project_authorization_role_set(self, project, memberships):
        roles = ProjectAuthorizationRoleSet()
        for included_resource in project.included:
            if included_resource.type != "project_authorization_role":
                continue
            project_authorization_role = included_resource
            relationships = (
                project_authorization_role.relationships
                if project_authorization_role.relationships
                else {}
            )

            users = []
            for user in relationships.get("principal_users", {}).get("data", []):
                users.append(memberships.get(user["id"], user["id"]))

            groups = []
            for group in relationships.get("principal_user_groups", {}).get("data", []):
                groups.append(memberships.get(group["id"], group["id"]))

            role = project_authorization_role.attributes["name"]
            roles.roles[role] = ProjectAuthorizationRole(
                id=project_authorization_role.id,
                project_id=self.id,
                name=role,
                users=users,
                groups=groups,
            )
        return roles

    @staticmethod
    def _resolve_project_header(
        deletion_strategy: igz_mgmt.constants.ProjectDeletionStrategies = None,
    ):
        headers = {
            igz_mgmt.constants._RequestHeaders.projects_role_header: "igz-mgmt-sdk"
        }
        if deletion_strategy:
            headers[
                igz_mgmt.constants._RequestHeaders.deletion_strategy_header
            ] = deletion_strategy
        return headers

    @staticmethod
    def _fill_relationships(http_client, owner: typing.Union[str, "User", None]):
        relationships = collections.defaultdict(dict)
        if owner:
            owner = User._get_from_arg(http_client, owner)
            relationships["owner"] = {
                "data": {
                    "type": "user",
                    "id": owner.id,
                },
            }
        return relationships

    @staticmethod
    def _labels_validator(field_name, value):
        def is_valid_list_of_dicts():
            if not isinstance(value, list):
                return False
            for item in value:
                if not isinstance(item, dict) or len(item) != 2:
                    return False
                if "name" not in item or "value" not in item:
                    return False
                if not isinstance(item["name"], str) or not isinstance(
                    item["value"], str
                ):
                    return False
            return True

        if not is_valid_list_of_dicts():
            raise TypeError(
                f"'{field_name}' should be a list of dictionaries of strings of the pattern "
                "[{'name': 'dummy-name', 'value': 'dummy-value'}]."
            )


class Event(BaseResource):
    """Event resource represents events in the system.

    Events are used to notify about changes in the system.
    """

    type: str = "event"

    source: str = pydantic.Field(
        description="The originator of the event, in the form of a service ID (e.g. igz0.vn.3)",
        default="",
    )
    kind: str = pydantic.Field(
        description="A string in dot notation representing which event occurred",
        default="",
    )
    timestamp_uint64: typing.Optional[int] = pydantic.Field(
        description="64bit timestamp indicating when the event occurred. if 0 and timestampIso8601 is empty,"
        " the timestamp will added upon reception of the first platform step.",
        default=None,
    )
    timestamp_iso8601: typing.Optional[str] = pydantic.Field(
        description="string representation of the timestamp, in ISO8601 format",
        default=None,
    )
    timestamp_uint64_str: typing.Optional[str] = pydantic.Field(
        description="Same as 'timestampUint64' but in string form",
        default=None,
    )
    parameters_uint64: typing.Optional[
        typing.List[igz_mgmt.schemas.events.ParametersUint64]
    ] = pydantic.Field(
        description="A list of parameters, each containing a name and an int value",
        default=None,
    )
    parameters_text: typing.Optional[
        typing.List[igz_mgmt.schemas.events.ParametersText]
    ] = pydantic.Field(
        description="A list of parameters, each containing a name and a string value",
        default=None,
    )
    description: typing.Optional[str] = pydantic.Field(
        description="A description of the event", default=None
    )
    severity: typing.Optional[igz_mgmt.constants.EventSeverity] = pydantic.Field(
        description="The severity of the event, Required if event kind doesn't exists in the system",
        default=None,
    )
    tags: typing.Optional[typing.List[str]] = pydantic.Field(
        description="A list of tags to associate with the event, used for later filtering of events/alerts",
        default=None,
    )
    affected_resources: typing.Optional[
        typing.List[igz_mgmt.schemas.events.AffectedResource]
    ] = pydantic.Field(
        description="Resources affected by this event",
        default=None,
    )
    classification: typing.Optional[
        igz_mgmt.constants.EventClassification
    ] = pydantic.Field(
        description="The classification of the event, Required if event kind doesn't exists in the system",
        default=None,
    )
    system_event: typing.Optional[bool] = pydantic.Field(
        description="Whether this event is a system event or not",
        default=False,
    )
    visibility: typing.Optional[igz_mgmt.constants.EventVisibility] = pydantic.Field(
        description="Whom the event will be visible to",
        default=None,
    )

    @classmethod
    def delete_all(cls, http_client: igz_mgmt.client.APIClient):
        """Delete all events.

        Requires Iguazio privileged user.

        Args:
            http_client (APIClient): The client to use.
        """
        cls._get_crud().delete(http_client, "", False)

    def delete(
        self,
        http_client: igz_mgmt.client.APIClient,
        ignore_missing: bool = False,
        wait_for_job_deletion: bool = True,
    ) -> typing.Optional["Job"]:
        """Deleting a single event is not supported."""
        raise igz_mgmt.exceptions.ResourceDeleteException

    @classmethod
    def get(
        cls,
        http_client: igz_mgmt.client.APIClient,
        resource_id: typing.Union[int, str],
        include: typing.Optional[typing.List[str]] = None,
    ) -> "BaseResource":
        """Getting an event is not supported."""
        raise igz_mgmt.exceptions.ResourceGetException

    def update(
        self, http_client: igz_mgmt.client.APIClient, relationships=None, **kwargs
    ) -> "BaseResource":
        """Updating an event is not supported."""
        raise igz_mgmt.exceptions.ResourceUpdateException

    def emit(self, http_client, **kwargs):
        """Emit the event.

        Requires system-admin role.

        :param http_client: HTTP client to use
        """
        return igz_mgmt.operations.ManualEvents.emit(http_client, event=self, **kwargs)


class CommunicationEvent(Event):
    """CommunicationEvent resource represents internal communication events in the system.

    Communication events are used to communicate between internal components within the system.
    Their visibility is internal and the classification is usually "sw".
    """

    type = "communication_event"


class AuditEvent(Event):
    """AuditEvent resource represents audit events in the system.

    Audit events are used to represent user and system actions within the system

    """

    type = "audit_event"

    @classmethod
    def delete_all(cls, http_client: igz_mgmt.client.APIClient):
        """Deleting audit events are not supported."""
        raise igz_mgmt.exceptions.ResourceDeleteException

    def emit(self, http_client, **kwargs):
        """Emit the event.

        Requires system-admin role.

        :param http_client: HTTP client to use
        """
        return igz_mgmt.operations.ManualEvents.emit(
            http_client, audit_tenant_id=http_client.tenant_id, event=self, **kwargs
        )
