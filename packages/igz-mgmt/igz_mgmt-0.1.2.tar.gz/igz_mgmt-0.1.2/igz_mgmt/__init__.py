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
from igz_mgmt.schemas.app_services import (
    AppServiceBase,
    AppServiceSpec,
    AppServiceStatus,
    CustomAppServiceSpec,
    FilebeatSpec,
    JupyterSpec,
    ScaleResource,
    ScaleToZeroSpec,
)
from igz_mgmt.schemas.app_services import (
    ScaleToZeroSpecPresets as AppServiceScaleToZeroSpecPresets,
)

from .client import APIClient as Client
from .constants import (
    ApplyServicesMode,
    AppServiceDesiredStates,
    AppServicePriorityClass,
    ForceApplyAllMode,
    JupyterAppServicePrebakedImage,
    ProjectDeletionStrategies,
    ScaleToZeroMode,
    SslVerificationMode,
    TenantManagementRoles,
    UserAdminStatuses,
    UserAuthenticationMethods,
    UserOperationalStatuses,
)
from .cruds import ResourceListPagingQueryParams
from .logger import get_or_create_logger
from .operations import AppServices, ClusterConfigurations, ManualEvents
from .resources import (
    AccessKey,
    AppServicesManifest,
    AuditEvent,
    CommunicationEvent,
    Event,
    Group,
    Job,
    Project,
    User,
)

# FOR BC
ManualEventSchema = Event

__all__ = [
    "Client",
    "User",
    "Group",
    "AccessKey",
    "Job",
    "Event",
    "AuditEvent",
    "CommunicationEvent",
    "ClusterConfigurations",
    "AppServicesManifest",
    "AppServiceBase",
    "AppServiceSpec",
    "AppServiceStatus",
    "CustomAppServiceSpec",
    "JupyterSpec",
    "ScaleToZeroSpec",
    "ScaleResource",
    "ApplyServicesMode",
    "TenantManagementRoles",
    "ScaleToZeroMode",
    "AppServiceDesiredStates",
    "ForceApplyAllMode",
    "ResourceListPagingQueryParams",
    "AppServiceScaleToZeroSpecPresets",
    "AppServicePriorityClass",
    "UserAdminStatuses",
    "UserOperationalStatuses",
    "JupyterAppServicePrebakedImage",
    "AppServices",
    "get_or_create_logger",
    "ManualEvents",
    "ManualEventSchema",
    "ProjectDeletionStrategies",
    "Project",
    "SslVerificationMode",
    "UserAuthenticationMethods",
    "FilebeatSpec",
]
