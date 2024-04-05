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


class GetSourceByResourceName(BaseModel):
    source_by_resource_name: Optional[
        Annotated[
            Union[
                "GetSourceByResourceNameSourceByResourceNameSource",
                "GetSourceByResourceNameSourceByResourceNameAwsAthenaSource",
                "GetSourceByResourceNameSourceByResourceNameAwsKinesisSource",
                "GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource",
                "GetSourceByResourceNameSourceByResourceNameAwsS3Source",
                "GetSourceByResourceNameSourceByResourceNameAzureSynapseSource",
                "GetSourceByResourceNameSourceByResourceNameDatabricksSource",
                "GetSourceByResourceNameSourceByResourceNameDbtModelRunSource",
                "GetSourceByResourceNameSourceByResourceNameDbtTestResultSource",
                "GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource",
                "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource",
                "GetSourceByResourceNameSourceByResourceNameGcpPubSubSource",
                "GetSourceByResourceNameSourceByResourceNameGcpStorageSource",
                "GetSourceByResourceNameSourceByResourceNameKafkaSource",
                "GetSourceByResourceNameSourceByResourceNamePostgreSqlSource",
                "GetSourceByResourceNameSourceByResourceNameSnowflakeSource",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="sourceByResourceName")


class GetSourceByResourceNameSourceByResourceNameSource(BaseModel):
    typename__: Literal["DemoSource", "Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameSourceTags"]


class GetSourceByResourceNameSourceByResourceNameSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSource(BaseModel):
    typename__: Literal["AwsAthenaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceConfig"


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceConfig(BaseModel):
    catalog: str
    database: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSource(BaseModel):
    typename__: Literal["AwsKinesisSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceConfig"


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceConfig(BaseModel):
    region: str
    stream_name: str = Field(alias="streamName")
    message_format: Optional[
        "GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceConfigMessageFormat(
    BaseModel
):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource(BaseModel):
    typename__: Literal["AwsRedshiftSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceConfig"


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceByResourceNameSourceByResourceNameAwsS3Source(BaseModel):
    typename__: Literal["AwsS3Source"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameAwsS3SourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameAwsS3SourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameAwsS3SourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameAwsS3SourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfig"


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfig(BaseModel):
    bucket: str
    prefix: str
    csv: Optional["GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfigCsv"]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class GetSourceByResourceNameSourceByResourceNameAzureSynapseSource(BaseModel):
    typename__: Literal["AzureSynapseSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceCredential"
    windows: List[
        "GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceWindows"
    ]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceConfig"


class GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceCredential(
    BaseModel
):
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


class GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceByResourceNameSourceByResourceNameDatabricksSource(BaseModel):
    typename__: Literal["DatabricksSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameDatabricksSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameDatabricksSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameDatabricksSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameDatabricksSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameDatabricksSourceConfig"


class GetSourceByResourceNameSourceByResourceNameDatabricksSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameDatabricksSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameDatabricksSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameDatabricksSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameDatabricksSourceConfig(BaseModel):
    catalog: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceByResourceNameSourceByResourceNameDbtModelRunSource(BaseModel):
    typename__: Literal["DbtModelRunSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceConfig"


class GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class GetSourceByResourceNameSourceByResourceNameDbtTestResultSource(BaseModel):
    typename__: Literal["DbtTestResultSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceCredential"
    windows: List[
        "GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceWindows"
    ]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceConfig"


class GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceCredential(
    BaseModel
):
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


class GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceConfig(BaseModel):
    job_name: str = Field(alias="jobName")
    project_name: str = Field(alias="projectName")
    schedule: Optional[CronExpression]


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource(BaseModel):
    typename__: Literal["GcpBigQuerySource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceConfig"


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceConfig(BaseModel):
    project: str
    dataset: str
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource(BaseModel):
    typename__: Literal["GcpPubSubLiteSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceCredential"
    windows: List[
        "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceWindows"
    ]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceConfig"


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceCredential(
    BaseModel
):
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


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceConfig(BaseModel):
    location: str
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceConfigMessageFormat(
    BaseModel
):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSource(BaseModel):
    typename__: Literal["GcpPubSubSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceConfig"


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceConfig(BaseModel):
    project: str
    subscription_id: str = Field(alias="subscriptionId")
    message_format: Optional[
        "GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceConfigMessageFormat(
    BaseModel
):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class GetSourceByResourceNameSourceByResourceNameGcpStorageSource(BaseModel):
    typename__: Literal["GcpStorageSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameGcpStorageSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameGcpStorageSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameGcpStorageSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameGcpStorageSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfig"


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfig(BaseModel):
    project: str
    bucket: str
    folder: str
    csv: Optional[
        "GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfigCsv"
    ]
    schedule: Optional[CronExpression]
    file_pattern: Optional[str] = Field(alias="filePattern")
    file_format: Optional[FileFormat] = Field(alias="fileFormat")


class GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfigCsv(BaseModel):
    null_marker: Optional[str] = Field(alias="nullMarker")
    delimiter: str


class GetSourceByResourceNameSourceByResourceNameKafkaSource(BaseModel):
    typename__: Literal["KafkaSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameKafkaSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameKafkaSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameKafkaSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameKafkaSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameKafkaSourceConfig"


class GetSourceByResourceNameSourceByResourceNameKafkaSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameKafkaSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameKafkaSourceSegmentations(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameKafkaSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameKafkaSourceConfig(BaseModel):
    topic: str
    message_format: Optional[
        "GetSourceByResourceNameSourceByResourceNameKafkaSourceConfigMessageFormat"
    ] = Field(alias="messageFormat")


class GetSourceByResourceNameSourceByResourceNameKafkaSourceConfigMessageFormat(
    BaseModel
):
    format: StreamingSourceMessageFormat
    db_schema: Optional[str] = Field(alias="schema")


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSource(BaseModel):
    typename__: Literal["PostgreSqlSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceConfig"


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceConfig(BaseModel):
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


class GetSourceByResourceNameSourceByResourceNameSnowflakeSource(BaseModel):
    typename__: Literal["SnowflakeSource"] = Field(alias="__typename")
    id: SourceId
    name: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    credential: "GetSourceByResourceNameSourceByResourceNameSnowflakeSourceCredential"
    windows: List["GetSourceByResourceNameSourceByResourceNameSnowflakeSourceWindows"]
    segmentations: List[
        "GetSourceByResourceNameSourceByResourceNameSnowflakeSourceSegmentations"
    ]
    jtd_schema: JsonTypeDefinition = Field(alias="jtdSchema")
    state: SourceState
    state_updated_at: datetime = Field(alias="stateUpdatedAt")
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    tags: List["GetSourceByResourceNameSourceByResourceNameSnowflakeSourceTags"]
    config: "GetSourceByResourceNameSourceByResourceNameSnowflakeSourceConfig"


class GetSourceByResourceNameSourceByResourceNameSnowflakeSourceCredential(BaseModel):
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


class GetSourceByResourceNameSourceByResourceNameSnowflakeSourceWindows(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSnowflakeSourceSegmentations(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceByResourceNameSourceByResourceNameSnowflakeSourceTags(TagDetails):
    pass


class GetSourceByResourceNameSourceByResourceNameSnowflakeSourceConfig(BaseModel):
    role: Optional[str]
    warehouse: Optional[str]
    database: str
    db_schema: str = Field(alias="schema")
    table: str
    cursor_field: Optional[str] = Field(alias="cursorField")
    lookback_days: int = Field(alias="lookbackDays")
    schedule: Optional[CronExpression]


GetSourceByResourceName.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsAthenaSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsKinesisSourceConfigMessageFormat.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsRedshiftSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsS3Source.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAwsS3SourceConfigCsv.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAzureSynapseSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameAzureSynapseSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDatabricksSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDatabricksSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDatabricksSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDatabricksSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDatabricksSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDatabricksSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtModelRunSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtModelRunSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtTestResultSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameDbtTestResultSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpBigQuerySourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSourceConfigMessageFormat.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpPubSubSourceConfigMessageFormat.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpStorageSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameGcpStorageSourceConfigCsv.model_rebuild()
GetSourceByResourceNameSourceByResourceNameKafkaSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameKafkaSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameKafkaSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameKafkaSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameKafkaSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameKafkaSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameKafkaSourceConfigMessageFormat.model_rebuild()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNamePostgreSqlSourceConfig.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSnowflakeSource.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSnowflakeSourceCredential.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSnowflakeSourceWindows.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSnowflakeSourceSegmentations.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSnowflakeSourceTags.model_rebuild()
GetSourceByResourceNameSourceByResourceNameSnowflakeSourceConfig.model_rebuild()
