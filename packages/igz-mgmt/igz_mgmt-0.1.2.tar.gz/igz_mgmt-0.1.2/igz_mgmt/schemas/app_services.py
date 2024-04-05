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
import typing

import pydantic

import igz_mgmt.constants
import igz_mgmt.schemas


# helper function
def generate_scale_to_zero_spec(window_size: str) -> typing.List["ScaleResource"]:
    """Generates scale resource with metric name and window size.

    Args:
        window_size (str): Time to wait before scaling the service to zero.

    Returns:
        typing.List["ScaleResource"]: scale to zero spec.
    """
    return [
        ScaleResource(
            metric_name=igz_mgmt.constants.AppServicesScaleToZeroMetrics.num_of_requests,
            window_size=window_size,
        ),
        ScaleResource(
            metric_name=igz_mgmt.constants.AppServicesScaleToZeroMetrics.jupyter_kernel_busyness,
            window_size=window_size,
        ),
    ]


class AppServicesOperationBaseModel(pydantic.BaseModel):
    """Base model for all operations."""

    class Config:
        # be forward compatible
        extra = "allow"
        orm_mode = True
        use_enum_values = True


class CredentialsSpec(AppServicesOperationBaseModel):
    """Credentials spec.

    Spec for describing credentials with which the app service will preform its operations with in the Iguazio cluster.
    """

    username: str = pydantic.Field(description="Iguazio username")


class SystemResources(AppServicesOperationBaseModel):
    """System resource description for use with limits and requests."""

    cpu: typing.Optional[str]
    memory: typing.Optional[str]
    nvidia_gpu: typing.Optional[str]


class ResourcesSpec(AppServicesOperationBaseModel):
    """Resource spec describing the limits and requests for each app service."""

    limits: typing.Optional[SystemResources]
    requests: typing.Optional[SystemResources]


class ScaleResource(AppServicesOperationBaseModel):
    """Threshold descriptor for scaling app services to zero."""

    metric_name: str = pydantic.Field(description="The threshold metric to watch")
    threshold: int = pydantic.Field(
        0,
        description="The value of the metric where if exceeded, the resource will be scaled",
    )
    window_size: str = pydantic.Field(
        description="The amount of time for which the threshold has to be exceeded for the resource to be scaled"
    )


class ScaleToZeroSpec(AppServicesOperationBaseModel):
    """Spec describing the scale to zero resources/rules."""

    mode: igz_mgmt.constants.ScaleToZeroMode
    scale_resources: typing.Optional[typing.List[ScaleResource]]


class PvcSpec(AppServicesOperationBaseModel):
    """Pvc - kubernetes persistent volume claim spec for app service pod."""

    # TODO: convert mounts entries to dictionary
    mounts: typing.Optional[
        typing.Dict[str, typing.List[typing.Dict[str, str]]]
    ] = pydantic.Field(
        description="Dictionary describing the pvc mounts where the key is a volume and the values \
        is the path inside the container"
    )


class ScaleToZeroSpecPresets:
    """Scale to zero spec presets."""

    disabled = ScaleToZeroSpec(mode=igz_mgmt.constants.ScaleToZeroMode.disabled)
    one_minute = ScaleToZeroSpec(
        mode=igz_mgmt.constants.ScaleToZeroMode.enabled,
        scale_resources=generate_scale_to_zero_spec("1m"),
    )
    five_minutes = ScaleToZeroSpec(
        mode=igz_mgmt.constants.ScaleToZeroMode.enabled,
        scale_resources=generate_scale_to_zero_spec("5m"),
    )
    ten_minutes = ScaleToZeroSpec(
        mode=igz_mgmt.constants.ScaleToZeroMode.enabled,
        scale_resources=generate_scale_to_zero_spec("10m"),
    )
    one_hour = ScaleToZeroSpec(
        mode=igz_mgmt.constants.ScaleToZeroMode.enabled,
        scale_resources=generate_scale_to_zero_spec("1h"),
    )
    two_hours = ScaleToZeroSpec(
        mode=igz_mgmt.constants.ScaleToZeroMode.enabled,
        scale_resources=generate_scale_to_zero_spec("2h"),
    )
    four_hours = ScaleToZeroSpec(
        mode=igz_mgmt.constants.ScaleToZeroMode.enabled,
        scale_resources=generate_scale_to_zero_spec("4h"),
    )


class SecurityContextSpec(AppServicesOperationBaseModel):
    """Kubernetes Security context spec for app service pods."""

    run_as_user: str
    run_as_group: str
    fs_group: str
    supplemental_groups: typing.List[str]
    run_as_non_root: bool


class AdvancedSpec(AppServicesOperationBaseModel):
    """Advanced app service spec."""

    # TODO: convert node_selector entries to dictionary
    # "entries" kind of list. e.g.: {"entries:[{"key":"", "value":""}, ...]}
    node_selector: typing.Optional[typing.Dict[str, typing.List[typing.Dict[str, str]]]]
    priority_class_name: typing.Optional[str] = pydantic.Field(
        description="Use `igz_mgmt.AppServicePriorityClass` enum for the value. \
        However, it is possible to pass any priority class name you want"
    )


class Url(AppServicesOperationBaseModel):
    """URL for accessing app services."""

    kind: str
    url: str


class Meta(AppServicesOperationBaseModel):
    """App services metadata class."""

    labels: typing.Optional[typing.Dict[str, str]] = pydantic.Field(
        description="Labels for the app service. these will be propagated to all the app service resources"
    )

    # TODO: convert annotations entries to dictionary
    # annotations: typing.Optional[typing.Dict[str, str]]


class StatusErrorInfo(AppServicesOperationBaseModel):
    """App service Status error info."""

    description: str
    timestamp: str


class AppServiceStatus(AppServicesOperationBaseModel):
    """App service status."""

    state: str
    urls: typing.Optional[typing.List[Url]]
    api_urls: typing.Optional[typing.List[Url]]
    internal_api_urls: typing.Optional[typing.List[Url]]
    version: typing.Optional[str]
    last_error: typing.Optional[str]
    display_name: typing.Optional[str]
    error_info: typing.Optional[StatusErrorInfo]

    presto: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(
        description="Presto specific app service status"
    )
    filebeat: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(
        description="Filebeat specific app service status"
    )
    shell: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(
        description="Shell specific app service status"
    )
    jupyter: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(
        description="jupyter specific app service status"
    )


class HomeContainer(AppServicesOperationBaseModel):
    """Home container."""

    container: str
    prefix: str


class SSHServerSpec(AppServicesOperationBaseModel):
    """SSH configuration for accessing interactive shell app services (e.g. jupyter, shell)."""

    force_key_regeneration: bool
    port: int


class CustomAppServiceSpec(AppServicesOperationBaseModel):
    """Base class for custom app service spec."""

    pass


class JupyterSpec(CustomAppServiceSpec):
    """Jupyter app service spec."""

    image_name: str = (
        igz_mgmt.constants.JupyterAppServicePrebakedImage.full_stack
    )  # TODO: change to optional when backend changed

    # optional fields
    spark_name: typing.Optional[str]
    presto_name: typing.Optional[str]
    framesd: typing.Optional[str]
    home_spec: typing.Optional[HomeContainer]

    # TODO: convert extra_environment_vars entries to dictionary
    # "entries" kind of list. e.g.: {"entries:[{"key":"", "value":""}, ...]}
    extra_environment_vars: typing.Optional[
        typing.Dict[str, typing.List[typing.Dict[str, str]]]
    ]
    demos_datasets_archive_address: typing.Optional[str]
    docker_registry_name: typing.Optional[str]
    ssh_enabled: typing.Optional[bool]
    ssh_server: typing.Optional[SSHServerSpec]


class FilebeatSpec(CustomAppServiceSpec):
    """Filebeat app service spec."""

    elasticsearch_url: typing.Optional[str] = pydantic.Field(
        description="Elasticsearch node to connect to"
    )
    elasticsearch_username: typing.Optional[str] = pydantic.Field(
        description="The basic authentication username for connecting to Elasticsearch"
    )
    elasticsearch_password: typing.Optional[str] = pydantic.Field(
        description="The basic authentication password for connecting to Elasticsearch"
    )
    elasticsearch_ssl_verification_mode: typing.Optional[
        igz_mgmt.constants.SslVerificationMode
    ] = pydantic.Field(
        igz_mgmt.constants.SslVerificationMode.full,
        description="Controls the verification of server certificates",
    )
    update_index_template: typing.Optional[bool] = pydantic.Field(
        True,
        description="When this option is True, the platform updates the Elasticsearch index "
        "template that's used for Log Forwarder indices. Send False if you wish to "
        "configure the index template yourself",
    )


class AppServiceSpec(AppServicesOperationBaseModel):
    """App service spec."""

    name: str = pydantic.Field(description="The name of the app service")
    kind: str = pydantic.Field(description="The app service kind (jupyter / shell .. )")

    # optional fields
    owner: typing.Optional[str] = pydantic.Field(
        description="The owner of the app service (an iguazio username)"
    )
    display_name: typing.Optional[str] = pydantic.Field(
        description="The display name of the app service in the UI"
    )
    description: typing.Optional[str] = pydantic.Field(
        description="Description of the app service"
    )
    credentials: typing.Optional[CredentialsSpec]
    resources: typing.Optional[ResourcesSpec]
    target_cpu: typing.Optional[int]
    max_replicas: typing.Optional[int] = pydantic.Field(
        description="Maximum replicas for scaling the app service"
    )
    min_replicas: typing.Optional[int] = pydantic.Field(
        description="Minimum replicas for scaling the app service"
    )
    enabled: typing.Optional[bool] = pydantic.Field(
        description="Whether to deploy the app service or not"
    )
    avatar: typing.Optional[str] = pydantic.Field(
        description="Icon for displaying in the UI"
    )
    mark_for_restart: bool = pydantic.Field(
        False, description="Set this to True in order to restart the app service"
    )
    mark_as_changed: bool = pydantic.Field(
        False,
        description="Set this to True in order to pick up any changes in the \
        app service and redeploy it according to those changes",
    )
    visible_to_all: typing.Optional[bool] = pydantic.Field(
        description="Whether the app service is visible to all users or only the owner"
    )
    scale_to_zero: typing.Optional[ScaleToZeroSpec]
    pvc: typing.Optional[PvcSpec]
    desired_state: typing.Optional[igz_mgmt.constants.AppServiceDesiredStates]
    authentication_mode: typing.Optional[str]
    security_context: typing.Optional[SecurityContextSpec]
    persistency_mode: typing.Optional[str]
    advanced: typing.Optional[AdvancedSpec]

    # app services
    jupyter: typing.Optional[JupyterSpec]
    filebeat: typing.Optional[FilebeatSpec]

    # TODO: add service specs
    webapi: typing.Optional[CustomAppServiceSpec]
    v3io_prometheus: typing.Optional[CustomAppServiceSpec]
    nuclio: typing.Optional[CustomAppServiceSpec]
    docker_registry: typing.Optional[CustomAppServiceSpec]
    shell: typing.Optional[CustomAppServiceSpec]
    presto: typing.Optional[CustomAppServiceSpec]
    grafana: typing.Optional[CustomAppServiceSpec]
    mariadb: typing.Optional[CustomAppServiceSpec]
    hive: typing.Optional[CustomAppServiceSpec]
    monitoring: typing.Optional[CustomAppServiceSpec]
    dex: typing.Optional[CustomAppServiceSpec]
    oauth2_proxy: typing.Optional[CustomAppServiceSpec]
    metrics_server_exporter: typing.Optional[CustomAppServiceSpec]
    mlrun: typing.Optional[CustomAppServiceSpec]
    spark_history_server: typing.Optional[CustomAppServiceSpec]
    tensorboard: typing.Optional[CustomAppServiceSpec]

    # internal
    coredns_updater: typing.Optional[CustomAppServiceSpec]
    aws_node_termination_handler: typing.Optional[CustomAppServiceSpec]
    nvidia_device_plugin: typing.Optional[CustomAppServiceSpec]

    # deprecated
    tsdb_nuclio: typing.Optional[CustomAppServiceSpec]
    netops_demo: typing.Optional[CustomAppServiceSpec]
    zeppelin: typing.Optional[CustomAppServiceSpec]

    def __init__(self, **kwargs):
        if "kind" not in kwargs:
            for field_name in self.__fields__:
                if issubclass(
                    self.__fields__[field_name].type_, CustomAppServiceSpec
                ) and kwargs.get(field_name):
                    kwargs["kind"] = field_name
                    break
        super().__init__(**kwargs)


class AppServiceBase(AppServicesOperationBaseModel):
    """App service base class."""

    spec: AppServiceSpec
    meta: typing.Optional[Meta]
    status: typing.Optional[AppServiceStatus]
