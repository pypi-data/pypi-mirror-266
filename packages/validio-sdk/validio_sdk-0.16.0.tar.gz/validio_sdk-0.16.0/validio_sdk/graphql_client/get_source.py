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
from .fragments import TagDetails


class GetSource(BaseModel):
    source: Optional[
        Annotated[
            Union[
                "GetSourceSourceSource",
                "GetSourceSourceAwsAthenaSource",
                "GetSourceSourceAwsKinesisSource",
                "GetSourceSourceAwsRedshiftSource",
                "GetSourceSourceAwsS3Source",
                "GetSourceSourceAzureSynapseSource",
                "GetSourceSourceDatabricksSource",
                "GetSourceSourceDbtModelRunSource",
                "GetSourceSourceDbtTestResultSource",
                "GetSourceSourceGcpBigQuerySource",
                "GetSourceSourceGcpPubSubLiteSource",
                "GetSourceSourceGcpPubSubSource",
                "GetSourceSourceGcpStorageSource",
                "GetSourceSourceKafkaSource",
                "GetSourceSourcePostgreSqlSource",
                "GetSourceSourceSnowflakeSource",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class GetSourceSourceSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceSourceCredential"
    windows: List["GetSourceSourceSourceWindows"]
    segmentations: List["GetSourceSourceSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceSourceTags"]


class GetSourceSourceSourceCredential(BaseModel):
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


class GetSourceSourceSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSourceTags(TagDetails):
    pass


class GetSourceSourceAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceAwsAthenaSourceCredential"
    windows: List["GetSourceSourceAwsAthenaSourceWindows"]
    segmentations: List["GetSourceSourceAwsAthenaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceAwsAthenaSourceTags"]
    config: "GetSourceSourceAwsAthenaSourceConfig"


class GetSourceSourceAwsAthenaSourceCredential(BaseModel):
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


class GetSourceSourceAwsAthenaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsAthenaSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsAthenaSourceTags(TagDetails):
    pass


class GetSourceSourceAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceSourceAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceAwsKinesisSourceCredential"
    windows: List["GetSourceSourceAwsKinesisSourceWindows"]
    segmentations: List["GetSourceSourceAwsKinesisSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceAwsKinesisSourceTags"]
    config: "GetSourceSourceAwsKinesisSourceConfig"


class GetSourceSourceAwsKinesisSourceCredential(BaseModel):
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


class GetSourceSourceAwsKinesisSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsKinesisSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsKinesisSourceTags(TagDetails):
    pass


class GetSourceSourceAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")
    message_format: Optional[
        "GetSourceSourceAwsKinesisSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class GetSourceSourceAwsKinesisSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class GetSourceSourceAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceAwsRedshiftSourceCredential"
    windows: List["GetSourceSourceAwsRedshiftSourceWindows"]
    segmentations: List["GetSourceSourceAwsRedshiftSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceAwsRedshiftSourceTags"]
    config: "GetSourceSourceAwsRedshiftSourceConfig"


class GetSourceSourceAwsRedshiftSourceCredential(BaseModel):
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


class GetSourceSourceAwsRedshiftSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsRedshiftSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsRedshiftSourceTags(TagDetails):
    pass


class GetSourceSourceAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceSourceAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceAwsS3SourceCredential"
    windows: List["GetSourceSourceAwsS3SourceWindows"]
    segmentations: List["GetSourceSourceAwsS3SourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceAwsS3SourceTags"]
    config: "GetSourceSourceAwsS3SourceConfig"


class GetSourceSourceAwsS3SourceCredential(BaseModel):
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


class GetSourceSourceAwsS3SourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsS3SourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAwsS3SourceTags(TagDetails):
    pass


class GetSourceSourceAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["GetSourceSourceAwsS3SourceConfigCsv"]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class GetSourceSourceAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class GetSourceSourceAzureSynapseSource(BaseModel):
    typename__: Literal["AzureSynapseSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceAzureSynapseSourceCredential"
    windows: List["GetSourceSourceAzureSynapseSourceWindows"]
    segmentations: List["GetSourceSourceAzureSynapseSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceAzureSynapseSourceTags"]
    config: "GetSourceSourceAzureSynapseSourceConfig"


class GetSourceSourceAzureSynapseSourceCredential(BaseModel):
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


class GetSourceSourceAzureSynapseSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAzureSynapseSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceAzureSynapseSourceTags(TagDetails):
    pass


class GetSourceSourceAzureSynapseSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceSourceDatabricksSource(BaseModel):
    typename__: Literal["DatabricksSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceDatabricksSourceCredential"
    windows: List["GetSourceSourceDatabricksSourceWindows"]
    segmentations: List["GetSourceSourceDatabricksSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceDatabricksSourceTags"]
    config: "GetSourceSourceDatabricksSourceConfig"


class GetSourceSourceDatabricksSourceCredential(BaseModel):
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


class GetSourceSourceDatabricksSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceDatabricksSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceDatabricksSourceTags(TagDetails):
    pass


class GetSourceSourceDatabricksSourceConfig(BaseModel):
    catalog: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceSourceDbtModelRunSource(BaseModel):
    typename__: Literal["DbtModelRunSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceDbtModelRunSourceCredential"
    windows: List["GetSourceSourceDbtModelRunSourceWindows"]
    segmentations: List["GetSourceSourceDbtModelRunSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceDbtModelRunSourceTags"]
    config: "GetSourceSourceDbtModelRunSourceConfig"


class GetSourceSourceDbtModelRunSourceCredential(BaseModel):
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


class GetSourceSourceDbtModelRunSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceDbtModelRunSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceDbtModelRunSourceTags(TagDetails):
    pass


class GetSourceSourceDbtModelRunSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class GetSourceSourceDbtTestResultSource(BaseModel):
    typename__: Literal["DbtTestResultSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceDbtTestResultSourceCredential"
    windows: List["GetSourceSourceDbtTestResultSourceWindows"]
    segmentations: List["GetSourceSourceDbtTestResultSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceDbtTestResultSourceTags"]
    config: "GetSourceSourceDbtTestResultSourceConfig"


class GetSourceSourceDbtTestResultSourceCredential(BaseModel):
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


class GetSourceSourceDbtTestResultSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceDbtTestResultSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceDbtTestResultSourceTags(TagDetails):
    pass


class GetSourceSourceDbtTestResultSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class GetSourceSourceGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceGcpBigQuerySourceCredential"
    windows: List["GetSourceSourceGcpBigQuerySourceWindows"]
    segmentations: List["GetSourceSourceGcpBigQuerySourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceGcpBigQuerySourceTags"]
    config: "GetSourceSourceGcpBigQuerySourceConfig"


class GetSourceSourceGcpBigQuerySourceCredential(BaseModel):
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


class GetSourceSourceGcpBigQuerySourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpBigQuerySourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpBigQuerySourceTags(TagDetails):
    pass


class GetSourceSourceGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceSourceGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceGcpPubSubLiteSourceCredential"
    windows: List["GetSourceSourceGcpPubSubLiteSourceWindows"]
    segmentations: List["GetSourceSourceGcpPubSubLiteSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceGcpPubSubLiteSourceTags"]
    config: "GetSourceSourceGcpPubSubLiteSourceConfig"


class GetSourceSourceGcpPubSubLiteSourceCredential(BaseModel):
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


class GetSourceSourceGcpPubSubLiteSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubLiteSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubLiteSourceTags(TagDetails):
    pass


class GetSourceSourceGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "GetSourceSourceGcpPubSubLiteSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class GetSourceSourceGcpPubSubLiteSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class GetSourceSourceGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceGcpPubSubSourceCredential"
    windows: List["GetSourceSourceGcpPubSubSourceWindows"]
    segmentations: List["GetSourceSourceGcpPubSubSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceGcpPubSubSourceTags"]
    config: "GetSourceSourceGcpPubSubSourceConfig"


class GetSourceSourceGcpPubSubSourceCredential(BaseModel):
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


class GetSourceSourceGcpPubSubSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpPubSubSourceTags(TagDetails):
    pass


class GetSourceSourceGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "GetSourceSourceGcpPubSubSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class GetSourceSourceGcpPubSubSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class GetSourceSourceGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceGcpStorageSourceCredential"
    windows: List["GetSourceSourceGcpStorageSourceWindows"]
    segmentations: List["GetSourceSourceGcpStorageSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceGcpStorageSourceTags"]
    config: "GetSourceSourceGcpStorageSourceConfig"


class GetSourceSourceGcpStorageSourceCredential(BaseModel):
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


class GetSourceSourceGcpStorageSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpStorageSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceGcpStorageSourceTags(TagDetails):
    pass


class GetSourceSourceGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional["GetSourceSourceGcpStorageSourceConfigCsv"]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class GetSourceSourceGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class GetSourceSourceKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceKafkaSourceCredential"
    windows: List["GetSourceSourceKafkaSourceWindows"]
    segmentations: List["GetSourceSourceKafkaSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceKafkaSourceTags"]
    config: "GetSourceSourceKafkaSourceConfig"


class GetSourceSourceKafkaSourceCredential(BaseModel):
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


class GetSourceSourceKafkaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceKafkaSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceKafkaSourceTags(TagDetails):
    pass


class GetSourceSourceKafkaSourceConfig(BaseModel):
    topic: str
    message_format: Optional["GetSourceSourceKafkaSourceConfigMessageFormat"] = Field(
        alias="messageFormat"
    )


class GetSourceSourceKafkaSourceConfigMessageFormat(BaseModel):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class GetSourceSourcePostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourcePostgreSqlSourceCredential"
    windows: List["GetSourceSourcePostgreSqlSourceWindows"]
    segmentations: List["GetSourceSourcePostgreSqlSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourcePostgreSqlSourceTags"]
    config: "GetSourceSourcePostgreSqlSourceConfig"


class GetSourceSourcePostgreSqlSourceCredential(BaseModel):
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


class GetSourceSourcePostgreSqlSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourcePostgreSqlSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourcePostgreSqlSourceTags(TagDetails):
    pass


class GetSourceSourcePostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceSourceSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceSourceSnowflakeSourceCredential"
    windows: List["GetSourceSourceSnowflakeSourceWindows"]
    segmentations: List["GetSourceSourceSnowflakeSourceSegmentations"]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceSourceSnowflakeSourceTags"]
    config: "GetSourceSourceSnowflakeSourceConfig"


class GetSourceSourceSnowflakeSourceCredential(BaseModel):
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


class GetSourceSourceSnowflakeSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSnowflakeSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceSourceSnowflakeSourceTags(TagDetails):
    pass


class GetSourceSourceSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


GetSource.model_rebuild()
GetSourceSourceSource.model_rebuild()
GetSourceSourceSourceCredential.model_rebuild()
GetSourceSourceSourceWindows.model_rebuild()
GetSourceSourceSourceSegmentations.model_rebuild()
GetSourceSourceSourceTags.model_rebuild()
GetSourceSourceAwsAthenaSource.model_rebuild()
GetSourceSourceAwsAthenaSourceCredential.model_rebuild()
GetSourceSourceAwsAthenaSourceWindows.model_rebuild()
GetSourceSourceAwsAthenaSourceSegmentations.model_rebuild()
GetSourceSourceAwsAthenaSourceTags.model_rebuild()
GetSourceSourceAwsAthenaSourceConfig.model_rebuild()
GetSourceSourceAwsKinesisSource.model_rebuild()
GetSourceSourceAwsKinesisSourceCredential.model_rebuild()
GetSourceSourceAwsKinesisSourceWindows.model_rebuild()
GetSourceSourceAwsKinesisSourceSegmentations.model_rebuild()
GetSourceSourceAwsKinesisSourceTags.model_rebuild()
GetSourceSourceAwsKinesisSourceConfig.model_rebuild()
GetSourceSourceAwsKinesisSourceConfigMessageFormat.model_rebuild()
GetSourceSourceAwsRedshiftSource.model_rebuild()
GetSourceSourceAwsRedshiftSourceCredential.model_rebuild()
GetSourceSourceAwsRedshiftSourceWindows.model_rebuild()
GetSourceSourceAwsRedshiftSourceSegmentations.model_rebuild()
GetSourceSourceAwsRedshiftSourceTags.model_rebuild()
GetSourceSourceAwsRedshiftSourceConfig.model_rebuild()
GetSourceSourceAwsS3Source.model_rebuild()
GetSourceSourceAwsS3SourceCredential.model_rebuild()
GetSourceSourceAwsS3SourceWindows.model_rebuild()
GetSourceSourceAwsS3SourceSegmentations.model_rebuild()
GetSourceSourceAwsS3SourceTags.model_rebuild()
GetSourceSourceAwsS3SourceConfig.model_rebuild()
GetSourceSourceAwsS3SourceConfigCsv.model_rebuild()
GetSourceSourceAzureSynapseSource.model_rebuild()
GetSourceSourceAzureSynapseSourceCredential.model_rebuild()
GetSourceSourceAzureSynapseSourceWindows.model_rebuild()
GetSourceSourceAzureSynapseSourceSegmentations.model_rebuild()
GetSourceSourceAzureSynapseSourceTags.model_rebuild()
GetSourceSourceAzureSynapseSourceConfig.model_rebuild()
GetSourceSourceDatabricksSource.model_rebuild()
GetSourceSourceDatabricksSourceCredential.model_rebuild()
GetSourceSourceDatabricksSourceWindows.model_rebuild()
GetSourceSourceDatabricksSourceSegmentations.model_rebuild()
GetSourceSourceDatabricksSourceTags.model_rebuild()
GetSourceSourceDatabricksSourceConfig.model_rebuild()
GetSourceSourceDbtModelRunSource.model_rebuild()
GetSourceSourceDbtModelRunSourceCredential.model_rebuild()
GetSourceSourceDbtModelRunSourceWindows.model_rebuild()
GetSourceSourceDbtModelRunSourceSegmentations.model_rebuild()
GetSourceSourceDbtModelRunSourceTags.model_rebuild()
GetSourceSourceDbtModelRunSourceConfig.model_rebuild()
GetSourceSourceDbtTestResultSource.model_rebuild()
GetSourceSourceDbtTestResultSourceCredential.model_rebuild()
GetSourceSourceDbtTestResultSourceWindows.model_rebuild()
GetSourceSourceDbtTestResultSourceSegmentations.model_rebuild()
GetSourceSourceDbtTestResultSourceTags.model_rebuild()
GetSourceSourceDbtTestResultSourceConfig.model_rebuild()
GetSourceSourceGcpBigQuerySource.model_rebuild()
GetSourceSourceGcpBigQuerySourceCredential.model_rebuild()
GetSourceSourceGcpBigQuerySourceWindows.model_rebuild()
GetSourceSourceGcpBigQuerySourceSegmentations.model_rebuild()
GetSourceSourceGcpBigQuerySourceTags.model_rebuild()
GetSourceSourceGcpBigQuerySourceConfig.model_rebuild()
GetSourceSourceGcpPubSubLiteSource.model_rebuild()
GetSourceSourceGcpPubSubLiteSourceCredential.model_rebuild()
GetSourceSourceGcpPubSubLiteSourceWindows.model_rebuild()
GetSourceSourceGcpPubSubLiteSourceSegmentations.model_rebuild()
GetSourceSourceGcpPubSubLiteSourceTags.model_rebuild()
GetSourceSourceGcpPubSubLiteSourceConfig.model_rebuild()
GetSourceSourceGcpPubSubLiteSourceConfigMessageFormat.model_rebuild()
GetSourceSourceGcpPubSubSource.model_rebuild()
GetSourceSourceGcpPubSubSourceCredential.model_rebuild()
GetSourceSourceGcpPubSubSourceWindows.model_rebuild()
GetSourceSourceGcpPubSubSourceSegmentations.model_rebuild()
GetSourceSourceGcpPubSubSourceTags.model_rebuild()
GetSourceSourceGcpPubSubSourceConfig.model_rebuild()
GetSourceSourceGcpPubSubSourceConfigMessageFormat.model_rebuild()
GetSourceSourceGcpStorageSource.model_rebuild()
GetSourceSourceGcpStorageSourceCredential.model_rebuild()
GetSourceSourceGcpStorageSourceWindows.model_rebuild()
GetSourceSourceGcpStorageSourceSegmentations.model_rebuild()
GetSourceSourceGcpStorageSourceTags.model_rebuild()
GetSourceSourceGcpStorageSourceConfig.model_rebuild()
GetSourceSourceGcpStorageSourceConfigCsv.model_rebuild()
GetSourceSourceKafkaSource.model_rebuild()
GetSourceSourceKafkaSourceCredential.model_rebuild()
GetSourceSourceKafkaSourceWindows.model_rebuild()
GetSourceSourceKafkaSourceSegmentations.model_rebuild()
GetSourceSourceKafkaSourceTags.model_rebuild()
GetSourceSourceKafkaSourceConfig.model_rebuild()
GetSourceSourceKafkaSourceConfigMessageFormat.model_rebuild()
GetSourceSourcePostgreSqlSource.model_rebuild()
GetSourceSourcePostgreSqlSourceCredential.model_rebuild()
GetSourceSourcePostgreSqlSourceWindows.model_rebuild()
GetSourceSourcePostgreSqlSourceSegmentations.model_rebuild()
GetSourceSourcePostgreSqlSourceTags.model_rebuild()
GetSourceSourcePostgreSqlSourceConfig.model_rebuild()
GetSourceSourceSnowflakeSource.model_rebuild()
GetSourceSourceSnowflakeSourceCredential.model_rebuild()
GetSourceSourceSnowflakeSourceWindows.model_rebuild()
GetSourceSourceSnowflakeSourceSegmentations.model_rebuild()
GetSourceSourceSnowflakeSourceTags.model_rebuild()
GetSourceSourceSnowflakeSourceConfig.model_rebuild()
