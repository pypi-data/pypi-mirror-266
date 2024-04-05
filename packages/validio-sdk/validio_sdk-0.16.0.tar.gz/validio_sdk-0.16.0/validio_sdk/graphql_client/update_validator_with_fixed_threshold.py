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
from .fragments import ErrorDetails


class UpdateValidatorWithFixedThreshold(BaseModel):
    validator_with_fixed_threshold_update: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate" = Field(
        alias="validatorWithFixedThresholdUpdate"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate(BaseModel):
    errors: List[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateErrors"
    ]
    validator: Optional[
        Annotated[
            Union[
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidator",
                "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateErrors(
    ErrorDetails
):
    pass


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidator(
    BaseModel
):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidator(
    BaseModel
):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidator(
    BaseModel
):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfig"


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfig(
    BaseModel
):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidator(
    BaseModel
):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidator(
    BaseModel
):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfig"
    reference_source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidator(
    BaseModel
):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfig"


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidator(
    BaseModel
):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfig"


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfig(
    BaseModel
):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidator(
    BaseModel
):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidator(
    BaseModel
):
    typename__: Literal["SqlValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorConfig"


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorConfig(
    BaseModel
):
    query: str
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidator(
    BaseModel
):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfig"


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfig(
    BaseModel
):
    source: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSource"
    window: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSource(
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


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


UpdateValidatorWithFixedThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateErrors.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdDynamicThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorFreshnessValidatorConfigThresholdFixedThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdDynamicThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorNumericValidatorConfigThresholdFixedThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorConfigThresholdDynamicThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorSqlValidatorConfigThresholdFixedThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidator.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSource.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigWindow.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorSourceConfigSegmentation.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfig.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdateValidatorVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
