from datetime import datetime
from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import Field

from validio_sdk.scalars import (
    CredentialId,
    CronExpression,
    JsonFilterExpression,
    JsonPointer,
    JsonTypeDefinition,
    SegmentationId,
    SourceId,
    ValidatorId,
    WindowId,
)

from .base_model import BaseModel
from .enums import (
    ApiErrorCode,
    CategoricalDistributionMetric,
    ComparisonOperator,
    DecisionBoundsType,
    FileFormat,
    IdentityDeleteErrorCode,
    IdentityProviderCreateErrorCode,
    IdentityProviderDeleteErrorCode,
    IdentityProviderUpdateErrorCode,
    IncidentSeverity,
    IssueTypename,
    NumericAnomalyMetric,
    NumericDistributionMetric,
    NumericMetric,
    RelativeTimeMetric,
    RelativeVolumeMetric,
    Role,
    SourceState,
    StreamingSourceMessageFormat,
    UserDeleteErrorCode,
    UserStatus,
    UserUpdateErrorCode,
    VolumeMetric,
    WindowTimeUnit,
)


class ErrorDetails(BaseModel):
    typename__: str = Field(alias="__typename")
    code: ApiErrorCode
    message: str


class ChannelCreation(BaseModel):
    errors: List["ChannelCreationErrors"]
    channel: Optional[
        Annotated[
            Union[
                "ChannelCreationChannelChannel",
                "ChannelCreationChannelMsTeamsChannel",
                "ChannelCreationChannelSlackChannel",
                "ChannelCreationChannelWebhookChannel",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class ChannelCreationErrors(ErrorDetails):
    pass


class ChannelCreationChannelChannel(BaseModel):
    typename__: Literal["Channel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List["ChannelCreationChannelChannelNotificationRules"] = Field(
        alias="notificationRules"
    )


class ChannelCreationChannelChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class ChannelCreationChannelMsTeamsChannel(BaseModel):
    typename__: Literal["MsTeamsChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "ChannelCreationChannelMsTeamsChannelNotificationRules"
    ] = Field(alias="notificationRules")
    config: "ChannelCreationChannelMsTeamsChannelConfig"


class ChannelCreationChannelMsTeamsChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class ChannelCreationChannelMsTeamsChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class ChannelCreationChannelSlackChannel(BaseModel):
    typename__: Literal["SlackChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "ChannelCreationChannelSlackChannelNotificationRules"
    ] = Field(alias="notificationRules")
    config: "ChannelCreationChannelSlackChannelConfig"


class ChannelCreationChannelSlackChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class ChannelCreationChannelSlackChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class ChannelCreationChannelWebhookChannel(BaseModel):
    typename__: Literal["WebhookChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "ChannelCreationChannelWebhookChannelNotificationRules"
    ] = Field(alias="notificationRules")
    config: "ChannelCreationChannelWebhookChannelConfig"


class ChannelCreationChannelWebhookChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class ChannelCreationChannelWebhookChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")


class ChannelDeletion(BaseModel):
    errors: List["ChannelDeletionErrors"]
    channel: Optional["ChannelDeletionChannel"]


class ChannelDeletionErrors(BaseModel):
    code: ApiErrorCode
    message: str


class ChannelDeletionChannel(BaseModel):
    typename__: Literal[
        "Channel", "MsTeamsChannel", "SlackChannel", "WebhookChannel"
    ] = Field(alias="__typename")
    id: Any
    name: str


class ChannelUpdate(BaseModel):
    errors: List["ChannelUpdateErrors"]
    channel: Optional[
        Annotated[
            Union[
                "ChannelUpdateChannelChannel",
                "ChannelUpdateChannelMsTeamsChannel",
                "ChannelUpdateChannelSlackChannel",
                "ChannelUpdateChannelWebhookChannel",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class ChannelUpdateErrors(BaseModel):
    code: ApiErrorCode
    message: str


class ChannelUpdateChannelChannel(BaseModel):
    typename__: Literal["Channel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List["ChannelUpdateChannelChannelNotificationRules"] = Field(
        alias="notificationRules"
    )


class ChannelUpdateChannelChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class ChannelUpdateChannelMsTeamsChannel(BaseModel):
    typename__: Literal["MsTeamsChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "ChannelUpdateChannelMsTeamsChannelNotificationRules"
    ] = Field(alias="notificationRules")
    config: "ChannelUpdateChannelMsTeamsChannelConfig"


class ChannelUpdateChannelMsTeamsChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class ChannelUpdateChannelMsTeamsChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class ChannelUpdateChannelSlackChannel(BaseModel):
    typename__: Literal["SlackChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "ChannelUpdateChannelSlackChannelNotificationRules"
    ] = Field(alias="notificationRules")
    config: "ChannelUpdateChannelSlackChannelConfig"


class ChannelUpdateChannelSlackChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class ChannelUpdateChannelSlackChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class ChannelUpdateChannelWebhookChannel(BaseModel):
    typename__: Literal["WebhookChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "ChannelUpdateChannelWebhookChannelNotificationRules"
    ] = Field(alias="notificationRules")
    config: "ChannelUpdateChannelWebhookChannelConfig"


class ChannelUpdateChannelWebhookChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class ChannelUpdateChannelWebhookChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")


class CredentialBase(BaseModel):
    id: CredentialId
    typename__: str = Field(alias="__typename")
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class CredentialCreation(BaseModel):
    typename__: str = Field(alias="__typename")
    errors: List["CredentialCreationErrors"]
    credential: Optional[
        Annotated[
            Union[
                "CredentialCreationCredentialCredential",
                "CredentialCreationCredentialAwsAthenaCredential",
                "CredentialCreationCredentialAwsCredential",
                "CredentialCreationCredentialAwsRedshiftCredential",
                "CredentialCreationCredentialAzureSynapseEntraIdCredential",
                "CredentialCreationCredentialAzureSynapseSqlCredential",
                "CredentialCreationCredentialDatabricksCredential",
                "CredentialCreationCredentialDbtCloudCredential",
                "CredentialCreationCredentialDbtCoreCredential",
                "CredentialCreationCredentialKafkaSaslSslPlainCredential",
                "CredentialCreationCredentialKafkaSslCredential",
                "CredentialCreationCredentialLookerCredential",
                "CredentialCreationCredentialPostgreSqlCredential",
                "CredentialCreationCredentialSnowflakeCredential",
                "CredentialCreationCredentialTableauConnectedAppCredential",
                "CredentialCreationCredentialTableauPersonalAccessTokenCredential",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class CredentialCreationErrors(ErrorDetails):
    pass


class CredentialCreationCredentialCredential(BaseModel):
    typename__: Literal["Credential", "DemoCredential", "GcpCredential"] = Field(
        alias="__typename"
    )
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class CredentialCreationCredentialAwsAthenaCredential(BaseModel):
    typename__: Literal["AwsAthenaCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialAwsAthenaCredentialConfig"


class CredentialCreationCredentialAwsAthenaCredentialConfig(BaseModel):
    access_key: str = Field(alias="accessKey")
    region: str
    query_result_location: str = Field(alias="queryResultLocation")


class CredentialCreationCredentialAwsCredential(BaseModel):
    typename__: Literal["AwsCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialAwsCredentialConfig"


class CredentialCreationCredentialAwsCredentialConfig(BaseModel):
    access_key: str = Field(alias="accessKey")


class CredentialCreationCredentialAwsRedshiftCredential(BaseModel):
    typename__: Literal["AwsRedshiftCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialAwsRedshiftCredentialConfig"


class CredentialCreationCredentialAwsRedshiftCredentialConfig(BaseModel):
    host: str
    port: int
    user: str
    default_database: str = Field(alias="defaultDatabase")


class CredentialCreationCredentialAzureSynapseEntraIdCredential(BaseModel):
    typename__: Literal["AzureSynapseEntraIdCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialAzureSynapseEntraIdCredentialConfig"


class CredentialCreationCredentialAzureSynapseEntraIdCredentialConfig(BaseModel):
    client_id: str = Field(alias="clientId")
    host: str
    port: int
    database: Optional[str]


class CredentialCreationCredentialAzureSynapseSqlCredential(BaseModel):
    typename__: Literal["AzureSynapseSqlCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialAzureSynapseSqlCredentialConfig"


class CredentialCreationCredentialAzureSynapseSqlCredentialConfig(BaseModel):
    username: str
    host: str
    port: int
    database: Optional[str]


class CredentialCreationCredentialDatabricksCredential(BaseModel):
    typename__: Literal["DatabricksCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialDatabricksCredentialConfig"


class CredentialCreationCredentialDatabricksCredentialConfig(BaseModel):
    host: str
    port: int
    http_path: str = Field(alias="httpPath")


class CredentialCreationCredentialDbtCloudCredential(BaseModel):
    typename__: Literal["DbtCloudCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialDbtCloudCredentialConfig"


class CredentialCreationCredentialDbtCloudCredentialConfig(BaseModel):
    warehouse_credential: "CredentialCreationCredentialDbtCloudCredentialConfigWarehouseCredential" = Field(
        alias="warehouseCredential"
    )
    account_id: str = Field(alias="accountId")
    api_base_url: Optional[str] = Field(alias="apiBaseUrl")


class CredentialCreationCredentialDbtCloudCredentialConfigWarehouseCredential(
    CredentialBase
):
    pass


class CredentialCreationCredentialDbtCoreCredential(BaseModel):
    typename__: Literal["DbtCoreCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialDbtCoreCredentialConfig"


class CredentialCreationCredentialDbtCoreCredentialConfig(BaseModel):
    warehouse_credential: "CredentialCreationCredentialDbtCoreCredentialConfigWarehouseCredential" = Field(
        alias="warehouseCredential"
    )


class CredentialCreationCredentialDbtCoreCredentialConfigWarehouseCredential(
    CredentialBase
):
    pass


class CredentialCreationCredentialKafkaSaslSslPlainCredential(BaseModel):
    typename__: Literal["KafkaSaslSslPlainCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialKafkaSaslSslPlainCredentialConfig"


class CredentialCreationCredentialKafkaSaslSslPlainCredentialConfig(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    username: str


class CredentialCreationCredentialKafkaSslCredential(BaseModel):
    typename__: Literal["KafkaSslCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialKafkaSslCredentialConfig"


class CredentialCreationCredentialKafkaSslCredentialConfig(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    ca_certificate: str = Field(alias="caCertificate")


class CredentialCreationCredentialLookerCredential(BaseModel):
    typename__: Literal["LookerCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialLookerCredentialConfig"


class CredentialCreationCredentialLookerCredentialConfig(BaseModel):
    base_url: str = Field(alias="baseUrl")
    client_id: str = Field(alias="clientId")


class CredentialCreationCredentialPostgreSqlCredential(BaseModel):
    typename__: Literal["PostgreSqlCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialPostgreSqlCredentialConfig"


class CredentialCreationCredentialPostgreSqlCredentialConfig(BaseModel):
    host: str
    port: int
    user: str
    default_database: str = Field(alias="defaultDatabase")


class CredentialCreationCredentialSnowflakeCredential(BaseModel):
    typename__: Literal["SnowflakeCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialSnowflakeCredentialConfig"


class CredentialCreationCredentialSnowflakeCredentialConfig(BaseModel):
    account: str
    user: str
    role: Optional[str]
    warehouse: Optional[str]


class CredentialCreationCredentialTableauConnectedAppCredential(BaseModel):
    typename__: Literal["TableauConnectedAppCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialTableauConnectedAppCredentialConfig"


class CredentialCreationCredentialTableauConnectedAppCredentialConfig(BaseModel):
    host: str
    site: str
    user: str
    client_id: str = Field(alias="clientId")
    secret_id: str = Field(alias="secretId")


class CredentialCreationCredentialTableauPersonalAccessTokenCredential(BaseModel):
    typename__: Literal["TableauPersonalAccessTokenCredential"] = Field(
        alias="__typename"
    )
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialCreationCredentialTableauPersonalAccessTokenCredentialConfig"


class CredentialCreationCredentialTableauPersonalAccessTokenCredentialConfig(BaseModel):
    host: str
    site: str
    token_name: str = Field(alias="tokenName")


class CredentialSecretChanged(BaseModel):
    errors: List["CredentialSecretChangedErrors"]
    has_changed: Optional[bool] = Field(alias="hasChanged")


class CredentialSecretChangedErrors(ErrorDetails):
    pass


class CredentialUpdate(BaseModel):
    errors: List["CredentialUpdateErrors"]
    credential: Optional[
        Annotated[
            Union[
                "CredentialUpdateCredentialCredential",
                "CredentialUpdateCredentialAwsAthenaCredential",
                "CredentialUpdateCredentialAwsCredential",
                "CredentialUpdateCredentialAwsRedshiftCredential",
                "CredentialUpdateCredentialAzureSynapseEntraIdCredential",
                "CredentialUpdateCredentialAzureSynapseSqlCredential",
                "CredentialUpdateCredentialDatabricksCredential",
                "CredentialUpdateCredentialDbtCloudCredential",
                "CredentialUpdateCredentialDbtCoreCredential",
                "CredentialUpdateCredentialKafkaSaslSslPlainCredential",
                "CredentialUpdateCredentialKafkaSslCredential",
                "CredentialUpdateCredentialLookerCredential",
                "CredentialUpdateCredentialPostgreSqlCredential",
                "CredentialUpdateCredentialSnowflakeCredential",
                "CredentialUpdateCredentialTableauConnectedAppCredential",
                "CredentialUpdateCredentialTableauPersonalAccessTokenCredential",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class CredentialUpdateErrors(ErrorDetails):
    pass


class CredentialUpdateCredentialCredential(BaseModel):
    typename__: Literal["Credential", "DemoCredential", "GcpCredential"] = Field(
        alias="__typename"
    )
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class CredentialUpdateCredentialAwsAthenaCredential(BaseModel):
    typename__: Literal["AwsAthenaCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialAwsAthenaCredentialConfig"


class CredentialUpdateCredentialAwsAthenaCredentialConfig(BaseModel):
    access_key: str = Field(alias="accessKey")
    region: str
    query_result_location: str = Field(alias="queryResultLocation")


class CredentialUpdateCredentialAwsCredential(BaseModel):
    typename__: Literal["AwsCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialAwsCredentialConfig"


class CredentialUpdateCredentialAwsCredentialConfig(BaseModel):
    access_key: str = Field(alias="accessKey")


class CredentialUpdateCredentialAwsRedshiftCredential(BaseModel):
    typename__: Literal["AwsRedshiftCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialAwsRedshiftCredentialConfig"


class CredentialUpdateCredentialAwsRedshiftCredentialConfig(BaseModel):
    host: str
    port: int
    user: str
    default_database: str = Field(alias="defaultDatabase")


class CredentialUpdateCredentialAzureSynapseEntraIdCredential(BaseModel):
    typename__: Literal["AzureSynapseEntraIdCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialAzureSynapseEntraIdCredentialConfig"


class CredentialUpdateCredentialAzureSynapseEntraIdCredentialConfig(BaseModel):
    client_id: str = Field(alias="clientId")
    host: str
    port: int
    database: Optional[str]


class CredentialUpdateCredentialAzureSynapseSqlCredential(BaseModel):
    typename__: Literal["AzureSynapseSqlCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialAzureSynapseSqlCredentialConfig"


class CredentialUpdateCredentialAzureSynapseSqlCredentialConfig(BaseModel):
    username: str
    host: str
    port: int
    database: Optional[str]


class CredentialUpdateCredentialDatabricksCredential(BaseModel):
    typename__: Literal["DatabricksCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialDatabricksCredentialConfig"


class CredentialUpdateCredentialDatabricksCredentialConfig(BaseModel):
    host: str
    port: int
    http_path: str = Field(alias="httpPath")


class CredentialUpdateCredentialDbtCloudCredential(BaseModel):
    typename__: Literal["DbtCloudCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialDbtCloudCredentialConfig"


class CredentialUpdateCredentialDbtCloudCredentialConfig(BaseModel):
    warehouse_credential: "CredentialUpdateCredentialDbtCloudCredentialConfigWarehouseCredential" = Field(
        alias="warehouseCredential"
    )
    account_id: str = Field(alias="accountId")
    api_base_url: Optional[str] = Field(alias="apiBaseUrl")


class CredentialUpdateCredentialDbtCloudCredentialConfigWarehouseCredential(
    CredentialBase
):
    pass


class CredentialUpdateCredentialDbtCoreCredential(BaseModel):
    typename__: Literal["DbtCoreCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialDbtCoreCredentialConfig"


class CredentialUpdateCredentialDbtCoreCredentialConfig(BaseModel):
    warehouse_credential: "CredentialUpdateCredentialDbtCoreCredentialConfigWarehouseCredential" = Field(
        alias="warehouseCredential"
    )


class CredentialUpdateCredentialDbtCoreCredentialConfigWarehouseCredential(
    CredentialBase
):
    pass


class CredentialUpdateCredentialKafkaSaslSslPlainCredential(BaseModel):
    typename__: Literal["KafkaSaslSslPlainCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialKafkaSaslSslPlainCredentialConfig"


class CredentialUpdateCredentialKafkaSaslSslPlainCredentialConfig(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    username: str


class CredentialUpdateCredentialKafkaSslCredential(BaseModel):
    typename__: Literal["KafkaSslCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialKafkaSslCredentialConfig"


class CredentialUpdateCredentialKafkaSslCredentialConfig(BaseModel):
    bootstrap_servers: List[str] = Field(alias="bootstrapServers")
    ca_certificate: str = Field(alias="caCertificate")


class CredentialUpdateCredentialLookerCredential(BaseModel):
    typename__: Literal["LookerCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialLookerCredentialConfig"


class CredentialUpdateCredentialLookerCredentialConfig(BaseModel):
    base_url: str = Field(alias="baseUrl")
    client_id: str = Field(alias="clientId")


class CredentialUpdateCredentialPostgreSqlCredential(BaseModel):
    typename__: Literal["PostgreSqlCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialPostgreSqlCredentialConfig"


class CredentialUpdateCredentialPostgreSqlCredentialConfig(BaseModel):
    host: str
    port: int
    user: str
    default_database: str = Field(alias="defaultDatabase")


class CredentialUpdateCredentialSnowflakeCredential(BaseModel):
    typename__: Literal["SnowflakeCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialSnowflakeCredentialConfig"


class CredentialUpdateCredentialSnowflakeCredentialConfig(BaseModel):
    account: str
    user: str
    role: Optional[str]
    warehouse: Optional[str]


class CredentialUpdateCredentialTableauConnectedAppCredential(BaseModel):
    typename__: Literal["TableauConnectedAppCredential"] = Field(alias="__typename")
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialTableauConnectedAppCredentialConfig"


class CredentialUpdateCredentialTableauConnectedAppCredentialConfig(BaseModel):
    host: str
    site: str
    user: str
    client_id: str = Field(alias="clientId")
    secret_id: str = Field(alias="secretId")


class CredentialUpdateCredentialTableauPersonalAccessTokenCredential(BaseModel):
    typename__: Literal["TableauPersonalAccessTokenCredential"] = Field(
        alias="__typename"
    )
    id: CredentialId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "CredentialUpdateCredentialTableauPersonalAccessTokenCredentialConfig"


class CredentialUpdateCredentialTableauPersonalAccessTokenCredentialConfig(BaseModel):
    host: str
    site: str
    token_name: str = Field(alias="tokenName")


class IdentityDeletion(BaseModel):
    errors: List["IdentityDeletionErrors"]


class IdentityDeletionErrors(BaseModel):
    code: IdentityDeleteErrorCode
    message: str


class IdentityProviderCreation(BaseModel):
    errors: List["IdentityProviderCreationErrors"]
    identity_provider: Optional[
        Annotated[
            Union[
                "IdentityProviderCreationIdentityProviderIdentityProvider",
                "IdentityProviderCreationIdentityProviderSamlIdentityProvider",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="identityProvider")


class IdentityProviderCreationErrors(BaseModel):
    code: IdentityProviderCreateErrorCode
    message: Optional[str]


class IdentityProviderCreationIdentityProviderIdentityProvider(BaseModel):
    typename__: Literal["IdentityProvider", "LocalIdentityProvider"] = Field(
        alias="__typename"
    )
    id: str
    name: str
    disabled: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class IdentityProviderCreationIdentityProviderSamlIdentityProvider(BaseModel):
    typename__: Literal["SamlIdentityProvider"] = Field(alias="__typename")
    id: str
    name: str
    disabled: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "IdentityProviderCreationIdentityProviderSamlIdentityProviderConfig"


class IdentityProviderCreationIdentityProviderSamlIdentityProviderConfig(BaseModel):
    entry_point: str = Field(alias="entryPoint")
    entity_id: str = Field(alias="entityId")
    cert: str


class IdentityProviderDeletion(BaseModel):
    errors: List["IdentityProviderDeletionErrors"]


class IdentityProviderDeletionErrors(BaseModel):
    code: IdentityProviderDeleteErrorCode
    message: Optional[str]


class IdentityProviderUpdate(BaseModel):
    errors: List["IdentityProviderUpdateErrors"]
    identity_provider: Optional[
        Annotated[
            Union[
                "IdentityProviderUpdateIdentityProviderIdentityProvider",
                "IdentityProviderUpdateIdentityProviderSamlIdentityProvider",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="identityProvider")


class IdentityProviderUpdateErrors(BaseModel):
    code: IdentityProviderUpdateErrorCode
    message: Optional[str]


class IdentityProviderUpdateIdentityProviderIdentityProvider(BaseModel):
    typename__: Literal["IdentityProvider", "LocalIdentityProvider"] = Field(
        alias="__typename"
    )
    id: str
    name: str
    disabled: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class IdentityProviderUpdateIdentityProviderSamlIdentityProvider(BaseModel):
    typename__: Literal["SamlIdentityProvider"] = Field(alias="__typename")
    id: str
    name: str
    disabled: bool
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "IdentityProviderUpdateIdentityProviderSamlIdentityProviderConfig"


class IdentityProviderUpdateIdentityProviderSamlIdentityProviderConfig(BaseModel):
    entry_point: str = Field(alias="entryPoint")
    entity_id: str = Field(alias="entityId")
    cert: str


class NamespaceUpdate(BaseModel):
    errors: List["NamespaceUpdateErrors"]
    resource_name: Optional[str] = Field(alias="resourceName")
    resource_namespace: Optional[str] = Field(alias="resourceNamespace")


class NamespaceUpdateErrors(ErrorDetails):
    pass


class NotificationRuleConditionCreation(BaseModel):
    errors: List["NotificationRuleConditionCreationErrors"]


class NotificationRuleConditionCreationErrors(BaseModel):
    code: ApiErrorCode
    message: str


class NotificationRuleDetails(BaseModel):
    typename__: str = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    conditions: List[
        Annotated[
            Union[
                "NotificationRuleDetailsConditionsNotificationRuleCondition",
                "NotificationRuleDetailsConditionsOwnerNotificationRuleCondition",
                "NotificationRuleDetailsConditionsSegmentNotificationRuleCondition",
                "NotificationRuleDetailsConditionsSeverityNotificationRuleCondition",
                "NotificationRuleDetailsConditionsSourceNotificationRuleCondition",
                "NotificationRuleDetailsConditionsTagNotificationRuleCondition",
                "NotificationRuleDetailsConditionsTypeNotificationRuleCondition",
            ],
            Field(discriminator="typename__"),
        ]
    ]
    channel: Union[
        "NotificationRuleDetailsChannelChannel",
        "NotificationRuleDetailsChannelMsTeamsChannel",
        "NotificationRuleDetailsChannelSlackChannel",
        "NotificationRuleDetailsChannelWebhookChannel",
    ] = Field(discriminator="typename__")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class NotificationRuleDetailsConditionsNotificationRuleCondition(BaseModel):
    typename__: Literal["NotificationRuleCondition"] = Field(alias="__typename")
    id: str
    notification_rule_id: Any = Field(alias="notificationRuleId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class NotificationRuleDetailsConditionsOwnerNotificationRuleCondition(BaseModel):
    typename__: Literal["OwnerNotificationRuleCondition"] = Field(alias="__typename")
    id: str
    notification_rule_id: Any = Field(alias="notificationRuleId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    config: "NotificationRuleDetailsConditionsOwnerNotificationRuleConditionConfig"


class NotificationRuleDetailsConditionsOwnerNotificationRuleConditionConfig(BaseModel):
    owners: List[
        "NotificationRuleDetailsConditionsOwnerNotificationRuleConditionConfigOwners"
    ]


class NotificationRuleDetailsConditionsOwnerNotificationRuleConditionConfigOwners(
    BaseModel
):
    id: str
    display_name: str = Field(alias="displayName")


class NotificationRuleDetailsConditionsSegmentNotificationRuleCondition(BaseModel):
    typename__: Literal["SegmentNotificationRuleCondition"] = Field(alias="__typename")
    id: str
    notification_rule_id: Any = Field(alias="notificationRuleId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    config: "NotificationRuleDetailsConditionsSegmentNotificationRuleConditionConfig"


class NotificationRuleDetailsConditionsSegmentNotificationRuleConditionConfig(
    BaseModel
):
    segments: List[
        "NotificationRuleDetailsConditionsSegmentNotificationRuleConditionConfigSegments"
    ]


class NotificationRuleDetailsConditionsSegmentNotificationRuleConditionConfigSegments(
    BaseModel
):
    field: JsonPointer
    value: str


class NotificationRuleDetailsConditionsSeverityNotificationRuleCondition(BaseModel):
    typename__: Literal["SeverityNotificationRuleCondition"] = Field(alias="__typename")
    id: str
    notification_rule_id: Any = Field(alias="notificationRuleId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    config: "NotificationRuleDetailsConditionsSeverityNotificationRuleConditionConfig"


class NotificationRuleDetailsConditionsSeverityNotificationRuleConditionConfig(
    BaseModel
):
    severities: List[IncidentSeverity]


class NotificationRuleDetailsConditionsSourceNotificationRuleCondition(BaseModel):
    typename__: Literal["SourceNotificationRuleCondition"] = Field(alias="__typename")
    id: str
    notification_rule_id: Any = Field(alias="notificationRuleId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    config: "NotificationRuleDetailsConditionsSourceNotificationRuleConditionConfig"


class NotificationRuleDetailsConditionsSourceNotificationRuleConditionConfig(BaseModel):
    sources: List[
        Optional[
            "NotificationRuleDetailsConditionsSourceNotificationRuleConditionConfigSources"
        ]
    ]


class NotificationRuleDetailsConditionsSourceNotificationRuleConditionConfigSources(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str


class NotificationRuleDetailsConditionsTagNotificationRuleCondition(BaseModel):
    typename__: Literal["TagNotificationRuleCondition"] = Field(alias="__typename")
    id: str
    notification_rule_id: Any = Field(alias="notificationRuleId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    config: "NotificationRuleDetailsConditionsTagNotificationRuleConditionConfig"


class NotificationRuleDetailsConditionsTagNotificationRuleConditionConfig(BaseModel):
    tags: List[
        "NotificationRuleDetailsConditionsTagNotificationRuleConditionConfigTags"
    ]


class NotificationRuleDetailsConditionsTagNotificationRuleConditionConfigTags(
    BaseModel
):
    id: Any
    key: str
    value: str


class NotificationRuleDetailsConditionsTypeNotificationRuleCondition(BaseModel):
    typename__: Literal["TypeNotificationRuleCondition"] = Field(alias="__typename")
    id: str
    notification_rule_id: Any = Field(alias="notificationRuleId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    config: "NotificationRuleDetailsConditionsTypeNotificationRuleConditionConfig"


class NotificationRuleDetailsConditionsTypeNotificationRuleConditionConfig(BaseModel):
    types: List[IssueTypename]


class NotificationRuleDetailsChannelChannel(BaseModel):
    typename__: Literal["Channel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "NotificationRuleDetailsChannelChannelNotificationRules"
    ] = Field(alias="notificationRules")


class NotificationRuleDetailsChannelChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class NotificationRuleDetailsChannelMsTeamsChannel(BaseModel):
    typename__: Literal["MsTeamsChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "NotificationRuleDetailsChannelMsTeamsChannelNotificationRules"
    ] = Field(alias="notificationRules")
    config: "NotificationRuleDetailsChannelMsTeamsChannelConfig"


class NotificationRuleDetailsChannelMsTeamsChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class NotificationRuleDetailsChannelMsTeamsChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class NotificationRuleDetailsChannelSlackChannel(BaseModel):
    typename__: Literal["SlackChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "NotificationRuleDetailsChannelSlackChannelNotificationRules"
    ] = Field(alias="notificationRules")
    config: "NotificationRuleDetailsChannelSlackChannelConfig"


class NotificationRuleDetailsChannelSlackChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class NotificationRuleDetailsChannelSlackChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    timezone: Optional[str]
    application_link_url: str = Field(alias="applicationLinkUrl")


class NotificationRuleDetailsChannelWebhookChannel(BaseModel):
    typename__: Literal["WebhookChannel"] = Field(alias="__typename")
    id: Any
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    notification_rules: List[
        "NotificationRuleDetailsChannelWebhookChannelNotificationRules"
    ] = Field(alias="notificationRules")
    config: "NotificationRuleDetailsChannelWebhookChannelConfig"


class NotificationRuleDetailsChannelWebhookChannelNotificationRules(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class NotificationRuleDetailsChannelWebhookChannelConfig(BaseModel):
    webhook_url: str = Field(alias="webhookUrl")
    application_link_url: str = Field(alias="applicationLinkUrl")
    auth_header: Optional[str] = Field(alias="authHeader")


class NotificationRuleCreation(BaseModel):
    errors: List["NotificationRuleCreationErrors"]
    notification_rule: Optional["NotificationRuleCreationNotificationRule"] = Field(
        alias="notificationRule"
    )


class NotificationRuleCreationErrors(BaseModel):
    code: ApiErrorCode
    message: str


class NotificationRuleCreationNotificationRule(NotificationRuleDetails):
    pass


class NotificationRuleDeletion(BaseModel):
    errors: List["NotificationRuleDeletionErrors"]
    notification_rule: Optional["NotificationRuleDeletionNotificationRule"] = Field(
        alias="notificationRule"
    )


class NotificationRuleDeletionErrors(BaseModel):
    code: ApiErrorCode
    message: str


class NotificationRuleDeletionNotificationRule(BaseModel):
    typename__: Literal["NotificationRule"] = Field(alias="__typename")
    id: Any
    name: str


class NotificationRuleUpdate(BaseModel):
    errors: List["NotificationRuleUpdateErrors"]
    notification_rule: Optional["NotificationRuleUpdateNotificationRule"] = Field(
        alias="notificationRule"
    )


class NotificationRuleUpdateErrors(BaseModel):
    code: ApiErrorCode
    message: str


class NotificationRuleUpdateNotificationRule(NotificationRuleDetails):
    pass


class ReferenceSourceConfigDetails(BaseModel):
    source: "ReferenceSourceConfigDetailsSource"
    window: "ReferenceSourceConfigDetailsWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ReferenceSourceConfigDetailsSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ReferenceSourceConfigDetailsWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SegmentDetails(BaseModel):
    typename__: str = Field(alias="__typename")
    id: Any
    fields: List["SegmentDetailsFields"]
    muted: bool
    data_quality: Optional["SegmentDetailsDataQuality"] = Field(alias="dataQuality")


class SegmentDetailsFields(BaseModel):
    field: JsonPointer
    value: str


class SegmentDetailsDataQuality(BaseModel):
    incident_count: int = Field(alias="incidentCount")
    total_count: int = Field(alias="totalCount")
    quality: float
    quality_diff: float = Field(alias="qualityDiff")


class SegmentationDetails(BaseModel):
    typename__: str = Field(alias="__typename")
    id: SegmentationId
    name: str
    source: "SegmentationDetailsSource"
    fields: List[str]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SegmentationDetailsSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SegmentationCreation(BaseModel):
    errors: List["SegmentationCreationErrors"]
    segmentation: Optional["SegmentationCreationSegmentation"]


class SegmentationCreationErrors(ErrorDetails):
    pass


class SegmentationCreationSegmentation(SegmentationDetails):
    pass


class SegmentationSummary(BaseModel):
    typename__: str = Field(alias="__typename")
    id: SegmentationId
    name: str
    fields: List[str]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class SourceBase(BaseModel):
    id: SourceId
    typename__: str = Field(alias="__typename")
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class TagDetails(BaseModel):
    id: Any
    key: str
    value: str
    is_imported: bool = Field(alias="isImported")
    is_system_tag: bool = Field(alias="isSystemTag")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class SourceCreation(BaseModel):
    errors: List["SourceCreationErrors"]
    source: Optional[
        Annotated[
            Union[
                "SourceCreationSourceSource",
                "SourceCreationSourceAwsAthenaSource",
                "SourceCreationSourceAwsKinesisSource",
                "SourceCreationSourceAwsRedshiftSource",
                "SourceCreationSourceAwsS3Source",
                "SourceCreationSourceAzureSynapseSource",
                "SourceCreationSourceDatabricksSource",
                "SourceCreationSourceDbtModelRunSource",
                "SourceCreationSourceDbtTestResultSource",
                "SourceCreationSourceGcpBigQuerySource",
                "SourceCreationSourceGcpPubSubLiteSource",
                "SourceCreationSourceGcpPubSubSource",
                "SourceCreationSourceGcpStorageSource",
                "SourceCreationSourceKafkaSource",
                "SourceCreationSourcePostgreSqlSource",
                "SourceCreationSourceSnowflakeSource",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class SourceCreationErrors(ErrorDetails):
    pass


class SourceCreationSourceSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceSourceCredential"
    windows: List["SourceCreationSourceSourceWindows"]
    segmentations: List["SourceCreationSourceSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceSourceTags"]


class SourceCreationSourceSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSourceTags(TagDetails):
    pass


class SourceCreationSourceAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceAwsAthenaSourceCredential"
    windows: List["SourceCreationSourceAwsAthenaSourceWindows"]
    segmentations: List["SourceCreationSourceAwsAthenaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceAwsAthenaSourceTags"]
    config: "SourceCreationSourceAwsAthenaSourceConfig"


class SourceCreationSourceAwsAthenaSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsAthenaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsAthenaSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsAthenaSourceTags(TagDetails):
    pass


class SourceCreationSourceAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceCreationSourceAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceAwsKinesisSourceCredential"
    windows: List["SourceCreationSourceAwsKinesisSourceWindows"]
    segmentations: List["SourceCreationSourceAwsKinesisSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceAwsKinesisSourceTags"]
    config: "SourceCreationSourceAwsKinesisSourceConfig"


class SourceCreationSourceAwsKinesisSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsKinesisSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsKinesisSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsKinesisSourceTags(TagDetails):
    pass


class SourceCreationSourceAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")
    message_format: Optional[
        "SourceCreationSourceAwsKinesisSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class SourceCreationSourceAwsKinesisSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class SourceCreationSourceAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceAwsRedshiftSourceCredential"
    windows: List["SourceCreationSourceAwsRedshiftSourceWindows"]
    segmentations: List["SourceCreationSourceAwsRedshiftSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceAwsRedshiftSourceTags"]
    config: "SourceCreationSourceAwsRedshiftSourceConfig"


class SourceCreationSourceAwsRedshiftSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsRedshiftSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsRedshiftSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsRedshiftSourceTags(TagDetails):
    pass


class SourceCreationSourceAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceCreationSourceAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceAwsS3SourceCredential"
    windows: List["SourceCreationSourceAwsS3SourceWindows"]
    segmentations: List["SourceCreationSourceAwsS3SourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceAwsS3SourceTags"]
    config: "SourceCreationSourceAwsS3SourceConfig"


class SourceCreationSourceAwsS3SourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsS3SourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsS3SourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAwsS3SourceTags(TagDetails):
    pass


class SourceCreationSourceAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["SourceCreationSourceAwsS3SourceConfigCsv"]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class SourceCreationSourceAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class SourceCreationSourceAzureSynapseSource(BaseModel):
    typename__: Literal["AzureSynapseSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceAzureSynapseSourceCredential"
    windows: List["SourceCreationSourceAzureSynapseSourceWindows"]
    segmentations: List["SourceCreationSourceAzureSynapseSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceAzureSynapseSourceTags"]
    config: "SourceCreationSourceAzureSynapseSourceConfig"


class SourceCreationSourceAzureSynapseSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAzureSynapseSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAzureSynapseSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceAzureSynapseSourceTags(TagDetails):
    pass


class SourceCreationSourceAzureSynapseSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceCreationSourceDatabricksSource(BaseModel):
    typename__: Literal["DatabricksSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceDatabricksSourceCredential"
    windows: List["SourceCreationSourceDatabricksSourceWindows"]
    segmentations: List["SourceCreationSourceDatabricksSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceDatabricksSourceTags"]
    config: "SourceCreationSourceDatabricksSourceConfig"


class SourceCreationSourceDatabricksSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceDatabricksSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceDatabricksSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceDatabricksSourceTags(TagDetails):
    pass


class SourceCreationSourceDatabricksSourceConfig(BaseModel):
    catalog: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceCreationSourceDbtModelRunSource(BaseModel):
    typename__: Literal["DbtModelRunSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceDbtModelRunSourceCredential"
    windows: List["SourceCreationSourceDbtModelRunSourceWindows"]
    segmentations: List["SourceCreationSourceDbtModelRunSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceDbtModelRunSourceTags"]
    config: "SourceCreationSourceDbtModelRunSourceConfig"


class SourceCreationSourceDbtModelRunSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceDbtModelRunSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceDbtModelRunSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceDbtModelRunSourceTags(TagDetails):
    pass


class SourceCreationSourceDbtModelRunSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class SourceCreationSourceDbtTestResultSource(BaseModel):
    typename__: Literal["DbtTestResultSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceDbtTestResultSourceCredential"
    windows: List["SourceCreationSourceDbtTestResultSourceWindows"]
    segmentations: List["SourceCreationSourceDbtTestResultSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceDbtTestResultSourceTags"]
    config: "SourceCreationSourceDbtTestResultSourceConfig"


class SourceCreationSourceDbtTestResultSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceDbtTestResultSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceDbtTestResultSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceDbtTestResultSourceTags(TagDetails):
    pass


class SourceCreationSourceDbtTestResultSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class SourceCreationSourceGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceGcpBigQuerySourceCredential"
    windows: List["SourceCreationSourceGcpBigQuerySourceWindows"]
    segmentations: List["SourceCreationSourceGcpBigQuerySourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceGcpBigQuerySourceTags"]
    config: "SourceCreationSourceGcpBigQuerySourceConfig"


class SourceCreationSourceGcpBigQuerySourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpBigQuerySourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpBigQuerySourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpBigQuerySourceTags(TagDetails):
    pass


class SourceCreationSourceGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceCreationSourceGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceGcpPubSubLiteSourceCredential"
    windows: List["SourceCreationSourceGcpPubSubLiteSourceWindows"]
    segmentations: List["SourceCreationSourceGcpPubSubLiteSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceGcpPubSubLiteSourceTags"]
    config: "SourceCreationSourceGcpPubSubLiteSourceConfig"


class SourceCreationSourceGcpPubSubLiteSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubLiteSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubLiteSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubLiteSourceTags(TagDetails):
    pass


class SourceCreationSourceGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "SourceCreationSourceGcpPubSubLiteSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class SourceCreationSourceGcpPubSubLiteSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class SourceCreationSourceGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceGcpPubSubSourceCredential"
    windows: List["SourceCreationSourceGcpPubSubSourceWindows"]
    segmentations: List["SourceCreationSourceGcpPubSubSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceGcpPubSubSourceTags"]
    config: "SourceCreationSourceGcpPubSubSourceConfig"


class SourceCreationSourceGcpPubSubSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpPubSubSourceTags(TagDetails):
    pass


class SourceCreationSourceGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "SourceCreationSourceGcpPubSubSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class SourceCreationSourceGcpPubSubSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class SourceCreationSourceGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceGcpStorageSourceCredential"
    windows: List["SourceCreationSourceGcpStorageSourceWindows"]
    segmentations: List["SourceCreationSourceGcpStorageSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceGcpStorageSourceTags"]
    config: "SourceCreationSourceGcpStorageSourceConfig"


class SourceCreationSourceGcpStorageSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpStorageSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpStorageSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceGcpStorageSourceTags(TagDetails):
    pass


class SourceCreationSourceGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional["SourceCreationSourceGcpStorageSourceConfigCsv"]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class SourceCreationSourceGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class SourceCreationSourceKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceKafkaSourceCredential"
    windows: List["SourceCreationSourceKafkaSourceWindows"]
    segmentations: List["SourceCreationSourceKafkaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceKafkaSourceTags"]
    config: "SourceCreationSourceKafkaSourceConfig"


class SourceCreationSourceKafkaSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceKafkaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceKafkaSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceKafkaSourceTags(TagDetails):
    pass


class SourceCreationSourceKafkaSourceConfig(BaseModel):
    topic: str
    message_format: Optional[
        "SourceCreationSourceKafkaSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class SourceCreationSourceKafkaSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class SourceCreationSourcePostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourcePostgreSqlSourceCredential"
    windows: List["SourceCreationSourcePostgreSqlSourceWindows"]
    segmentations: List["SourceCreationSourcePostgreSqlSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourcePostgreSqlSourceTags"]
    config: "SourceCreationSourcePostgreSqlSourceConfig"


class SourceCreationSourcePostgreSqlSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourcePostgreSqlSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourcePostgreSqlSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourcePostgreSqlSourceTags(TagDetails):
    pass


class SourceCreationSourcePostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceCreationSourceSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceCreationSourceSnowflakeSourceCredential"
    windows: List["SourceCreationSourceSnowflakeSourceWindows"]
    segmentations: List["SourceCreationSourceSnowflakeSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceCreationSourceSnowflakeSourceTags"]
    config: "SourceCreationSourceSnowflakeSourceConfig"


class SourceCreationSourceSnowflakeSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSnowflakeSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSnowflakeSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceCreationSourceSnowflakeSourceTags(TagDetails):
    pass


class SourceCreationSourceSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceUpdate(BaseModel):
    errors: List["SourceUpdateErrors"]
    source: Optional[
        Annotated[
            Union[
                "SourceUpdateSourceSource",
                "SourceUpdateSourceAwsAthenaSource",
                "SourceUpdateSourceAwsKinesisSource",
                "SourceUpdateSourceAwsRedshiftSource",
                "SourceUpdateSourceAwsS3Source",
                "SourceUpdateSourceAzureSynapseSource",
                "SourceUpdateSourceDatabricksSource",
                "SourceUpdateSourceDbtModelRunSource",
                "SourceUpdateSourceDbtTestResultSource",
                "SourceUpdateSourceGcpBigQuerySource",
                "SourceUpdateSourceGcpPubSubLiteSource",
                "SourceUpdateSourceGcpPubSubSource",
                "SourceUpdateSourceGcpStorageSource",
                "SourceUpdateSourceKafkaSource",
                "SourceUpdateSourcePostgreSqlSource",
                "SourceUpdateSourceSnowflakeSource",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class SourceUpdateErrors(ErrorDetails):
    pass


class SourceUpdateSourceSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceSourceCredential"
    windows: List["SourceUpdateSourceSourceWindows"]
    segmentations: List["SourceUpdateSourceSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceSourceTags"]


class SourceUpdateSourceSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSourceTags(TagDetails):
    pass


class SourceUpdateSourceAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceAwsAthenaSourceCredential"
    windows: List["SourceUpdateSourceAwsAthenaSourceWindows"]
    segmentations: List["SourceUpdateSourceAwsAthenaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceAwsAthenaSourceTags"]
    config: "SourceUpdateSourceAwsAthenaSourceConfig"


class SourceUpdateSourceAwsAthenaSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsAthenaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsAthenaSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsAthenaSourceTags(TagDetails):
    pass


class SourceUpdateSourceAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceUpdateSourceAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceAwsKinesisSourceCredential"
    windows: List["SourceUpdateSourceAwsKinesisSourceWindows"]
    segmentations: List["SourceUpdateSourceAwsKinesisSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceAwsKinesisSourceTags"]
    config: "SourceUpdateSourceAwsKinesisSourceConfig"


class SourceUpdateSourceAwsKinesisSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsKinesisSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsKinesisSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsKinesisSourceTags(TagDetails):
    pass


class SourceUpdateSourceAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")
    message_format: Optional[
        "SourceUpdateSourceAwsKinesisSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class SourceUpdateSourceAwsKinesisSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class SourceUpdateSourceAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceAwsRedshiftSourceCredential"
    windows: List["SourceUpdateSourceAwsRedshiftSourceWindows"]
    segmentations: List["SourceUpdateSourceAwsRedshiftSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceAwsRedshiftSourceTags"]
    config: "SourceUpdateSourceAwsRedshiftSourceConfig"


class SourceUpdateSourceAwsRedshiftSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsRedshiftSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsRedshiftSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsRedshiftSourceTags(TagDetails):
    pass


class SourceUpdateSourceAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceUpdateSourceAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceAwsS3SourceCredential"
    windows: List["SourceUpdateSourceAwsS3SourceWindows"]
    segmentations: List["SourceUpdateSourceAwsS3SourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceAwsS3SourceTags"]
    config: "SourceUpdateSourceAwsS3SourceConfig"


class SourceUpdateSourceAwsS3SourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsS3SourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsS3SourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAwsS3SourceTags(TagDetails):
    pass


class SourceUpdateSourceAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["SourceUpdateSourceAwsS3SourceConfigCsv"]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class SourceUpdateSourceAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class SourceUpdateSourceAzureSynapseSource(BaseModel):
    typename__: Literal["AzureSynapseSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceAzureSynapseSourceCredential"
    windows: List["SourceUpdateSourceAzureSynapseSourceWindows"]
    segmentations: List["SourceUpdateSourceAzureSynapseSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceAzureSynapseSourceTags"]
    config: "SourceUpdateSourceAzureSynapseSourceConfig"


class SourceUpdateSourceAzureSynapseSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAzureSynapseSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAzureSynapseSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceAzureSynapseSourceTags(TagDetails):
    pass


class SourceUpdateSourceAzureSynapseSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceUpdateSourceDatabricksSource(BaseModel):
    typename__: Literal["DatabricksSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceDatabricksSourceCredential"
    windows: List["SourceUpdateSourceDatabricksSourceWindows"]
    segmentations: List["SourceUpdateSourceDatabricksSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceDatabricksSourceTags"]
    config: "SourceUpdateSourceDatabricksSourceConfig"


class SourceUpdateSourceDatabricksSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceDatabricksSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceDatabricksSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceDatabricksSourceTags(TagDetails):
    pass


class SourceUpdateSourceDatabricksSourceConfig(BaseModel):
    catalog: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceUpdateSourceDbtModelRunSource(BaseModel):
    typename__: Literal["DbtModelRunSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceDbtModelRunSourceCredential"
    windows: List["SourceUpdateSourceDbtModelRunSourceWindows"]
    segmentations: List["SourceUpdateSourceDbtModelRunSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceDbtModelRunSourceTags"]
    config: "SourceUpdateSourceDbtModelRunSourceConfig"


class SourceUpdateSourceDbtModelRunSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceDbtModelRunSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceDbtModelRunSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceDbtModelRunSourceTags(TagDetails):
    pass


class SourceUpdateSourceDbtModelRunSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class SourceUpdateSourceDbtTestResultSource(BaseModel):
    typename__: Literal["DbtTestResultSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceDbtTestResultSourceCredential"
    windows: List["SourceUpdateSourceDbtTestResultSourceWindows"]
    segmentations: List["SourceUpdateSourceDbtTestResultSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceDbtTestResultSourceTags"]
    config: "SourceUpdateSourceDbtTestResultSourceConfig"


class SourceUpdateSourceDbtTestResultSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceDbtTestResultSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceDbtTestResultSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceDbtTestResultSourceTags(TagDetails):
    pass


class SourceUpdateSourceDbtTestResultSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class SourceUpdateSourceGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceGcpBigQuerySourceCredential"
    windows: List["SourceUpdateSourceGcpBigQuerySourceWindows"]
    segmentations: List["SourceUpdateSourceGcpBigQuerySourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceGcpBigQuerySourceTags"]
    config: "SourceUpdateSourceGcpBigQuerySourceConfig"


class SourceUpdateSourceGcpBigQuerySourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpBigQuerySourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpBigQuerySourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpBigQuerySourceTags(TagDetails):
    pass


class SourceUpdateSourceGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceUpdateSourceGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceGcpPubSubLiteSourceCredential"
    windows: List["SourceUpdateSourceGcpPubSubLiteSourceWindows"]
    segmentations: List["SourceUpdateSourceGcpPubSubLiteSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceGcpPubSubLiteSourceTags"]
    config: "SourceUpdateSourceGcpPubSubLiteSourceConfig"


class SourceUpdateSourceGcpPubSubLiteSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubLiteSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubLiteSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubLiteSourceTags(TagDetails):
    pass


class SourceUpdateSourceGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "SourceUpdateSourceGcpPubSubLiteSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class SourceUpdateSourceGcpPubSubLiteSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class SourceUpdateSourceGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceGcpPubSubSourceCredential"
    windows: List["SourceUpdateSourceGcpPubSubSourceWindows"]
    segmentations: List["SourceUpdateSourceGcpPubSubSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceGcpPubSubSourceTags"]
    config: "SourceUpdateSourceGcpPubSubSourceConfig"


class SourceUpdateSourceGcpPubSubSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpPubSubSourceTags(TagDetails):
    pass


class SourceUpdateSourceGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "SourceUpdateSourceGcpPubSubSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class SourceUpdateSourceGcpPubSubSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class SourceUpdateSourceGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceGcpStorageSourceCredential"
    windows: List["SourceUpdateSourceGcpStorageSourceWindows"]
    segmentations: List["SourceUpdateSourceGcpStorageSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceGcpStorageSourceTags"]
    config: "SourceUpdateSourceGcpStorageSourceConfig"


class SourceUpdateSourceGcpStorageSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpStorageSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpStorageSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceGcpStorageSourceTags(TagDetails):
    pass


class SourceUpdateSourceGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional["SourceUpdateSourceGcpStorageSourceConfigCsv"]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class SourceUpdateSourceGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class SourceUpdateSourceKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceKafkaSourceCredential"
    windows: List["SourceUpdateSourceKafkaSourceWindows"]
    segmentations: List["SourceUpdateSourceKafkaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceKafkaSourceTags"]
    config: "SourceUpdateSourceKafkaSourceConfig"


class SourceUpdateSourceKafkaSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceKafkaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceKafkaSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceKafkaSourceTags(TagDetails):
    pass


class SourceUpdateSourceKafkaSourceConfig(BaseModel):
    topic: str
    message_format: Optional[
        "SourceUpdateSourceKafkaSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class SourceUpdateSourceKafkaSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class SourceUpdateSourcePostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourcePostgreSqlSourceCredential"
    windows: List["SourceUpdateSourcePostgreSqlSourceWindows"]
    segmentations: List["SourceUpdateSourcePostgreSqlSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourcePostgreSqlSourceTags"]
    config: "SourceUpdateSourcePostgreSqlSourceConfig"


class SourceUpdateSourcePostgreSqlSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourcePostgreSqlSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourcePostgreSqlSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourcePostgreSqlSourceTags(TagDetails):
    pass


class SourceUpdateSourcePostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class SourceUpdateSourceSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "SourceUpdateSourceSnowflakeSourceCredential"
    windows: List["SourceUpdateSourceSnowflakeSourceWindows"]
    segmentations: List["SourceUpdateSourceSnowflakeSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["SourceUpdateSourceSnowflakeSourceTags"]
    config: "SourceUpdateSourceSnowflakeSourceConfig"


class SourceUpdateSourceSnowflakeSourceCredential(BaseModel):
    typename__: Literal[
        "AwsAthenaCredential",
        "AwsCredential",
        "AwsRedshiftCredential",
        "AzureSynapseEntraIdCredential",
        "AzureSynapseSqlCredential",
        "Credential",
        "DatabricksCredential",
        "DbtCloudCredential",
        "DbtCoreCredential",
        "DemoCredential",
        "GcpCredential",
        "KafkaSaslSslPlainCredential",
        "KafkaSslCredential",
        "LookerCredential",
        "PostgreSqlCredential",
        "SnowflakeCredential",
        "TableauConnectedAppCredential",
        "TableauPersonalAccessTokenCredential",
    ] = Field(alias="__typename")
    id: CredentialId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSnowflakeSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSnowflakeSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class SourceUpdateSourceSnowflakeSourceTags(TagDetails):
    pass


class SourceUpdateSourceSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class UserDetails(BaseModel):
    id: str
    display_name: str = Field(alias="displayName")
    full_name: Optional[str] = Field(alias="fullName")
    email: Optional[str]
    role: Role
    status: UserStatus
    identities: List[
        Annotated[
            Union[
                "UserDetailsIdentitiesFederatedIdentity",
                "UserDetailsIdentitiesLocalIdentity",
            ],
            Field(discriminator="typename__"),
        ]
    ]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    last_login_at: Optional[datetime] = Field(alias="lastLoginAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UserDetailsIdentitiesFederatedIdentity(BaseModel):
    typename__: Literal["FederatedIdentity"] = Field(alias="__typename")
    id: str
    user_id: Optional[str] = Field(alias="userId")
    idp: "UserDetailsIdentitiesFederatedIdentityIdp"
    created_at: datetime = Field(alias="createdAt")


class UserDetailsIdentitiesFederatedIdentityIdp(BaseModel):
    typename__: Literal[
        "IdentityProvider", "LocalIdentityProvider", "SamlIdentityProvider"
    ] = Field(alias="__typename")
    id: str
    name: str


class UserDetailsIdentitiesLocalIdentity(BaseModel):
    typename__: Literal["LocalIdentity"] = Field(alias="__typename")
    id: str
    user_id: Optional[str] = Field(alias="userId")
    username: str
    created_at: datetime = Field(alias="createdAt")


class UserCreation(BaseModel):
    errors: List["UserCreationErrors"]
    user: Optional["UserCreationUser"]


class UserCreationErrors(BaseModel):
    code: Optional[str]
    message: Optional[str]


class UserCreationUser(UserDetails):
    pass


class UserDeletion(BaseModel):
    errors: List["UserDeletionErrors"]
    user: Optional["UserDeletionUser"]


class UserDeletionErrors(BaseModel):
    code: UserDeleteErrorCode
    message: str


class UserDeletionUser(UserDetails):
    pass


class UserSummary(BaseModel):
    id: str
    display_name: str = Field(alias="displayName")
    full_name: Optional[str] = Field(alias="fullName")
    email: Optional[str]


class UserUpdate(BaseModel):
    errors: List["UserUpdateErrors"]
    user: Optional["UserUpdateUser"]


class UserUpdateErrors(BaseModel):
    code: UserUpdateErrorCode
    message: str


class UserUpdateUser(UserDetails):
    pass


class ValidatorCreation(BaseModel):
    errors: List["ValidatorCreationErrors"]
    validator: Optional[
        Annotated[
            Union[
                "ValidatorCreationValidatorValidator",
                "ValidatorCreationValidatorCategoricalDistributionValidator",
                "ValidatorCreationValidatorFreshnessValidator",
                "ValidatorCreationValidatorNumericAnomalyValidator",
                "ValidatorCreationValidatorNumericDistributionValidator",
                "ValidatorCreationValidatorNumericValidator",
                "ValidatorCreationValidatorRelativeTimeValidator",
                "ValidatorCreationValidatorRelativeVolumeValidator",
                "ValidatorCreationValidatorSqlValidator",
                "ValidatorCreationValidatorVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class ValidatorCreationErrors(ErrorDetails):
    pass


class ValidatorCreationValidatorValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorCategoricalDistributionValidator(BaseModel):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorCategoricalDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorFreshnessValidatorConfig"


class ValidatorCreationValidatorFreshnessValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorFreshnessValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorFreshnessValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorFreshnessValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorFreshnessValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorFreshnessValidatorConfig(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    threshold: Union[
        "ValidatorCreationValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorNumericAnomalyValidator(BaseModel):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorNumericAnomalyValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorCreationValidatorNumericAnomalyValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    sensitivity: float
    minimum_reference_datapoints: Optional[float] = Field(
        alias="minimumReferenceDatapoints"
    )
    minimum_absolute_difference: float = Field(alias="minimumAbsoluteDifference")
    minimum_relative_difference_percent: float = Field(
        alias="minimumRelativeDifferencePercent"
    )


class ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidator(BaseModel):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorNumericDistributionValidatorConfig"
    reference_source_config: "ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorCreationValidatorNumericDistributionValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorNumericValidatorConfig"


class ValidatorCreationValidatorNumericValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorNumericValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorNumericValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorNumericValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorRelativeTimeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorRelativeTimeValidatorConfig"


class ValidatorCreationValidatorRelativeTimeValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeTimeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeTimeValidatorConfig(BaseModel):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorRelativeVolumeValidator(BaseModel):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorRelativeVolumeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorCreationValidatorRelativeVolumeValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorSqlValidator(BaseModel):
    typename__: Literal["SqlValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorSqlValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorSqlValidatorConfig"


class ValidatorCreationValidatorSqlValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorSqlValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorSqlValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorSqlValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorSqlValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorSqlValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorSqlValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorSqlValidatorConfig(BaseModel):
    query: str
    threshold: Union[
        "ValidatorCreationValidatorSqlValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorSqlValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")


class ValidatorCreationValidatorSqlValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorSqlValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorCreationValidatorVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorCreationValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorCreationValidatorVolumeValidatorConfig"


class ValidatorCreationValidatorVolumeValidatorSourceConfig(BaseModel):
    source: "ValidatorCreationValidatorVolumeValidatorSourceConfigSource"
    window: "ValidatorCreationValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "ValidatorCreationValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorCreationValidatorVolumeValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorVolumeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorVolumeValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorCreationValidatorVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorCreationValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "ValidatorCreationValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorCreationValidatorVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorCreationValidatorVolumeValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorRecommendationApplication(BaseModel):
    typename__: str = Field(alias="__typename")
    failed_ids: List[Any] = Field(alias="failedIds")
    success_ids: List[str] = Field(alias="successIds")


class ValidatorRecommendationDismissal(BaseModel):
    typename__: str = Field(alias="__typename")
    errors: List["ValidatorRecommendationDismissalErrors"]
    recommendation_ids: List[str] = Field(alias="recommendationIds")


class ValidatorRecommendationDismissalErrors(ErrorDetails):
    pass


class ValidatorUpdate(BaseModel):
    errors: List["ValidatorUpdateErrors"]
    validator: Optional[
        Annotated[
            Union[
                "ValidatorUpdateValidatorValidator",
                "ValidatorUpdateValidatorCategoricalDistributionValidator",
                "ValidatorUpdateValidatorFreshnessValidator",
                "ValidatorUpdateValidatorNumericAnomalyValidator",
                "ValidatorUpdateValidatorNumericDistributionValidator",
                "ValidatorUpdateValidatorNumericValidator",
                "ValidatorUpdateValidatorRelativeTimeValidator",
                "ValidatorUpdateValidatorRelativeVolumeValidator",
                "ValidatorUpdateValidatorSqlValidator",
                "ValidatorUpdateValidatorVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class ValidatorUpdateErrors(ErrorDetails):
    pass


class ValidatorUpdateValidatorValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorCategoricalDistributionValidator(BaseModel):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorCategoricalDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorFreshnessValidatorConfig"


class ValidatorUpdateValidatorFreshnessValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorFreshnessValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorFreshnessValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorFreshnessValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorFreshnessValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorFreshnessValidatorConfig(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    threshold: Union[
        "ValidatorUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorNumericAnomalyValidator(BaseModel):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    sensitivity: float
    minimum_reference_datapoints: Optional[float] = Field(
        alias="minimumReferenceDatapoints"
    )
    minimum_absolute_difference: float = Field(alias="minimumAbsoluteDifference")
    minimum_relative_difference_percent: float = Field(
        alias="minimumRelativeDifferencePercent"
    )


class ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidator(BaseModel):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorNumericDistributionValidatorConfig"
    reference_source_config: "ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorUpdateValidatorNumericDistributionValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorNumericValidatorConfig"


class ValidatorUpdateValidatorNumericValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorNumericValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorNumericValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorNumericValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorNumericValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorRelativeTimeValidatorConfig"


class ValidatorUpdateValidatorRelativeTimeValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeTimeValidatorConfig(BaseModel):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorRelativeVolumeValidator(BaseModel):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
    BaseModel
):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorSqlValidator(BaseModel):
    typename__: Literal["SqlValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorSqlValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorSqlValidatorConfig"


class ValidatorUpdateValidatorSqlValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorSqlValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorSqlValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorSqlValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorSqlValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorSqlValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorSqlValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorSqlValidatorConfig(BaseModel):
    query: str
    threshold: Union[
        "ValidatorUpdateValidatorSqlValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorSqlValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")


class ValidatorUpdateValidatorSqlValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorSqlValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ValidatorUpdateValidatorVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ValidatorUpdateValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ValidatorUpdateValidatorVolumeValidatorConfig"


class ValidatorUpdateValidatorVolumeValidatorSourceConfig(BaseModel):
    source: "ValidatorUpdateValidatorVolumeValidatorSourceConfigSource"
    window: "ValidatorUpdateValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "ValidatorUpdateValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ValidatorUpdateValidatorVolumeValidatorSourceConfigSource(BaseModel):
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorVolumeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorVolumeValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ValidatorUpdateValidatorVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ValidatorUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "ValidatorUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ValidatorUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ValidatorUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class WindowCreation(BaseModel):
    errors: List["WindowCreationErrors"]
    window: Optional[
        Annotated[
            Union[
                "WindowCreationWindowWindow",
                "WindowCreationWindowFileWindow",
                "WindowCreationWindowFixedBatchWindow",
                "WindowCreationWindowTumblingWindow",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class WindowCreationErrors(ErrorDetails):
    pass


class WindowCreationWindowWindow(BaseModel):
    typename__: Literal["GlobalWindow", "Window"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowCreationWindowWindowSource"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowCreationWindowWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")


class WindowCreationWindowFileWindow(BaseModel):
    typename__: Literal["FileWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowCreationWindowFileWindowSource"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    data_time_field: JsonPointer = Field(alias="dataTimeField")


class WindowCreationWindowFileWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")


class WindowCreationWindowFixedBatchWindow(BaseModel):
    typename__: Literal["FixedBatchWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowCreationWindowFixedBatchWindowSource"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowCreationWindowFixedBatchWindowConfig"
    data_time_field: JsonPointer = Field(alias="dataTimeField")


class WindowCreationWindowFixedBatchWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")


class WindowCreationWindowFixedBatchWindowConfig(BaseModel):
    batch_size: int = Field(alias="batchSize")
    segmented_batching: bool = Field(alias="segmentedBatching")
    batch_timeout_secs: Optional[int] = Field(alias="batchTimeoutSecs")


class WindowCreationWindowTumblingWindow(BaseModel):
    typename__: Literal["TumblingWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowCreationWindowTumblingWindowSource"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowCreationWindowTumblingWindowConfig"
    data_time_field: JsonPointer = Field(alias="dataTimeField")


class WindowCreationWindowTumblingWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")


class WindowCreationWindowTumblingWindowConfig(BaseModel):
    window_size: int = Field(alias="windowSize")
    time_unit: WindowTimeUnit = Field(alias="timeUnit")
    window_timeout_disabled: bool = Field(alias="windowTimeoutDisabled")


class WindowUpdate(BaseModel):
    errors: List["WindowUpdateErrors"]
    window: Optional[
        Annotated[
            Union[
                "WindowUpdateWindowWindow",
                "WindowUpdateWindowFileWindow",
                "WindowUpdateWindowFixedBatchWindow",
                "WindowUpdateWindowTumblingWindow",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class WindowUpdateErrors(ErrorDetails):
    pass


class WindowUpdateWindowWindow(BaseModel):
    typename__: Literal["GlobalWindow", "Window"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowUpdateWindowWindowSource"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class WindowUpdateWindowWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")


class WindowUpdateWindowFileWindow(BaseModel):
    typename__: Literal["FileWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowUpdateWindowFileWindowSource"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    data_time_field: JsonPointer = Field(alias="dataTimeField")


class WindowUpdateWindowFileWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")


class WindowUpdateWindowFixedBatchWindow(BaseModel):
    typename__: Literal["FixedBatchWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowUpdateWindowFixedBatchWindowSource"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowUpdateWindowFixedBatchWindowConfig"
    data_time_field: JsonPointer = Field(alias="dataTimeField")


class WindowUpdateWindowFixedBatchWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")


class WindowUpdateWindowFixedBatchWindowConfig(BaseModel):
    batch_size: int = Field(alias="batchSize")
    segmented_batching: bool = Field(alias="segmentedBatching")
    batch_timeout_secs: Optional[int] = Field(alias="batchTimeoutSecs")


class WindowUpdateWindowTumblingWindow(BaseModel):
    typename__: Literal["TumblingWindow"] = Field(alias="__typename")
    id: WindowId
    name: str
    source: "WindowUpdateWindowTumblingWindowSource"
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "WindowUpdateWindowTumblingWindowConfig"
    data_time_field: JsonPointer = Field(alias="dataTimeField")


class WindowUpdateWindowTumblingWindowSource(BaseModel):
    id: SourceId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    typename__: Literal[
        "AwsAthenaSource",
        "AwsKinesisSource",
        "AwsRedshiftSource",
        "AwsS3Source",
        "AzureSynapseSource",
        "DatabricksSource",
        "DbtModelRunSource",
        "DbtTestResultSource",
        "DemoSource",
        "GcpBigQuerySource",
        "GcpPubSubLiteSource",
        "GcpPubSubSource",
        "GcpStorageSource",
        "KafkaSource",
        "PostgreSqlSource",
        "SnowflakeSource",
        "Source",
    ] = Field(alias="__typename")


class WindowUpdateWindowTumblingWindowConfig(BaseModel):
    window_size: int = Field(alias="windowSize")
    time_unit: WindowTimeUnit = Field(alias="timeUnit")
    window_timeout_disabled: bool = Field(alias="windowTimeoutDisabled")


ErrorDetails.model_rebuild()
ChannelCreation.model_rebuild()
ChannelCreationErrors.model_rebuild()
ChannelCreationChannelChannel.model_rebuild()
ChannelCreationChannelChannelNotificationRules.model_rebuild()
ChannelCreationChannelMsTeamsChannel.model_rebuild()
ChannelCreationChannelMsTeamsChannelNotificationRules.model_rebuild()
ChannelCreationChannelMsTeamsChannelConfig.model_rebuild()
ChannelCreationChannelSlackChannel.model_rebuild()
ChannelCreationChannelSlackChannelNotificationRules.model_rebuild()
ChannelCreationChannelSlackChannelConfig.model_rebuild()
ChannelCreationChannelWebhookChannel.model_rebuild()
ChannelCreationChannelWebhookChannelNotificationRules.model_rebuild()
ChannelCreationChannelWebhookChannelConfig.model_rebuild()
ChannelDeletion.model_rebuild()
ChannelDeletionErrors.model_rebuild()
ChannelDeletionChannel.model_rebuild()
ChannelUpdate.model_rebuild()
ChannelUpdateErrors.model_rebuild()
ChannelUpdateChannelChannel.model_rebuild()
ChannelUpdateChannelChannelNotificationRules.model_rebuild()
ChannelUpdateChannelMsTeamsChannel.model_rebuild()
ChannelUpdateChannelMsTeamsChannelNotificationRules.model_rebuild()
ChannelUpdateChannelMsTeamsChannelConfig.model_rebuild()
ChannelUpdateChannelSlackChannel.model_rebuild()
ChannelUpdateChannelSlackChannelNotificationRules.model_rebuild()
ChannelUpdateChannelSlackChannelConfig.model_rebuild()
ChannelUpdateChannelWebhookChannel.model_rebuild()
ChannelUpdateChannelWebhookChannelNotificationRules.model_rebuild()
ChannelUpdateChannelWebhookChannelConfig.model_rebuild()
CredentialBase.model_rebuild()
CredentialCreation.model_rebuild()
CredentialCreationErrors.model_rebuild()
CredentialCreationCredentialCredential.model_rebuild()
CredentialCreationCredentialAwsAthenaCredential.model_rebuild()
CredentialCreationCredentialAwsAthenaCredentialConfig.model_rebuild()
CredentialCreationCredentialAwsCredential.model_rebuild()
CredentialCreationCredentialAwsCredentialConfig.model_rebuild()
CredentialCreationCredentialAwsRedshiftCredential.model_rebuild()
CredentialCreationCredentialAwsRedshiftCredentialConfig.model_rebuild()
CredentialCreationCredentialAzureSynapseEntraIdCredential.model_rebuild()
CredentialCreationCredentialAzureSynapseEntraIdCredentialConfig.model_rebuild()
CredentialCreationCredentialAzureSynapseSqlCredential.model_rebuild()
CredentialCreationCredentialAzureSynapseSqlCredentialConfig.model_rebuild()
CredentialCreationCredentialDatabricksCredential.model_rebuild()
CredentialCreationCredentialDatabricksCredentialConfig.model_rebuild()
CredentialCreationCredentialDbtCloudCredential.model_rebuild()
CredentialCreationCredentialDbtCloudCredentialConfig.model_rebuild()
CredentialCreationCredentialDbtCloudCredentialConfigWarehouseCredential.model_rebuild()
CredentialCreationCredentialDbtCoreCredential.model_rebuild()
CredentialCreationCredentialDbtCoreCredentialConfig.model_rebuild()
CredentialCreationCredentialDbtCoreCredentialConfigWarehouseCredential.model_rebuild()
CredentialCreationCredentialKafkaSaslSslPlainCredential.model_rebuild()
CredentialCreationCredentialKafkaSaslSslPlainCredentialConfig.model_rebuild()
CredentialCreationCredentialKafkaSslCredential.model_rebuild()
CredentialCreationCredentialKafkaSslCredentialConfig.model_rebuild()
CredentialCreationCredentialLookerCredential.model_rebuild()
CredentialCreationCredentialLookerCredentialConfig.model_rebuild()
CredentialCreationCredentialPostgreSqlCredential.model_rebuild()
CredentialCreationCredentialPostgreSqlCredentialConfig.model_rebuild()
CredentialCreationCredentialSnowflakeCredential.model_rebuild()
CredentialCreationCredentialSnowflakeCredentialConfig.model_rebuild()
CredentialCreationCredentialTableauConnectedAppCredential.model_rebuild()
CredentialCreationCredentialTableauConnectedAppCredentialConfig.model_rebuild()
CredentialCreationCredentialTableauPersonalAccessTokenCredential.model_rebuild()
CredentialCreationCredentialTableauPersonalAccessTokenCredentialConfig.model_rebuild()
CredentialSecretChanged.model_rebuild()
CredentialSecretChangedErrors.model_rebuild()
CredentialUpdate.model_rebuild()
CredentialUpdateErrors.model_rebuild()
CredentialUpdateCredentialCredential.model_rebuild()
CredentialUpdateCredentialAwsAthenaCredential.model_rebuild()
CredentialUpdateCredentialAwsAthenaCredentialConfig.model_rebuild()
CredentialUpdateCredentialAwsCredential.model_rebuild()
CredentialUpdateCredentialAwsCredentialConfig.model_rebuild()
CredentialUpdateCredentialAwsRedshiftCredential.model_rebuild()
CredentialUpdateCredentialAwsRedshiftCredentialConfig.model_rebuild()
CredentialUpdateCredentialAzureSynapseEntraIdCredential.model_rebuild()
CredentialUpdateCredentialAzureSynapseEntraIdCredentialConfig.model_rebuild()
CredentialUpdateCredentialAzureSynapseSqlCredential.model_rebuild()
CredentialUpdateCredentialAzureSynapseSqlCredentialConfig.model_rebuild()
CredentialUpdateCredentialDatabricksCredential.model_rebuild()
CredentialUpdateCredentialDatabricksCredentialConfig.model_rebuild()
CredentialUpdateCredentialDbtCloudCredential.model_rebuild()
CredentialUpdateCredentialDbtCloudCredentialConfig.model_rebuild()
CredentialUpdateCredentialDbtCloudCredentialConfigWarehouseCredential.model_rebuild()
CredentialUpdateCredentialDbtCoreCredential.model_rebuild()
CredentialUpdateCredentialDbtCoreCredentialConfig.model_rebuild()
CredentialUpdateCredentialDbtCoreCredentialConfigWarehouseCredential.model_rebuild()
CredentialUpdateCredentialKafkaSaslSslPlainCredential.model_rebuild()
CredentialUpdateCredentialKafkaSaslSslPlainCredentialConfig.model_rebuild()
CredentialUpdateCredentialKafkaSslCredential.model_rebuild()
CredentialUpdateCredentialKafkaSslCredentialConfig.model_rebuild()
CredentialUpdateCredentialLookerCredential.model_rebuild()
CredentialUpdateCredentialLookerCredentialConfig.model_rebuild()
CredentialUpdateCredentialPostgreSqlCredential.model_rebuild()
CredentialUpdateCredentialPostgreSqlCredentialConfig.model_rebuild()
CredentialUpdateCredentialSnowflakeCredential.model_rebuild()
CredentialUpdateCredentialSnowflakeCredentialConfig.model_rebuild()
CredentialUpdateCredentialTableauConnectedAppCredential.model_rebuild()
CredentialUpdateCredentialTableauConnectedAppCredentialConfig.model_rebuild()
CredentialUpdateCredentialTableauPersonalAccessTokenCredential.model_rebuild()
CredentialUpdateCredentialTableauPersonalAccessTokenCredentialConfig.model_rebuild()
IdentityDeletion.model_rebuild()
IdentityDeletionErrors.model_rebuild()
IdentityProviderCreation.model_rebuild()
IdentityProviderCreationErrors.model_rebuild()
IdentityProviderCreationIdentityProviderIdentityProvider.model_rebuild()
IdentityProviderCreationIdentityProviderSamlIdentityProvider.model_rebuild()
IdentityProviderCreationIdentityProviderSamlIdentityProviderConfig.model_rebuild()
IdentityProviderDeletion.model_rebuild()
IdentityProviderDeletionErrors.model_rebuild()
IdentityProviderUpdate.model_rebuild()
IdentityProviderUpdateErrors.model_rebuild()
IdentityProviderUpdateIdentityProviderIdentityProvider.model_rebuild()
IdentityProviderUpdateIdentityProviderSamlIdentityProvider.model_rebuild()
IdentityProviderUpdateIdentityProviderSamlIdentityProviderConfig.model_rebuild()
NamespaceUpdate.model_rebuild()
NamespaceUpdateErrors.model_rebuild()
NotificationRuleConditionCreation.model_rebuild()
NotificationRuleConditionCreationErrors.model_rebuild()
NotificationRuleDetails.model_rebuild()
NotificationRuleDetailsConditionsNotificationRuleCondition.model_rebuild()
NotificationRuleDetailsConditionsOwnerNotificationRuleCondition.model_rebuild()
NotificationRuleDetailsConditionsOwnerNotificationRuleConditionConfig.model_rebuild()
NotificationRuleDetailsConditionsOwnerNotificationRuleConditionConfigOwners.model_rebuild()
NotificationRuleDetailsConditionsSegmentNotificationRuleCondition.model_rebuild()
NotificationRuleDetailsConditionsSegmentNotificationRuleConditionConfig.model_rebuild()
NotificationRuleDetailsConditionsSegmentNotificationRuleConditionConfigSegments.model_rebuild()
NotificationRuleDetailsConditionsSeverityNotificationRuleCondition.model_rebuild()
NotificationRuleDetailsConditionsSeverityNotificationRuleConditionConfig.model_rebuild()
NotificationRuleDetailsConditionsSourceNotificationRuleCondition.model_rebuild()
NotificationRuleDetailsConditionsSourceNotificationRuleConditionConfig.model_rebuild()
NotificationRuleDetailsConditionsSourceNotificationRuleConditionConfigSources.model_rebuild()
NotificationRuleDetailsConditionsTagNotificationRuleCondition.model_rebuild()
NotificationRuleDetailsConditionsTagNotificationRuleConditionConfig.model_rebuild()
NotificationRuleDetailsConditionsTagNotificationRuleConditionConfigTags.model_rebuild()
NotificationRuleDetailsConditionsTypeNotificationRuleCondition.model_rebuild()
NotificationRuleDetailsConditionsTypeNotificationRuleConditionConfig.model_rebuild()
NotificationRuleDetailsChannelChannel.model_rebuild()
NotificationRuleDetailsChannelChannelNotificationRules.model_rebuild()
NotificationRuleDetailsChannelMsTeamsChannel.model_rebuild()
NotificationRuleDetailsChannelMsTeamsChannelNotificationRules.model_rebuild()
NotificationRuleDetailsChannelMsTeamsChannelConfig.model_rebuild()
NotificationRuleDetailsChannelSlackChannel.model_rebuild()
NotificationRuleDetailsChannelSlackChannelNotificationRules.model_rebuild()
NotificationRuleDetailsChannelSlackChannelConfig.model_rebuild()
NotificationRuleDetailsChannelWebhookChannel.model_rebuild()
NotificationRuleDetailsChannelWebhookChannelNotificationRules.model_rebuild()
NotificationRuleDetailsChannelWebhookChannelConfig.model_rebuild()
NotificationRuleCreation.model_rebuild()
NotificationRuleCreationErrors.model_rebuild()
NotificationRuleCreationNotificationRule.model_rebuild()
NotificationRuleDeletion.model_rebuild()
NotificationRuleDeletionErrors.model_rebuild()
NotificationRuleDeletionNotificationRule.model_rebuild()
NotificationRuleUpdate.model_rebuild()
NotificationRuleUpdateErrors.model_rebuild()
NotificationRuleUpdateNotificationRule.model_rebuild()
ReferenceSourceConfigDetails.model_rebuild()
ReferenceSourceConfigDetailsSource.model_rebuild()
ReferenceSourceConfigDetailsWindow.model_rebuild()
SegmentDetails.model_rebuild()
SegmentDetailsFields.model_rebuild()
SegmentDetailsDataQuality.model_rebuild()
SegmentationDetails.model_rebuild()
SegmentationDetailsSource.model_rebuild()
SegmentationCreation.model_rebuild()
SegmentationCreationErrors.model_rebuild()
SegmentationCreationSegmentation.model_rebuild()
SegmentationSummary.model_rebuild()
SourceBase.model_rebuild()
TagDetails.model_rebuild()
SourceCreation.model_rebuild()
SourceCreationErrors.model_rebuild()
SourceCreationSourceSource.model_rebuild()
SourceCreationSourceSourceCredential.model_rebuild()
SourceCreationSourceSourceWindows.model_rebuild()
SourceCreationSourceSourceSegmentations.model_rebuild()
SourceCreationSourceSourceTags.model_rebuild()
SourceCreationSourceAwsAthenaSource.model_rebuild()
SourceCreationSourceAwsAthenaSourceCredential.model_rebuild()
SourceCreationSourceAwsAthenaSourceWindows.model_rebuild()
SourceCreationSourceAwsAthenaSourceSegmentations.model_rebuild()
SourceCreationSourceAwsAthenaSourceTags.model_rebuild()
SourceCreationSourceAwsAthenaSourceConfig.model_rebuild()
SourceCreationSourceAwsKinesisSource.model_rebuild()
SourceCreationSourceAwsKinesisSourceCredential.model_rebuild()
SourceCreationSourceAwsKinesisSourceWindows.model_rebuild()
SourceCreationSourceAwsKinesisSourceSegmentations.model_rebuild()
SourceCreationSourceAwsKinesisSourceTags.model_rebuild()
SourceCreationSourceAwsKinesisSourceConfig.model_rebuild()
SourceCreationSourceAwsKinesisSourceConfigMessageFormat.model_rebuild()
SourceCreationSourceAwsRedshiftSource.model_rebuild()
SourceCreationSourceAwsRedshiftSourceCredential.model_rebuild()
SourceCreationSourceAwsRedshiftSourceWindows.model_rebuild()
SourceCreationSourceAwsRedshiftSourceSegmentations.model_rebuild()
SourceCreationSourceAwsRedshiftSourceTags.model_rebuild()
SourceCreationSourceAwsRedshiftSourceConfig.model_rebuild()
SourceCreationSourceAwsS3Source.model_rebuild()
SourceCreationSourceAwsS3SourceCredential.model_rebuild()
SourceCreationSourceAwsS3SourceWindows.model_rebuild()
SourceCreationSourceAwsS3SourceSegmentations.model_rebuild()
SourceCreationSourceAwsS3SourceTags.model_rebuild()
SourceCreationSourceAwsS3SourceConfig.model_rebuild()
SourceCreationSourceAwsS3SourceConfigCsv.model_rebuild()
SourceCreationSourceAzureSynapseSource.model_rebuild()
SourceCreationSourceAzureSynapseSourceCredential.model_rebuild()
SourceCreationSourceAzureSynapseSourceWindows.model_rebuild()
SourceCreationSourceAzureSynapseSourceSegmentations.model_rebuild()
SourceCreationSourceAzureSynapseSourceTags.model_rebuild()
SourceCreationSourceAzureSynapseSourceConfig.model_rebuild()
SourceCreationSourceDatabricksSource.model_rebuild()
SourceCreationSourceDatabricksSourceCredential.model_rebuild()
SourceCreationSourceDatabricksSourceWindows.model_rebuild()
SourceCreationSourceDatabricksSourceSegmentations.model_rebuild()
SourceCreationSourceDatabricksSourceTags.model_rebuild()
SourceCreationSourceDatabricksSourceConfig.model_rebuild()
SourceCreationSourceDbtModelRunSource.model_rebuild()
SourceCreationSourceDbtModelRunSourceCredential.model_rebuild()
SourceCreationSourceDbtModelRunSourceWindows.model_rebuild()
SourceCreationSourceDbtModelRunSourceSegmentations.model_rebuild()
SourceCreationSourceDbtModelRunSourceTags.model_rebuild()
SourceCreationSourceDbtModelRunSourceConfig.model_rebuild()
SourceCreationSourceDbtTestResultSource.model_rebuild()
SourceCreationSourceDbtTestResultSourceCredential.model_rebuild()
SourceCreationSourceDbtTestResultSourceWindows.model_rebuild()
SourceCreationSourceDbtTestResultSourceSegmentations.model_rebuild()
SourceCreationSourceDbtTestResultSourceTags.model_rebuild()
SourceCreationSourceDbtTestResultSourceConfig.model_rebuild()
SourceCreationSourceGcpBigQuerySource.model_rebuild()
SourceCreationSourceGcpBigQuerySourceCredential.model_rebuild()
SourceCreationSourceGcpBigQuerySourceWindows.model_rebuild()
SourceCreationSourceGcpBigQuerySourceSegmentations.model_rebuild()
SourceCreationSourceGcpBigQuerySourceTags.model_rebuild()
SourceCreationSourceGcpBigQuerySourceConfig.model_rebuild()
SourceCreationSourceGcpPubSubLiteSource.model_rebuild()
SourceCreationSourceGcpPubSubLiteSourceCredential.model_rebuild()
SourceCreationSourceGcpPubSubLiteSourceWindows.model_rebuild()
SourceCreationSourceGcpPubSubLiteSourceSegmentations.model_rebuild()
SourceCreationSourceGcpPubSubLiteSourceTags.model_rebuild()
SourceCreationSourceGcpPubSubLiteSourceConfig.model_rebuild()
SourceCreationSourceGcpPubSubLiteSourceConfigMessageFormat.model_rebuild()
SourceCreationSourceGcpPubSubSource.model_rebuild()
SourceCreationSourceGcpPubSubSourceCredential.model_rebuild()
SourceCreationSourceGcpPubSubSourceWindows.model_rebuild()
SourceCreationSourceGcpPubSubSourceSegmentations.model_rebuild()
SourceCreationSourceGcpPubSubSourceTags.model_rebuild()
SourceCreationSourceGcpPubSubSourceConfig.model_rebuild()
SourceCreationSourceGcpPubSubSourceConfigMessageFormat.model_rebuild()
SourceCreationSourceGcpStorageSource.model_rebuild()
SourceCreationSourceGcpStorageSourceCredential.model_rebuild()
SourceCreationSourceGcpStorageSourceWindows.model_rebuild()
SourceCreationSourceGcpStorageSourceSegmentations.model_rebuild()
SourceCreationSourceGcpStorageSourceTags.model_rebuild()
SourceCreationSourceGcpStorageSourceConfig.model_rebuild()
SourceCreationSourceGcpStorageSourceConfigCsv.model_rebuild()
SourceCreationSourceKafkaSource.model_rebuild()
SourceCreationSourceKafkaSourceCredential.model_rebuild()
SourceCreationSourceKafkaSourceWindows.model_rebuild()
SourceCreationSourceKafkaSourceSegmentations.model_rebuild()
SourceCreationSourceKafkaSourceTags.model_rebuild()
SourceCreationSourceKafkaSourceConfig.model_rebuild()
SourceCreationSourceKafkaSourceConfigMessageFormat.model_rebuild()
SourceCreationSourcePostgreSqlSource.model_rebuild()
SourceCreationSourcePostgreSqlSourceCredential.model_rebuild()
SourceCreationSourcePostgreSqlSourceWindows.model_rebuild()
SourceCreationSourcePostgreSqlSourceSegmentations.model_rebuild()
SourceCreationSourcePostgreSqlSourceTags.model_rebuild()
SourceCreationSourcePostgreSqlSourceConfig.model_rebuild()
SourceCreationSourceSnowflakeSource.model_rebuild()
SourceCreationSourceSnowflakeSourceCredential.model_rebuild()
SourceCreationSourceSnowflakeSourceWindows.model_rebuild()
SourceCreationSourceSnowflakeSourceSegmentations.model_rebuild()
SourceCreationSourceSnowflakeSourceTags.model_rebuild()
SourceCreationSourceSnowflakeSourceConfig.model_rebuild()
SourceUpdate.model_rebuild()
SourceUpdateErrors.model_rebuild()
SourceUpdateSourceSource.model_rebuild()
SourceUpdateSourceSourceCredential.model_rebuild()
SourceUpdateSourceSourceWindows.model_rebuild()
SourceUpdateSourceSourceSegmentations.model_rebuild()
SourceUpdateSourceSourceTags.model_rebuild()
SourceUpdateSourceAwsAthenaSource.model_rebuild()
SourceUpdateSourceAwsAthenaSourceCredential.model_rebuild()
SourceUpdateSourceAwsAthenaSourceWindows.model_rebuild()
SourceUpdateSourceAwsAthenaSourceSegmentations.model_rebuild()
SourceUpdateSourceAwsAthenaSourceTags.model_rebuild()
SourceUpdateSourceAwsAthenaSourceConfig.model_rebuild()
SourceUpdateSourceAwsKinesisSource.model_rebuild()
SourceUpdateSourceAwsKinesisSourceCredential.model_rebuild()
SourceUpdateSourceAwsKinesisSourceWindows.model_rebuild()
SourceUpdateSourceAwsKinesisSourceSegmentations.model_rebuild()
SourceUpdateSourceAwsKinesisSourceTags.model_rebuild()
SourceUpdateSourceAwsKinesisSourceConfig.model_rebuild()
SourceUpdateSourceAwsKinesisSourceConfigMessageFormat.model_rebuild()
SourceUpdateSourceAwsRedshiftSource.model_rebuild()
SourceUpdateSourceAwsRedshiftSourceCredential.model_rebuild()
SourceUpdateSourceAwsRedshiftSourceWindows.model_rebuild()
SourceUpdateSourceAwsRedshiftSourceSegmentations.model_rebuild()
SourceUpdateSourceAwsRedshiftSourceTags.model_rebuild()
SourceUpdateSourceAwsRedshiftSourceConfig.model_rebuild()
SourceUpdateSourceAwsS3Source.model_rebuild()
SourceUpdateSourceAwsS3SourceCredential.model_rebuild()
SourceUpdateSourceAwsS3SourceWindows.model_rebuild()
SourceUpdateSourceAwsS3SourceSegmentations.model_rebuild()
SourceUpdateSourceAwsS3SourceTags.model_rebuild()
SourceUpdateSourceAwsS3SourceConfig.model_rebuild()
SourceUpdateSourceAwsS3SourceConfigCsv.model_rebuild()
SourceUpdateSourceAzureSynapseSource.model_rebuild()
SourceUpdateSourceAzureSynapseSourceCredential.model_rebuild()
SourceUpdateSourceAzureSynapseSourceWindows.model_rebuild()
SourceUpdateSourceAzureSynapseSourceSegmentations.model_rebuild()
SourceUpdateSourceAzureSynapseSourceTags.model_rebuild()
SourceUpdateSourceAzureSynapseSourceConfig.model_rebuild()
SourceUpdateSourceDatabricksSource.model_rebuild()
SourceUpdateSourceDatabricksSourceCredential.model_rebuild()
SourceUpdateSourceDatabricksSourceWindows.model_rebuild()
SourceUpdateSourceDatabricksSourceSegmentations.model_rebuild()
SourceUpdateSourceDatabricksSourceTags.model_rebuild()
SourceUpdateSourceDatabricksSourceConfig.model_rebuild()
SourceUpdateSourceDbtModelRunSource.model_rebuild()
SourceUpdateSourceDbtModelRunSourceCredential.model_rebuild()
SourceUpdateSourceDbtModelRunSourceWindows.model_rebuild()
SourceUpdateSourceDbtModelRunSourceSegmentations.model_rebuild()
SourceUpdateSourceDbtModelRunSourceTags.model_rebuild()
SourceUpdateSourceDbtModelRunSourceConfig.model_rebuild()
SourceUpdateSourceDbtTestResultSource.model_rebuild()
SourceUpdateSourceDbtTestResultSourceCredential.model_rebuild()
SourceUpdateSourceDbtTestResultSourceWindows.model_rebuild()
SourceUpdateSourceDbtTestResultSourceSegmentations.model_rebuild()
SourceUpdateSourceDbtTestResultSourceTags.model_rebuild()
SourceUpdateSourceDbtTestResultSourceConfig.model_rebuild()
SourceUpdateSourceGcpBigQuerySource.model_rebuild()
SourceUpdateSourceGcpBigQuerySourceCredential.model_rebuild()
SourceUpdateSourceGcpBigQuerySourceWindows.model_rebuild()
SourceUpdateSourceGcpBigQuerySourceSegmentations.model_rebuild()
SourceUpdateSourceGcpBigQuerySourceTags.model_rebuild()
SourceUpdateSourceGcpBigQuerySourceConfig.model_rebuild()
SourceUpdateSourceGcpPubSubLiteSource.model_rebuild()
SourceUpdateSourceGcpPubSubLiteSourceCredential.model_rebuild()
SourceUpdateSourceGcpPubSubLiteSourceWindows.model_rebuild()
SourceUpdateSourceGcpPubSubLiteSourceSegmentations.model_rebuild()
SourceUpdateSourceGcpPubSubLiteSourceTags.model_rebuild()
SourceUpdateSourceGcpPubSubLiteSourceConfig.model_rebuild()
SourceUpdateSourceGcpPubSubLiteSourceConfigMessageFormat.model_rebuild()
SourceUpdateSourceGcpPubSubSource.model_rebuild()
SourceUpdateSourceGcpPubSubSourceCredential.model_rebuild()
SourceUpdateSourceGcpPubSubSourceWindows.model_rebuild()
SourceUpdateSourceGcpPubSubSourceSegmentations.model_rebuild()
SourceUpdateSourceGcpPubSubSourceTags.model_rebuild()
SourceUpdateSourceGcpPubSubSourceConfig.model_rebuild()
SourceUpdateSourceGcpPubSubSourceConfigMessageFormat.model_rebuild()
SourceUpdateSourceGcpStorageSource.model_rebuild()
SourceUpdateSourceGcpStorageSourceCredential.model_rebuild()
SourceUpdateSourceGcpStorageSourceWindows.model_rebuild()
SourceUpdateSourceGcpStorageSourceSegmentations.model_rebuild()
SourceUpdateSourceGcpStorageSourceTags.model_rebuild()
SourceUpdateSourceGcpStorageSourceConfig.model_rebuild()
SourceUpdateSourceGcpStorageSourceConfigCsv.model_rebuild()
SourceUpdateSourceKafkaSource.model_rebuild()
SourceUpdateSourceKafkaSourceCredential.model_rebuild()
SourceUpdateSourceKafkaSourceWindows.model_rebuild()
SourceUpdateSourceKafkaSourceSegmentations.model_rebuild()
SourceUpdateSourceKafkaSourceTags.model_rebuild()
SourceUpdateSourceKafkaSourceConfig.model_rebuild()
SourceUpdateSourceKafkaSourceConfigMessageFormat.model_rebuild()
SourceUpdateSourcePostgreSqlSource.model_rebuild()
SourceUpdateSourcePostgreSqlSourceCredential.model_rebuild()
SourceUpdateSourcePostgreSqlSourceWindows.model_rebuild()
SourceUpdateSourcePostgreSqlSourceSegmentations.model_rebuild()
SourceUpdateSourcePostgreSqlSourceTags.model_rebuild()
SourceUpdateSourcePostgreSqlSourceConfig.model_rebuild()
SourceUpdateSourceSnowflakeSource.model_rebuild()
SourceUpdateSourceSnowflakeSourceCredential.model_rebuild()
SourceUpdateSourceSnowflakeSourceWindows.model_rebuild()
SourceUpdateSourceSnowflakeSourceSegmentations.model_rebuild()
SourceUpdateSourceSnowflakeSourceTags.model_rebuild()
SourceUpdateSourceSnowflakeSourceConfig.model_rebuild()
UserDetails.model_rebuild()
UserDetailsIdentitiesFederatedIdentity.model_rebuild()
UserDetailsIdentitiesFederatedIdentityIdp.model_rebuild()
UserDetailsIdentitiesLocalIdentity.model_rebuild()
UserCreation.model_rebuild()
UserCreationErrors.model_rebuild()
UserCreationUser.model_rebuild()
UserDeletion.model_rebuild()
UserDeletionErrors.model_rebuild()
UserDeletionUser.model_rebuild()
UserSummary.model_rebuild()
UserUpdate.model_rebuild()
UserUpdateErrors.model_rebuild()
UserUpdateUser.model_rebuild()
ValidatorCreation.model_rebuild()
ValidatorCreationErrors.model_rebuild()
ValidatorCreationValidatorValidator.model_rebuild()
ValidatorCreationValidatorValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidator.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorConfig.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfig.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.model_rebuild()
ValidatorCreationValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorFreshnessValidator.model_rebuild()
ValidatorCreationValidatorFreshnessValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorFreshnessValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorFreshnessValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorFreshnessValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorFreshnessValidatorConfig.model_rebuild()
ValidatorCreationValidatorFreshnessValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorCreationValidatorFreshnessValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidator.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorConfig.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfig.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigSource.model_rebuild()
ValidatorCreationValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidator.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorConfig.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfig.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigSource.model_rebuild()
ValidatorCreationValidatorNumericDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorNumericValidator.model_rebuild()
ValidatorCreationValidatorNumericValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorNumericValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorNumericValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorNumericValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorNumericValidatorConfig.model_rebuild()
ValidatorCreationValidatorNumericValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorCreationValidatorNumericValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorCreationValidatorRelativeTimeValidator.model_rebuild()
ValidatorCreationValidatorRelativeTimeValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorRelativeTimeValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorRelativeTimeValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorRelativeTimeValidatorConfig.model_rebuild()
ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorCreationValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidator.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorConfig.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfig.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigSource.model_rebuild()
ValidatorCreationValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorSqlValidator.model_rebuild()
ValidatorCreationValidatorSqlValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorSqlValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorSqlValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorSqlValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorSqlValidatorConfig.model_rebuild()
ValidatorCreationValidatorSqlValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorCreationValidatorSqlValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorCreationValidatorVolumeValidator.model_rebuild()
ValidatorCreationValidatorVolumeValidatorSourceConfig.model_rebuild()
ValidatorCreationValidatorVolumeValidatorSourceConfigSource.model_rebuild()
ValidatorCreationValidatorVolumeValidatorSourceConfigWindow.model_rebuild()
ValidatorCreationValidatorVolumeValidatorSourceConfigSegmentation.model_rebuild()
ValidatorCreationValidatorVolumeValidatorConfig.model_rebuild()
ValidatorCreationValidatorVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorCreationValidatorVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorRecommendationApplication.model_rebuild()
ValidatorRecommendationDismissal.model_rebuild()
ValidatorRecommendationDismissalErrors.model_rebuild()
ValidatorUpdate.model_rebuild()
ValidatorUpdateErrors.model_rebuild()
ValidatorUpdateValidatorValidator.model_rebuild()
ValidatorUpdateValidatorValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidator.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorConfig.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorFreshnessValidator.model_rebuild()
ValidatorUpdateValidatorFreshnessValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorFreshnessValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorFreshnessValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorFreshnessValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorFreshnessValidatorConfig.model_rebuild()
ValidatorUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidator.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorConfig.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidator.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorConfig.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfig.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorNumericValidator.model_rebuild()
ValidatorUpdateValidatorNumericValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorNumericValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorNumericValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorNumericValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorNumericValidatorConfig.model_rebuild()
ValidatorUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorUpdateValidatorNumericValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorUpdateValidatorRelativeTimeValidator.model_rebuild()
ValidatorUpdateValidatorRelativeTimeValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorRelativeTimeValidatorConfig.model_rebuild()
ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidator.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorConfig.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorSqlValidator.model_rebuild()
ValidatorUpdateValidatorSqlValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorSqlValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorSqlValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorSqlValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorSqlValidatorConfig.model_rebuild()
ValidatorUpdateValidatorSqlValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorUpdateValidatorSqlValidatorConfigThresholdFixedThreshold.model_rebuild()
ValidatorUpdateValidatorVolumeValidator.model_rebuild()
ValidatorUpdateValidatorVolumeValidatorSourceConfig.model_rebuild()
ValidatorUpdateValidatorVolumeValidatorSourceConfigSource.model_rebuild()
ValidatorUpdateValidatorVolumeValidatorSourceConfigWindow.model_rebuild()
ValidatorUpdateValidatorVolumeValidatorSourceConfigSegmentation.model_rebuild()
ValidatorUpdateValidatorVolumeValidatorConfig.model_rebuild()
ValidatorUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
ValidatorUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
WindowCreation.model_rebuild()
WindowCreationErrors.model_rebuild()
WindowCreationWindowWindow.model_rebuild()
WindowCreationWindowWindowSource.model_rebuild()
WindowCreationWindowFileWindow.model_rebuild()
WindowCreationWindowFileWindowSource.model_rebuild()
WindowCreationWindowFixedBatchWindow.model_rebuild()
WindowCreationWindowFixedBatchWindowSource.model_rebuild()
WindowCreationWindowFixedBatchWindowConfig.model_rebuild()
WindowCreationWindowTumblingWindow.model_rebuild()
WindowCreationWindowTumblingWindowSource.model_rebuild()
WindowCreationWindowTumblingWindowConfig.model_rebuild()
WindowUpdate.model_rebuild()
WindowUpdateErrors.model_rebuild()
WindowUpdateWindowWindow.model_rebuild()
WindowUpdateWindowWindowSource.model_rebuild()
WindowUpdateWindowFileWindow.model_rebuild()
WindowUpdateWindowFileWindowSource.model_rebuild()
WindowUpdateWindowFixedBatchWindow.model_rebuild()
WindowUpdateWindowFixedBatchWindowSource.model_rebuild()
WindowUpdateWindowFixedBatchWindowConfig.model_rebuild()
WindowUpdateWindowTumblingWindow.model_rebuild()
WindowUpdateWindowTumblingWindowSource.model_rebuild()
WindowUpdateWindowTumblingWindowConfig.model_rebuild()
