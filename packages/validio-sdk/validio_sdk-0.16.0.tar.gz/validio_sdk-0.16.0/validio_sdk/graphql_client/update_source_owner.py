from datetime import datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import Field

from validio_sdk.scalars import (
    CredentialId,
    CronExpression,
    JsonTypeDefinition,
    SegmentationId,
    SourceId,
    WindowId,
)

from .base_model import BaseModel
from .enums import FileFormat, SourceState, StreamingSourceMessageFormat
from .fragments import ErrorDetails, TagDetails


class UpdateSourceOwner(BaseModel):
    source_owner_update: "UpdateSourceOwnerSourceOwnerUpdate" = Field(
        alias="sourceOwnerUpdate"
    )


class UpdateSourceOwnerSourceOwnerUpdate(BaseModel):
    errors: List["UpdateSourceOwnerSourceOwnerUpdateErrors"]
    source: Optional[
        Annotated[
            Union[
                "UpdateSourceOwnerSourceOwnerUpdateSourceSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3Source",
                "UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSource",
                "UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSource",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class UpdateSourceOwnerSourceOwnerUpdateErrors(ErrorDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceSourceWindows"]
    segmentations: List["UpdateSourceOwnerSourceOwnerUpdateSourceSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceSourceTags"]


class UpdateSourceOwnerSourceOwnerUpdateSourceSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")
    message_format: Optional[
        "UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceConfigMessageFormat(
    BaseModel
):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceConfigCsv"]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSource(BaseModel):
    typename__: Literal["AzureSynapseSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSource(BaseModel):
    typename__: Literal["DatabricksSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceConfig(BaseModel):
    catalog: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSource(BaseModel):
    typename__: Literal["DbtModelRunSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSource(BaseModel):
    typename__: Literal["DbtTestResultSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceConfigMessageFormat(
    BaseModel
):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceConfigMessageFormat(
    BaseModel
):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional["UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceConfigCsv"]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceConfig(BaseModel):
    topic: str
    message_format: Optional[
        "UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceCredential"
    windows: List["UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceWindows"]
    segmentations: List[
        "UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceTags"]
    config: "UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceConfig"


class UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceCredential(BaseModel):
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


class UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceTags(TagDetails):
    pass


class UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


UpdateSourceOwner.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdate.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateErrors.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsAthenaSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsKinesisSourceConfigMessageFormat.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsRedshiftSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3Source.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAwsS3SourceConfigCsv.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceAzureSynapseSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDatabricksSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtModelRunSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceDbtTestResultSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpBigQuerySourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubLiteSourceConfigMessageFormat.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpPubSubSourceConfigMessageFormat.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceGcpStorageSourceConfigCsv.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceKafkaSourceConfigMessageFormat.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourcePostgreSqlSourceConfig.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSource.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceCredential.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceWindows.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceSegmentations.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceTags.model_rebuild()
UpdateSourceOwnerSourceOwnerUpdateSourceSnowflakeSourceConfig.model_rebuild()
