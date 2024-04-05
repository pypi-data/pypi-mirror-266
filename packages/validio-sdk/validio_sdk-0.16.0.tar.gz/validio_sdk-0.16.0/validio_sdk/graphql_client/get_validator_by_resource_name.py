from datetime import datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import Field

from validio_sdk.scalars import (
    JsonFilterExpression,
    JsonPointer,
    SegmentationId,
    SourceId,
    ValidatorId,
    WindowId,
)

from .base_model import BaseModel
from .enums import (
    CategoricalDistributionMetric,
    ComparisonOperator,
    DecisionBoundsType,
    NumericAnomalyMetric,
    NumericDistributionMetric,
    NumericMetric,
    RelativeTimeMetric,
    RelativeVolumeMetric,
    VolumeMetric,
)


class GetValidatorByResourceName(BaseModel):
    validator_by_resource_name: Optional[
        Annotated[
            Union[
                "GetValidatorByResourceNameValidatorByResourceNameValidator",
                "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator",
                "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator",
                "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator",
                "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator",
                "GetValidatorByResourceNameValidatorByResourceNameNumericValidator",
                "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator",
                "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator",
                "GetValidatorByResourceNameValidatorByResourceNameSqlValidator",
                "GetValidatorByResourceNameValidatorByResourceNameVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="validatorByResourceName")


class GetValidatorByResourceNameValidatorByResourceNameValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfig(BaseModel):
    source: "GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator(
    BaseModel
):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfig"
    reference_source_config: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfig"


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfig(
    BaseModel
):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator(
    BaseModel
):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfig"
    reference_source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator(
    BaseModel
):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfig"
    reference_source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfig"


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfig"


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfig(
    BaseModel
):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator(
    BaseModel
):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfig"
    reference_source_config: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameSqlValidator(BaseModel):
    typename__: Literal["SqlValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameSqlValidatorConfig"


class GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameSqlValidatorConfig(BaseModel):
    query: str
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameSqlValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameSqlValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")


class GetValidatorByResourceNameValidatorByResourceNameSqlValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameSqlValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfig"


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSource"
    window: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSource(
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


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


GetValidatorByResourceName.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameFreshnessValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameNumericValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameSqlValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameSqlValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameSqlValidatorConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameSqlValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameSqlValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidator.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSource.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigWindow.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfig.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorByResourceNameValidatorByResourceNameVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
