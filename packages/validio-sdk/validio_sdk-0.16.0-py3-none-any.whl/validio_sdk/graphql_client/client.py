from typing import Any, Dict, List, Optional, Union

from validio_sdk.scalars import (
    CredentialId,
    JsonTypeDefinition,
    SegmentationId,
    SourceId,
    ValidatorId,
    WindowId,
)

from .apply_validator_recommendation import (
    ApplyValidatorRecommendation,
    ApplyValidatorRecommendationValidatorRecommendationApply,
)
from .async_base_client import AsyncBaseClient
from .aws_athena_credential_secret_changed import (
    AwsAthenaCredentialSecretChanged,
    AwsAthenaCredentialSecretChangedAwsAthenaCredentialSecretChanged,
)
from .aws_credential_secret_changed import (
    AwsCredentialSecretChanged,
    AwsCredentialSecretChangedAwsCredentialSecretChanged,
)
from .aws_redshift_credential_secret_changed import (
    AwsRedshiftCredentialSecretChanged,
    AwsRedshiftCredentialSecretChangedAwsRedshiftCredentialSecretChanged,
)
from .azure_synapse_entra_id_credential_secret_changed import (
    AzureSynapseEntraIdCredentialSecretChanged,
    AzureSynapseEntraIdCredentialSecretChangedAzureSynapseEntraIdCredentialSecretChanged,
)
from .azure_synapse_sql_credential_secret_changed import (
    AzureSynapseSqlCredentialSecretChanged,
    AzureSynapseSqlCredentialSecretChangedAzureSynapseSqlCredentialSecretChanged,
)
from .backfill_source import BackfillSource, BackfillSourceSourceBackfill
from .base_model import UNSET, UnsetType
from .create_aws_athena_credential import (
    CreateAwsAthenaCredential,
    CreateAwsAthenaCredentialAwsAthenaCredentialCreate,
)
from .create_aws_athena_source import (
    CreateAwsAthenaSource,
    CreateAwsAthenaSourceAwsAthenaSourceCreate,
)
from .create_aws_credential import (
    CreateAwsCredential,
    CreateAwsCredentialAwsCredentialCreate,
)
from .create_aws_kinesis_source import (
    CreateAwsKinesisSource,
    CreateAwsKinesisSourceAwsKinesisSourceCreate,
)
from .create_aws_redshift_credential import (
    CreateAwsRedshiftCredential,
    CreateAwsRedshiftCredentialAwsRedshiftCredentialCreate,
)
from .create_aws_redshift_source import (
    CreateAwsRedshiftSource,
    CreateAwsRedshiftSourceAwsRedshiftSourceCreate,
)
from .create_aws_s3_source import CreateAwsS3Source, CreateAwsS3SourceAwsS3SourceCreate
from .create_azure_synapse_entra_id_credential import (
    CreateAzureSynapseEntraIdCredential,
    CreateAzureSynapseEntraIdCredentialAzureSynapseEntraIdCredentialCreate,
)
from .create_azure_synapse_source import (
    CreateAzureSynapseSource,
    CreateAzureSynapseSourceAzureSynapseSourceCreate,
)
from .create_azure_synapse_sql_credential import (
    CreateAzureSynapseSqlCredential,
    CreateAzureSynapseSqlCredentialAzureSynapseSqlCredentialCreate,
)
from .create_categorical_distribution_validator_with_dynamic_threshold import (
    CreateCategoricalDistributionValidatorWithDynamicThreshold,
    CreateCategoricalDistributionValidatorWithDynamicThresholdCategoricalDistributionValidatorWithDynamicThresholdCreate,
)
from .create_categorical_distribution_validator_with_fixed_threshold import (
    CreateCategoricalDistributionValidatorWithFixedThreshold,
    CreateCategoricalDistributionValidatorWithFixedThresholdCategoricalDistributionValidatorWithFixedThresholdCreate,
)
from .create_databricks_credential import (
    CreateDatabricksCredential,
    CreateDatabricksCredentialDatabricksCredentialCreate,
)
from .create_databricks_source import (
    CreateDatabricksSource,
    CreateDatabricksSourceDatabricksSourceCreate,
)
from .create_dbt_cloud_credential import (
    CreateDbtCloudCredential,
    CreateDbtCloudCredentialDbtCloudCredentialCreate,
)
from .create_dbt_core_credential import (
    CreateDbtCoreCredential,
    CreateDbtCoreCredentialDbtCoreCredentialCreate,
)
from .create_dbt_model_run_source import (
    CreateDbtModelRunSource,
    CreateDbtModelRunSourceDbtModelRunSourceCreate,
)
from .create_dbt_test_result_source import (
    CreateDbtTestResultSource,
    CreateDbtTestResultSourceDbtTestResultSourceCreate,
)
from .create_demo_credential import (
    CreateDemoCredential,
    CreateDemoCredentialDemoCredentialCreate,
)
from .create_demo_source import CreateDemoSource, CreateDemoSourceDemoSourceCreate
from .create_file_window import CreateFileWindow, CreateFileWindowFileWindowCreate
from .create_fixed_batch_window import (
    CreateFixedBatchWindow,
    CreateFixedBatchWindowFixedBatchWindowCreate,
)
from .create_freshness_validator_with_dynamic_threshold import (
    CreateFreshnessValidatorWithDynamicThreshold,
    CreateFreshnessValidatorWithDynamicThresholdFreshnessValidatorWithDynamicThresholdCreate,
)
from .create_freshness_validator_with_fixed_threshold import (
    CreateFreshnessValidatorWithFixedThreshold,
    CreateFreshnessValidatorWithFixedThresholdFreshnessValidatorWithFixedThresholdCreate,
)
from .create_gcp_big_query_source import (
    CreateGcpBigQuerySource,
    CreateGcpBigQuerySourceGcpBigQuerySourceCreate,
)
from .create_gcp_credential import (
    CreateGcpCredential,
    CreateGcpCredentialGcpCredentialCreate,
)
from .create_gcp_pub_sub_lite_source import (
    CreateGcpPubSubLiteSource,
    CreateGcpPubSubLiteSourceGcpPubSubLiteSourceCreate,
)
from .create_gcp_pub_sub_source import (
    CreateGcpPubSubSource,
    CreateGcpPubSubSourceGcpPubSubSourceCreate,
)
from .create_gcp_storage_source import (
    CreateGcpStorageSource,
    CreateGcpStorageSourceGcpStorageSourceCreate,
)
from .create_global_window import (
    CreateGlobalWindow,
    CreateGlobalWindowGlobalWindowCreate,
)
from .create_kafka_sasl_ssl_plain_credential import (
    CreateKafkaSaslSslPlainCredential,
    CreateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialCreate,
)
from .create_kafka_source import CreateKafkaSource, CreateKafkaSourceKafkaSourceCreate
from .create_kafka_ssl_credential import (
    CreateKafkaSslCredential,
    CreateKafkaSslCredentialKafkaSslCredentialCreate,
)
from .create_ms_teams_channel import (
    CreateMsTeamsChannel,
    CreateMsTeamsChannelMsTeamsChannelCreate,
)
from .create_notification_rule import (
    CreateNotificationRule,
    CreateNotificationRuleNotificationRuleCreate,
)
from .create_numeric_anomaly_validator_with_dynamic_threshold import (
    CreateNumericAnomalyValidatorWithDynamicThreshold,
    CreateNumericAnomalyValidatorWithDynamicThresholdNumericAnomalyValidatorWithDynamicThresholdCreate,
)
from .create_numeric_anomaly_validator_with_fixed_threshold import (
    CreateNumericAnomalyValidatorWithFixedThreshold,
    CreateNumericAnomalyValidatorWithFixedThresholdNumericAnomalyValidatorWithFixedThresholdCreate,
)
from .create_numeric_distribution_validator_with_dynamic_threshold import (
    CreateNumericDistributionValidatorWithDynamicThreshold,
    CreateNumericDistributionValidatorWithDynamicThresholdNumericDistributionValidatorWithDynamicThresholdCreate,
)
from .create_numeric_distribution_validator_with_fixed_threshold import (
    CreateNumericDistributionValidatorWithFixedThreshold,
    CreateNumericDistributionValidatorWithFixedThresholdNumericDistributionValidatorWithFixedThresholdCreate,
)
from .create_numeric_validator_with_dynamic_threshold import (
    CreateNumericValidatorWithDynamicThreshold,
    CreateNumericValidatorWithDynamicThresholdNumericValidatorWithDynamicThresholdCreate,
)
from .create_numeric_validator_with_fixed_threshold import (
    CreateNumericValidatorWithFixedThreshold,
    CreateNumericValidatorWithFixedThresholdNumericValidatorWithFixedThresholdCreate,
)
from .create_owner_notification_rule_condition import (
    CreateOwnerNotificationRuleCondition,
    CreateOwnerNotificationRuleConditionOwnerNotificationRuleConditionCreate,
)
from .create_postgre_sql_credential import (
    CreatePostgreSqlCredential,
    CreatePostgreSqlCredentialPostgreSqlCredentialCreate,
)
from .create_postgre_sql_source import (
    CreatePostgreSqlSource,
    CreatePostgreSqlSourcePostgreSqlSourceCreate,
)
from .create_relative_time_validator_with_dynamic_threshold import (
    CreateRelativeTimeValidatorWithDynamicThreshold,
    CreateRelativeTimeValidatorWithDynamicThresholdRelativeTimeValidatorWithDynamicThresholdCreate,
)
from .create_relative_time_validator_with_fixed_threshold import (
    CreateRelativeTimeValidatorWithFixedThreshold,
    CreateRelativeTimeValidatorWithFixedThresholdRelativeTimeValidatorWithFixedThresholdCreate,
)
from .create_relative_volume_validator_with_dynamic_threshold import (
    CreateRelativeVolumeValidatorWithDynamicThreshold,
    CreateRelativeVolumeValidatorWithDynamicThresholdRelativeVolumeValidatorWithDynamicThresholdCreate,
)
from .create_relative_volume_validator_with_fixed_threshold import (
    CreateRelativeVolumeValidatorWithFixedThreshold,
    CreateRelativeVolumeValidatorWithFixedThresholdRelativeVolumeValidatorWithFixedThresholdCreate,
)
from .create_saml_identity_provider import (
    CreateSamlIdentityProvider,
    CreateSamlIdentityProviderSamlIdentityProviderCreate,
)
from .create_segment_notification_rule_condition import (
    CreateSegmentNotificationRuleCondition,
    CreateSegmentNotificationRuleConditionSegmentNotificationRuleConditionCreate,
)
from .create_segmentation import (
    CreateSegmentation,
    CreateSegmentationSegmentationCreate,
)
from .create_severity_notification_rule_condition import (
    CreateSeverityNotificationRuleCondition,
    CreateSeverityNotificationRuleConditionSeverityNotificationRuleConditionCreate,
)
from .create_slack_channel import (
    CreateSlackChannel,
    CreateSlackChannelSlackChannelCreate,
)
from .create_snowflake_credential import (
    CreateSnowflakeCredential,
    CreateSnowflakeCredentialSnowflakeCredentialCreate,
)
from .create_snowflake_source import (
    CreateSnowflakeSource,
    CreateSnowflakeSourceSnowflakeSourceCreate,
)
from .create_source_notification_rule_condition import (
    CreateSourceNotificationRuleCondition,
    CreateSourceNotificationRuleConditionSourceNotificationRuleConditionCreate,
)
from .create_sql_validator_with_dynamic_threshold import (
    CreateSqlValidatorWithDynamicThreshold,
    CreateSqlValidatorWithDynamicThresholdSqlValidatorWithDynamicThresholdCreate,
)
from .create_sql_validator_with_fixed_threshold import (
    CreateSqlValidatorWithFixedThreshold,
    CreateSqlValidatorWithFixedThresholdSqlValidatorWithFixedThresholdCreate,
)
from .create_tableau_connected_app_credential import (
    CreateTableauConnectedAppCredential,
    CreateTableauConnectedAppCredentialTableauConnectedAppCredentialCreate,
)
from .create_tableau_personal_access_token_credential import (
    CreateTableauPersonalAccessTokenCredential,
    CreateTableauPersonalAccessTokenCredentialTableauPersonalAccessTokenCredentialCreate,
)
from .create_tag_notification_rule_condition import (
    CreateTagNotificationRuleCondition,
    CreateTagNotificationRuleConditionTagNotificationRuleConditionCreate,
)
from .create_tumbling_window import (
    CreateTumblingWindow,
    CreateTumblingWindowTumblingWindowCreate,
)
from .create_type_notification_rule_condition import (
    CreateTypeNotificationRuleCondition,
    CreateTypeNotificationRuleConditionTypeNotificationRuleConditionCreate,
)
from .create_user import CreateUser, CreateUserUserCreate
from .create_volume_validator_with_dynamic_threshold import (
    CreateVolumeValidatorWithDynamicThreshold,
    CreateVolumeValidatorWithDynamicThresholdVolumeValidatorWithDynamicThresholdCreate,
)
from .create_volume_validator_with_fixed_threshold import (
    CreateVolumeValidatorWithFixedThreshold,
    CreateVolumeValidatorWithFixedThresholdVolumeValidatorWithFixedThresholdCreate,
)
from .create_webhook_channel import (
    CreateWebhookChannel,
    CreateWebhookChannelWebhookChannelCreate,
)
from .databricks_credential_secret_changed import (
    DatabricksCredentialSecretChanged,
    DatabricksCredentialSecretChangedDatabricksCredentialSecretChanged,
)
from .dbt_artifact_multipart_upload_append_part import (
    DbtArtifactMultipartUploadAppendPart,
    DbtArtifactMultipartUploadAppendPartDbtArtifactMultipartUploadAppendPart,
)
from .dbt_artifact_multipart_upload_complete import (
    DbtArtifactMultipartUploadComplete,
    DbtArtifactMultipartUploadCompleteDbtArtifactMultipartUploadComplete,
)
from .dbt_artifact_multipart_upload_create import (
    DbtArtifactMultipartUploadCreate,
    DbtArtifactMultipartUploadCreateDbtArtifactMultipartUploadCreate,
)
from .dbt_artifact_upload import DbtArtifactUpload, DbtArtifactUploadDbtArtifactUpload
from .delete_channel import DeleteChannel, DeleteChannelChannelDelete
from .delete_credential import DeleteCredential, DeleteCredentialCredentialsDelete
from .delete_credentials import DeleteCredentials, DeleteCredentialsCredentialsDelete
from .delete_identity import DeleteIdentity, DeleteIdentityIdentityDelete
from .delete_identity_provider import (
    DeleteIdentityProvider,
    DeleteIdentityProviderIdentityProviderDelete,
)
from .delete_notification_rule import (
    DeleteNotificationRule,
    DeleteNotificationRuleNotificationRuleDelete,
)
from .delete_segmentation import (
    DeleteSegmentation,
    DeleteSegmentationSegmentationsDelete,
)
from .delete_source import DeleteSource, DeleteSourceSourcesDelete
from .delete_sources import DeleteSources, DeleteSourcesSourcesDelete
from .delete_user import DeleteUser, DeleteUserUserDelete
from .delete_validators import DeleteValidators, DeleteValidatorsValidatorsDelete
from .delete_window import DeleteWindow, DeleteWindowWindowsDelete
from .delete_windows import DeleteWindows, DeleteWindowsWindowsDelete
from .dismiss_validator_recommendation import (
    DismissValidatorRecommendation,
    DismissValidatorRecommendationValidatorRecommendationDismiss,
)
from .gcp_credential_secret_changed import (
    GcpCredentialSecretChanged,
    GcpCredentialSecretChangedGcpCredentialSecretChanged,
)
from .get_channel_by_resource_name import (
    GetChannelByResourceName,
    GetChannelByResourceNameChannelByResourceNameChannel,
    GetChannelByResourceNameChannelByResourceNameMsTeamsChannel,
    GetChannelByResourceNameChannelByResourceNameSlackChannel,
    GetChannelByResourceNameChannelByResourceNameWebhookChannel,
)
from .get_channels import (
    GetChannels,
    GetChannelsChannelsChannel,
    GetChannelsChannelsMsTeamsChannel,
    GetChannelsChannelsSlackChannel,
    GetChannelsChannelsWebhookChannel,
)
from .get_credential_by_resource_name import (
    GetCredentialByResourceName,
    GetCredentialByResourceNameCredentialByResourceNameAwsAthenaCredential,
    GetCredentialByResourceNameCredentialByResourceNameAwsCredential,
    GetCredentialByResourceNameCredentialByResourceNameAwsRedshiftCredential,
    GetCredentialByResourceNameCredentialByResourceNameAzureSynapseEntraIdCredential,
    GetCredentialByResourceNameCredentialByResourceNameAzureSynapseSqlCredential,
    GetCredentialByResourceNameCredentialByResourceNameCredential,
    GetCredentialByResourceNameCredentialByResourceNameDatabricksCredential,
    GetCredentialByResourceNameCredentialByResourceNameDbtCloudCredential,
    GetCredentialByResourceNameCredentialByResourceNameDbtCoreCredential,
    GetCredentialByResourceNameCredentialByResourceNameKafkaSaslSslPlainCredential,
    GetCredentialByResourceNameCredentialByResourceNameKafkaSslCredential,
    GetCredentialByResourceNameCredentialByResourceNameLookerCredential,
    GetCredentialByResourceNameCredentialByResourceNamePostgreSqlCredential,
    GetCredentialByResourceNameCredentialByResourceNameSnowflakeCredential,
    GetCredentialByResourceNameCredentialByResourceNameTableauConnectedAppCredential,
    GetCredentialByResourceNameCredentialByResourceNameTableauPersonalAccessTokenCredential,
)
from .get_databricks_warehouse_info import (
    GetDatabricksWarehouseInfo,
    GetDatabricksWarehouseInfoDatabricksWarehouseInfo,
)
from .get_identity_provider_by_resource_name import (
    GetIdentityProviderByResourceName,
    GetIdentityProviderByResourceNameIdentityProviderByResourceNameIdentityProvider,
    GetIdentityProviderByResourceNameIdentityProviderByResourceNameSamlIdentityProvider,
)
from .get_identity_providers import (
    GetIdentityProviders,
    GetIdentityProvidersIdentityProvidersIdentityProvider,
    GetIdentityProvidersIdentityProvidersSamlIdentityProvider,
)
from .get_incidents import (
    GetIncidents,
    GetIncidentsIncidentsListIncident,
    GetIncidentsIncidentsListValidatorIncident,
)
from .get_notification_rule import (
    GetNotificationRule,
    GetNotificationRuleNotificationRule,
)
from .get_notification_rule_by_resource_name import (
    GetNotificationRuleByResourceName,
    GetNotificationRuleByResourceNameNotificationRuleByResourceName,
)
from .get_notification_rules import (
    GetNotificationRules,
    GetNotificationRulesNotificationRules,
)
from .get_segmentation import GetSegmentation, GetSegmentationSegmentation
from .get_segmentation_by_resource_name import (
    GetSegmentationByResourceName,
    GetSegmentationByResourceNameSegmentationByResourceName,
)
from .get_segments_by_segmentation import (
    GetSegmentsBySegmentation,
    GetSegmentsBySegmentationSegmentation,
)
from .get_source import (
    GetSource,
    GetSourceSourceAwsAthenaSource,
    GetSourceSourceAwsKinesisSource,
    GetSourceSourceAwsRedshiftSource,
    GetSourceSourceAwsS3Source,
    GetSourceSourceAzureSynapseSource,
    GetSourceSourceDatabricksSource,
    GetSourceSourceDbtModelRunSource,
    GetSourceSourceDbtTestResultSource,
    GetSourceSourceGcpBigQuerySource,
    GetSourceSourceGcpPubSubLiteSource,
    GetSourceSourceGcpPubSubSource,
    GetSourceSourceGcpStorageSource,
    GetSourceSourceKafkaSource,
    GetSourceSourcePostgreSqlSource,
    GetSourceSourceSnowflakeSource,
    GetSourceSourceSource,
)
from .get_source_by_resource_name import (
    GetSourceByResourceName,
    GetSourceByResourceNameSourceByResourceNameAwsAthenaSource,
    GetSourceByResourceNameSourceByResourceNameAwsKinesisSource,
    GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource,
    GetSourceByResourceNameSourceByResourceNameAwsS3Source,
    GetSourceByResourceNameSourceByResourceNameAzureSynapseSource,
    GetSourceByResourceNameSourceByResourceNameDatabricksSource,
    GetSourceByResourceNameSourceByResourceNameDbtModelRunSource,
    GetSourceByResourceNameSourceByResourceNameDbtTestResultSource,
    GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource,
    GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource,
    GetSourceByResourceNameSourceByResourceNameGcpPubSubSource,
    GetSourceByResourceNameSourceByResourceNameGcpStorageSource,
    GetSourceByResourceNameSourceByResourceNameKafkaSource,
    GetSourceByResourceNameSourceByResourceNamePostgreSqlSource,
    GetSourceByResourceNameSourceByResourceNameSnowflakeSource,
    GetSourceByResourceNameSourceByResourceNameSource,
)
from .get_source_incidents import GetSourceIncidents, GetSourceIncidentsSource
from .get_source_recommended_validators import (
    GetSourceRecommendedValidators,
    GetSourceRecommendedValidatorsSource,
)
from .get_user_by_resource_name import (
    GetUserByResourceName,
    GetUserByResourceNameUserByResourceName,
)
from .get_users import GetUsers, GetUsersUsers
from .get_validator import (
    GetValidator,
    GetValidatorValidatorCategoricalDistributionValidator,
    GetValidatorValidatorFreshnessValidator,
    GetValidatorValidatorNumericAnomalyValidator,
    GetValidatorValidatorNumericDistributionValidator,
    GetValidatorValidatorNumericValidator,
    GetValidatorValidatorRelativeTimeValidator,
    GetValidatorValidatorRelativeVolumeValidator,
    GetValidatorValidatorSqlValidator,
    GetValidatorValidatorValidator,
    GetValidatorValidatorVolumeValidator,
)
from .get_validator_by_resource_name import (
    GetValidatorByResourceName,
    GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator,
    GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator,
    GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator,
    GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator,
    GetValidatorByResourceNameValidatorByResourceNameNumericValidator,
    GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator,
    GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator,
    GetValidatorByResourceNameValidatorByResourceNameSqlValidator,
    GetValidatorByResourceNameValidatorByResourceNameValidator,
    GetValidatorByResourceNameValidatorByResourceNameVolumeValidator,
)
from .get_validator_incidents import (
    GetValidatorIncidents,
    GetValidatorIncidentsValidator,
)
from .get_validator_metric_debug_info import (
    GetValidatorMetricDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsAthenaSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsRedShiftSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsS3SourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoAzureSynapseSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpBigQuerySourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpStorageSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoPostgreSQLSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoSnowflakeSourceDebugInfo,
    GetValidatorMetricDebugInfoValidatorMetricDebugInfoValidatorMetricDebugInfo,
)
from .get_validator_metric_debug_records import (
    GetValidatorMetricDebugRecords,
    GetValidatorMetricDebugRecordsValidatorMetricDebugRecords,
)
from .get_validator_segment_metrics import (
    GetValidatorSegmentMetrics,
    GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistory,
    GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistory,
)
from .get_window_by_resource_name import (
    GetWindowByResourceName,
    GetWindowByResourceNameWindowByResourceNameFileWindow,
    GetWindowByResourceNameWindowByResourceNameFixedBatchWindow,
    GetWindowByResourceNameWindowByResourceNameTumblingWindow,
    GetWindowByResourceNameWindowByResourceNameWindow,
)
from .infer_aws_athena_schema import InferAwsAthenaSchema
from .infer_aws_kinesis_schema import InferAwsKinesisSchema
from .infer_aws_redshift_schema import InferAwsRedshiftSchema
from .infer_aws_s3_schema import InferAwsS3Schema
from .infer_azure_synapse_schema import InferAzureSynapseSchema
from .infer_databricks_schema import InferDatabricksSchema
from .infer_dbt_model_run_schema import InferDbtModelRunSchema
from .infer_dbt_test_result_schema import InferDbtTestResultSchema
from .infer_demo_schema import InferDemoSchema
from .infer_gcp_big_query_schema import InferGcpBigQuerySchema
from .infer_gcp_pub_sub_lite_schema import InferGcpPubSubLiteSchema
from .infer_gcp_pub_sub_schema import InferGcpPubSubSchema
from .infer_gcp_storage_schema import InferGcpStorageSchema
from .infer_kafka_schema import InferKafkaSchema
from .infer_postgre_sql_schema import InferPostgreSqlSchema
from .infer_sample_schema import InferSampleSchema
from .infer_snowflake_schema import InferSnowflakeSchema
from .input_types import (
    AwsAthenaCredentialCreateInput,
    AwsAthenaCredentialSecretChangedInput,
    AwsAthenaCredentialUpdateInput,
    AwsAthenaInferSchemaInput,
    AwsAthenaSourceCreateInput,
    AwsAthenaSourceUpdateInput,
    AwsCredentialCreateInput,
    AwsCredentialSecretChangedInput,
    AwsCredentialUpdateInput,
    AwsKinesisInferSchemaInput,
    AwsKinesisSourceCreateInput,
    AwsKinesisSourceUpdateInput,
    AwsRedshiftCredentialCreateInput,
    AwsRedshiftCredentialSecretChangedInput,
    AwsRedshiftCredentialUpdateInput,
    AwsRedshiftInferSchemaInput,
    AwsRedshiftSourceCreateInput,
    AwsRedshiftSourceUpdateInput,
    AwsS3InferSchemaInput,
    AwsS3SourceCreateInput,
    AwsS3SourceUpdateInput,
    AzureSynapseEntraIdCredentialCreateInput,
    AzureSynapseEntraIdCredentialSecretChangedInput,
    AzureSynapseEntraIdCredentialUpdateInput,
    AzureSynapseInferSchemaInput,
    AzureSynapseSourceCreateInput,
    AzureSynapseSourceUpdateInput,
    AzureSynapseSqlCredentialCreateInput,
    AzureSynapseSqlCredentialSecretChangedInput,
    AzureSynapseSqlCredentialUpdateInput,
    CategoricalDistributionValidatorCreateInput,
    CategoricalDistributionValidatorUpdateInput,
    ChannelDeleteInput,
    DatabricksCredentialCreateInput,
    DatabricksCredentialSecretChangedInput,
    DatabricksCredentialUpdateInput,
    DatabricksInferSchemaInput,
    DatabricksListCatalogsInput,
    DatabricksListSchemasInput,
    DatabricksListTablesInput,
    DatabricksSourceCreateInput,
    DatabricksSourceUpdateInput,
    DatabricksStartWarehouseInput,
    DatabricksWarehouseInfoInput,
    DbtArtifactMultipartUploadAppendPartInput,
    DbtArtifactMultipartUploadCompleteInput,
    DbtArtifactMultipartUploadCreateInput,
    DbtArtifactUploadInput,
    DbtCloudCredentialCreateInput,
    DbtCloudCredentialUpdateInput,
    DbtCoreCredentialCreateInput,
    DbtCoreCredentialUpdateInput,
    DbtModelListJobsInput,
    DbtModelRunSourceCreateInput,
    DbtModelRunSourceUpdateInput,
    DbtTestResultSourceCreateInput,
    DbtTestResultSourceUpdateInput,
    DemoCredentialCreateInput,
    DemoSourceCreateInput,
    DynamicThresholdCreateInput,
    FileWindowCreateInput,
    FixedBatchWindowCreateInput,
    FixedBatchWindowUpdateInput,
    FixedThresholdCreateInput,
    FreshnessValidatorCreateInput,
    FreshnessValidatorUpdateInput,
    GcpBigQueryInferSchemaInput,
    GcpBigQuerySourceCreateInput,
    GcpBigQuerySourceUpdateInput,
    GcpCredentialCreateInput,
    GcpCredentialSecretChangedInput,
    GcpCredentialUpdateInput,
    GcpPubSubInferSchemaInput,
    GcpPubSubLiteInferSchemaInput,
    GcpPubSubLiteSourceCreateInput,
    GcpPubSubLiteSourceUpdateInput,
    GcpPubSubSourceCreateInput,
    GcpPubSubSourceUpdateInput,
    GcpStorageInferSchemaInput,
    GcpStorageSourceCreateInput,
    GcpStorageSourceUpdateInput,
    GlobalWindowCreateInput,
    IdentityDeleteInput,
    IdentityProviderDeleteInput,
    KafkaInferSchemaInput,
    KafkaSaslSslPlainCredentialCreateInput,
    KafkaSaslSslPlainCredentialSecretChangedInput,
    KafkaSaslSslPlainCredentialUpdateInput,
    KafkaSourceCreateInput,
    KafkaSourceUpdateInput,
    KafkaSslCredentialCreateInput,
    KafkaSslCredentialSecretChangedInput,
    KafkaSslCredentialUpdateInput,
    LocalIdentityProviderUpdateInput,
    LookerCredentialSecretChangedInput,
    MsTeamsChannelCreateInput,
    MsTeamsChannelUpdateInput,
    NotificationRuleCreateInput,
    NotificationRuleDeleteInput,
    NotificationRuleUpdateInput,
    NumericAnomalyValidatorCreateInput,
    NumericAnomalyValidatorUpdateInput,
    NumericDistributionValidatorCreateInput,
    NumericDistributionValidatorUpdateInput,
    NumericValidatorCreateInput,
    NumericValidatorUpdateInput,
    OwnerNotificationRuleConditionCreateInput,
    OwnerNotificationRuleConditionUpdateInput,
    PostgreSqlCredentialCreateInput,
    PostgreSqlCredentialSecretChangedInput,
    PostgreSqlCredentialUpdateInput,
    PostgreSqlInferSchemaInput,
    PostgreSqlSourceCreateInput,
    PostgreSqlSourceUpdateInput,
    RelativeTimeValidatorCreateInput,
    RelativeTimeValidatorUpdateInput,
    RelativeVolumeValidatorCreateInput,
    RelativeVolumeValidatorUpdateInput,
    ResourceFilter,
    ResourceNamespaceUpdateInput,
    SamlIdentityProviderCreateInput,
    SamlIdentityProviderUpdateInput,
    SegmentationCreateInput,
    SegmentNotificationRuleConditionCreateInput,
    SegmentNotificationRuleConditionUpdateInput,
    SeverityNotificationRuleConditionCreateInput,
    SeverityNotificationRuleConditionUpdateInput,
    SlackChannelCreateInput,
    SlackChannelUpdateInput,
    SnowflakeCredentialCreateInput,
    SnowflakeCredentialSecretChangedInput,
    SnowflakeCredentialUpdateInput,
    SnowflakeInferSchemaInput,
    SnowflakeSourceCreateInput,
    SnowflakeSourceUpdateInput,
    SourceNotificationRuleConditionCreateInput,
    SourceNotificationRuleConditionUpdateInput,
    SourceOwnerUpdateInput,
    SqlValidatorCreateInput,
    TableauConnectedAppCredentialCreateInput,
    TableauConnectedAppCredentialSecretChangedInput,
    TableauConnectedAppCredentialUpdateInput,
    TableauPersonalAccessTokenCredentialCreateInput,
    TableauPersonalAccessTokenCredentialSecretChangedInput,
    TableauPersonalAccessTokenCredentialUpdateInput,
    TagNotificationRuleConditionCreateInput,
    TagNotificationRuleConditionUpdateInput,
    TimeRangeInput,
    TumblingWindowCreateInput,
    TumblingWindowUpdateInput,
    TypeNotificationRuleConditionCreateInput,
    TypeNotificationRuleConditionUpdateInput,
    UserCreateInput,
    UserDeleteInput,
    UserUpdateInput,
    ValidatorMetricDebugInfoInput,
    ValidatorRecommendationApplyInput,
    ValidatorRecommendationDismissInput,
    ValidatorSegmentMetricsInput,
    ValidatorWithDynamicThresholdUpdateInput,
    ValidatorWithFixedThresholdUpdateInput,
    VolumeValidatorCreateInput,
    VolumeValidatorUpdateInput,
    WebhookChannelCreateInput,
    WebhookChannelUpdateInput,
)
from .kafka_sasl_ssl_plain_credential_secret_changed import (
    KafkaSaslSslPlainCredentialSecretChanged,
    KafkaSaslSslPlainCredentialSecretChangedKafkaSaslSslPlainCredentialSecretChanged,
)
from .kafka_ssl_credential_secret_changed import (
    KafkaSslCredentialSecretChanged,
    KafkaSslCredentialSecretChangedKafkaSslCredentialSecretChanged,
)
from .list_credentials import (
    ListCredentials,
    ListCredentialsCredentialsListAwsAthenaCredential,
    ListCredentialsCredentialsListAwsCredential,
    ListCredentialsCredentialsListAwsRedshiftCredential,
    ListCredentialsCredentialsListAzureSynapseEntraIdCredential,
    ListCredentialsCredentialsListAzureSynapseSqlCredential,
    ListCredentialsCredentialsListCredential,
    ListCredentialsCredentialsListDatabricksCredential,
    ListCredentialsCredentialsListDbtCloudCredential,
    ListCredentialsCredentialsListDbtCoreCredential,
    ListCredentialsCredentialsListKafkaSaslSslPlainCredential,
    ListCredentialsCredentialsListKafkaSslCredential,
    ListCredentialsCredentialsListLookerCredential,
    ListCredentialsCredentialsListPostgreSqlCredential,
    ListCredentialsCredentialsListSnowflakeCredential,
    ListCredentialsCredentialsListTableauConnectedAppCredential,
    ListCredentialsCredentialsListTableauPersonalAccessTokenCredential,
)
from .list_databricks_catalogs import ListDatabricksCatalogs
from .list_databricks_schemas import ListDatabricksSchemas
from .list_databricks_tables import ListDatabricksTables
from .list_dbt_model_jobs import ListDbtModelJobs
from .list_dbt_model_projects import ListDbtModelProjects
from .list_resource_namespaces import (
    ListResourceNamespaces,
    ListResourceNamespacesResourceNamespacesList,
)
from .list_segmentations import ListSegmentations, ListSegmentationsSegmentationsList
from .list_sources import (
    ListSources,
    ListSourcesSourcesListAwsAthenaSource,
    ListSourcesSourcesListAwsKinesisSource,
    ListSourcesSourcesListAwsRedshiftSource,
    ListSourcesSourcesListAwsS3Source,
    ListSourcesSourcesListAzureSynapseSource,
    ListSourcesSourcesListDatabricksSource,
    ListSourcesSourcesListDbtModelRunSource,
    ListSourcesSourcesListDbtTestResultSource,
    ListSourcesSourcesListGcpBigQuerySource,
    ListSourcesSourcesListGcpPubSubLiteSource,
    ListSourcesSourcesListGcpPubSubSource,
    ListSourcesSourcesListGcpStorageSource,
    ListSourcesSourcesListKafkaSource,
    ListSourcesSourcesListPostgreSqlSource,
    ListSourcesSourcesListSnowflakeSource,
    ListSourcesSourcesListSource,
)
from .list_tags import ListTags, ListTagsTagsList
from .list_validators import (
    ListValidators,
    ListValidatorsValidatorsListCategoricalDistributionValidator,
    ListValidatorsValidatorsListFreshnessValidator,
    ListValidatorsValidatorsListNumericAnomalyValidator,
    ListValidatorsValidatorsListNumericDistributionValidator,
    ListValidatorsValidatorsListNumericValidator,
    ListValidatorsValidatorsListRelativeTimeValidator,
    ListValidatorsValidatorsListRelativeVolumeValidator,
    ListValidatorsValidatorsListSqlValidator,
    ListValidatorsValidatorsListValidator,
    ListValidatorsValidatorsListVolumeValidator,
)
from .list_windows import (
    ListWindows,
    ListWindowsWindowsListFileWindow,
    ListWindowsWindowsListFixedBatchWindow,
    ListWindowsWindowsListTumblingWindow,
    ListWindowsWindowsListWindow,
)
from .looker_credential_secret_changed import (
    LookerCredentialSecretChanged,
    LookerCredentialSecretChangedLookerCredentialSecretChanged,
)
from .poll_source import PollSource, PollSourceSourcePoll
from .postgre_sql_credential_secret_changed import (
    PostgreSqlCredentialSecretChanged,
    PostgreSqlCredentialSecretChangedPostgreSqlCredentialSecretChanged,
)
from .reset_source import ResetSource, ResetSourceSourceReset
from .segments import Segments, SegmentsSegments
from .segments_by_resource_name import (
    SegmentsByResourceName,
    SegmentsByResourceNameSegmentsByResourceName,
)
from .snowflake_credential_secret_changed import (
    SnowflakeCredentialSecretChanged,
    SnowflakeCredentialSecretChangedSnowflakeCredentialSecretChanged,
)
from .start_databricks_warehouse import StartDatabricksWarehouse
from .start_source import StartSource, StartSourceSourceStart
from .stop_source import StopSource, StopSourceSourceStop
from .tableau_connected_app_credential_secret_changed import (
    TableauConnectedAppCredentialSecretChanged,
    TableauConnectedAppCredentialSecretChangedTableauConnectedAppCredentialSecretChanged,
)
from .tableau_personal_access_token_credential_secret_changed import (
    TableauPersonalAccessTokenCredentialSecretChanged,
    TableauPersonalAccessTokenCredentialSecretChangedTableauPersonalAccessTokenCredentialSecretChanged,
)
from .update_aws_athena_credential import (
    UpdateAwsAthenaCredential,
    UpdateAwsAthenaCredentialAwsAthenaCredentialUpdate,
)
from .update_aws_athena_source import (
    UpdateAwsAthenaSource,
    UpdateAwsAthenaSourceAwsAthenaSourceUpdate,
)
from .update_aws_credential import (
    UpdateAwsCredential,
    UpdateAwsCredentialAwsCredentialUpdate,
)
from .update_aws_kinesis_source import (
    UpdateAwsKinesisSource,
    UpdateAwsKinesisSourceAwsKinesisSourceUpdate,
)
from .update_aws_redshift_credential import (
    UpdateAwsRedshiftCredential,
    UpdateAwsRedshiftCredentialAwsRedshiftCredentialUpdate,
)
from .update_aws_redshift_source import (
    UpdateAwsRedshiftSource,
    UpdateAwsRedshiftSourceAwsRedshiftSourceUpdate,
)
from .update_aws_s3_source import UpdateAwsS3Source, UpdateAwsS3SourceAwsS3SourceUpdate
from .update_azure_synapse_entra_id_credential import (
    UpdateAzureSynapseEntraIdCredential,
    UpdateAzureSynapseEntraIdCredentialAzureSynapseEntraIdCredentialUpdate,
)
from .update_azure_synapse_source import (
    UpdateAzureSynapseSource,
    UpdateAzureSynapseSourceAzureSynapseSourceUpdate,
)
from .update_azure_synapse_sql_credential import (
    UpdateAzureSynapseSqlCredential,
    UpdateAzureSynapseSqlCredentialAzureSynapseSqlCredentialUpdate,
)
from .update_categorical_distribution_validator import (
    UpdateCategoricalDistributionValidator,
    UpdateCategoricalDistributionValidatorCategoricalDistributionValidatorUpdate,
)
from .update_channel_namespace import (
    UpdateChannelNamespace,
    UpdateChannelNamespaceChannelNamespaceUpdate,
)
from .update_credential_namespace import (
    UpdateCredentialNamespace,
    UpdateCredentialNamespaceCredentialNamespaceUpdate,
)
from .update_databricks_credential import (
    UpdateDatabricksCredential,
    UpdateDatabricksCredentialDatabricksCredentialUpdate,
)
from .update_databricks_source import (
    UpdateDatabricksSource,
    UpdateDatabricksSourceDatabricksSourceUpdate,
)
from .update_dbt_cloud_credential import (
    UpdateDbtCloudCredential,
    UpdateDbtCloudCredentialDbtCloudCredentialUpdate,
)
from .update_dbt_core_credential import (
    UpdateDbtCoreCredential,
    UpdateDbtCoreCredentialDbtCoreCredentialUpdate,
)
from .update_dbt_model_run_source import (
    UpdateDbtModelRunSource,
    UpdateDbtModelRunSourceDbtModelRunSourceUpdate,
)
from .update_dbt_test_result_source import (
    UpdateDbtTestResultSource,
    UpdateDbtTestResultSourceDbtTestResultSourceUpdate,
)
from .update_fixed_batch_window import (
    UpdateFixedBatchWindow,
    UpdateFixedBatchWindowFixedBatchWindowUpdate,
)
from .update_freshness_validator import (
    UpdateFreshnessValidator,
    UpdateFreshnessValidatorFreshnessValidatorUpdate,
)
from .update_gcp_big_query_source import (
    UpdateGcpBigQuerySource,
    UpdateGcpBigQuerySourceGcpBigQuerySourceUpdate,
)
from .update_gcp_credential import (
    UpdateGcpCredential,
    UpdateGcpCredentialGcpCredentialUpdate,
)
from .update_gcp_pub_sub_lite_source import (
    UpdateGcpPubSubLiteSource,
    UpdateGcpPubSubLiteSourceGcpPubSubLiteSourceUpdate,
)
from .update_gcp_pub_sub_source import (
    UpdateGcpPubSubSource,
    UpdateGcpPubSubSourceGcpPubSubSourceUpdate,
)
from .update_gcp_storage_source import (
    UpdateGcpStorageSource,
    UpdateGcpStorageSourceGcpStorageSourceUpdate,
)
from .update_identity_provider_namespace import (
    UpdateIdentityProviderNamespace,
    UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate,
)
from .update_kafka_sasl_ssl_plain_credential import (
    UpdateKafkaSaslSslPlainCredential,
    UpdateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialUpdate,
)
from .update_kafka_source import UpdateKafkaSource, UpdateKafkaSourceKafkaSourceUpdate
from .update_kafka_ssl_credential import (
    UpdateKafkaSslCredential,
    UpdateKafkaSslCredentialKafkaSslCredentialUpdate,
)
from .update_local_identity_provider import (
    UpdateLocalIdentityProvider,
    UpdateLocalIdentityProviderLocalIdentityProviderUpdate,
)
from .update_ms_teams_channel import (
    UpdateMsTeamsChannel,
    UpdateMsTeamsChannelMsTeamsChannelUpdate,
)
from .update_notification_rule import (
    UpdateNotificationRule,
    UpdateNotificationRuleNotificationRuleUpdate,
)
from .update_notification_rule_namespace import (
    UpdateNotificationRuleNamespace,
    UpdateNotificationRuleNamespaceNotificationRuleNamespaceUpdate,
)
from .update_numeric_anomaly_validator import (
    UpdateNumericAnomalyValidator,
    UpdateNumericAnomalyValidatorNumericAnomalyValidatorUpdate,
)
from .update_numeric_distribution_validator import (
    UpdateNumericDistributionValidator,
    UpdateNumericDistributionValidatorNumericDistributionValidatorUpdate,
)
from .update_numeric_validator import (
    UpdateNumericValidator,
    UpdateNumericValidatorNumericValidatorUpdate,
)
from .update_owner_notification_rule_condition import (
    UpdateOwnerNotificationRuleCondition,
    UpdateOwnerNotificationRuleConditionOwnerNotificationRuleConditionUpdate,
)
from .update_postgre_sql_credential import (
    UpdatePostgreSqlCredential,
    UpdatePostgreSqlCredentialPostgreSqlCredentialUpdate,
)
from .update_postgre_sql_source import (
    UpdatePostgreSqlSource,
    UpdatePostgreSqlSourcePostgreSqlSourceUpdate,
)
from .update_relative_time_validator import (
    UpdateRelativeTimeValidator,
    UpdateRelativeTimeValidatorRelativeTimeValidatorUpdate,
)
from .update_relative_volume_validator import (
    UpdateRelativeVolumeValidator,
    UpdateRelativeVolumeValidatorRelativeVolumeValidatorUpdate,
)
from .update_saml_identity_provider import (
    UpdateSamlIdentityProvider,
    UpdateSamlIdentityProviderSamlIdentityProviderUpdate,
)
from .update_segment_notification_rule_condition import (
    UpdateSegmentNotificationRuleCondition,
    UpdateSegmentNotificationRuleConditionSegmentNotificationRuleConditionUpdate,
)
from .update_segmentation_namespace import (
    UpdateSegmentationNamespace,
    UpdateSegmentationNamespaceSegmentationNamespaceUpdate,
)
from .update_severity_notification_rule_condition import (
    UpdateSeverityNotificationRuleCondition,
    UpdateSeverityNotificationRuleConditionSeverityNotificationRuleConditionUpdate,
)
from .update_slack_channel import (
    UpdateSlackChannel,
    UpdateSlackChannelSlackChannelUpdate,
)
from .update_snowflake_credential import (
    UpdateSnowflakeCredential,
    UpdateSnowflakeCredentialSnowflakeCredentialUpdate,
)
from .update_snowflake_source import (
    UpdateSnowflakeSource,
    UpdateSnowflakeSourceSnowflakeSourceUpdate,
)
from .update_source_namespace import (
    UpdateSourceNamespace,
    UpdateSourceNamespaceSourceNamespaceUpdate,
)
from .update_source_notification_rule_condition import (
    UpdateSourceNotificationRuleCondition,
    UpdateSourceNotificationRuleConditionSourceNotificationRuleConditionUpdate,
)
from .update_source_owner import UpdateSourceOwner, UpdateSourceOwnerSourceOwnerUpdate
from .update_tableau_connected_app_credential import (
    UpdateTableauConnectedAppCredential,
    UpdateTableauConnectedAppCredentialTableauConnectedAppCredentialUpdate,
)
from .update_tableau_personal_access_token_credential import (
    UpdateTableauPersonalAccessTokenCredential,
    UpdateTableauPersonalAccessTokenCredentialTableauPersonalAccessTokenCredentialUpdate,
)
from .update_tag_notification_rule_condition import (
    UpdateTagNotificationRuleCondition,
    UpdateTagNotificationRuleConditionTagNotificationRuleConditionUpdate,
)
from .update_tumbling_window import (
    UpdateTumblingWindow,
    UpdateTumblingWindowTumblingWindowUpdate,
)
from .update_type_notification_rule_condition import (
    UpdateTypeNotificationRuleCondition,
    UpdateTypeNotificationRuleConditionTypeNotificationRuleConditionUpdate,
)
from .update_user import UpdateUser, UpdateUserUserUpdate
from .update_user_namespace import (
    UpdateUserNamespace,
    UpdateUserNamespaceUserNamespaceUpdate,
)
from .update_validator_namespace import (
    UpdateValidatorNamespace,
    UpdateValidatorNamespaceValidatorNamespaceUpdate,
)
from .update_validator_with_dynamic_threshold import (
    UpdateValidatorWithDynamicThreshold,
    UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdate,
)
from .update_validator_with_fixed_threshold import (
    UpdateValidatorWithFixedThreshold,
    UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate,
)
from .update_volume_validator import (
    UpdateVolumeValidator,
    UpdateVolumeValidatorVolumeValidatorUpdate,
)
from .update_webhook_channel import (
    UpdateWebhookChannel,
    UpdateWebhookChannelWebhookChannelUpdate,
)
from .update_window_namespace import (
    UpdateWindowNamespace,
    UpdateWindowNamespaceWindowNamespaceUpdate,
)
from .verify_source_schema import (
    VerifySourceSchema,
    VerifySourceSchemaSourceSchemaVerify,
)


def gql(q: str) -> str:
    return q


class Client(AsyncBaseClient):
    async def apply_validator_recommendation(
        self, input: ValidatorRecommendationApplyInput
    ) -> ApplyValidatorRecommendationValidatorRecommendationApply:
        query = gql(
            """
            mutation ApplyValidatorRecommendation($input: ValidatorRecommendationApplyInput!) {
              validatorRecommendationApply(input: $input) {
                ...ValidatorRecommendationApplication
              }
            }

            fragment ValidatorRecommendationApplication on ValidatorRecommendationApplyResult {
              __typename
              failedIds
              successIds
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ApplyValidatorRecommendation.model_validate(
            data
        ).validator_recommendation_apply

    async def aws_athena_credential_secret_changed(
        self, input: AwsAthenaCredentialSecretChangedInput
    ) -> AwsAthenaCredentialSecretChangedAwsAthenaCredentialSecretChanged:
        query = gql(
            """
            query AwsAthenaCredentialSecretChanged($input: AwsAthenaCredentialSecretChangedInput!) {
              awsAthenaCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AwsAthenaCredentialSecretChanged.model_validate(
            data
        ).aws_athena_credential_secret_changed

    async def aws_credential_secret_changed(
        self, input: AwsCredentialSecretChangedInput
    ) -> AwsCredentialSecretChangedAwsCredentialSecretChanged:
        query = gql(
            """
            query AwsCredentialSecretChanged($input: AwsCredentialSecretChangedInput!) {
              awsCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AwsCredentialSecretChanged.model_validate(
            data
        ).aws_credential_secret_changed

    async def aws_redshift_credential_secret_changed(
        self, input: AwsRedshiftCredentialSecretChangedInput
    ) -> AwsRedshiftCredentialSecretChangedAwsRedshiftCredentialSecretChanged:
        query = gql(
            """
            query AwsRedshiftCredentialSecretChanged($input: AwsRedshiftCredentialSecretChangedInput!) {
              awsRedshiftCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AwsRedshiftCredentialSecretChanged.model_validate(
            data
        ).aws_redshift_credential_secret_changed

    async def azure_synapse_entra_id_credential_secret_changed(
        self, input: AzureSynapseEntraIdCredentialSecretChangedInput
    ) -> AzureSynapseEntraIdCredentialSecretChangedAzureSynapseEntraIdCredentialSecretChanged:
        query = gql(
            """
            query AzureSynapseEntraIdCredentialSecretChanged($input: AzureSynapseEntraIdCredentialSecretChangedInput!) {
              azureSynapseEntraIdCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AzureSynapseEntraIdCredentialSecretChanged.model_validate(
            data
        ).azure_synapse_entra_id_credential_secret_changed

    async def azure_synapse_sql_credential_secret_changed(
        self, input: AzureSynapseSqlCredentialSecretChangedInput
    ) -> AzureSynapseSqlCredentialSecretChangedAzureSynapseSqlCredentialSecretChanged:
        query = gql(
            """
            query AzureSynapseSqlCredentialSecretChanged($input: AzureSynapseSqlCredentialSecretChangedInput!) {
              azureSynapseSqlCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AzureSynapseSqlCredentialSecretChanged.model_validate(
            data
        ).azure_synapse_sql_credential_secret_changed

    async def backfill_source(self, id: SourceId) -> BackfillSourceSourceBackfill:
        query = gql(
            """
            mutation BackfillSource($id: SourceId!) {
              sourceBackfill(id: $id) {
                errors {
                  ...ErrorDetails
                }
                state
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return BackfillSource.model_validate(data).source_backfill

    async def create_aws_athena_credential(
        self, input: AwsAthenaCredentialCreateInput
    ) -> CreateAwsAthenaCredentialAwsAthenaCredentialCreate:
        query = gql(
            """
            mutation CreateAwsAthenaCredential($input: AwsAthenaCredentialCreateInput!) {
              awsAthenaCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsAthenaCredential.model_validate(
            data
        ).aws_athena_credential_create

    async def create_aws_athena_source(
        self, input: AwsAthenaSourceCreateInput
    ) -> CreateAwsAthenaSourceAwsAthenaSourceCreate:
        query = gql(
            """
            mutation CreateAwsAthenaSource($input: AwsAthenaSourceCreateInput!) {
              awsAthenaSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsAthenaSource.model_validate(data).aws_athena_source_create

    async def create_aws_credential(
        self, input: AwsCredentialCreateInput
    ) -> CreateAwsCredentialAwsCredentialCreate:
        query = gql(
            """
            mutation CreateAwsCredential($input: AwsCredentialCreateInput!) {
              awsCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsCredential.model_validate(data).aws_credential_create

    async def create_aws_kinesis_source(
        self, input: AwsKinesisSourceCreateInput
    ) -> CreateAwsKinesisSourceAwsKinesisSourceCreate:
        query = gql(
            """
            mutation CreateAwsKinesisSource($input: AwsKinesisSourceCreateInput!) {
              awsKinesisSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsKinesisSource.model_validate(data).aws_kinesis_source_create

    async def create_aws_redshift_credential(
        self, input: AwsRedshiftCredentialCreateInput
    ) -> CreateAwsRedshiftCredentialAwsRedshiftCredentialCreate:
        query = gql(
            """
            mutation CreateAwsRedshiftCredential($input: AwsRedshiftCredentialCreateInput!) {
              awsRedshiftCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsRedshiftCredential.model_validate(
            data
        ).aws_redshift_credential_create

    async def create_aws_redshift_source(
        self, input: AwsRedshiftSourceCreateInput
    ) -> CreateAwsRedshiftSourceAwsRedshiftSourceCreate:
        query = gql(
            """
            mutation CreateAwsRedshiftSource($input: AwsRedshiftSourceCreateInput!) {
              awsRedshiftSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsRedshiftSource.model_validate(data).aws_redshift_source_create

    async def create_aws_s3_source(
        self, input: AwsS3SourceCreateInput
    ) -> CreateAwsS3SourceAwsS3SourceCreate:
        query = gql(
            """
            mutation CreateAwsS3Source($input: AwsS3SourceCreateInput!) {
              awsS3SourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAwsS3Source.model_validate(data).aws_s3_source_create

    async def create_azure_synapse_entra_id_credential(
        self, input: AzureSynapseEntraIdCredentialCreateInput
    ) -> CreateAzureSynapseEntraIdCredentialAzureSynapseEntraIdCredentialCreate:
        query = gql(
            """
            mutation CreateAzureSynapseEntraIdCredential($input: AzureSynapseEntraIdCredentialCreateInput!) {
              azureSynapseEntraIdCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAzureSynapseEntraIdCredential.model_validate(
            data
        ).azure_synapse_entra_id_credential_create

    async def create_azure_synapse_source(
        self, input: AzureSynapseSourceCreateInput
    ) -> CreateAzureSynapseSourceAzureSynapseSourceCreate:
        query = gql(
            """
            mutation CreateAzureSynapseSource($input: AzureSynapseSourceCreateInput!) {
              azureSynapseSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAzureSynapseSource.model_validate(data).azure_synapse_source_create

    async def create_azure_synapse_sql_credential(
        self, input: AzureSynapseSqlCredentialCreateInput
    ) -> CreateAzureSynapseSqlCredentialAzureSynapseSqlCredentialCreate:
        query = gql(
            """
            mutation CreateAzureSynapseSqlCredential($input: AzureSynapseSqlCredentialCreateInput!) {
              azureSynapseSqlCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateAzureSynapseSqlCredential.model_validate(
            data
        ).azure_synapse_sql_credential_create

    async def create_categorical_distribution_validator_with_dynamic_threshold(
        self,
        input: CategoricalDistributionValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateCategoricalDistributionValidatorWithDynamicThresholdCategoricalDistributionValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateCategoricalDistributionValidatorWithDynamicThreshold($input: CategoricalDistributionValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              categoricalDistributionValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return (
            CreateCategoricalDistributionValidatorWithDynamicThreshold.model_validate(
                data
            ).categorical_distribution_validator_with_dynamic_threshold_create
        )

    async def create_categorical_distribution_validator_with_fixed_threshold(
        self,
        input: CategoricalDistributionValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateCategoricalDistributionValidatorWithFixedThresholdCategoricalDistributionValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateCategoricalDistributionValidatorWithFixedThreshold($input: CategoricalDistributionValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              categoricalDistributionValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateCategoricalDistributionValidatorWithFixedThreshold.model_validate(
            data
        ).categorical_distribution_validator_with_fixed_threshold_create

    async def create_databricks_credential(
        self, input: DatabricksCredentialCreateInput
    ) -> CreateDatabricksCredentialDatabricksCredentialCreate:
        query = gql(
            """
            mutation CreateDatabricksCredential($input: DatabricksCredentialCreateInput!) {
              databricksCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDatabricksCredential.model_validate(
            data
        ).databricks_credential_create

    async def create_databricks_source(
        self, input: DatabricksSourceCreateInput
    ) -> CreateDatabricksSourceDatabricksSourceCreate:
        query = gql(
            """
            mutation CreateDatabricksSource($input: DatabricksSourceCreateInput!) {
              databricksSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDatabricksSource.model_validate(data).databricks_source_create

    async def create_dbt_cloud_credential(
        self, input: DbtCloudCredentialCreateInput
    ) -> CreateDbtCloudCredentialDbtCloudCredentialCreate:
        query = gql(
            """
            mutation CreateDbtCloudCredential($input: DbtCloudCredentialCreateInput!) {
              dbtCloudCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDbtCloudCredential.model_validate(data).dbt_cloud_credential_create

    async def create_dbt_core_credential(
        self, input: DbtCoreCredentialCreateInput
    ) -> CreateDbtCoreCredentialDbtCoreCredentialCreate:
        query = gql(
            """
            mutation CreateDbtCoreCredential($input: DbtCoreCredentialCreateInput!) {
              dbtCoreCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDbtCoreCredential.model_validate(data).dbt_core_credential_create

    async def create_dbt_model_run_source(
        self, input: DbtModelRunSourceCreateInput
    ) -> CreateDbtModelRunSourceDbtModelRunSourceCreate:
        query = gql(
            """
            mutation CreateDbtModelRunSource($input: DbtModelRunSourceCreateInput!) {
              dbtModelRunSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDbtModelRunSource.model_validate(data).dbt_model_run_source_create

    async def create_dbt_test_result_source(
        self, input: DbtTestResultSourceCreateInput
    ) -> CreateDbtTestResultSourceDbtTestResultSourceCreate:
        query = gql(
            """
            mutation CreateDbtTestResultSource($input: DbtTestResultSourceCreateInput!) {
              dbtTestResultSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDbtTestResultSource.model_validate(
            data
        ).dbt_test_result_source_create

    async def create_demo_credential(
        self, input: DemoCredentialCreateInput
    ) -> CreateDemoCredentialDemoCredentialCreate:
        query = gql(
            """
            mutation CreateDemoCredential($input: DemoCredentialCreateInput!) {
              demoCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDemoCredential.model_validate(data).demo_credential_create

    async def create_demo_source(
        self, input: DemoSourceCreateInput
    ) -> CreateDemoSourceDemoSourceCreate:
        query = gql(
            """
            mutation CreateDemoSource($input: DemoSourceCreateInput!) {
              demoSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateDemoSource.model_validate(data).demo_source_create

    async def create_file_window(
        self, input: FileWindowCreateInput
    ) -> CreateFileWindowFileWindowCreate:
        query = gql(
            """
            mutation CreateFileWindow($input: FileWindowCreateInput!) {
              fileWindowCreate(input: $input) {
                ...WindowCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowCreation on WindowCreateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
                __typename
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FileWindow {
                dataTimeField
              }
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
                dataTimeField
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                  windowTimeoutDisabled
                }
                dataTimeField
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateFileWindow.model_validate(data).file_window_create

    async def create_fixed_batch_window(
        self, input: FixedBatchWindowCreateInput
    ) -> CreateFixedBatchWindowFixedBatchWindowCreate:
        query = gql(
            """
            mutation CreateFixedBatchWindow($input: FixedBatchWindowCreateInput!) {
              fixedBatchWindowCreate(input: $input) {
                ...WindowCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowCreation on WindowCreateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
                __typename
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FileWindow {
                dataTimeField
              }
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
                dataTimeField
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                  windowTimeoutDisabled
                }
                dataTimeField
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateFixedBatchWindow.model_validate(data).fixed_batch_window_create

    async def create_freshness_validator_with_dynamic_threshold(
        self,
        input: FreshnessValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateFreshnessValidatorWithDynamicThresholdFreshnessValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateFreshnessValidatorWithDynamicThreshold($input: FreshnessValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              freshnessValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateFreshnessValidatorWithDynamicThreshold.model_validate(
            data
        ).freshness_validator_with_dynamic_threshold_create

    async def create_freshness_validator_with_fixed_threshold(
        self, input: FreshnessValidatorCreateInput, threshold: FixedThresholdCreateInput
    ) -> CreateFreshnessValidatorWithFixedThresholdFreshnessValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateFreshnessValidatorWithFixedThreshold($input: FreshnessValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              freshnessValidatorWithFixedThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateFreshnessValidatorWithFixedThreshold.model_validate(
            data
        ).freshness_validator_with_fixed_threshold_create

    async def create_gcp_big_query_source(
        self, input: GcpBigQuerySourceCreateInput
    ) -> CreateGcpBigQuerySourceGcpBigQuerySourceCreate:
        query = gql(
            """
            mutation CreateGcpBigQuerySource($input: GcpBigQuerySourceCreateInput!) {
              gcpBigQuerySourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpBigQuerySource.model_validate(data).gcp_big_query_source_create

    async def create_gcp_credential(
        self, input: GcpCredentialCreateInput
    ) -> CreateGcpCredentialGcpCredentialCreate:
        query = gql(
            """
            mutation CreateGcpCredential($input: GcpCredentialCreateInput!) {
              gcpCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpCredential.model_validate(data).gcp_credential_create

    async def create_gcp_pub_sub_lite_source(
        self, input: GcpPubSubLiteSourceCreateInput
    ) -> CreateGcpPubSubLiteSourceGcpPubSubLiteSourceCreate:
        query = gql(
            """
            mutation CreateGcpPubSubLiteSource($input: GcpPubSubLiteSourceCreateInput!) {
              gcpPubSubLiteSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpPubSubLiteSource.model_validate(
            data
        ).gcp_pub_sub_lite_source_create

    async def create_gcp_pub_sub_source(
        self, input: GcpPubSubSourceCreateInput
    ) -> CreateGcpPubSubSourceGcpPubSubSourceCreate:
        query = gql(
            """
            mutation CreateGcpPubSubSource($input: GcpPubSubSourceCreateInput!) {
              gcpPubSubSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpPubSubSource.model_validate(data).gcp_pub_sub_source_create

    async def create_gcp_storage_source(
        self, input: GcpStorageSourceCreateInput
    ) -> CreateGcpStorageSourceGcpStorageSourceCreate:
        query = gql(
            """
            mutation CreateGcpStorageSource($input: GcpStorageSourceCreateInput!) {
              gcpStorageSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGcpStorageSource.model_validate(data).gcp_storage_source_create

    async def create_global_window(
        self, input: GlobalWindowCreateInput
    ) -> CreateGlobalWindowGlobalWindowCreate:
        query = gql(
            """
            mutation CreateGlobalWindow($input: GlobalWindowCreateInput!) {
              globalWindowCreate(input: $input) {
                ...WindowCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowCreation on WindowCreateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
                __typename
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FileWindow {
                dataTimeField
              }
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
                dataTimeField
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                  windowTimeoutDisabled
                }
                dataTimeField
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateGlobalWindow.model_validate(data).global_window_create

    async def create_kafka_sasl_ssl_plain_credential(
        self, input: KafkaSaslSslPlainCredentialCreateInput
    ) -> CreateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialCreate:
        query = gql(
            """
            mutation CreateKafkaSaslSslPlainCredential($input: KafkaSaslSslPlainCredentialCreateInput!) {
              kafkaSaslSslPlainCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateKafkaSaslSslPlainCredential.model_validate(
            data
        ).kafka_sasl_ssl_plain_credential_create

    async def create_kafka_source(
        self, input: KafkaSourceCreateInput
    ) -> CreateKafkaSourceKafkaSourceCreate:
        query = gql(
            """
            mutation CreateKafkaSource($input: KafkaSourceCreateInput!) {
              kafkaSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateKafkaSource.model_validate(data).kafka_source_create

    async def create_kafka_ssl_credential(
        self, input: KafkaSslCredentialCreateInput
    ) -> CreateKafkaSslCredentialKafkaSslCredentialCreate:
        query = gql(
            """
            mutation CreateKafkaSslCredential($input: KafkaSslCredentialCreateInput!) {
              kafkaSslCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateKafkaSslCredential.model_validate(data).kafka_ssl_credential_create

    async def create_ms_teams_channel(
        self, input: MsTeamsChannelCreateInput
    ) -> CreateMsTeamsChannelMsTeamsChannelCreate:
        query = gql(
            """
            mutation CreateMsTeamsChannel($input: MsTeamsChannelCreateInput!) {
              msTeamsChannelCreate(input: $input) {
                ...ChannelCreation
              }
            }

            fragment ChannelCreation on ChannelCreateResult {
              errors {
                ...ErrorDetails
              }
              channel {
                ...ChannelDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateMsTeamsChannel.model_validate(data).ms_teams_channel_create

    async def create_notification_rule(
        self, input: NotificationRuleCreateInput
    ) -> CreateNotificationRuleNotificationRuleCreate:
        query = gql(
            """
            mutation CreateNotificationRule($input: NotificationRuleCreateInput!) {
              notificationRuleCreate(input: $input) {
                ...NotificationRuleCreation
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment NotificationRuleConditions on NotificationRuleCondition {
              __typename
              id
              notificationRuleId
              createdAt
              updatedAt
              ... on SourceNotificationRuleCondition {
                config {
                  sources {
                    __typename
                    id
                    name
                  }
                }
              }
              ... on SeverityNotificationRuleCondition {
                config {
                  severities
                }
              }
              ... on TypeNotificationRuleCondition {
                config {
                  types
                }
              }
              ... on OwnerNotificationRuleCondition {
                config {
                  owners {
                    id
                    displayName
                  }
                }
              }
              ... on TagNotificationRuleCondition {
                config {
                  tags {
                    id
                    key
                    value
                  }
                }
              }
              ... on SegmentNotificationRuleCondition {
                config {
                  segments {
                    field
                    value
                  }
                }
              }
            }

            fragment NotificationRuleCreation on NotificationRuleCreateResult {
              errors {
                code
                message
              }
              notificationRule {
                ...NotificationRuleDetails
              }
            }

            fragment NotificationRuleDetails on NotificationRule {
              __typename
              id
              name
              createdAt
              updatedAt
              conditions {
                ...NotificationRuleConditions
              }
              channel {
                ...ChannelDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNotificationRule.model_validate(data).notification_rule_create

    async def create_numeric_anomaly_validator_with_dynamic_threshold(
        self,
        input: NumericAnomalyValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateNumericAnomalyValidatorWithDynamicThresholdNumericAnomalyValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateNumericAnomalyValidatorWithDynamicThreshold($input: NumericAnomalyValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              numericAnomalyValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericAnomalyValidatorWithDynamicThreshold.model_validate(
            data
        ).numeric_anomaly_validator_with_dynamic_threshold_create

    async def create_numeric_anomaly_validator_with_fixed_threshold(
        self,
        input: NumericAnomalyValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateNumericAnomalyValidatorWithFixedThresholdNumericAnomalyValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateNumericAnomalyValidatorWithFixedThreshold($input: NumericAnomalyValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              numericAnomalyValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericAnomalyValidatorWithFixedThreshold.model_validate(
            data
        ).numeric_anomaly_validator_with_fixed_threshold_create

    async def create_numeric_distribution_validator_with_dynamic_threshold(
        self,
        input: NumericDistributionValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateNumericDistributionValidatorWithDynamicThresholdNumericDistributionValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateNumericDistributionValidatorWithDynamicThreshold($input: NumericDistributionValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              numericDistributionValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericDistributionValidatorWithDynamicThreshold.model_validate(
            data
        ).numeric_distribution_validator_with_dynamic_threshold_create

    async def create_numeric_distribution_validator_with_fixed_threshold(
        self,
        input: NumericDistributionValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateNumericDistributionValidatorWithFixedThresholdNumericDistributionValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateNumericDistributionValidatorWithFixedThreshold($input: NumericDistributionValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              numericDistributionValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericDistributionValidatorWithFixedThreshold.model_validate(
            data
        ).numeric_distribution_validator_with_fixed_threshold_create

    async def create_numeric_validator_with_dynamic_threshold(
        self, input: NumericValidatorCreateInput, threshold: DynamicThresholdCreateInput
    ) -> CreateNumericValidatorWithDynamicThresholdNumericValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateNumericValidatorWithDynamicThreshold($input: NumericValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              numericValidatorWithDynamicThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericValidatorWithDynamicThreshold.model_validate(
            data
        ).numeric_validator_with_dynamic_threshold_create

    async def create_numeric_validator_with_fixed_threshold(
        self, input: NumericValidatorCreateInput, threshold: FixedThresholdCreateInput
    ) -> CreateNumericValidatorWithFixedThresholdNumericValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateNumericValidatorWithFixedThreshold($input: NumericValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              numericValidatorWithFixedThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateNumericValidatorWithFixedThreshold.model_validate(
            data
        ).numeric_validator_with_fixed_threshold_create

    async def create_owner_notification_rule_condition(
        self, input: OwnerNotificationRuleConditionCreateInput
    ) -> CreateOwnerNotificationRuleConditionOwnerNotificationRuleConditionCreate:
        query = gql(
            """
            mutation CreateOwnerNotificationRuleCondition($input: OwnerNotificationRuleConditionCreateInput!) {
              ownerNotificationRuleConditionCreate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateOwnerNotificationRuleCondition.model_validate(
            data
        ).owner_notification_rule_condition_create

    async def create_postgre_sql_credential(
        self, input: PostgreSqlCredentialCreateInput
    ) -> CreatePostgreSqlCredentialPostgreSqlCredentialCreate:
        query = gql(
            """
            mutation CreatePostgreSqlCredential($input: PostgreSqlCredentialCreateInput!) {
              postgreSqlCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreatePostgreSqlCredential.model_validate(
            data
        ).postgre_sql_credential_create

    async def create_postgre_sql_source(
        self, input: PostgreSqlSourceCreateInput
    ) -> CreatePostgreSqlSourcePostgreSqlSourceCreate:
        query = gql(
            """
            mutation CreatePostgreSqlSource($input: PostgreSqlSourceCreateInput!) {
              postgreSqlSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreatePostgreSqlSource.model_validate(data).postgre_sql_source_create

    async def create_relative_time_validator_with_dynamic_threshold(
        self,
        input: RelativeTimeValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateRelativeTimeValidatorWithDynamicThresholdRelativeTimeValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateRelativeTimeValidatorWithDynamicThreshold($input: RelativeTimeValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              relativeTimeValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateRelativeTimeValidatorWithDynamicThreshold.model_validate(
            data
        ).relative_time_validator_with_dynamic_threshold_create

    async def create_relative_time_validator_with_fixed_threshold(
        self,
        input: RelativeTimeValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateRelativeTimeValidatorWithFixedThresholdRelativeTimeValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateRelativeTimeValidatorWithFixedThreshold($input: RelativeTimeValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              relativeTimeValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateRelativeTimeValidatorWithFixedThreshold.model_validate(
            data
        ).relative_time_validator_with_fixed_threshold_create

    async def create_relative_volume_validator_with_dynamic_threshold(
        self,
        input: RelativeVolumeValidatorCreateInput,
        threshold: DynamicThresholdCreateInput,
    ) -> CreateRelativeVolumeValidatorWithDynamicThresholdRelativeVolumeValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateRelativeVolumeValidatorWithDynamicThreshold($input: RelativeVolumeValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              relativeVolumeValidatorWithDynamicThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateRelativeVolumeValidatorWithDynamicThreshold.model_validate(
            data
        ).relative_volume_validator_with_dynamic_threshold_create

    async def create_relative_volume_validator_with_fixed_threshold(
        self,
        input: RelativeVolumeValidatorCreateInput,
        threshold: FixedThresholdCreateInput,
    ) -> CreateRelativeVolumeValidatorWithFixedThresholdRelativeVolumeValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateRelativeVolumeValidatorWithFixedThreshold($input: RelativeVolumeValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              relativeVolumeValidatorWithFixedThresholdCreate(
                input: $input
                threshold: $threshold
              ) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateRelativeVolumeValidatorWithFixedThreshold.model_validate(
            data
        ).relative_volume_validator_with_fixed_threshold_create

    async def create_saml_identity_provider(
        self, input: SamlIdentityProviderCreateInput
    ) -> CreateSamlIdentityProviderSamlIdentityProviderCreate:
        query = gql(
            """
            mutation CreateSamlIdentityProvider($input: SamlIdentityProviderCreateInput!) {
              samlIdentityProviderCreate(input: $input) {
                ...IdentityProviderCreation
              }
            }

            fragment IdentityProviderCreation on IdentityProviderCreateResult {
              errors {
                code
                message
              }
              identityProvider {
                ...IdentityProviderDetails
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSamlIdentityProvider.model_validate(
            data
        ).saml_identity_provider_create

    async def create_segment_notification_rule_condition(
        self, input: SegmentNotificationRuleConditionCreateInput
    ) -> CreateSegmentNotificationRuleConditionSegmentNotificationRuleConditionCreate:
        query = gql(
            """
            mutation CreateSegmentNotificationRuleCondition($input: SegmentNotificationRuleConditionCreateInput!) {
              segmentNotificationRuleConditionCreate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSegmentNotificationRuleCondition.model_validate(
            data
        ).segment_notification_rule_condition_create

    async def create_segmentation(
        self, input: SegmentationCreateInput
    ) -> CreateSegmentationSegmentationCreate:
        query = gql(
            """
            mutation CreateSegmentation($input: SegmentationCreateInput!) {
              segmentationCreate(input: $input) {
                ...SegmentationCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SegmentationCreation on SegmentationCreateResult {
              errors {
                ...ErrorDetails
              }
              segmentation {
                ...SegmentationDetails
              }
            }

            fragment SegmentationDetails on Segmentation {
              __typename
              id
              name
              source {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              fields
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSegmentation.model_validate(data).segmentation_create

    async def create_severity_notification_rule_condition(
        self, input: SeverityNotificationRuleConditionCreateInput
    ) -> CreateSeverityNotificationRuleConditionSeverityNotificationRuleConditionCreate:
        query = gql(
            """
            mutation CreateSeverityNotificationRuleCondition($input: SeverityNotificationRuleConditionCreateInput!) {
              severityNotificationRuleConditionCreate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSeverityNotificationRuleCondition.model_validate(
            data
        ).severity_notification_rule_condition_create

    async def create_slack_channel(
        self, input: SlackChannelCreateInput
    ) -> CreateSlackChannelSlackChannelCreate:
        query = gql(
            """
            mutation CreateSlackChannel($input: SlackChannelCreateInput!) {
              slackChannelCreate(input: $input) {
                ...ChannelCreation
              }
            }

            fragment ChannelCreation on ChannelCreateResult {
              errors {
                ...ErrorDetails
              }
              channel {
                ...ChannelDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSlackChannel.model_validate(data).slack_channel_create

    async def create_snowflake_credential(
        self, input: SnowflakeCredentialCreateInput
    ) -> CreateSnowflakeCredentialSnowflakeCredentialCreate:
        query = gql(
            """
            mutation CreateSnowflakeCredential($input: SnowflakeCredentialCreateInput!) {
              snowflakeCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSnowflakeCredential.model_validate(
            data
        ).snowflake_credential_create

    async def create_snowflake_source(
        self, input: SnowflakeSourceCreateInput
    ) -> CreateSnowflakeSourceSnowflakeSourceCreate:
        query = gql(
            """
            mutation CreateSnowflakeSource($input: SnowflakeSourceCreateInput!) {
              snowflakeSourceCreate(input: $input) {
                ...SourceCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceCreation on SourceCreateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSnowflakeSource.model_validate(data).snowflake_source_create

    async def create_source_notification_rule_condition(
        self, input: SourceNotificationRuleConditionCreateInput
    ) -> CreateSourceNotificationRuleConditionSourceNotificationRuleConditionCreate:
        query = gql(
            """
            mutation CreateSourceNotificationRuleCondition($input: SourceNotificationRuleConditionCreateInput!) {
              sourceNotificationRuleConditionCreate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSourceNotificationRuleCondition.model_validate(
            data
        ).source_notification_rule_condition_create

    async def create_sql_validator_with_dynamic_threshold(
        self, input: SqlValidatorCreateInput, threshold: DynamicThresholdCreateInput
    ) -> CreateSqlValidatorWithDynamicThresholdSqlValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateSqlValidatorWithDynamicThreshold($input: SqlValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              sqlValidatorWithDynamicThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSqlValidatorWithDynamicThreshold.model_validate(
            data
        ).sql_validator_with_dynamic_threshold_create

    async def create_sql_validator_with_fixed_threshold(
        self, input: SqlValidatorCreateInput, threshold: FixedThresholdCreateInput
    ) -> CreateSqlValidatorWithFixedThresholdSqlValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateSqlValidatorWithFixedThreshold($input: SqlValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              sqlValidatorWithFixedThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateSqlValidatorWithFixedThreshold.model_validate(
            data
        ).sql_validator_with_fixed_threshold_create

    async def create_tableau_connected_app_credential(
        self, input: TableauConnectedAppCredentialCreateInput
    ) -> CreateTableauConnectedAppCredentialTableauConnectedAppCredentialCreate:
        query = gql(
            """
            mutation CreateTableauConnectedAppCredential($input: TableauConnectedAppCredentialCreateInput!) {
              tableauConnectedAppCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateTableauConnectedAppCredential.model_validate(
            data
        ).tableau_connected_app_credential_create

    async def create_tableau_personal_access_token_credential(
        self, input: TableauPersonalAccessTokenCredentialCreateInput
    ) -> CreateTableauPersonalAccessTokenCredentialTableauPersonalAccessTokenCredentialCreate:
        query = gql(
            """
            mutation CreateTableauPersonalAccessTokenCredential($input: TableauPersonalAccessTokenCredentialCreateInput!) {
              tableauPersonalAccessTokenCredentialCreate(input: $input) {
                ...CredentialCreation
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialCreation on CredentialCreateResult {
              __typename
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateTableauPersonalAccessTokenCredential.model_validate(
            data
        ).tableau_personal_access_token_credential_create

    async def create_tag_notification_rule_condition(
        self, input: TagNotificationRuleConditionCreateInput
    ) -> CreateTagNotificationRuleConditionTagNotificationRuleConditionCreate:
        query = gql(
            """
            mutation CreateTagNotificationRuleCondition($input: TagNotificationRuleConditionCreateInput!) {
              tagNotificationRuleConditionCreate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateTagNotificationRuleCondition.model_validate(
            data
        ).tag_notification_rule_condition_create

    async def create_tumbling_window(
        self, input: TumblingWindowCreateInput
    ) -> CreateTumblingWindowTumblingWindowCreate:
        query = gql(
            """
            mutation CreateTumblingWindow($input: TumblingWindowCreateInput!) {
              tumblingWindowCreate(input: $input) {
                ...WindowCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowCreation on WindowCreateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
                __typename
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FileWindow {
                dataTimeField
              }
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
                dataTimeField
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                  windowTimeoutDisabled
                }
                dataTimeField
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateTumblingWindow.model_validate(data).tumbling_window_create

    async def create_type_notification_rule_condition(
        self, input: TypeNotificationRuleConditionCreateInput
    ) -> CreateTypeNotificationRuleConditionTypeNotificationRuleConditionCreate:
        query = gql(
            """
            mutation CreateTypeNotificationRuleCondition($input: TypeNotificationRuleConditionCreateInput!) {
              typeNotificationRuleConditionCreate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateTypeNotificationRuleCondition.model_validate(
            data
        ).type_notification_rule_condition_create

    async def create_user(self, input: UserCreateInput) -> CreateUserUserCreate:
        query = gql(
            """
            mutation CreateUser($input: UserCreateInput!) {
              userCreate(input: $input) {
                ...UserCreation
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserCreation on UserCreateResult {
              errors {
                code
                message
              }
              user {
                ...UserDetails
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              lastLoginAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateUser.model_validate(data).user_create

    async def create_volume_validator_with_dynamic_threshold(
        self, input: VolumeValidatorCreateInput, threshold: DynamicThresholdCreateInput
    ) -> CreateVolumeValidatorWithDynamicThresholdVolumeValidatorWithDynamicThresholdCreate:
        query = gql(
            """
            mutation CreateVolumeValidatorWithDynamicThreshold($input: VolumeValidatorCreateInput!, $threshold: DynamicThresholdCreateInput!) {
              volumeValidatorWithDynamicThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateVolumeValidatorWithDynamicThreshold.model_validate(
            data
        ).volume_validator_with_dynamic_threshold_create

    async def create_volume_validator_with_fixed_threshold(
        self, input: VolumeValidatorCreateInput, threshold: FixedThresholdCreateInput
    ) -> CreateVolumeValidatorWithFixedThresholdVolumeValidatorWithFixedThresholdCreate:
        query = gql(
            """
            mutation CreateVolumeValidatorWithFixedThreshold($input: VolumeValidatorCreateInput!, $threshold: FixedThresholdCreateInput!) {
              volumeValidatorWithFixedThresholdCreate(input: $input, threshold: $threshold) {
                ...ValidatorCreation
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorCreation on ValidatorCreateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input, "threshold": threshold}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateVolumeValidatorWithFixedThreshold.model_validate(
            data
        ).volume_validator_with_fixed_threshold_create

    async def create_webhook_channel(
        self, input: WebhookChannelCreateInput
    ) -> CreateWebhookChannelWebhookChannelCreate:
        query = gql(
            """
            mutation CreateWebhookChannel($input: WebhookChannelCreateInput!) {
              webhookChannelCreate(input: $input) {
                ...ChannelCreation
              }
            }

            fragment ChannelCreation on ChannelCreateResult {
              errors {
                ...ErrorDetails
              }
              channel {
                ...ChannelDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return CreateWebhookChannel.model_validate(data).webhook_channel_create

    async def databricks_credential_secret_changed(
        self, input: DatabricksCredentialSecretChangedInput
    ) -> DatabricksCredentialSecretChangedDatabricksCredentialSecretChanged:
        query = gql(
            """
            query DatabricksCredentialSecretChanged($input: DatabricksCredentialSecretChangedInput!) {
              databricksCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DatabricksCredentialSecretChanged.model_validate(
            data
        ).databricks_credential_secret_changed

    async def dbt_artifact_multipart_upload_append_part(
        self, input: DbtArtifactMultipartUploadAppendPartInput
    ) -> DbtArtifactMultipartUploadAppendPartDbtArtifactMultipartUploadAppendPart:
        query = gql(
            """
            mutation DbtArtifactMultipartUploadAppendPart($input: DbtArtifactMultipartUploadAppendPartInput!) {
              dbtArtifactMultipartUploadAppendPart(input: $input) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DbtArtifactMultipartUploadAppendPart.model_validate(
            data
        ).dbt_artifact_multipart_upload_append_part

    async def dbt_artifact_multipart_upload_complete(
        self, input: DbtArtifactMultipartUploadCompleteInput
    ) -> DbtArtifactMultipartUploadCompleteDbtArtifactMultipartUploadComplete:
        query = gql(
            """
            mutation DbtArtifactMultipartUploadComplete($input: DbtArtifactMultipartUploadCompleteInput!) {
              dbtArtifactMultipartUploadComplete(input: $input) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DbtArtifactMultipartUploadComplete.model_validate(
            data
        ).dbt_artifact_multipart_upload_complete

    async def dbt_artifact_multipart_upload_create(
        self, input: DbtArtifactMultipartUploadCreateInput
    ) -> DbtArtifactMultipartUploadCreateDbtArtifactMultipartUploadCreate:
        query = gql(
            """
            mutation DbtArtifactMultipartUploadCreate($input: DbtArtifactMultipartUploadCreateInput!) {
              dbtArtifactMultipartUploadCreate(input: $input) {
                id
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DbtArtifactMultipartUploadCreate.model_validate(
            data
        ).dbt_artifact_multipart_upload_create

    async def dbt_artifact_upload(
        self, input: DbtArtifactUploadInput
    ) -> DbtArtifactUploadDbtArtifactUpload:
        query = gql(
            """
            mutation DbtArtifactUpload($input: DbtArtifactUploadInput!) {
              dbtArtifactUpload(input: $input) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DbtArtifactUpload.model_validate(data).dbt_artifact_upload

    async def delete_channel(
        self, input: ChannelDeleteInput
    ) -> DeleteChannelChannelDelete:
        query = gql(
            """
            mutation DeleteChannel($input: ChannelDeleteInput!) {
              channelDelete(input: $input) {
                ...ChannelDeletion
              }
            }

            fragment ChannelDeletion on ChannelDeleteResult {
              errors {
                code
                message
              }
              channel {
                __typename
                id
                name
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteChannel.model_validate(data).channel_delete

    async def delete_credential(
        self, id: CredentialId
    ) -> DeleteCredentialCredentialsDelete:
        query = gql(
            """
            mutation DeleteCredential($id: CredentialId!) {
              credentialsDelete(ids: [$id]) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteCredential.model_validate(data).credentials_delete

    async def delete_credentials(
        self, ids: List[CredentialId]
    ) -> DeleteCredentialsCredentialsDelete:
        query = gql(
            """
            mutation DeleteCredentials($ids: [CredentialId!]!) {
              credentialsDelete(ids: $ids) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"ids": ids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteCredentials.model_validate(data).credentials_delete

    async def delete_identity(
        self, input: IdentityDeleteInput
    ) -> DeleteIdentityIdentityDelete:
        query = gql(
            """
            mutation DeleteIdentity($input: IdentityDeleteInput!) {
              identityDelete(input: $input) {
                ...IdentityDeletion
              }
            }

            fragment IdentityDeletion on IdentityDeleteResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteIdentity.model_validate(data).identity_delete

    async def delete_identity_provider(
        self, input: IdentityProviderDeleteInput
    ) -> DeleteIdentityProviderIdentityProviderDelete:
        query = gql(
            """
            mutation DeleteIdentityProvider($input: IdentityProviderDeleteInput!) {
              identityProviderDelete(input: $input) {
                ...IdentityProviderDeletion
              }
            }

            fragment IdentityProviderDeletion on IdentityProviderDeleteResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteIdentityProvider.model_validate(data).identity_provider_delete

    async def delete_notification_rule(
        self, input: NotificationRuleDeleteInput
    ) -> DeleteNotificationRuleNotificationRuleDelete:
        query = gql(
            """
            mutation DeleteNotificationRule($input: NotificationRuleDeleteInput!) {
              notificationRuleDelete(input: $input) {
                ...NotificationRuleDeletion
              }
            }

            fragment NotificationRuleDeletion on NotificationRuleDeleteResult {
              errors {
                code
                message
              }
              notificationRule {
                __typename
                id
                name
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteNotificationRule.model_validate(data).notification_rule_delete

    async def delete_segmentation(
        self, id: SegmentationId
    ) -> DeleteSegmentationSegmentationsDelete:
        query = gql(
            """
            mutation DeleteSegmentation($id: SegmentationId!) {
              segmentationsDelete(ids: [$id]) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteSegmentation.model_validate(data).segmentations_delete

    async def delete_source(self, id: SourceId) -> DeleteSourceSourcesDelete:
        query = gql(
            """
            mutation DeleteSource($id: SourceId!) {
              sourcesDelete(ids: [$id]) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteSource.model_validate(data).sources_delete

    async def delete_sources(self, ids: List[SourceId]) -> DeleteSourcesSourcesDelete:
        query = gql(
            """
            mutation DeleteSources($ids: [SourceId!]!) {
              sourcesDelete(ids: $ids) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"ids": ids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteSources.model_validate(data).sources_delete

    async def delete_user(self, input: UserDeleteInput) -> DeleteUserUserDelete:
        query = gql(
            """
            mutation DeleteUser($input: UserDeleteInput!) {
              userDelete(input: $input) {
                ...UserDeletion
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserDeletion on UserDeleteResult {
              errors {
                code
                message
              }
              user {
                ...UserDetails
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              lastLoginAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteUser.model_validate(data).user_delete

    async def delete_validators(
        self, ids: List[ValidatorId]
    ) -> DeleteValidatorsValidatorsDelete:
        query = gql(
            """
            mutation DeleteValidators($ids: [ValidatorId!]!) {
              validatorsDelete(ids: $ids) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"ids": ids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteValidators.model_validate(data).validators_delete

    async def delete_window(self, id: WindowId) -> DeleteWindowWindowsDelete:
        query = gql(
            """
            mutation DeleteWindow($id: WindowId!) {
              windowsDelete(ids: [$id]) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteWindow.model_validate(data).windows_delete

    async def delete_windows(self, ids: List[WindowId]) -> DeleteWindowsWindowsDelete:
        query = gql(
            """
            mutation DeleteWindows($ids: [WindowId!]!) {
              windowsDelete(ids: $ids) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"ids": ids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeleteWindows.model_validate(data).windows_delete

    async def dismiss_validator_recommendation(
        self, input: ValidatorRecommendationDismissInput
    ) -> DismissValidatorRecommendationValidatorRecommendationDismiss:
        query = gql(
            """
            mutation DismissValidatorRecommendation($input: ValidatorRecommendationDismissInput!) {
              validatorRecommendationDismiss(input: $input) {
                ...ValidatorRecommendationDismissal
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorRecommendationDismissal on ValidatorRecommendationDismissResult {
              __typename
              errors {
                ...ErrorDetails
              }
              recommendationIds
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DismissValidatorRecommendation.model_validate(
            data
        ).validator_recommendation_dismiss

    async def gcp_credential_secret_changed(
        self, input: GcpCredentialSecretChangedInput
    ) -> GcpCredentialSecretChangedGcpCredentialSecretChanged:
        query = gql(
            """
            query GcpCredentialSecretChanged($input: GcpCredentialSecretChangedInput!) {
              gcpCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GcpCredentialSecretChanged.model_validate(
            data
        ).gcp_credential_secret_changed

    async def get_channel_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetChannelByResourceNameChannelByResourceNameChannel,
            GetChannelByResourceNameChannelByResourceNameMsTeamsChannel,
            GetChannelByResourceNameChannelByResourceNameSlackChannel,
            GetChannelByResourceNameChannelByResourceNameWebhookChannel,
        ]
    ]:
        query = gql(
            """
            query GetChannelByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              channelByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...ChannelDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetChannelByResourceName.model_validate(data).channel_by_resource_name

    async def get_channels(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            GetChannelsChannelsChannel,
            GetChannelsChannelsMsTeamsChannel,
            GetChannelsChannelsSlackChannel,
            GetChannelsChannelsWebhookChannel,
        ]
    ]:
        query = gql(
            """
            query GetChannels($filter: ResourceFilter) {
              channels(filter: $filter) {
                ...ChannelDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetChannels.model_validate(data).channels

    async def get_credential_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetCredentialByResourceNameCredentialByResourceNameCredential,
            GetCredentialByResourceNameCredentialByResourceNameAwsAthenaCredential,
            GetCredentialByResourceNameCredentialByResourceNameAwsCredential,
            GetCredentialByResourceNameCredentialByResourceNameAwsRedshiftCredential,
            GetCredentialByResourceNameCredentialByResourceNameAzureSynapseEntraIdCredential,
            GetCredentialByResourceNameCredentialByResourceNameAzureSynapseSqlCredential,
            GetCredentialByResourceNameCredentialByResourceNameDatabricksCredential,
            GetCredentialByResourceNameCredentialByResourceNameDbtCloudCredential,
            GetCredentialByResourceNameCredentialByResourceNameDbtCoreCredential,
            GetCredentialByResourceNameCredentialByResourceNameKafkaSaslSslPlainCredential,
            GetCredentialByResourceNameCredentialByResourceNameKafkaSslCredential,
            GetCredentialByResourceNameCredentialByResourceNameLookerCredential,
            GetCredentialByResourceNameCredentialByResourceNamePostgreSqlCredential,
            GetCredentialByResourceNameCredentialByResourceNameSnowflakeCredential,
            GetCredentialByResourceNameCredentialByResourceNameTableauConnectedAppCredential,
            GetCredentialByResourceNameCredentialByResourceNameTableauPersonalAccessTokenCredential,
        ]
    ]:
        query = gql(
            """
            query GetCredentialByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              credentialByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...CredentialDetails
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetCredentialByResourceName.model_validate(
            data
        ).credential_by_resource_name

    async def get_databricks_warehouse_info(
        self, input: DatabricksWarehouseInfoInput
    ) -> GetDatabricksWarehouseInfoDatabricksWarehouseInfo:
        query = gql(
            """
            query GetDatabricksWarehouseInfo($input: DatabricksWarehouseInfoInput!) {
              databricksWarehouseInfo(input: $input) {
                name
                state
                autoStopMinutes
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetDatabricksWarehouseInfo.model_validate(data).databricks_warehouse_info

    async def get_identity_provider_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetIdentityProviderByResourceNameIdentityProviderByResourceNameIdentityProvider,
            GetIdentityProviderByResourceNameIdentityProviderByResourceNameSamlIdentityProvider,
        ]
    ]:
        query = gql(
            """
            query GetIdentityProviderByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              identityProviderByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...IdentityProviderDetails
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetIdentityProviderByResourceName.model_validate(
            data
        ).identity_provider_by_resource_name

    async def get_identity_providers(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            GetIdentityProvidersIdentityProvidersIdentityProvider,
            GetIdentityProvidersIdentityProvidersSamlIdentityProvider,
        ]
    ]:
        query = gql(
            """
            query GetIdentityProviders($filter: ResourceFilter) {
              identityProviders(filter: $filter) {
                ...IdentityProviderDetails
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetIdentityProviders.model_validate(data).identity_providers

    async def get_incidents(
        self, time_range: Union[Optional[TimeRangeInput], UnsetType] = UNSET
    ) -> List[
        Union[
            GetIncidentsIncidentsListIncident,
            GetIncidentsIncidentsListValidatorIncident,
        ]
    ]:
        query = gql(
            """
            query GetIncidents($timeRange: TimeRangeInput) {
              incidentsList(timeRange: $timeRange) {
                ...IncidentDetails
              }
            }

            fragment IncidentDetails on Incident {
              __typename
              id
              createdAt
              ... on ValidatorIncident {
                segment {
                  ...SegmentDetails
                }
                metric {
                  ...ValidatorMetricDetails
                }
                validator {
                  ...ValidatorDetails
                }
                source {
                  ...SourceBase
                }
                owner {
                  ...UserSummary
                }
                status
                severity
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
              dataQuality {
                incidentCount
                totalCount
                quality
                qualityDiff
              }
            }

            fragment SourceBase on Source {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment UserSummary on User {
              id
              displayName
              fullName
              email
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorMetricDetails on ValidatorMetric {
              __typename
              startTime
              endTime
              isIncident
              value
              deviation
              severity
              ... on ValidatorMetricWithFixedThreshold {
                operator
                bound
              }
              ... on ValidatorMetricWithDynamicThreshold {
                lowerBound
                upperBound
                decisionBoundsType
                isBurnIn
              }
            }
            """
        )
        variables: Dict[str, object] = {"timeRange": time_range}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetIncidents.model_validate(data).incidents_list

    async def get_notification_rule(
        self, id: Any
    ) -> Optional[GetNotificationRuleNotificationRule]:
        query = gql(
            """
            query GetNotificationRule($id: NotificationRuleId!) {
              notificationRule(id: $id) {
                ...NotificationRuleDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment NotificationRuleConditions on NotificationRuleCondition {
              __typename
              id
              notificationRuleId
              createdAt
              updatedAt
              ... on SourceNotificationRuleCondition {
                config {
                  sources {
                    __typename
                    id
                    name
                  }
                }
              }
              ... on SeverityNotificationRuleCondition {
                config {
                  severities
                }
              }
              ... on TypeNotificationRuleCondition {
                config {
                  types
                }
              }
              ... on OwnerNotificationRuleCondition {
                config {
                  owners {
                    id
                    displayName
                  }
                }
              }
              ... on TagNotificationRuleCondition {
                config {
                  tags {
                    id
                    key
                    value
                  }
                }
              }
              ... on SegmentNotificationRuleCondition {
                config {
                  segments {
                    field
                    value
                  }
                }
              }
            }

            fragment NotificationRuleDetails on NotificationRule {
              __typename
              id
              name
              createdAt
              updatedAt
              conditions {
                ...NotificationRuleConditions
              }
              channel {
                ...ChannelDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetNotificationRule.model_validate(data).notification_rule

    async def get_notification_rule_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[GetNotificationRuleByResourceNameNotificationRuleByResourceName]:
        query = gql(
            """
            query GetNotificationRuleByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              notificationRuleByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...NotificationRuleDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment NotificationRuleConditions on NotificationRuleCondition {
              __typename
              id
              notificationRuleId
              createdAt
              updatedAt
              ... on SourceNotificationRuleCondition {
                config {
                  sources {
                    __typename
                    id
                    name
                  }
                }
              }
              ... on SeverityNotificationRuleCondition {
                config {
                  severities
                }
              }
              ... on TypeNotificationRuleCondition {
                config {
                  types
                }
              }
              ... on OwnerNotificationRuleCondition {
                config {
                  owners {
                    id
                    displayName
                  }
                }
              }
              ... on TagNotificationRuleCondition {
                config {
                  tags {
                    id
                    key
                    value
                  }
                }
              }
              ... on SegmentNotificationRuleCondition {
                config {
                  segments {
                    field
                    value
                  }
                }
              }
            }

            fragment NotificationRuleDetails on NotificationRule {
              __typename
              id
              name
              createdAt
              updatedAt
              conditions {
                ...NotificationRuleConditions
              }
              channel {
                ...ChannelDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetNotificationRuleByResourceName.model_validate(
            data
        ).notification_rule_by_resource_name

    async def get_notification_rules(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[GetNotificationRulesNotificationRules]:
        query = gql(
            """
            query GetNotificationRules($filter: ResourceFilter) {
              notificationRules(filter: $filter) {
                ...NotificationRuleDetails
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment NotificationRuleConditions on NotificationRuleCondition {
              __typename
              id
              notificationRuleId
              createdAt
              updatedAt
              ... on SourceNotificationRuleCondition {
                config {
                  sources {
                    __typename
                    id
                    name
                  }
                }
              }
              ... on SeverityNotificationRuleCondition {
                config {
                  severities
                }
              }
              ... on TypeNotificationRuleCondition {
                config {
                  types
                }
              }
              ... on OwnerNotificationRuleCondition {
                config {
                  owners {
                    id
                    displayName
                  }
                }
              }
              ... on TagNotificationRuleCondition {
                config {
                  tags {
                    id
                    key
                    value
                  }
                }
              }
              ... on SegmentNotificationRuleCondition {
                config {
                  segments {
                    field
                    value
                  }
                }
              }
            }

            fragment NotificationRuleDetails on NotificationRule {
              __typename
              id
              name
              createdAt
              updatedAt
              conditions {
                ...NotificationRuleConditions
              }
              channel {
                ...ChannelDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetNotificationRules.model_validate(data).notification_rules

    async def get_segmentation(
        self, id: SegmentationId
    ) -> Optional[GetSegmentationSegmentation]:
        query = gql(
            """
            query GetSegmentation($id: SegmentationId!) {
              segmentation(id: $id) {
                ...SegmentationDetails
              }
            }

            fragment SegmentationDetails on Segmentation {
              __typename
              id
              name
              source {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              fields
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSegmentation.model_validate(data).segmentation

    async def get_segmentation_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[GetSegmentationByResourceNameSegmentationByResourceName]:
        query = gql(
            """
            query GetSegmentationByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              segmentationByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...SegmentationDetails
              }
            }

            fragment SegmentationDetails on Segmentation {
              __typename
              id
              name
              source {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              fields
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSegmentationByResourceName.model_validate(
            data
        ).segmentation_by_resource_name

    async def get_segments_by_segmentation(
        self,
        id: SegmentationId,
        limit: Union[Optional[int], UnsetType] = UNSET,
        before: Union[Optional[str], UnsetType] = UNSET,
        after: Union[Optional[str], UnsetType] = UNSET,
    ) -> Optional[GetSegmentsBySegmentationSegmentation]:
        query = gql(
            """
            query GetSegmentsBySegmentation($id: SegmentationId!, $limit: Int, $before: String, $after: String) {
              segmentation(id: $id) {
                ...SegmentationDetails
                segments(limit: $limit, before: $before, after: $after) {
                  elements {
                    fields {
                      field
                      value
                    }
                  }
                  pageInfo {
                    startCursor
                    endCursor
                    hasNextPage
                    hasPreviousPage
                    filteredCount
                    totalCount
                  }
                }
              }
            }

            fragment SegmentationDetails on Segmentation {
              __typename
              id
              name
              source {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              fields
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {
            "id": id,
            "limit": limit,
            "before": before,
            "after": after,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSegmentsBySegmentation.model_validate(data).segmentation

    async def get_source(
        self, id: SourceId
    ) -> Optional[
        Union[
            GetSourceSourceSource,
            GetSourceSourceAwsAthenaSource,
            GetSourceSourceAwsKinesisSource,
            GetSourceSourceAwsRedshiftSource,
            GetSourceSourceAwsS3Source,
            GetSourceSourceAzureSynapseSource,
            GetSourceSourceDatabricksSource,
            GetSourceSourceDbtModelRunSource,
            GetSourceSourceDbtTestResultSource,
            GetSourceSourceGcpBigQuerySource,
            GetSourceSourceGcpPubSubLiteSource,
            GetSourceSourceGcpPubSubSource,
            GetSourceSourceGcpStorageSource,
            GetSourceSourceKafkaSource,
            GetSourceSourcePostgreSqlSource,
            GetSourceSourceSnowflakeSource,
        ]
    ]:
        query = gql(
            """
            query GetSource($id: SourceId!) {
              source(id: $id) {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSource.model_validate(data).source

    async def get_source_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetSourceByResourceNameSourceByResourceNameSource,
            GetSourceByResourceNameSourceByResourceNameAwsAthenaSource,
            GetSourceByResourceNameSourceByResourceNameAwsKinesisSource,
            GetSourceByResourceNameSourceByResourceNameAwsRedshiftSource,
            GetSourceByResourceNameSourceByResourceNameAwsS3Source,
            GetSourceByResourceNameSourceByResourceNameAzureSynapseSource,
            GetSourceByResourceNameSourceByResourceNameDatabricksSource,
            GetSourceByResourceNameSourceByResourceNameDbtModelRunSource,
            GetSourceByResourceNameSourceByResourceNameDbtTestResultSource,
            GetSourceByResourceNameSourceByResourceNameGcpBigQuerySource,
            GetSourceByResourceNameSourceByResourceNameGcpPubSubLiteSource,
            GetSourceByResourceNameSourceByResourceNameGcpPubSubSource,
            GetSourceByResourceNameSourceByResourceNameGcpStorageSource,
            GetSourceByResourceNameSourceByResourceNameKafkaSource,
            GetSourceByResourceNameSourceByResourceNamePostgreSqlSource,
            GetSourceByResourceNameSourceByResourceNameSnowflakeSource,
        ]
    ]:
        query = gql(
            """
            query GetSourceByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              sourceByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSourceByResourceName.model_validate(data).source_by_resource_name

    async def get_source_incidents(
        self, id: SourceId, range: TimeRangeInput
    ) -> Optional[GetSourceIncidentsSource]:
        query = gql(
            """
            query GetSourceIncidents($id: SourceId!, $range: TimeRangeInput!) {
              source(id: $id) {
                __typename
                id
                incidents(range: $range) {
                  ...IncidentDetails
                }
              }
            }

            fragment IncidentDetails on Incident {
              __typename
              id
              createdAt
              ... on ValidatorIncident {
                segment {
                  ...SegmentDetails
                }
                metric {
                  ...ValidatorMetricDetails
                }
                validator {
                  ...ValidatorDetails
                }
                source {
                  ...SourceBase
                }
                owner {
                  ...UserSummary
                }
                status
                severity
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
              dataQuality {
                incidentCount
                totalCount
                quality
                qualityDiff
              }
            }

            fragment SourceBase on Source {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment UserSummary on User {
              id
              displayName
              fullName
              email
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorMetricDetails on ValidatorMetric {
              __typename
              startTime
              endTime
              isIncident
              value
              deviation
              severity
              ... on ValidatorMetricWithFixedThreshold {
                operator
                bound
              }
              ... on ValidatorMetricWithDynamicThreshold {
                lowerBound
                upperBound
                decisionBoundsType
                isBurnIn
              }
            }
            """
        )
        variables: Dict[str, object] = {"id": id, "range": range}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSourceIncidents.model_validate(data).source

    async def get_source_recommended_validators(
        self, id: SourceId
    ) -> Optional[GetSourceRecommendedValidatorsSource]:
        query = gql(
            """
            query GetSourceRecommendedValidators($id: SourceId!) {
              source(id: $id) {
                state
                recommendedValidators {
                  id
                  __typename
                  name
                  sourceConfig {
                    segmentation {
                      name
                    }
                  }
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetSourceRecommendedValidators.model_validate(data).source

    async def get_user_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[GetUserByResourceNameUserByResourceName]:
        query = gql(
            """
            query GetUserByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              userByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...UserDetails
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              lastLoginAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetUserByResourceName.model_validate(data).user_by_resource_name

    async def get_users(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[GetUsersUsers]:
        query = gql(
            """
            query GetUsers($filter: ResourceFilter) {
              users(filter: $filter) {
                ...UserDetails
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              lastLoginAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetUsers.model_validate(data).users

    async def get_validator(
        self, id: ValidatorId
    ) -> Optional[
        Union[
            GetValidatorValidatorValidator,
            GetValidatorValidatorCategoricalDistributionValidator,
            GetValidatorValidatorFreshnessValidator,
            GetValidatorValidatorNumericAnomalyValidator,
            GetValidatorValidatorNumericDistributionValidator,
            GetValidatorValidatorNumericValidator,
            GetValidatorValidatorRelativeTimeValidator,
            GetValidatorValidatorRelativeVolumeValidator,
            GetValidatorValidatorSqlValidator,
            GetValidatorValidatorVolumeValidator,
        ]
    ]:
        query = gql(
            """
            query GetValidator($id: ValidatorId!) {
              validator(id: $id) {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidator.model_validate(data).validator

    async def get_validator_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetValidatorByResourceNameValidatorByResourceNameValidator,
            GetValidatorByResourceNameValidatorByResourceNameCategoricalDistributionValidator,
            GetValidatorByResourceNameValidatorByResourceNameFreshnessValidator,
            GetValidatorByResourceNameValidatorByResourceNameNumericAnomalyValidator,
            GetValidatorByResourceNameValidatorByResourceNameNumericDistributionValidator,
            GetValidatorByResourceNameValidatorByResourceNameNumericValidator,
            GetValidatorByResourceNameValidatorByResourceNameRelativeTimeValidator,
            GetValidatorByResourceNameValidatorByResourceNameRelativeVolumeValidator,
            GetValidatorByResourceNameValidatorByResourceNameSqlValidator,
            GetValidatorByResourceNameValidatorByResourceNameVolumeValidator,
        ]
    ]:
        query = gql(
            """
            query GetValidatorByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              validatorByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorByResourceName.model_validate(
            data
        ).validator_by_resource_name

    async def get_validator_incidents(
        self,
        id: ValidatorId,
        range: TimeRangeInput,
        segment_id: Union[Optional[Any], UnsetType] = UNSET,
    ) -> Optional[GetValidatorIncidentsValidator]:
        query = gql(
            """
            query GetValidatorIncidents($id: ValidatorId!, $range: TimeRangeInput!, $segmentId: SegmentId) {
              validator(id: $id) {
                __typename
                id
                incidents(range: $range, segmentId: $segmentId) {
                  ...IncidentDetails
                }
              }
            }

            fragment IncidentDetails on Incident {
              __typename
              id
              createdAt
              ... on ValidatorIncident {
                segment {
                  ...SegmentDetails
                }
                metric {
                  ...ValidatorMetricDetails
                }
                validator {
                  ...ValidatorDetails
                }
                source {
                  ...SourceBase
                }
                owner {
                  ...UserSummary
                }
                status
                severity
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
              dataQuality {
                incidentCount
                totalCount
                quality
                qualityDiff
              }
            }

            fragment SourceBase on Source {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment UserSummary on User {
              id
              displayName
              fullName
              email
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorMetricDetails on ValidatorMetric {
              __typename
              startTime
              endTime
              isIncident
              value
              deviation
              severity
              ... on ValidatorMetricWithFixedThreshold {
                operator
                bound
              }
              ... on ValidatorMetricWithDynamicThreshold {
                lowerBound
                upperBound
                decisionBoundsType
                isBurnIn
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "id": id,
            "range": range,
            "segmentId": segment_id,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorIncidents.model_validate(data).validator

    async def get_validator_metric_debug_info(
        self, input: ValidatorMetricDebugInfoInput
    ) -> Union[
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoValidatorMetricDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsAthenaSourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsRedShiftSourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoAwsS3SourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoAzureSynapseSourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpBigQuerySourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoGcpStorageSourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoPostgreSQLSourceDebugInfo,
        GetValidatorMetricDebugInfoValidatorMetricDebugInfoSnowflakeSourceDebugInfo,
    ]:
        query = gql(
            """
            query GetValidatorMetricDebugInfo($input: ValidatorMetricDebugInfoInput!) {
              validatorMetricDebugInfo(input: $input) {
                ...ValidatorMetricDebugInfoDetails
              }
            }

            fragment ValidatorMetricDebugInfoDetails on ValidatorMetricDebugInfo {
              __typename
              startTime
              endTime
              ... on AzureSynapseSourceDebugInfo {
                sqlQuery
              }
              ... on GcpBigQuerySourceDebugInfo {
                sqlQuery
              }
              ... on GcpStorageSourceDebugInfo {
                bucket
                filePath
              }
              ... on AwsS3SourceDebugInfo {
                bucket
                filePath
              }
              ... on AwsRedShiftSourceDebugInfo {
                sqlQuery
              }
              ... on AwsAthenaSourceDebugInfo {
                sqlQuery
              }
              ... on SnowflakeSourceDebugInfo {
                sqlQuery
              }
              ... on PostgreSQLSourceDebugInfo {
                sqlQuery
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorMetricDebugInfo.model_validate(
            data
        ).validator_metric_debug_info

    async def get_validator_metric_debug_records(
        self, input: ValidatorMetricDebugInfoInput
    ) -> GetValidatorMetricDebugRecordsValidatorMetricDebugRecords:
        query = gql(
            """
            query GetValidatorMetricDebugRecords($input: ValidatorMetricDebugInfoInput!) {
              validatorMetricDebugRecords(input: $input) {
                columns
                rows
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorMetricDebugRecords.model_validate(
            data
        ).validator_metric_debug_records

    async def get_validator_segment_metrics(
        self, input: ValidatorSegmentMetricsInput
    ) -> Union[
        GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithDynamicThresholdHistory,
        GetValidatorSegmentMetricsValidatorSegmentMetricsValidatorMetricWithFixedThresholdHistory,
    ]:
        query = gql(
            """
            query GetValidatorSegmentMetrics($input: ValidatorSegmentMetricsInput!) {
              validatorSegmentMetrics(input: $input) {
                __typename
                ... on ValidatorMetricWithFixedThresholdHistory {
                  values {
                    ...ValidatorMetricDetails
                  }
                }
                ... on ValidatorMetricWithDynamicThresholdHistory {
                  values {
                    ...ValidatorMetricDetails
                  }
                }
              }
            }

            fragment ValidatorMetricDetails on ValidatorMetric {
              __typename
              startTime
              endTime
              isIncident
              value
              deviation
              severity
              ... on ValidatorMetricWithFixedThreshold {
                operator
                bound
              }
              ... on ValidatorMetricWithDynamicThreshold {
                lowerBound
                upperBound
                decisionBoundsType
                isBurnIn
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetValidatorSegmentMetrics.model_validate(data).validator_segment_metrics

    async def get_window_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> Optional[
        Union[
            GetWindowByResourceNameWindowByResourceNameWindow,
            GetWindowByResourceNameWindowByResourceNameFileWindow,
            GetWindowByResourceNameWindowByResourceNameFixedBatchWindow,
            GetWindowByResourceNameWindowByResourceNameTumblingWindow,
        ]
    ]:
        query = gql(
            """
            query GetWindowByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              windowByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
                __typename
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FileWindow {
                dataTimeField
              }
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
                dataTimeField
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                  windowTimeoutDisabled
                }
                dataTimeField
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetWindowByResourceName.model_validate(data).window_by_resource_name

    async def infer_aws_athena_schema(
        self, input: AwsAthenaInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferAwsAthenaSchema($input: AwsAthenaInferSchemaInput!) {
              awsAthenaInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferAwsAthenaSchema.model_validate(data).aws_athena_infer_schema

    async def infer_aws_kinesis_schema(
        self, input: AwsKinesisInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferAwsKinesisSchema($input: AwsKinesisInferSchemaInput!) {
              awsKinesisInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferAwsKinesisSchema.model_validate(data).aws_kinesis_infer_schema

    async def infer_aws_redshift_schema(
        self, input: AwsRedshiftInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferAwsRedshiftSchema($input: AwsRedshiftInferSchemaInput!) {
              awsRedshiftInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferAwsRedshiftSchema.model_validate(data).aws_redshift_infer_schema

    async def infer_aws_s3_schema(
        self, input: AwsS3InferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferAwsS3Schema($input: AwsS3InferSchemaInput!) {
              awsS3InferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferAwsS3Schema.model_validate(data).aws_s3_infer_schema

    async def infer_azure_synapse_schema(
        self, input: AzureSynapseInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferAzureSynapseSchema($input: AzureSynapseInferSchemaInput!) {
              azureSynapseInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferAzureSynapseSchema.model_validate(data).azure_synapse_infer_schema

    async def infer_databricks_schema(
        self, input: DatabricksInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferDatabricksSchema($input: DatabricksInferSchemaInput!) {
              databricksInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferDatabricksSchema.model_validate(data).databricks_infer_schema

    async def infer_dbt_model_run_schema(self) -> JsonTypeDefinition:
        query = gql(
            """
            query InferDbtModelRunSchema {
              dbtModelRunInferSchema
            }
            """
        )
        variables: Dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferDbtModelRunSchema.model_validate(data).dbt_model_run_infer_schema

    async def infer_dbt_test_result_schema(self) -> JsonTypeDefinition:
        query = gql(
            """
            query InferDbtTestResultSchema {
              dbtTestResultInferSchema
            }
            """
        )
        variables: Dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferDbtTestResultSchema.model_validate(
            data
        ).dbt_test_result_infer_schema

    async def infer_demo_schema(self) -> JsonTypeDefinition:
        query = gql(
            """
            query InferDemoSchema {
              demoInferSchema
            }
            """
        )
        variables: Dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferDemoSchema.model_validate(data).demo_infer_schema

    async def infer_gcp_big_query_schema(
        self, input: GcpBigQueryInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferGcpBigQuerySchema($input: GcpBigQueryInferSchemaInput!) {
              gcpBigQueryInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferGcpBigQuerySchema.model_validate(data).gcp_big_query_infer_schema

    async def infer_gcp_pub_sub_lite_schema(
        self, input: GcpPubSubLiteInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferGcpPubSubLiteSchema($input: GcpPubSubLiteInferSchemaInput!) {
              gcpPubSubLiteInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferGcpPubSubLiteSchema.model_validate(
            data
        ).gcp_pub_sub_lite_infer_schema

    async def infer_gcp_pub_sub_schema(
        self, input: GcpPubSubInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferGcpPubSubSchema($input: GcpPubSubInferSchemaInput!) {
              gcpPubSubInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferGcpPubSubSchema.model_validate(data).gcp_pub_sub_infer_schema

    async def infer_gcp_storage_schema(
        self, input: GcpStorageInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferGcpStorageSchema($input: GcpStorageInferSchemaInput!) {
              gcpStorageInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferGcpStorageSchema.model_validate(data).gcp_storage_infer_schema

    async def infer_kafka_schema(
        self, input: KafkaInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferKafkaSchema($input: KafkaInferSchemaInput!) {
              kafkaInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferKafkaSchema.model_validate(data).kafka_infer_schema

    async def infer_postgre_sql_schema(
        self, input: PostgreSqlInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferPostgreSqlSchema($input: PostgreSqlInferSchemaInput!) {
              postgreSqlInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferPostgreSqlSchema.model_validate(data).postgre_sql_infer_schema

    async def infer_sample_schema(self, input: List[Any]) -> JsonTypeDefinition:
        query = gql(
            """
            query InferSampleSchema($input: [JSONObject!]!) {
              sampleInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferSampleSchema.model_validate(data).sample_infer_schema

    async def infer_snowflake_schema(
        self, input: SnowflakeInferSchemaInput
    ) -> JsonTypeDefinition:
        query = gql(
            """
            query InferSnowflakeSchema($input: SnowflakeInferSchemaInput!) {
              snowflakeInferSchema(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return InferSnowflakeSchema.model_validate(data).snowflake_infer_schema

    async def kafka_sasl_ssl_plain_credential_secret_changed(
        self, input: KafkaSaslSslPlainCredentialSecretChangedInput
    ) -> KafkaSaslSslPlainCredentialSecretChangedKafkaSaslSslPlainCredentialSecretChanged:
        query = gql(
            """
            query KafkaSaslSslPlainCredentialSecretChanged($input: KafkaSaslSslPlainCredentialSecretChangedInput!) {
              kafkaSaslSslPlainCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return KafkaSaslSslPlainCredentialSecretChanged.model_validate(
            data
        ).kafka_sasl_ssl_plain_credential_secret_changed

    async def kafka_ssl_credential_secret_changed(
        self, input: KafkaSslCredentialSecretChangedInput
    ) -> KafkaSslCredentialSecretChangedKafkaSslCredentialSecretChanged:
        query = gql(
            """
            query KafkaSslCredentialSecretChanged($input: KafkaSslCredentialSecretChangedInput!) {
              kafkaSslCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return KafkaSslCredentialSecretChanged.model_validate(
            data
        ).kafka_ssl_credential_secret_changed

    async def list_credentials(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            ListCredentialsCredentialsListCredential,
            ListCredentialsCredentialsListAwsAthenaCredential,
            ListCredentialsCredentialsListAwsCredential,
            ListCredentialsCredentialsListAwsRedshiftCredential,
            ListCredentialsCredentialsListAzureSynapseEntraIdCredential,
            ListCredentialsCredentialsListAzureSynapseSqlCredential,
            ListCredentialsCredentialsListDatabricksCredential,
            ListCredentialsCredentialsListDbtCloudCredential,
            ListCredentialsCredentialsListDbtCoreCredential,
            ListCredentialsCredentialsListKafkaSaslSslPlainCredential,
            ListCredentialsCredentialsListKafkaSslCredential,
            ListCredentialsCredentialsListLookerCredential,
            ListCredentialsCredentialsListPostgreSqlCredential,
            ListCredentialsCredentialsListSnowflakeCredential,
            ListCredentialsCredentialsListTableauConnectedAppCredential,
            ListCredentialsCredentialsListTableauPersonalAccessTokenCredential,
        ]
    ]:
        query = gql(
            """
            query ListCredentials($filter: ResourceFilter) {
              credentialsList(filter: $filter) {
                ...CredentialDetails
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListCredentials.model_validate(data).credentials_list

    async def list_databricks_catalogs(
        self, input: DatabricksListCatalogsInput
    ) -> List[str]:
        query = gql(
            """
            query ListDatabricksCatalogs($input: DatabricksListCatalogsInput!) {
              databricksListCatalogs(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListDatabricksCatalogs.model_validate(data).databricks_list_catalogs

    async def list_databricks_schemas(
        self, input: DatabricksListSchemasInput
    ) -> List[str]:
        query = gql(
            """
            query ListDatabricksSchemas($input: DatabricksListSchemasInput!) {
              databricksListSchemas(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListDatabricksSchemas.model_validate(data).databricks_list_schemas

    async def list_databricks_tables(
        self, input: DatabricksListTablesInput
    ) -> List[str]:
        query = gql(
            """
            query ListDatabricksTables($input: DatabricksListTablesInput!) {
              databricksListTables(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListDatabricksTables.model_validate(data).databricks_list_tables

    async def list_dbt_model_jobs(self, input: DbtModelListJobsInput) -> List[str]:
        query = gql(
            """
            query ListDbtModelJobs($input: DbtModelListJobsInput!) {
              dbtModelListJobs(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListDbtModelJobs.model_validate(data).dbt_model_list_jobs

    async def list_dbt_model_projects(self) -> List[str]:
        query = gql(
            """
            query ListDbtModelProjects {
              dbtModelListProjects
            }
            """
        )
        variables: Dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListDbtModelProjects.model_validate(data).dbt_model_list_projects

    async def list_resource_namespaces(
        self,
    ) -> List[ListResourceNamespacesResourceNamespacesList]:
        query = gql(
            """
            query listResourceNamespaces {
              resourceNamespacesList {
                resourceNamespace
              }
            }
            """
        )
        variables: Dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListResourceNamespaces.model_validate(data).resource_namespaces_list

    async def list_segmentations(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[ListSegmentationsSegmentationsList]:
        query = gql(
            """
            query ListSegmentations($filter: ResourceFilter) {
              segmentationsList(filter: $filter) {
                ...SegmentationDetails
              }
            }

            fragment SegmentationDetails on Segmentation {
              __typename
              id
              name
              source {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              fields
              createdAt
              updatedAt
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListSegmentations.model_validate(data).segmentations_list

    async def list_sources(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            ListSourcesSourcesListSource,
            ListSourcesSourcesListAwsAthenaSource,
            ListSourcesSourcesListAwsKinesisSource,
            ListSourcesSourcesListAwsRedshiftSource,
            ListSourcesSourcesListAwsS3Source,
            ListSourcesSourcesListAzureSynapseSource,
            ListSourcesSourcesListDatabricksSource,
            ListSourcesSourcesListDbtModelRunSource,
            ListSourcesSourcesListDbtTestResultSource,
            ListSourcesSourcesListGcpBigQuerySource,
            ListSourcesSourcesListGcpPubSubLiteSource,
            ListSourcesSourcesListGcpPubSubSource,
            ListSourcesSourcesListGcpStorageSource,
            ListSourcesSourcesListKafkaSource,
            ListSourcesSourcesListPostgreSqlSource,
            ListSourcesSourcesListSnowflakeSource,
        ]
    ]:
        query = gql(
            """
            query ListSources($filter: ResourceFilter) {
              sourcesList(filter: $filter) {
                ...SourceDetails
              }
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListSources.model_validate(data).sources_list

    async def list_tags(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[ListTagsTagsList]:
        query = gql(
            """
            query ListTags($filter: ResourceFilter) {
              tagsList(filter: $filter) {
                ...TagDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListTags.model_validate(data).tags_list

    async def list_validators(
        self, id: SourceId, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            ListValidatorsValidatorsListValidator,
            ListValidatorsValidatorsListCategoricalDistributionValidator,
            ListValidatorsValidatorsListFreshnessValidator,
            ListValidatorsValidatorsListNumericAnomalyValidator,
            ListValidatorsValidatorsListNumericDistributionValidator,
            ListValidatorsValidatorsListNumericValidator,
            ListValidatorsValidatorsListRelativeTimeValidator,
            ListValidatorsValidatorsListRelativeVolumeValidator,
            ListValidatorsValidatorsListSqlValidator,
            ListValidatorsValidatorsListVolumeValidator,
        ]
    ]:
        query = gql(
            """
            query ListValidators($id: SourceId!, $filter: ResourceFilter) {
              validatorsList(id: $id, filter: $filter) {
                ...ValidatorDetails
              }
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"id": id, "filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListValidators.model_validate(data).validators_list

    async def list_windows(
        self, filter: Union[Optional[ResourceFilter], UnsetType] = UNSET
    ) -> List[
        Union[
            ListWindowsWindowsListWindow,
            ListWindowsWindowsListFileWindow,
            ListWindowsWindowsListFixedBatchWindow,
            ListWindowsWindowsListTumblingWindow,
        ]
    ]:
        query = gql(
            """
            query ListWindows($filter: ResourceFilter) {
              windowsList(filter: $filter) {
                ...WindowDetails
              }
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
                __typename
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FileWindow {
                dataTimeField
              }
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
                dataTimeField
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                  windowTimeoutDisabled
                }
                dataTimeField
              }
            }
            """
        )
        variables: Dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListWindows.model_validate(data).windows_list

    async def looker_credential_secret_changed(
        self, input: LookerCredentialSecretChangedInput
    ) -> LookerCredentialSecretChangedLookerCredentialSecretChanged:
        query = gql(
            """
            query LookerCredentialSecretChanged($input: LookerCredentialSecretChangedInput!) {
              lookerCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return LookerCredentialSecretChanged.model_validate(
            data
        ).looker_credential_secret_changed

    async def poll_source(self, id: SourceId) -> Optional[PollSourceSourcePoll]:
        query = gql(
            """
            mutation PollSource($id: SourceId!) {
              sourcePoll(id: $id) {
                errors {
                  ...ErrorDetails
                }
                state
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return PollSource.model_validate(data).source_poll

    async def postgre_sql_credential_secret_changed(
        self, input: PostgreSqlCredentialSecretChangedInput
    ) -> PostgreSqlCredentialSecretChangedPostgreSqlCredentialSecretChanged:
        query = gql(
            """
            query PostgreSqlCredentialSecretChanged($input: PostgreSqlCredentialSecretChangedInput!) {
              postgreSqlCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return PostgreSqlCredentialSecretChanged.model_validate(
            data
        ).postgre_sql_credential_secret_changed

    async def reset_source(self, id: SourceId) -> ResetSourceSourceReset:
        query = gql(
            """
            mutation ResetSource($id: SourceId!) {
              sourceReset(id: $id) {
                errors {
                  ...ErrorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ResetSource.model_validate(data).source_reset

    async def segments(self, id: SegmentationId) -> List[SegmentsSegments]:
        query = gql(
            """
            query Segments($id: SegmentationId!) {
              segments(id: $id) {
                ...SegmentDetails
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
              dataQuality {
                incidentCount
                totalCount
                quality
                qualityDiff
              }
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return Segments.model_validate(data).segments

    async def segments_by_resource_name(
        self, resource_name: str, resource_namespace: str
    ) -> List[SegmentsByResourceNameSegmentsByResourceName]:
        query = gql(
            """
            query SegmentsByResourceName($resourceName: String!, $resourceNamespace: String! = "default") {
              segmentsByResourceName(
                resourceName: $resourceName
                resourceNamespace: $resourceNamespace
              ) {
                ...SegmentDetails
              }
            }

            fragment SegmentDetails on Segment {
              __typename
              id
              fields {
                field
                value
              }
              muted
              dataQuality {
                incidentCount
                totalCount
                quality
                qualityDiff
              }
            }
            """
        )
        variables: Dict[str, object] = {
            "resourceName": resource_name,
            "resourceNamespace": resource_namespace,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return SegmentsByResourceName.model_validate(data).segments_by_resource_name

    async def snowflake_credential_secret_changed(
        self, input: SnowflakeCredentialSecretChangedInput
    ) -> SnowflakeCredentialSecretChangedSnowflakeCredentialSecretChanged:
        query = gql(
            """
            query SnowflakeCredentialSecretChanged($input: SnowflakeCredentialSecretChangedInput!) {
              snowflakeCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return SnowflakeCredentialSecretChanged.model_validate(
            data
        ).snowflake_credential_secret_changed

    async def start_databricks_warehouse(
        self, input: DatabricksStartWarehouseInput
    ) -> bool:
        query = gql(
            """
            query StartDatabricksWarehouse($input: DatabricksStartWarehouseInput!) {
              databricksStartWarehouse(input: $input)
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return StartDatabricksWarehouse.model_validate(data).databricks_start_warehouse

    async def start_source(self, id: SourceId) -> StartSourceSourceStart:
        query = gql(
            """
            mutation StartSource($id: SourceId!) {
              sourceStart(id: $id) {
                errors {
                  ...ErrorDetails
                }
                state
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return StartSource.model_validate(data).source_start

    async def stop_source(self, id: SourceId) -> StopSourceSourceStop:
        query = gql(
            """
            mutation StopSource($id: SourceId!) {
              sourceStop(id: $id) {
                errors {
                  ...ErrorDetails
                }
                state
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"id": id}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return StopSource.model_validate(data).source_stop

    async def tableau_connected_app_credential_secret_changed(
        self, input: TableauConnectedAppCredentialSecretChangedInput
    ) -> TableauConnectedAppCredentialSecretChangedTableauConnectedAppCredentialSecretChanged:
        query = gql(
            """
            query TableauConnectedAppCredentialSecretChanged($input: TableauConnectedAppCredentialSecretChangedInput!) {
              tableauConnectedAppCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TableauConnectedAppCredentialSecretChanged.model_validate(
            data
        ).tableau_connected_app_credential_secret_changed

    async def tableau_personal_access_token_credential_secret_changed(
        self, input: TableauPersonalAccessTokenCredentialSecretChangedInput
    ) -> TableauPersonalAccessTokenCredentialSecretChangedTableauPersonalAccessTokenCredentialSecretChanged:
        query = gql(
            """
            query TableauPersonalAccessTokenCredentialSecretChanged($input: TableauPersonalAccessTokenCredentialSecretChangedInput!) {
              tableauPersonalAccessTokenCredentialSecretChanged(input: $input) {
                ...CredentialSecretChanged
              }
            }

            fragment CredentialSecretChanged on CredentialSecretChangedResult {
              errors {
                ...ErrorDetails
              }
              hasChanged
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TableauPersonalAccessTokenCredentialSecretChanged.model_validate(
            data
        ).tableau_personal_access_token_credential_secret_changed

    async def update_aws_athena_credential(
        self, input: AwsAthenaCredentialUpdateInput
    ) -> UpdateAwsAthenaCredentialAwsAthenaCredentialUpdate:
        query = gql(
            """
            mutation UpdateAwsAthenaCredential($input: AwsAthenaCredentialUpdateInput!) {
              awsAthenaCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsAthenaCredential.model_validate(
            data
        ).aws_athena_credential_update

    async def update_aws_athena_source(
        self, input: AwsAthenaSourceUpdateInput
    ) -> UpdateAwsAthenaSourceAwsAthenaSourceUpdate:
        query = gql(
            """
            mutation UpdateAwsAthenaSource($input: AwsAthenaSourceUpdateInput!) {
              awsAthenaSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsAthenaSource.model_validate(data).aws_athena_source_update

    async def update_aws_credential(
        self, input: AwsCredentialUpdateInput
    ) -> UpdateAwsCredentialAwsCredentialUpdate:
        query = gql(
            """
            mutation UpdateAwsCredential($input: AwsCredentialUpdateInput!) {
              awsCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsCredential.model_validate(data).aws_credential_update

    async def update_aws_kinesis_source(
        self, input: AwsKinesisSourceUpdateInput
    ) -> UpdateAwsKinesisSourceAwsKinesisSourceUpdate:
        query = gql(
            """
            mutation UpdateAwsKinesisSource($input: AwsKinesisSourceUpdateInput!) {
              awsKinesisSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsKinesisSource.model_validate(data).aws_kinesis_source_update

    async def update_aws_redshift_credential(
        self, input: AwsRedshiftCredentialUpdateInput
    ) -> UpdateAwsRedshiftCredentialAwsRedshiftCredentialUpdate:
        query = gql(
            """
            mutation UpdateAwsRedshiftCredential($input: AwsRedshiftCredentialUpdateInput!) {
              awsRedshiftCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsRedshiftCredential.model_validate(
            data
        ).aws_redshift_credential_update

    async def update_aws_redshift_source(
        self, input: AwsRedshiftSourceUpdateInput
    ) -> UpdateAwsRedshiftSourceAwsRedshiftSourceUpdate:
        query = gql(
            """
            mutation UpdateAwsRedshiftSource($input: AwsRedshiftSourceUpdateInput!) {
              awsRedshiftSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsRedshiftSource.model_validate(data).aws_redshift_source_update

    async def update_aws_s3_source(
        self, input: AwsS3SourceUpdateInput
    ) -> UpdateAwsS3SourceAwsS3SourceUpdate:
        query = gql(
            """
            mutation UpdateAwsS3Source($input: AwsS3SourceUpdateInput!) {
              awsS3SourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAwsS3Source.model_validate(data).aws_s3_source_update

    async def update_azure_synapse_entra_id_credential(
        self, input: AzureSynapseEntraIdCredentialUpdateInput
    ) -> UpdateAzureSynapseEntraIdCredentialAzureSynapseEntraIdCredentialUpdate:
        query = gql(
            """
            mutation UpdateAzureSynapseEntraIdCredential($input: AzureSynapseEntraIdCredentialUpdateInput!) {
              azureSynapseEntraIdCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAzureSynapseEntraIdCredential.model_validate(
            data
        ).azure_synapse_entra_id_credential_update

    async def update_azure_synapse_source(
        self, input: AzureSynapseSourceUpdateInput
    ) -> UpdateAzureSynapseSourceAzureSynapseSourceUpdate:
        query = gql(
            """
            mutation UpdateAzureSynapseSource($input: AzureSynapseSourceUpdateInput!) {
              azureSynapseSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAzureSynapseSource.model_validate(data).azure_synapse_source_update

    async def update_azure_synapse_sql_credential(
        self, input: AzureSynapseSqlCredentialUpdateInput
    ) -> UpdateAzureSynapseSqlCredentialAzureSynapseSqlCredentialUpdate:
        query = gql(
            """
            mutation UpdateAzureSynapseSqlCredential($input: AzureSynapseSqlCredentialUpdateInput!) {
              azureSynapseSqlCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateAzureSynapseSqlCredential.model_validate(
            data
        ).azure_synapse_sql_credential_update

    async def update_categorical_distribution_validator(
        self, input: CategoricalDistributionValidatorUpdateInput
    ) -> UpdateCategoricalDistributionValidatorCategoricalDistributionValidatorUpdate:
        query = gql(
            """
            mutation UpdateCategoricalDistributionValidator($input: CategoricalDistributionValidatorUpdateInput!) {
              categoricalDistributionValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateCategoricalDistributionValidator.model_validate(
            data
        ).categorical_distribution_validator_update

    async def update_channel_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateChannelNamespaceChannelNamespaceUpdate:
        query = gql(
            """
            mutation UpdateChannelNamespace($input: ResourceNamespaceUpdateInput!) {
              channelNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateChannelNamespace.model_validate(data).channel_namespace_update

    async def update_credential_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateCredentialNamespaceCredentialNamespaceUpdate:
        query = gql(
            """
            mutation UpdateCredentialNamespace($input: ResourceNamespaceUpdateInput!) {
              credentialNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateCredentialNamespace.model_validate(
            data
        ).credential_namespace_update

    async def update_databricks_credential(
        self, input: DatabricksCredentialUpdateInput
    ) -> UpdateDatabricksCredentialDatabricksCredentialUpdate:
        query = gql(
            """
            mutation UpdateDatabricksCredential($input: DatabricksCredentialUpdateInput!) {
              databricksCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateDatabricksCredential.model_validate(
            data
        ).databricks_credential_update

    async def update_databricks_source(
        self, input: DatabricksSourceUpdateInput
    ) -> UpdateDatabricksSourceDatabricksSourceUpdate:
        query = gql(
            """
            mutation UpdateDatabricksSource($input: DatabricksSourceUpdateInput!) {
              databricksSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateDatabricksSource.model_validate(data).databricks_source_update

    async def update_dbt_cloud_credential(
        self, input: DbtCloudCredentialUpdateInput
    ) -> UpdateDbtCloudCredentialDbtCloudCredentialUpdate:
        query = gql(
            """
            mutation UpdateDbtCloudCredential($input: DbtCloudCredentialUpdateInput!) {
              dbtCloudCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateDbtCloudCredential.model_validate(data).dbt_cloud_credential_update

    async def update_dbt_core_credential(
        self, input: DbtCoreCredentialUpdateInput
    ) -> UpdateDbtCoreCredentialDbtCoreCredentialUpdate:
        query = gql(
            """
            mutation UpdateDbtCoreCredential($input: DbtCoreCredentialUpdateInput!) {
              dbtCoreCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateDbtCoreCredential.model_validate(data).dbt_core_credential_update

    async def update_dbt_model_run_source(
        self, input: DbtModelRunSourceUpdateInput
    ) -> UpdateDbtModelRunSourceDbtModelRunSourceUpdate:
        query = gql(
            """
            mutation UpdateDbtModelRunSource($input: DbtModelRunSourceUpdateInput!) {
              dbtModelRunSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateDbtModelRunSource.model_validate(data).dbt_model_run_source_update

    async def update_dbt_test_result_source(
        self, input: DbtTestResultSourceUpdateInput
    ) -> UpdateDbtTestResultSourceDbtTestResultSourceUpdate:
        query = gql(
            """
            mutation UpdateDbtTestResultSource($input: DbtTestResultSourceUpdateInput!) {
              dbtTestResultSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateDbtTestResultSource.model_validate(
            data
        ).dbt_test_result_source_update

    async def update_fixed_batch_window(
        self, input: FixedBatchWindowUpdateInput
    ) -> UpdateFixedBatchWindowFixedBatchWindowUpdate:
        query = gql(
            """
            mutation UpdateFixedBatchWindow($input: FixedBatchWindowUpdateInput!) {
              fixedBatchWindowUpdate(input: $input) {
                ...WindowUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
                __typename
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FileWindow {
                dataTimeField
              }
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
                dataTimeField
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                  windowTimeoutDisabled
                }
                dataTimeField
              }
            }

            fragment WindowUpdate on WindowUpdateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateFixedBatchWindow.model_validate(data).fixed_batch_window_update

    async def update_freshness_validator(
        self, input: FreshnessValidatorUpdateInput
    ) -> UpdateFreshnessValidatorFreshnessValidatorUpdate:
        query = gql(
            """
            mutation UpdateFreshnessValidator($input: FreshnessValidatorUpdateInput!) {
              freshnessValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateFreshnessValidator.model_validate(data).freshness_validator_update

    async def update_gcp_big_query_source(
        self, input: GcpBigQuerySourceUpdateInput
    ) -> UpdateGcpBigQuerySourceGcpBigQuerySourceUpdate:
        query = gql(
            """
            mutation UpdateGcpBigQuerySource($input: GcpBigQuerySourceUpdateInput!) {
              gcpBigQuerySourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpBigQuerySource.model_validate(data).gcp_big_query_source_update

    async def update_gcp_credential(
        self, input: GcpCredentialUpdateInput
    ) -> UpdateGcpCredentialGcpCredentialUpdate:
        query = gql(
            """
            mutation UpdateGcpCredential($input: GcpCredentialUpdateInput!) {
              gcpCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpCredential.model_validate(data).gcp_credential_update

    async def update_gcp_pub_sub_lite_source(
        self, input: GcpPubSubLiteSourceUpdateInput
    ) -> UpdateGcpPubSubLiteSourceGcpPubSubLiteSourceUpdate:
        query = gql(
            """
            mutation UpdateGcpPubSubLiteSource($input: GcpPubSubLiteSourceUpdateInput!) {
              gcpPubSubLiteSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpPubSubLiteSource.model_validate(
            data
        ).gcp_pub_sub_lite_source_update

    async def update_gcp_pub_sub_source(
        self, input: GcpPubSubSourceUpdateInput
    ) -> UpdateGcpPubSubSourceGcpPubSubSourceUpdate:
        query = gql(
            """
            mutation UpdateGcpPubSubSource($input: GcpPubSubSourceUpdateInput!) {
              gcpPubSubSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpPubSubSource.model_validate(data).gcp_pub_sub_source_update

    async def update_gcp_storage_source(
        self, input: GcpStorageSourceUpdateInput
    ) -> UpdateGcpStorageSourceGcpStorageSourceUpdate:
        query = gql(
            """
            mutation UpdateGcpStorageSource($input: GcpStorageSourceUpdateInput!) {
              gcpStorageSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateGcpStorageSource.model_validate(data).gcp_storage_source_update

    async def update_identity_provider_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateIdentityProviderNamespaceIdentityProviderNamespaceUpdate:
        query = gql(
            """
            mutation UpdateIdentityProviderNamespace($input: ResourceNamespaceUpdateInput!) {
              identityProviderNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateIdentityProviderNamespace.model_validate(
            data
        ).identity_provider_namespace_update

    async def update_kafka_sasl_ssl_plain_credential(
        self, input: KafkaSaslSslPlainCredentialUpdateInput
    ) -> UpdateKafkaSaslSslPlainCredentialKafkaSaslSslPlainCredentialUpdate:
        query = gql(
            """
            mutation UpdateKafkaSaslSslPlainCredential($input: KafkaSaslSslPlainCredentialUpdateInput!) {
              kafkaSaslSslPlainCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateKafkaSaslSslPlainCredential.model_validate(
            data
        ).kafka_sasl_ssl_plain_credential_update

    async def update_kafka_source(
        self, input: KafkaSourceUpdateInput
    ) -> UpdateKafkaSourceKafkaSourceUpdate:
        query = gql(
            """
            mutation UpdateKafkaSource($input: KafkaSourceUpdateInput!) {
              kafkaSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateKafkaSource.model_validate(data).kafka_source_update

    async def update_kafka_ssl_credential(
        self, input: KafkaSslCredentialUpdateInput
    ) -> UpdateKafkaSslCredentialKafkaSslCredentialUpdate:
        query = gql(
            """
            mutation UpdateKafkaSslCredential($input: KafkaSslCredentialUpdateInput!) {
              kafkaSslCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateKafkaSslCredential.model_validate(data).kafka_ssl_credential_update

    async def update_local_identity_provider(
        self, input: LocalIdentityProviderUpdateInput
    ) -> UpdateLocalIdentityProviderLocalIdentityProviderUpdate:
        query = gql(
            """
            mutation UpdateLocalIdentityProvider($input: LocalIdentityProviderUpdateInput!) {
              localIdentityProviderUpdate(input: $input) {
                ...IdentityProviderUpdate
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }

            fragment IdentityProviderUpdate on IdentityProviderUpdateResult {
              errors {
                code
                message
              }
              identityProvider {
                ...IdentityProviderDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateLocalIdentityProvider.model_validate(
            data
        ).local_identity_provider_update

    async def update_ms_teams_channel(
        self, input: MsTeamsChannelUpdateInput
    ) -> UpdateMsTeamsChannelMsTeamsChannelUpdate:
        query = gql(
            """
            mutation UpdateMsTeamsChannel($input: MsTeamsChannelUpdateInput!) {
              msTeamsChannelUpdate(input: $input) {
                ...ChannelUpdate
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment ChannelUpdate on ChannelUpdateResult {
              errors {
                code
                message
              }
              channel {
                ...ChannelDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateMsTeamsChannel.model_validate(data).ms_teams_channel_update

    async def update_notification_rule(
        self, input: NotificationRuleUpdateInput
    ) -> UpdateNotificationRuleNotificationRuleUpdate:
        query = gql(
            """
            mutation UpdateNotificationRule($input: NotificationRuleUpdateInput!) {
              notificationRuleUpdate(input: $input) {
                ...NotificationRuleUpdate
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment NotificationRuleConditions on NotificationRuleCondition {
              __typename
              id
              notificationRuleId
              createdAt
              updatedAt
              ... on SourceNotificationRuleCondition {
                config {
                  sources {
                    __typename
                    id
                    name
                  }
                }
              }
              ... on SeverityNotificationRuleCondition {
                config {
                  severities
                }
              }
              ... on TypeNotificationRuleCondition {
                config {
                  types
                }
              }
              ... on OwnerNotificationRuleCondition {
                config {
                  owners {
                    id
                    displayName
                  }
                }
              }
              ... on TagNotificationRuleCondition {
                config {
                  tags {
                    id
                    key
                    value
                  }
                }
              }
              ... on SegmentNotificationRuleCondition {
                config {
                  segments {
                    field
                    value
                  }
                }
              }
            }

            fragment NotificationRuleDetails on NotificationRule {
              __typename
              id
              name
              createdAt
              updatedAt
              conditions {
                ...NotificationRuleConditions
              }
              channel {
                ...ChannelDetails
              }
              resourceName
              resourceNamespace
            }

            fragment NotificationRuleUpdate on NotificationRuleUpdateResult {
              errors {
                code
                message
              }
              notificationRule {
                ...NotificationRuleDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNotificationRule.model_validate(data).notification_rule_update

    async def update_notification_rule_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateNotificationRuleNamespaceNotificationRuleNamespaceUpdate:
        query = gql(
            """
            mutation UpdateNotificationRuleNamespace($input: ResourceNamespaceUpdateInput!) {
              notificationRuleNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNotificationRuleNamespace.model_validate(
            data
        ).notification_rule_namespace_update

    async def update_numeric_anomaly_validator(
        self, input: NumericAnomalyValidatorUpdateInput
    ) -> UpdateNumericAnomalyValidatorNumericAnomalyValidatorUpdate:
        query = gql(
            """
            mutation UpdateNumericAnomalyValidator($input: NumericAnomalyValidatorUpdateInput!) {
              numericAnomalyValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNumericAnomalyValidator.model_validate(
            data
        ).numeric_anomaly_validator_update

    async def update_numeric_distribution_validator(
        self, input: NumericDistributionValidatorUpdateInput
    ) -> UpdateNumericDistributionValidatorNumericDistributionValidatorUpdate:
        query = gql(
            """
            mutation UpdateNumericDistributionValidator($input: NumericDistributionValidatorUpdateInput!) {
              numericDistributionValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNumericDistributionValidator.model_validate(
            data
        ).numeric_distribution_validator_update

    async def update_numeric_validator(
        self, input: NumericValidatorUpdateInput
    ) -> UpdateNumericValidatorNumericValidatorUpdate:
        query = gql(
            """
            mutation UpdateNumericValidator($input: NumericValidatorUpdateInput!) {
              numericValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateNumericValidator.model_validate(data).numeric_validator_update

    async def update_owner_notification_rule_condition(
        self, input: OwnerNotificationRuleConditionUpdateInput
    ) -> UpdateOwnerNotificationRuleConditionOwnerNotificationRuleConditionUpdate:
        query = gql(
            """
            mutation UpdateOwnerNotificationRuleCondition($input: OwnerNotificationRuleConditionUpdateInput!) {
              ownerNotificationRuleConditionUpdate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateOwnerNotificationRuleCondition.model_validate(
            data
        ).owner_notification_rule_condition_update

    async def update_postgre_sql_credential(
        self, input: PostgreSqlCredentialUpdateInput
    ) -> UpdatePostgreSqlCredentialPostgreSqlCredentialUpdate:
        query = gql(
            """
            mutation UpdatePostgreSqlCredential($input: PostgreSqlCredentialUpdateInput!) {
              postgreSqlCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdatePostgreSqlCredential.model_validate(
            data
        ).postgre_sql_credential_update

    async def update_postgre_sql_source(
        self, input: PostgreSqlSourceUpdateInput
    ) -> UpdatePostgreSqlSourcePostgreSqlSourceUpdate:
        query = gql(
            """
            mutation UpdatePostgreSqlSource($input: PostgreSqlSourceUpdateInput!) {
              postgreSqlSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdatePostgreSqlSource.model_validate(data).postgre_sql_source_update

    async def update_relative_time_validator(
        self, input: RelativeTimeValidatorUpdateInput
    ) -> UpdateRelativeTimeValidatorRelativeTimeValidatorUpdate:
        query = gql(
            """
            mutation UpdateRelativeTimeValidator($input: RelativeTimeValidatorUpdateInput!) {
              relativeTimeValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateRelativeTimeValidator.model_validate(
            data
        ).relative_time_validator_update

    async def update_relative_volume_validator(
        self, input: RelativeVolumeValidatorUpdateInput
    ) -> UpdateRelativeVolumeValidatorRelativeVolumeValidatorUpdate:
        query = gql(
            """
            mutation UpdateRelativeVolumeValidator($input: RelativeVolumeValidatorUpdateInput!) {
              relativeVolumeValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateRelativeVolumeValidator.model_validate(
            data
        ).relative_volume_validator_update

    async def update_saml_identity_provider(
        self, input: SamlIdentityProviderUpdateInput
    ) -> UpdateSamlIdentityProviderSamlIdentityProviderUpdate:
        query = gql(
            """
            mutation UpdateSamlIdentityProvider($input: SamlIdentityProviderUpdateInput!) {
              samlIdentityProviderUpdate(input: $input) {
                ...IdentityProviderUpdate
              }
            }

            fragment IdentityProviderDetails on IdentityProvider {
              __typename
              id
              name
              disabled
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on SamlIdentityProvider {
                config {
                  entryPoint
                  entityId
                  cert
                }
              }
            }

            fragment IdentityProviderUpdate on IdentityProviderUpdateResult {
              errors {
                code
                message
              }
              identityProvider {
                ...IdentityProviderDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSamlIdentityProvider.model_validate(
            data
        ).saml_identity_provider_update

    async def update_segment_notification_rule_condition(
        self, input: SegmentNotificationRuleConditionUpdateInput
    ) -> UpdateSegmentNotificationRuleConditionSegmentNotificationRuleConditionUpdate:
        query = gql(
            """
            mutation UpdateSegmentNotificationRuleCondition($input: SegmentNotificationRuleConditionUpdateInput!) {
              segmentNotificationRuleConditionUpdate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSegmentNotificationRuleCondition.model_validate(
            data
        ).segment_notification_rule_condition_update

    async def update_segmentation_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateSegmentationNamespaceSegmentationNamespaceUpdate:
        query = gql(
            """
            mutation UpdateSegmentationNamespace($input: ResourceNamespaceUpdateInput!) {
              segmentationNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSegmentationNamespace.model_validate(
            data
        ).segmentation_namespace_update

    async def update_severity_notification_rule_condition(
        self, input: SeverityNotificationRuleConditionUpdateInput
    ) -> UpdateSeverityNotificationRuleConditionSeverityNotificationRuleConditionUpdate:
        query = gql(
            """
            mutation UpdateSeverityNotificationRuleCondition($input: SeverityNotificationRuleConditionUpdateInput!) {
              severityNotificationRuleConditionUpdate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSeverityNotificationRuleCondition.model_validate(
            data
        ).severity_notification_rule_condition_update

    async def update_slack_channel(
        self, input: SlackChannelUpdateInput
    ) -> UpdateSlackChannelSlackChannelUpdate:
        query = gql(
            """
            mutation UpdateSlackChannel($input: SlackChannelUpdateInput!) {
              slackChannelUpdate(input: $input) {
                ...ChannelUpdate
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment ChannelUpdate on ChannelUpdateResult {
              errors {
                code
                message
              }
              channel {
                ...ChannelDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSlackChannel.model_validate(data).slack_channel_update

    async def update_snowflake_credential(
        self, input: SnowflakeCredentialUpdateInput
    ) -> UpdateSnowflakeCredentialSnowflakeCredentialUpdate:
        query = gql(
            """
            mutation UpdateSnowflakeCredential($input: SnowflakeCredentialUpdateInput!) {
              snowflakeCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSnowflakeCredential.model_validate(
            data
        ).snowflake_credential_update

    async def update_snowflake_source(
        self, input: SnowflakeSourceUpdateInput
    ) -> UpdateSnowflakeSourceSnowflakeSourceUpdate:
        query = gql(
            """
            mutation UpdateSnowflakeSource($input: SnowflakeSourceUpdateInput!) {
              snowflakeSourceUpdate(input: $input) {
                ...SourceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment SourceUpdate on SourceUpdateResult {
              errors {
                ...ErrorDetails
              }
              source {
                ...SourceDetails
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSnowflakeSource.model_validate(data).snowflake_source_update

    async def update_source_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateSourceNamespaceSourceNamespaceUpdate:
        query = gql(
            """
            mutation UpdateSourceNamespace($input: ResourceNamespaceUpdateInput!) {
              sourceNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSourceNamespace.model_validate(data).source_namespace_update

    async def update_source_notification_rule_condition(
        self, input: SourceNotificationRuleConditionUpdateInput
    ) -> UpdateSourceNotificationRuleConditionSourceNotificationRuleConditionUpdate:
        query = gql(
            """
            mutation UpdateSourceNotificationRuleCondition($input: SourceNotificationRuleConditionUpdateInput!) {
              sourceNotificationRuleConditionUpdate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSourceNotificationRuleCondition.model_validate(
            data
        ).source_notification_rule_condition_update

    async def update_source_owner(
        self, input: SourceOwnerUpdateInput
    ) -> UpdateSourceOwnerSourceOwnerUpdate:
        query = gql(
            """
            mutation UpdateSourceOwner($input: SourceOwnerUpdateInput!) {
              sourceOwnerUpdate(input: $input) {
                errors {
                  ...ErrorDetails
                }
                source {
                  ...SourceDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment SourceDetails on Source {
              __typename
              id
              name
              createdAt
              updatedAt
              credential {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              windows {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              segmentations {
                __typename
                id
                name
                resourceName
                resourceNamespace
              }
              jtdSchema
              state
              stateUpdatedAt
              resourceName
              resourceNamespace
              tags {
                ...TagDetails
              }
              ... on GcpStorageSource {
                config {
                  project
                  bucket
                  folder
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on GcpBigQuerySource {
                config {
                  project
                  dataset
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on GcpPubSubSource {
                config {
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on GcpPubSubLiteSource {
                config {
                  location
                  project
                  subscriptionId
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsAthenaSource {
                config {
                  catalog
                  database
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsKinesisSource {
                config {
                  region
                  streamName
                  messageFormat {
                    format
                    schema
                  }
                }
              }
              ... on AwsRedshiftSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on AwsS3Source {
                config {
                  bucket
                  prefix
                  csv {
                    nullMarker
                    delimiter
                  }
                  schedule
                  filePattern
                  fileFormat
                }
              }
              ... on AzureSynapseSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DatabricksSource {
                config {
                  catalog
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on DbtTestResultSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on DbtModelRunSource {
                config {
                  jobName
                  projectName
                  schedule
                }
              }
              ... on PostgreSqlSource {
                config {
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on SnowflakeSource {
                config {
                  role
                  warehouse
                  database
                  schema
                  table
                  cursorField
                  lookbackDays
                  schedule
                }
              }
              ... on KafkaSource {
                config {
                  topic
                  messageFormat {
                    format
                    schema
                  }
                }
              }
            }

            fragment TagDetails on Tag {
              id
              key
              value
              isImported
              isSystemTag
              createdAt
              updatedAt
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateSourceOwner.model_validate(data).source_owner_update

    async def update_tableau_connected_app_credential(
        self, input: TableauConnectedAppCredentialUpdateInput
    ) -> UpdateTableauConnectedAppCredentialTableauConnectedAppCredentialUpdate:
        query = gql(
            """
            mutation UpdateTableauConnectedAppCredential($input: TableauConnectedAppCredentialUpdateInput!) {
              tableauConnectedAppCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateTableauConnectedAppCredential.model_validate(
            data
        ).tableau_connected_app_credential_update

    async def update_tableau_personal_access_token_credential(
        self, input: TableauPersonalAccessTokenCredentialUpdateInput
    ) -> UpdateTableauPersonalAccessTokenCredentialTableauPersonalAccessTokenCredentialUpdate:
        query = gql(
            """
            mutation UpdateTableauPersonalAccessTokenCredential($input: TableauPersonalAccessTokenCredentialUpdateInput!) {
              tableauPersonalAccessTokenCredentialUpdate(input: $input) {
                ...CredentialUpdate
              }
            }

            fragment CredentialBase on Credential {
              id
              __typename
              name
              resourceName
              resourceNamespace
            }

            fragment CredentialDetails on Credential {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on AwsCredential {
                config {
                  accessKey
                }
              }
              ... on AwsAthenaCredential {
                config {
                  accessKey
                  region
                  queryResultLocation
                }
              }
              ... on AwsRedshiftCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on AzureSynapseEntraIdCredential {
                config {
                  clientId
                  host
                  port
                  database
                }
              }
              ... on AzureSynapseSqlCredential {
                config {
                  username
                  host
                  port
                  database
                }
              }
              ... on DatabricksCredential {
                config {
                  host
                  port
                  httpPath
                }
              }
              ... on DbtCloudCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                  accountId
                  apiBaseUrl
                }
              }
              ... on DbtCoreCredential {
                config {
                  warehouseCredential {
                    ...CredentialBase
                  }
                }
              }
              ... on LookerCredential {
                config {
                  baseUrl
                  clientId
                }
              }
              ... on PostgreSqlCredential {
                config {
                  host
                  port
                  user
                  defaultDatabase
                }
              }
              ... on SnowflakeCredential {
                config {
                  account
                  user
                  role
                  warehouse
                }
              }
              ... on KafkaSslCredential {
                config {
                  bootstrapServers
                  caCertificate
                }
              }
              ... on KafkaSaslSslPlainCredential {
                config {
                  bootstrapServers
                  username
                }
              }
              ... on TableauConnectedAppCredential {
                config {
                  host
                  site
                  user
                  clientId
                  secretId
                }
              }
              ... on TableauPersonalAccessTokenCredential {
                config {
                  host
                  site
                  tokenName
                }
              }
            }

            fragment CredentialUpdate on CredentialUpdateResult {
              errors {
                ...ErrorDetails
              }
              credential {
                ...CredentialDetails
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateTableauPersonalAccessTokenCredential.model_validate(
            data
        ).tableau_personal_access_token_credential_update

    async def update_tag_notification_rule_condition(
        self, input: TagNotificationRuleConditionUpdateInput
    ) -> UpdateTagNotificationRuleConditionTagNotificationRuleConditionUpdate:
        query = gql(
            """
            mutation UpdateTagNotificationRuleCondition($input: TagNotificationRuleConditionUpdateInput!) {
              tagNotificationRuleConditionUpdate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateTagNotificationRuleCondition.model_validate(
            data
        ).tag_notification_rule_condition_update

    async def update_tumbling_window(
        self, input: TumblingWindowUpdateInput
    ) -> UpdateTumblingWindowTumblingWindowUpdate:
        query = gql(
            """
            mutation UpdateTumblingWindow($input: TumblingWindowUpdateInput!) {
              tumblingWindowUpdate(input: $input) {
                ...WindowUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment WindowDetails on Window {
              __typename
              id
              name
              source {
                id
                name
                resourceName
                resourceNamespace
                __typename
              }
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              ... on FileWindow {
                dataTimeField
              }
              ... on FixedBatchWindow {
                config {
                  batchSize
                  segmentedBatching
                  batchTimeoutSecs
                }
                dataTimeField
              }
              ... on TumblingWindow {
                config {
                  windowSize
                  timeUnit
                  windowTimeoutDisabled
                }
                dataTimeField
              }
            }

            fragment WindowUpdate on WindowUpdateResult {
              errors {
                ...ErrorDetails
              }
              window {
                ...WindowDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateTumblingWindow.model_validate(data).tumbling_window_update

    async def update_type_notification_rule_condition(
        self, input: TypeNotificationRuleConditionUpdateInput
    ) -> UpdateTypeNotificationRuleConditionTypeNotificationRuleConditionUpdate:
        query = gql(
            """
            mutation UpdateTypeNotificationRuleCondition($input: TypeNotificationRuleConditionUpdateInput!) {
              typeNotificationRuleConditionUpdate(input: $input) {
                ...NotificationRuleConditionCreation
              }
            }

            fragment NotificationRuleConditionCreation on NotificationRuleConditionCreateResult {
              errors {
                code
                message
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateTypeNotificationRuleCondition.model_validate(
            data
        ).type_notification_rule_condition_update

    async def update_user(self, input: UserUpdateInput) -> UpdateUserUserUpdate:
        query = gql(
            """
            mutation UpdateUser($input: UserUpdateInput!) {
              userUpdate(input: $input) {
                ...UserUpdate
              }
            }

            fragment IdentityDetails on Identity {
              ... on LocalIdentity {
                __typename
                id
                userId
                username
                createdAt
              }
              ... on FederatedIdentity {
                __typename
                id
                userId
                idp {
                  __typename
                  id
                  name
                }
                createdAt
              }
            }

            fragment UserDetails on User {
              id
              displayName
              fullName
              email
              role
              status
              identities {
                ...IdentityDetails
              }
              createdAt
              updatedAt
              lastLoginAt
              resourceName
              resourceNamespace
            }

            fragment UserUpdate on UserUpdateResult {
              errors {
                code
                message
              }
              user {
                ...UserDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateUser.model_validate(data).user_update

    async def update_user_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateUserNamespaceUserNamespaceUpdate:
        query = gql(
            """
            mutation UpdateUserNamespace($input: ResourceNamespaceUpdateInput!) {
              userNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateUserNamespace.model_validate(data).user_namespace_update

    async def update_validator_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateValidatorNamespaceValidatorNamespaceUpdate:
        query = gql(
            """
            mutation UpdateValidatorNamespace($input: ResourceNamespaceUpdateInput!) {
              validatorNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateValidatorNamespace.model_validate(data).validator_namespace_update

    async def update_validator_with_dynamic_threshold(
        self, input: ValidatorWithDynamicThresholdUpdateInput
    ) -> UpdateValidatorWithDynamicThresholdValidatorWithDynamicThresholdUpdate:
        query = gql(
            """
            mutation UpdateValidatorWithDynamicThreshold($input: ValidatorWithDynamicThresholdUpdateInput!) {
              validatorWithDynamicThresholdUpdate(input: $input) {
                errors {
                  ...ErrorDetails
                }
                validator {
                  ...ValidatorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateValidatorWithDynamicThreshold.model_validate(
            data
        ).validator_with_dynamic_threshold_update

    async def update_validator_with_fixed_threshold(
        self, input: ValidatorWithFixedThresholdUpdateInput
    ) -> UpdateValidatorWithFixedThresholdValidatorWithFixedThresholdUpdate:
        query = gql(
            """
            mutation UpdateValidatorWithFixedThreshold($input: ValidatorWithFixedThresholdUpdateInput!) {
              validatorWithFixedThresholdUpdate(input: $input) {
                errors {
                  ...ErrorDetails
                }
                validator {
                  ...ValidatorDetails
                }
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateValidatorWithFixedThreshold.model_validate(
            data
        ).validator_with_fixed_threshold_update

    async def update_volume_validator(
        self, input: VolumeValidatorUpdateInput
    ) -> UpdateVolumeValidatorVolumeValidatorUpdate:
        query = gql(
            """
            mutation UpdateVolumeValidator($input: VolumeValidatorUpdateInput!) {
              volumeValidatorUpdate(input: $input) {
                ...ValidatorUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment ValidatorDetails on Validator {
              __typename
              id
              name
              hasCustomName
              createdAt
              updatedAt
              sourceConfig {
                source {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                window {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                segmentation {
                  __typename
                  id
                  name
                  resourceName
                  resourceNamespace
                }
                filter
              }
              resourceName
              resourceNamespace
              ... on NumericValidator {
                config {
                  sourceField
                  metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on CategoricalDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  categoricalDistributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on NumericDistributionValidator {
                config {
                  sourceField
                  referenceSourceField
                  distributionMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on VolumeValidator {
                config {
                  optionalSourceField: sourceField
                  sourceFields
                  volumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on NumericAnomalyValidator {
                config {
                  sourceField
                  numericAnomalyMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  referenceSourceField
                  sensitivity
                  minimumReferenceDatapoints
                  minimumAbsoluteDifference
                  minimumRelativeDifferencePercent
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on RelativeTimeValidator {
                config {
                  sourceFieldMinuend
                  sourceFieldSubtrahend
                  relativeTimeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on FreshnessValidator {
                config {
                  initializeWithBackfill
                  optionalSourceField: sourceField
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
              }
              ... on RelativeVolumeValidator {
                config {
                  optionalSourceField: sourceField
                  optionalReferenceSourceField: referenceSourceField
                  relativeVolumeMetric: metric
                  initializeWithBackfill
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                }
                referenceSourceConfig {
                  source {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  window {
                    __typename
                    id
                    name
                    resourceName
                    resourceNamespace
                  }
                  history
                  offset
                  filter
                }
              }
              ... on SqlValidator {
                config {
                  query
                  threshold {
                    __typename
                    ... on FixedThreshold {
                      operator
                      value
                    }
                    ... on DynamicThreshold {
                      sensitivity
                      decisionBoundsType
                    }
                  }
                  initializeWithBackfill
                }
              }
            }

            fragment ValidatorUpdate on ValidatorUpdateResult {
              errors {
                ...ErrorDetails
              }
              validator {
                ...ValidatorDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateVolumeValidator.model_validate(data).volume_validator_update

    async def update_webhook_channel(
        self, input: WebhookChannelUpdateInput
    ) -> UpdateWebhookChannelWebhookChannelUpdate:
        query = gql(
            """
            mutation UpdateWebhookChannel($input: WebhookChannelUpdateInput!) {
              webhookChannelUpdate(input: $input) {
                ...ChannelUpdate
              }
            }

            fragment ChannelDetails on Channel {
              __typename
              id
              name
              createdAt
              updatedAt
              resourceName
              resourceNamespace
              notificationRules {
                __typename
                id
                name
              }
              ... on SlackChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
              ... on WebhookChannel {
                config {
                  webhookUrl
                  applicationLinkUrl
                  authHeader
                }
              }
              ... on MsTeamsChannel {
                config {
                  webhookUrl
                  timezone
                  applicationLinkUrl
                }
              }
            }

            fragment ChannelUpdate on ChannelUpdateResult {
              errors {
                code
                message
              }
              channel {
                ...ChannelDetails
              }
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateWebhookChannel.model_validate(data).webhook_channel_update

    async def update_window_namespace(
        self, input: ResourceNamespaceUpdateInput
    ) -> UpdateWindowNamespaceWindowNamespaceUpdate:
        query = gql(
            """
            mutation UpdateWindowNamespace($input: ResourceNamespaceUpdateInput!) {
              windowNamespaceUpdate(input: $input) {
                ...NamespaceUpdate
              }
            }

            fragment ErrorDetails on ApiError {
              __typename
              code
              message
            }

            fragment NamespaceUpdate on ResourceNamespaceUpdatedResult {
              errors {
                ...ErrorDetails
              }
              resourceName
              resourceNamespace
            }
            """
        )
        variables: Dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UpdateWindowNamespace.model_validate(data).window_namespace_update

    async def verify_source_schema(
        self, id: SourceId, schema: JsonTypeDefinition
    ) -> VerifySourceSchemaSourceSchemaVerify:
        query = gql(
            """
            mutation VerifySourceSchema($id: SourceId!, $schema: JsonTypeDefinition!) {
              sourceSchemaVerify(id: $id, input: $schema) {
                validatorConflicts {
                  validator {
                    id
                    name
                  }
                  fields
                }
                segmentationConflicts {
                  segmentation {
                    id
                    name
                  }
                  fields
                }
                windowConflicts {
                  window {
                    __typename
                    id
                    name
                  }
                  fields
                }
              }
            }
            """
        )
        variables: Dict[str, object] = {"id": id, "schema": schema}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return VerifySourceSchema.model_validate(data).source_schema_verify
