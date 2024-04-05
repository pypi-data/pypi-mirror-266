from datetime import datetime
from typing import Annotated, Any, List, Literal, Optional, Union

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


class GetIncidents(BaseModel):
    incidents_list: List[
        Annotated[
            Union[
                "GetIncidentsIncidentsListIncident",
                "GetIncidentsIncidentsListValidatorIncident",
            ],
            Field(discriminator="typename__"),
        ]
    ] = Field(alias="incidentsList")


class GetIncidentsIncidentsListIncident(BaseModel):
    typename__: Literal["Incident"] = Field(alias="__typename")
    id: Any
    created_at: datetime = Field(alias="createdAt")


class GetIncidentsIncidentsListValidatorIncident(BaseModel):
    typename__: Literal["ValidatorIncident"] = Field(alias="__typename")
    id: Any
    created_at: datetime = Field(alias="createdAt")
    segment: "GetIncidentsIncidentsListValidatorIncidentSegment"
    metric: Union[
        "GetIncidentsIncidentsListValidatorIncidentMetricValidatorMetric",
        "GetIncidentsIncidentsListValidatorIncidentMetricValidatorMetricWithDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentMetricValidatorMetricWithFixedThreshold",
    ] = Field(discriminator="typename__")
    validator: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorValidator",
        "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidator",
        "GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidator",
        "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidator",
        "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidator",
        "GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidator",
        "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidator",
        "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidator",
        "GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidator",
        "GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidator",
    ] = Field(discriminator="typename__")
    source: "GetIncidentsIncidentsListValidatorIncidentSource"
    owner: Optional["GetIncidentsIncidentsListValidatorIncidentOwner"]
    status: IncidentStatus
    severity: IncidentSeverity


class GetIncidentsIncidentsListValidatorIncidentSegment(SegmentDetails):
    pass


class GetIncidentsIncidentsListValidatorIncidentMetricValidatorMetric(BaseModel):
    typename__: Literal["ValidatorMetric"] = Field(alias="__typename")
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    is_incident: bool = Field(alias="isIncident")
    value: float
    deviation: float
    severity: Optional[IncidentSeverity]


class GetIncidentsIncidentsListValidatorIncidentMetricValidatorMetricWithDynamicThreshold(
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


class GetIncidentsIncidentsListValidatorIncidentMetricValidatorMetricWithFixedThreshold(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorValidator(BaseModel):
    typename__: Literal["Validator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidator(
    BaseModel
):
    typename__: Literal["CategoricalDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorConfig"
    reference_source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    categorical_distribution_metric: CategoricalDistributionMetric = Field(
        alias="categoricalDistributionMetric"
    )
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorReferenceSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorReferenceSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidator(BaseModel):
    typename__: Literal["FreshnessValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorConfig"


class GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorConfig(
    BaseModel
):
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    threshold: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorConfigThresholdDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidator(
    BaseModel
):
    typename__: Literal["NumericAnomalyValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorConfig"
    reference_source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    numeric_anomaly_metric: NumericAnomalyMetric = Field(alias="numericAnomalyMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold",
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


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorReferenceSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorReferenceSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidator(
    BaseModel
):
    typename__: Literal["NumericDistributionValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorConfig"
    reference_source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    reference_source_field: JsonPointer = Field(alias="referenceSourceField")
    distribution_metric: NumericDistributionMetric = Field(alias="distributionMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorReferenceSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorReferenceSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidator(BaseModel):
    typename__: Literal["NumericValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorConfig"


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorConfig(
    BaseModel
):
    source_field: JsonPointer = Field(alias="sourceField")
    metric: NumericMetric
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorConfigThresholdDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidator(
    BaseModel
):
    typename__: Literal["RelativeTimeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorConfig"


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorConfig(
    BaseModel
):
    source_field_minuend: JsonPointer = Field(alias="sourceFieldMinuend")
    source_field_subtrahend: JsonPointer = Field(alias="sourceFieldSubtrahend")
    relative_time_metric: RelativeTimeMetric = Field(alias="relativeTimeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidator(
    BaseModel
):
    typename__: Literal["RelativeVolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorConfig"
    reference_source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorReferenceSourceConfig" = Field(
        alias="referenceSourceConfig"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    optional_reference_source_field: Optional[JsonPointer] = Field(
        alias="optionalReferenceSourceField"
    )
    relative_volume_metric: RelativeVolumeMetric = Field(alias="relativeVolumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorReferenceSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorReferenceSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorReferenceSourceConfigWindow"
    history: int
    offset: int
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorReferenceSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorReferenceSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidator(BaseModel):
    typename__: Literal["SqlValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorConfig"


class GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorConfig(BaseModel):
    query: str
    threshold: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorConfigThresholdDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")


class GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidator(BaseModel):
    typename__: Literal["VolumeValidator"] = Field(alias="__typename")
    id: ValidatorId
    name: str
    has_custom_name: bool = Field(alias="hasCustomName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    source_config: "GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfig" = Field(
        alias="sourceConfig"
    )
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")
    config: "GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorConfig"


class GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfig(
    BaseModel
):
    source: "GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfigSource"
    window: "GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfigWindow"
    segmentation: "GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfigSegmentation"
    filter: Optional[JsonFilterExpression]


class GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfigSource(
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


class GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfigWindow(
    BaseModel
):
    typename__: Literal[
        "FileWindow", "FixedBatchWindow", "GlobalWindow", "TumblingWindow", "Window"
    ] = Field(alias="__typename")
    id: WindowId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfigSegmentation(
    BaseModel
):
    typename__: Literal["Segmentation"] = Field(alias="__typename")
    id: SegmentationId
    name: str
    resource_name: str = Field(alias="resourceName")
    resource_namespace: str = Field(alias="resourceNamespace")


class GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorConfig(
    BaseModel
):
    optional_source_field: Optional[JsonPointer] = Field(alias="optionalSourceField")
    source_fields: List[JsonPointer] = Field(alias="sourceFields")
    volume_metric: VolumeMetric = Field(alias="volumeMetric")
    initialize_with_backfill: bool = Field(alias="initializeWithBackfill")
    threshold: Union[
        "GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorConfigThresholdDynamicThreshold",
        "GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorConfigThresholdFixedThreshold",
    ] = Field(discriminator="typename__")


class GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorConfigThresholdDynamicThreshold(
    BaseModel
):
    typename__: Literal["DynamicThreshold"] = Field(alias="__typename")
    sensitivity: float
    decision_bounds_type: Optional[DecisionBoundsType] = Field(
        alias="decisionBoundsType"
    )


class GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorConfigThresholdFixedThreshold(
    BaseModel
):
    typename__: Literal["FixedThreshold"] = Field(alias="__typename")
    operator: ComparisonOperator
    value: float


class GetIncidentsIncidentsListValidatorIncidentSource(SourceBase):
    pass


class GetIncidentsIncidentsListValidatorIncidentOwner(UserSummary):
    pass


GetIncidents.model_rebuild()
GetIncidentsIncidentsListIncident.model_rebuild()
GetIncidentsIncidentsListValidatorIncident.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentSegment.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentMetricValidatorMetric.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentMetricValidatorMetricWithDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentMetricValidatorMetricWithFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorReferenceSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorCategoricalDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorFreshnessValidatorConfigThresholdFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorConfigThresholdFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorReferenceSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorReferenceSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericAnomalyValidatorReferenceSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorConfigThresholdFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorReferenceSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorReferenceSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericDistributionValidatorReferenceSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorNumericValidatorConfigThresholdFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeTimeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorReferenceSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorReferenceSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorRelativeVolumeValidatorReferenceSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorSqlValidatorConfigThresholdFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidator.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfigSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfigWindow.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorSourceConfigSegmentation.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorConfig.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorConfigThresholdDynamicThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentValidatorVolumeValidatorConfigThresholdFixedThreshold.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentSource.model_rebuild()
GetIncidentsIncidentsListValidatorIncidentOwner.model_rebuild()
