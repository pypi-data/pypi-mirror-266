from datetime import datetime
from typing import Any, List, Literal, Optional, Union

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
    IncidentSeverity,
    IncidentStatus,
    NumericAnomalyMetric,
    NumericDistributionMetric,
    NumericMetric,
    RelativeTimeMetric,
    RelativeVolumeMetric,
    VolumeMetric,
)
from .fragments import SegmentDetails, SourceBase, UserSummary


class GetValidatorIncidents(BaseModel):
    validator: Optional["GetValidatorIncidentsValidator"]


class GetValidatorIncidentsValidator(BaseModel):
    typename__: Literal[
        "CategoricalDistributionValidator",
        "FreshnessValidator",
        "NumericAnomalyValidator",
        "NumericDistributionValidator",
        "NumericValidator",
        "RelativeTimeValidator",
        "RelativeVolumeValidator",
        "SqlValidator",
        "Validator",
        "VolumeValidator",
    ] = Field(alias="__typename")
    id: ValidatorId
    incidents: List["GetValidatorIncidentsValidatorIncidents"]


class GetValidatorIncidentsValidatorIncidents(BaseModel):
    typename__: Literal["ValidatorIncident"] = Field(alias="__typename")
    id: Any
    created_at: datetime = Field(alias="createdAt")
    segment: "GetValidatorIncidentsValidatorIncidentsSegment"
    metric: Union[
        "GetValidatorIncidentsValidatorIncidentsMetricValidatorMetric",
        "GetValidatorIncidentsValidatorIncidentsMetricValidatorMetricWithDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsMetricValidatorMetricWithFixedThreshold",
    ] = Field(discriminator="typename__")
    validator: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorValidator",
        "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidator",
        "GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidator",
        "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidator",
        "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidator",
        "GetValidatorIncidentsValidatorIncidentsValidatorNumericValidator",
        "GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidator",
        "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidator",
        "GetValidatorIncidentsValidatorIncidentsValidatorSqlValidator",
        "GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidator",
    ] = Field(discriminator="typename__")
    source: "GetValidatorIncidentsValidatorIncidentsSource"
    owner: Optional["GetValidatorIncidentsValidatorIncidentsOwner"]
    status: IncidentStatus
    severity: IncidentSeverity


class GetValidatorIncidentsValidatorIncidentsSegment(SegmentDetails):
    pass


class GetValidatorIncidentsValidatorIncidentsMetricValidatorMetric(BaseModel):
    typename__: Literal["ValidatorMetric"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    deviation: float
    severity: Optional[IncidentSeverity]


class GetValidatorIncidentsValidatorIncidentsMetricValidatorMetricWithDynamicThreshold(
    BaseModel
):
    typename__: Literal["ValidatorMetricWithDynamicThreshold"] = Field(
        alias="__typename"
    )
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    deviation: float
    severity: Optional[IncidentSeverity]
    lower_bound: float = Field(alias="lowerBound")
    upper_bound: float = Field(alias="upperBound")
    decision_bounds_type: DecisionBoundsType = Field(alias="decisionBoundsType")
    is_burn_in: bool = Field(alias="isBurnIn")


class GetValidatorIncidentsValidatorIncidentsMetricValidatorMetricWithFixedThreshold(
    BaseModel
):
    typename__: Literal["ValidatorMetricWithFixedThreshold"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    deviation: float
    severity: Optional[IncidentSeverity]
    operator: ComparisonOperator
    bound: float


class GetValidatorIncidentsValidatorIncidentsValidatorValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfig(BaseModel):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidator(
    BaseModel
):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorConfig"


class GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorConfig(
    BaseModel
):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    threshold: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidator(
    BaseModel
):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidator(
    BaseModel
):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorConfig"
    reference_source_config: "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorConfig"


class GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorConfig"


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorConfig(
    BaseModel
):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidator(
    BaseModel
):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorSqlValidator(BaseModel):
    typename__: Literal["SqlValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorConfig"


class GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorConfig(BaseModel):
    query: str
    threshold: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorConfigThresholdDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")


class GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorConfig"


class GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfigSource"
    window: "GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfigSource(
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


class GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetValidatorIncidentsValidatorIncidentsSource(SourceBase):
    pass


class GetValidatorIncidentsValidatorIncidentsOwner(UserSummary):
    pass


GetValidatorIncidents.model_rebuild()
GetValidatorIncidentsValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidents.model_rebuild()
GetValidatorIncidentsValidatorIncidentsSegment.model_rebuild()
GetValidatorIncidentsValidatorIncidentsMetricValidatorMetric.model_rebuild()
GetValidatorIncidentsValidatorIncidentsMetricValidatorMetricWithDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsMetricValidatorMetricWithFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorFreshnessValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorReferenceSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorNumericValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorSqlValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorSqlValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidator.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfigSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfigWindow.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorConfig.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsValidatorVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetValidatorIncidentsValidatorIncidentsSource.model_rebuild()
GetValidatorIncidentsValidatorIncidentsOwner.model_rebuild()
