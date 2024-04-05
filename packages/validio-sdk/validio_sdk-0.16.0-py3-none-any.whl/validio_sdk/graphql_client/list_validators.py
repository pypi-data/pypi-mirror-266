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


class ListValidators(BaseModel):
    validators_list: List[
        Annotated[
            Union[
                "ListValidatorsValidatorsListValidator",
                "ListValidatorsValidatorsListCategoricalDistributionValidator",
                "ListValidatorsValidatorsListFreshnessValidator",
                "ListValidatorsValidatorsListNumericAnomalyValidator",
                "ListValidatorsValidatorsListNumericDistributionValidator",
                "ListValidatorsValidatorsListNumericValidator",
                "ListValidatorsValidatorsListRelativeTimeValidator",
                "ListValidatorsValidatorsListRelativeVolumeValidator",
                "ListValidatorsValidatorsListSqlValidator",
                "ListValidatorsValidatorsListVolumeValidator",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="validatorsList")


class ListValidatorsValidatorsListValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListValidatorSourceConfigSource(BaseModel):
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


class ListValidatorsValidatorsListValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListCategoricalDistributionValidator(BaseModel):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListCategoricalDistributionValidatorConfig"
    reference_source_config: "ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSource(
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


class ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListCategoricalDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigSource(
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


class ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListFreshnessValidatorConfig"


class ListValidatorsValidatorsListFreshnessValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListFreshnessValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListFreshnessValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListFreshnessValidatorSourceConfigSource(BaseModel):
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


class ListValidatorsValidatorsListFreshnessValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListFreshnessValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListFreshnessValidatorConfig(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    threshold: Union[
        "ListValidatorsValidatorsListFreshnessValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListNumericAnomalyValidator(BaseModel):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListNumericAnomalyValidatorConfig"
    reference_source_config: "ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSource(BaseModel):
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


class ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericAnomalyValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigSource(
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


class ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericDistributionValidator(BaseModel):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListNumericDistributionValidatorConfig"
    reference_source_config: "ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ListValidatorsValidatorsListNumericDistributionValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSource(
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


class ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericDistributionValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigSource(
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


class ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListNumericValidatorConfig"


class ListValidatorsValidatorsListNumericValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListNumericValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListNumericValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListNumericValidatorSourceConfigSource(BaseModel):
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


class ListValidatorsValidatorsListNumericValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListNumericValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListRelativeTimeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListRelativeTimeValidatorConfig"


class ListValidatorsValidatorsListRelativeTimeValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSource(BaseModel):
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


class ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeTimeValidatorConfig(BaseModel):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListRelativeVolumeValidator(BaseModel):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListRelativeVolumeValidatorConfig"
    reference_source_config: "ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSource(BaseModel):
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


class ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListRelativeVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigSource(
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


class ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListSqlValidator(BaseModel):
    typename__: Literal["SqlValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListSqlValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListSqlValidatorConfig"


class ListValidatorsValidatorsListSqlValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListSqlValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListSqlValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListSqlValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListSqlValidatorSourceConfigSource(BaseModel):
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


class ListValidatorsValidatorsListSqlValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListSqlValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListSqlValidatorConfig(BaseModel):
    query: str
    threshold: Union[
        "ListValidatorsValidatorsListSqlValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListSqlValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")


class ListValidatorsValidatorsListSqlValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListSqlValidatorConfigThresholdFixedThreshold(BaseModel):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class ListValidatorsValidatorsListVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "ListValidatorsValidatorsListVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "ListValidatorsValidatorsListVolumeValidatorConfig"


class ListValidatorsValidatorsListVolumeValidatorSourceConfig(BaseModel):
    source: "ListValidatorsValidatorsListVolumeValidatorSourceConfigSource"
    window: "ListValidatorsValidatorsListVolumeValidatorSourceConfigWindow"
    segmentation: "ListValidatorsValidatorsListVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class ListValidatorsValidatorsListVolumeValidatorSourceConfigSource(BaseModel):
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


class ListValidatorsValidatorsListVolumeValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListVolumeValidatorSourceConfigSegmentation(BaseModel):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class ListValidatorsValidatorsListVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "ListValidatorsValidatorsListVolumeValidatorConfigThresholdDynamicThreshold",
        "ListValidatorsValidatorsListVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class ListValidatorsValidatorsListVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class ListValidatorsValidatorsListVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


ListValidators.model_rebuild()
ListValidatorsValidatorsListValidator.model_rebuild()
ListValidatorsValidatorsListValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidator.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorConfig.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfig.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListCategoricalDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListFreshnessValidator.model_rebuild()
ListValidatorsValidatorsListFreshnessValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListFreshnessValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListFreshnessValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListFreshnessValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListFreshnessValidatorConfig.model_rebuild()
ListValidatorsValidatorsListFreshnessValidatorConfigThresholdDynamicThreshold.model_rebuild()
ListValidatorsValidatorsListFreshnessValidatorConfigThresholdFixedThreshold.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidator.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorConfig.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdDynamicThreshold.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorConfigThresholdFixedThreshold.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfig.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListNumericAnomalyValidatorReferenceSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidator.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorConfig.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfig.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListNumericDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListNumericValidator.model_rebuild()
ListValidatorsValidatorsListNumericValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListNumericValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListNumericValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListNumericValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListNumericValidatorConfig.model_rebuild()
ListValidatorsValidatorsListNumericValidatorConfigThresholdDynamicThreshold.model_rebuild()
ListValidatorsValidatorsListNumericValidatorConfigThresholdFixedThreshold.model_rebuild()
ListValidatorsValidatorsListRelativeTimeValidator.model_rebuild()
ListValidatorsValidatorsListRelativeTimeValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListRelativeTimeValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListRelativeTimeValidatorConfig.model_rebuild()
ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdDynamicThreshold.model_rebuild()
ListValidatorsValidatorsListRelativeTimeValidatorConfigThresholdFixedThreshold.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidator.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorConfig.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfig.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListRelativeVolumeValidatorReferenceSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListSqlValidator.model_rebuild()
ListValidatorsValidatorsListSqlValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListSqlValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListSqlValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListSqlValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListSqlValidatorConfig.model_rebuild()
ListValidatorsValidatorsListSqlValidatorConfigThresholdDynamicThreshold.model_rebuild()
ListValidatorsValidatorsListSqlValidatorConfigThresholdFixedThreshold.model_rebuild()
ListValidatorsValidatorsListVolumeValidator.model_rebuild()
ListValidatorsValidatorsListVolumeValidatorSourceConfig.model_rebuild()
ListValidatorsValidatorsListVolumeValidatorSourceConfigSource.model_rebuild()
ListValidatorsValidatorsListVolumeValidatorSourceConfigWindow.model_rebuild()
ListValidatorsValidatorsListVolumeValidatorSourceConfigSegmentation.model_rebuild()
ListValidatorsValidatorsListVolumeValidatorConfig.model_rebuild()
ListValidatorsValidatorsListVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
ListValidatorsValidatorsListVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
