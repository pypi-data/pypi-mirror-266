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


class GetValidator(BaseModel):
    validator: Optional[
        Annotated[
            Union[
                "GetValidatorValidatorValidator",
                "GetValidatorValidatorCategoricalDistributionValidator",
                "GetValidatorValidatorFreshnessValidator",
                "GetValidatorValidatorNumericAnomalyValidator",
                "GetValidatorValidatorNumericDistributionValidator",
                "GetValidatorValidatorNumericValidator",
                "GetValidatorValidatorRelativeTimeValidator",
                "GetValidatorValidatorRelativeVolumeValidator",
                "GetValidatorValidatorSqlValidator",
                "GetValidatorValidatorVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class GetValidatorValidatorValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorValidatorSourceConfigSource"
    window: "GetValidatorValidatorValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorValidatorSourceConfigSource(BaseModel):
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


class GetValidatorValidatorValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorCategoricalDistributionValidator(BaseModel):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorValidatorCategoricalDistributionValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "GetValidatorValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSource(
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


class GetValidatorValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorCategoricalDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
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


class GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorFreshnessValidatorConfig"


class GetValidatorValidatorFreshnessValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorFreshnessValidatorSourceConfigSource"
    window: "GetValidatorValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorFreshnessValidatorSourceConfigSource(BaseModel):
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


class GetValidatorValidatorFreshnessValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorFreshnessValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorFreshnessValidatorConfig(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    threshold: Union[
        "GetValidatorValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorFreshnessValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorFreshnessValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorNumericAnomalyValidator(BaseModel):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorValidatorNumericAnomalyValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "GetValidatorValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericAnomalyValidatorSourceConfigSource(BaseModel):
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


class GetValidatorValidatorNumericAnomalyValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericAnomalyValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericAnomalyValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class GetValidatorValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
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


class GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericDistributionValidator(BaseModel):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorNumericDistributionValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorNumericDistributionValidatorConfig"
    reference_source_config: "GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorValidatorNumericDistributionValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericDistributionValidatorSourceConfigSource"
    window: "GetValidatorValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericDistributionValidatorSourceConfigSource(BaseModel):
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


class GetValidatorValidatorNumericDistributionValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigSource(
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


class GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorNumericValidatorConfig"


class GetValidatorValidatorNumericValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorNumericValidatorSourceConfigSource"
    window: "GetValidatorValidatorNumericValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorNumericValidatorSourceConfigSource(BaseModel):
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


class GetValidatorValidatorNumericValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorNumericValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorNumericValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorRelativeTimeValidatorConfig"


class GetValidatorValidatorRelativeTimeValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorRelativeTimeValidatorSourceConfigSource"
    window: "GetValidatorValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorRelativeTimeValidatorSourceConfigSource(BaseModel):
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


class GetValidatorValidatorRelativeTimeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeTimeValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeTimeValidatorConfig(BaseModel):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorRelativeVolumeValidator(BaseModel):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorValidatorRelativeVolumeValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "GetValidatorValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorRelativeVolumeValidatorSourceConfigSource(BaseModel):
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


class GetValidatorValidatorRelativeVolumeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeVolumeValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorRelativeVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfig(BaseModel):
    source: "GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
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


class GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorSqlValidator(BaseModel):
    typename__: Literal["SqlValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorSqlValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorSqlValidatorConfig"


class GetValidatorValidatorSqlValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorSqlValidatorSourceConfigSource"
    window: "GetValidatorValidatorSqlValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorSqlValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorSqlValidatorSourceConfigSource(BaseModel):
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


class GetValidatorValidatorSqlValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorSqlValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorSqlValidatorConfig(BaseModel):
    query: str
    threshold: Union[
        "GetValidatorValidatorSqlValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorSqlValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")


class GetValidatorValidatorSqlValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorSqlValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorValidatorVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorValidatorVolumeValidatorConfig"


class GetValidatorValidatorVolumeValidatorSourceConfig(BaseModel):
    source: "GetValidatorValidatorVolumeValidatorSourceConfigSource"
    window: "GetValidatorValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorValidatorVolumeValidatorSourceConfigSource(BaseModel):
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


class GetValidatorValidatorVolumeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorVolumeValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorValidatorVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorValidatorVolumeValidatorConfigThresholdDynamicThreshold(BaseModel):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorValidatorVolumeValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


GetValidator.model_rebuild()
GetValidatorValidatorValidator.model_rebuild()
GetValidatorValidatorValidatorSourceConfig.model_rebuild()
GetValidatorValidatorValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidator.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorSourceConfig.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorConfig.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfig.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorValidatorFreshnessValidator.model_rebuild()
GetValidatorValidatorFreshnessValidatorSourceConfig.model_rebuild()
GetValidatorValidatorFreshnessValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorFreshnessValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorFreshnessValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorFreshnessValidatorConfig.model_rebuild()
GetValidatorValidatorFreshnessValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorValidatorFreshnessValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorValidatorNumericAnomalyValidator.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorSourceConfig.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorConfig.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfig.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorValidatorNumericDistributionValidator.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorSourceConfig.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorConfig.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfig.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorValidatorNumericDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorValidatorNumericValidator.model_rebuild()
GetValidatorValidatorNumericValidatorSourceConfig.model_rebuild()
GetValidatorValidatorNumericValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorNumericValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorNumericValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorNumericValidatorConfig.model_rebuild()
GetValidatorValidatorNumericValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorValidatorNumericValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorValidatorRelativeTimeValidator.model_rebuild()
GetValidatorValidatorRelativeTimeValidatorSourceConfig.model_rebuild()
GetValidatorValidatorRelativeTimeValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorRelativeTimeValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorRelativeTimeValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorRelativeTimeValidatorConfig.model_rebuild()
GetValidatorValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorValidatorRelativeVolumeValidator.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorSourceConfig.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorConfig.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfig.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorValidatorSqlValidator.model_rebuild()
GetValidatorValidatorSqlValidatorSourceConfig.model_rebuild()
GetValidatorValidatorSqlValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorSqlValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorSqlValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorSqlValidatorConfig.model_rebuild()
GetValidatorValidatorSqlValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorValidatorSqlValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorValidatorVolumeValidator.model_rebuild()
GetValidatorValidatorVolumeValidatorSourceConfig.model_rebuild()
GetValidatorValidatorVolumeValidatorSourceConfigSource.model_rebuild()
GetValidatorValidatorVolumeValidatorSourceConfigWindow.model_rebuild()
GetValidatorValidatorVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorValidatorVolumeValidatorConfig.model_rebuild()
GetValidatorValidatorVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorValidatorVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
