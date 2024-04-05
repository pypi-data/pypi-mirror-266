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
import http

import inflection


class ResourceDeleteException(Exception):
    """The resource is not delete-able."""

    def __str__(self):
        return "This resource is not delete-able"


class ResourceUpdateException(Exception):
    """The resource is not update-able."""

    def __str__(self):
        return "This resource is not update-able"


class ResourceListException(Exception):
    """The resource is not list-able."""

    def __str__(self):
        return "This resource is not list-able"


class ResourceGetException(Exception):
    """The resource is not get-able."""

    def __str__(self):
        return "This resource is not get-able"


class AppServiceNotExistsException(Exception):
    """The app service not exists in app services list.

    Args:
        name (str): App service name.
    """

    def __init__(self, name: str):
        self.message = f"App service:{name} not exists in app services list"
        super().__init__(self.message)


class ResourceNotFoundException(Exception):
    """The resource is not found."""

    def __init__(self, resource, name_or_id):
        self.message = f"{inflection.humanize(resource)} {name_or_id} not found"
        self.status_code = http.HTTPStatus.NOT_FOUND
        super().__init__(self.message)


class ResourceNotInitializedError(Exception):
    """The resource is not initialized."""

    def __init__(self, name):
        self.message = (
            f"Resource {name} is not initialized. "
            f"Please use the .get() or .list() methods to initialize the resource."
        )
        super().__init__(self.message)


class MemberAlreadyExistsInProject(Exception):
    """The member we want to add already exists in project."""

    def __init__(self, member, role_name):
        if member.type == "user":
            prefix = f"User: {member.username}"
        else:
            prefix = f"Group: {member.name}"
        self.message = f"{prefix} already exists in project with role: {role_name}"
        super().__init__(self.message)


class UserIsInPrimaryGroupError(Exception):
    """The user is in primary group."""

    def __init__(self, user, group):
        self.message = (
            f"Cannot remove user: {user.username} from {group.name} because it is the user's primary group."
            f"Set force=True to override it."
        )
        super().__init__(self.message)
