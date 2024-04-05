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
import enum


class _BaseEnum(enum.Enum):
    @classmethod
    def all(cls):
        return [member.value for member in cls]


class _BaseEnumStr(str, _BaseEnum):
    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class SessionPlanes(_BaseEnumStr):
    """Session plane types."""

    data = "data"
    control = "control"


class UserAuthenticationMethods(_BaseEnumStr):
    """User authentication methods types."""

    password = "password"
    sso = "sso"


class TenantManagementRoles(_BaseEnumStr):
    """Tenant management roles types."""

    it_admin = "IT Admin"
    it_admin_read_only = "IT Admin Read Only"
    application_admin = "Application Admin"
    security_admin = "Security Admin"
    project_security_admin = "Project Security Admin"
    project_read_only = "Project Read Only"
    application_read_only = "Application Read Only"
    data = "Data"
    tenant_admin = "Tenant Admin"
    developer = "Developer"
    service_admin = "Service Admin"
    system_admin = "System Admin"


class ConfigTypes(_BaseEnumStr):
    """Configuration types."""

    artifact_version_manifest = "artifact_version_manifest"
    events = "events"
    cluster = "cluster"
    app_services = "app_services"


class JobStates(_BaseEnumStr):
    """Job states types."""

    created = "created"
    dispatched = "dispatched"
    in_progress = "in_progress"
    completed = "completed"
    canceled = "canceled"
    republishing = "republishing"
    failed = "failed"

    @staticmethod
    def terminal_states():
        """Job optional terminal states."""
        return [
            JobStates.completed.value,
            JobStates.failed.value,
            JobStates.canceled.value,
        ]


class ApplyServicesMode(_BaseEnumStr):
    """Apply services mode."""

    default = "default"
    """The default apply services mode."""

    scale_from_zero_only = "scaleFromZeroOnly"
    """used for scaling services from zero (either service admin or service owner).
    NOTE: In iguazio 3.5.3, this mode was deprecated."""

    service_owner_edit = "serviceOwnerEdit"
    """used for editing services (service admin or service owner).
    NOTE: currently supports both restarting and scaling app services from zero (for iguazio version >= 3.5.3)."""


class ForceApplyAllMode(_BaseEnumStr):
    """To force apply to all services or not."""

    enabled = "enabled"
    """All services will be applied"""

    disabled = "disabled"


class AppServiceDesiredStates(_BaseEnumStr):
    """App service desired state."""

    ready = "ready"
    disabled = "disabled"
    scaled_to_zero = "scaledToZero"


class ScaleToZeroMode(_BaseEnumStr):
    """App service can scale to zero or not."""

    enabled = "enabled"
    disabled = "disabled"


class AppServicesManifestStates(_BaseEnumStr):
    """App services manifest state."""

    ready = "ready"
    error = "error"
    provisioning = "provisioning"
    scaling_from_zero = "scalingFromZero"
    scaling_to_zero = "scalingToZero"
    waiting_for_provisioning = "waitingForProvisioning"
    waiting_for_scaling_from_zero = "waitingForScalingFromZero"
    waiting_for_scaling_to_zero = "waitingForScalingToZero"

    @staticmethod
    def terminal_states():
        """App services manifest optional terminal states."""
        return [
            AppServicesManifestStates.ready.value,
            AppServicesManifestStates.error.value,
        ]


class AppServicesScaleToZeroMetrics(_BaseEnumStr):
    """App service scale to zero metrics name."""

    num_of_requests = "num_of_requests"
    jupyter_kernel_busyness = "jupyter_kernel_busyness"


class AppServicePriorityClass(_BaseEnumStr):
    """App service priority class."""

    workload_low = "igz-workload-low"
    workload_medium = "igz-workload-medium"
    workload_high = "igz-workload-high"
    system_medium = "igz-system-medium"
    system_high = "igz-system-high"
    system_critical = "igz-system-critical"


class UserAdminStatuses(_BaseEnumStr):
    """Admin status types to disable/enable user."""

    up = "up"
    down = "down"


class UserOperationalStatuses(_BaseEnumStr):
    """User operational status types."""

    up = "up"
    deleting = "deleting"
    down = "down"


class JupyterAppServicePrebakedImage:
    """Jupyter app service images types."""

    gpu_cuda = "jupyter-gpu-cuda"
    """Full stack with GPU."""

    full_stack = "jupyter-all"
    """Full stack without GPU"""


class SslVerificationMode(_BaseEnumStr):
    """Controls the verification of filebeat server certificates."""

    none = "none"
    """Performs no verification of the server’s certificate.
    This mode disables many of the security benefits of SSL/TLS and should only be used after cautious consideration.
    It is primarily intended as a temporary diagnostic mechanism when attempting to resolve TLS errors.
    Its use in production environments is strongly discouraged."""

    full = "full"
    """Verifies that the provided certificate is signed by a trusted authority (CA)
    and also verifies that the server’s hostname (or IP address) matches the names identified within the certificate."""


class EventSeverity(_BaseEnumStr):
    """Severity types."""

    unknown = "unknown"
    debug = "debug"
    info = "info"
    warning = "warning"
    major = "major"
    critical = "critical"


class EventClassification(_BaseEnumStr):
    """Classification types.

    mapping to zebo event classification.
    """

    unknown = "unknown"
    hardware = "hw"
    user_action = "ua"
    background = "bg"
    software = "sw"
    sla = "sla"
    capacity = "cap"
    security = "sec"
    audit = "audit"
    system = "system"


class EventVisibility(_BaseEnumStr):
    """Visibility types."""

    unknown = "unknown"
    internal = "internal"
    external = "external"
    customer_only = "customerOnly"


class ProjectAdminStatuses(_BaseEnumStr):
    """Project admin status types."""

    online = "online"
    offline = "offline"
    archived = "archived"


class ProjectOperationalStatuses(_BaseEnumStr):
    """Project operational status types."""

    unknown = "unknown"
    creating = "creating"
    deleting = "deleting"
    online = "online"
    offline = "offline"
    archived = "archived"


class ProjectAuthorizationRoles(_BaseEnumStr):
    """Project membership types."""

    admin = "Admin"
    editor = "Editor"
    viewer = "Viewer"


# role order by priority (from highest to lowest)
ROLE_ORDER = [
    ProjectAuthorizationRoles.admin,
    ProjectAuthorizationRoles.editor,
    ProjectAuthorizationRoles.viewer,
]


class AddMemberMode(_BaseEnumStr):
    """Add member mode."""

    override = "override"
    """If member exists, override its role."""

    best_effort = "best_effort"
    """If member exists, warn but don't fail."""

    fail_on_existing = "fail_on_existing"
    """If member exists, fail."""


class _RequestHeaders(_BaseEnumStr):
    content_type_header = "Content-Type"
    authorization_header = "Authorization"
    projects_role_header = "x-projects-role"
    deletion_strategy_header = "igz-project-deletion-strategy"


class ProjectDeletionStrategies(_BaseEnumStr):
    """Project deletion strategies types."""

    restricted = "restricted"
    """Restrict deletion if project has resources such as functions, runs, etc."""

    cascading = "cascading"
    """Delete the project with all resources"""
