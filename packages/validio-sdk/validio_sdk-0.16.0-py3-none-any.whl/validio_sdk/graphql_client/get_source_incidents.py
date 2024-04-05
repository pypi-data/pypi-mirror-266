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


class GetSourceIncidents(BaseModel):
    source: Optional["GetSourceIncidentsSource"]


class GetSourceIncidentsSource(BaseModel):
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
    incidents: List["GetSourceIncidentsSourceIncidents"]


class GetSourceIncidentsSourceIncidents(BaseModel):
    typename__: Literal["ValidatorIncident"] = Field(alias="__typename")
    id: Any
    created_at: datetime = Field(alias="createdAt")
    segment: "GetSourceIncidentsSourceIncidentsSegment"
    metric: Union[
        "GetSourceIncidentsSourceIncidentsMetricValidatorMetric",
        "GetSourceIncidentsSourceIncidentsMetricValidatorMetricWithDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsMetricValidatorMetricWithFixedThreshold",
    ] = Field(discriminator="typename__")
    validator: Union[
        "GetSourceIncidentsSourceIncidentsValidatorValidator",
        "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidator",
        "GetSourceIncidentsSourceIncidentsValidatorFreshnessValidator",
        "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidator",
        "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidator",
        "GetSourceIncidentsSourceIncidentsValidatorNumericValidator",
        "GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidator",
        "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidator",
        "GetSourceIncidentsSourceIncidentsValidatorSqlValidator",
        "GetSourceIncidentsSourceIncidentsValidatorVolumeValidator",
    ] = Field(discriminator="typename__")
    source: "GetSourceIncidentsSourceIncidentsSource"
    owner: Optional["GetSourceIncidentsSourceIncidentsOwner"]
    status: IncidentStatus
    severity: IncidentSeverity


class GetSourceIncidentsSourceIncidentsSegment(SegmentDetails):
    pass


class GetSourceIncidentsSourceIncidentsMetricValidatorMetric(BaseModel):
    typename__: Literal["ValidatorMetric"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    deviation: float
    severity: Optional[IncidentSeverity]


class GetSourceIncidentsSourceIncidentsMetricValidatorMetricWithDynamicThreshold(
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


class GetSourceIncidentsSourceIncidentsMetricValidatorMetricWithFixedThreshold(
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


class GetSourceIncidentsSourceIncidentsValidatorValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfig" = (
        Field(alias="sourceConfig")
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfig(BaseModel):
    source: "GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfigSource(BaseModel):
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


class GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfigWindow(BaseModel):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidator(
    BaseModel
):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorConfig"


class GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorConfig(BaseModel):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    threshold: Union[
        "GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidator(BaseModel):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidator(BaseModel):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorConfig"
    reference_source_config: "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceIncidentsSourceIncidentsValidatorNumericValidatorConfig"


class GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfig(BaseModel):
    source: "GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorNumericValidatorConfig(BaseModel):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetSourceIncidentsSourceIncidentsValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetSourceIncidentsSourceIncidentsValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetSourceIncidentsSourceIncidentsValidatorNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidator(BaseModel):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorConfig"


class GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorConfig(BaseModel):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidator(BaseModel):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorSqlValidator(BaseModel):
    typename__: Literal["SqlValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceIncidentsSourceIncidentsValidatorSqlValidatorConfig"


class GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfig(BaseModel):
    source: "GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorSqlValidatorConfig(BaseModel):
    query: str
    threshold: Union[
        "GetSourceIncidentsSourceIncidentsValidatorSqlValidatorConfigThresholdDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsValidatorSqlValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")


class GetSourceIncidentsSourceIncidentsValidatorSqlValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetSourceIncidentsSourceIncidentsValidatorSqlValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetSourceIncidentsSourceIncidentsValidatorVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorConfig"


class GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfig(BaseModel):
    source: "GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfigSource"
    window: "GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfigSource(
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


class GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorConfig(BaseModel):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetSourceIncidentsSourceIncidentsSource(SourceBase):
    pass


class GetSourceIncidentsSourceIncidentsOwner(UserSummary):
    pass


GetSourceIncidents.model_rebuild()
GetSourceIncidentsSource.model_rebuild()
GetSourceIncidentsSourceIncidents.model_rebuild()
GetSourceIncidentsSourceIncidentsSegment.model_rebuild()
GetSourceIncidentsSourceIncidentsMetricValidatorMetric.model_rebuild()
GetSourceIncidentsSourceIncidentsMetricValidatorMetricWithDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsMetricValidatorMetricWithFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorFreshnessValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorFreshnessValidatorConfigThresholdFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorReferenceSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericValidatorConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorNumericValidatorConfigThresholdFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorSqlValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorSqlValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorSqlValidatorConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorSqlValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorSqlValidatorConfigThresholdFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorVolumeValidator.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfigSource.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfigWindow.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorConfig.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsValidatorVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetSourceIncidentsSourceIncidentsSource.model_rebuild()
GetSourceIncidentsSourceIncidentsOwner.model_rebuild()
