from enum import Enum


class ApiErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"


class CategoricalDistributionMetric(str, Enum):
    ADDED = "ADDED"
    CHANGED = "CHANGED"
    RELATIVE_ENTROPY = "RELATIVE_ENTROPY"
    REMOVED = "REMOVED"


class ComparisonOperator(str, Enum):
    EQUAL = "EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    NOT_EQUAL = "NOT_EQUAL"


class DecisionBoundsType(str, Enum):
    LOWER = "LOWER"
    UPPER = "UPPER"
    UPPER_AND_LOWER = "UPPER_AND_LOWER"


class FileFormat(str, Enum):
    CSV = "CSV"
    JSON = "JSON"
    PARQUET = "PARQUET"


class IdentityDeleteErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"


class IdentityProviderCreateErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"


class IdentityProviderDeleteErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"


class IdentityProviderUpdateErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"


class IncidentSeverity(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"
    MEDIUM = "MEDIUM"


class IncidentStatus(str, Enum):
    INVESTIGATING = "INVESTIGATING"
    RESOLVED_EXPECTED = "RESOLVED_EXPECTED"
    RESOLVED_NOT_AN_ANOMALY = "RESOLVED_NOT_AN_ANOMALY"
    RESOLVED_UNEXPECTED = "RESOLVED_UNEXPECTED"
    TRIAGE = "TRIAGE"


class IssueTypename(str, Enum):
    GenericSourceError = "GenericSourceError"
    SchemaChangeSourceError = "SchemaChangeSourceError"
    SegmentLimitExceededSourceError = "SegmentLimitExceededSourceError"
    ValidatorIncident = "ValidatorIncident"


class NumericAnomalyMetric(str, Enum):
    COUNT = "COUNT"
    PERCENTAGE = "PERCENTAGE"


class NumericDistributionMetric(str, Enum):
    MAXIMUM_RATIO = "MAXIMUM_RATIO"
    MEAN_RATIO = "MEAN_RATIO"
    MINIMUM_RATIO = "MINIMUM_RATIO"
    RELATIVE_ENTROPY = "RELATIVE_ENTROPY"
    STANDARD_DEVIATION_RATIO = "STANDARD_DEVIATION_RATIO"
    SUM_RATIO = "SUM_RATIO"


class NumericMetric(str, Enum):
    MAX = "MAX"
    MEAN = "MEAN"
    MIN = "MIN"
    STD = "STD"
    SUM = "SUM"


class RelativeTimeMetric(str, Enum):
    MAXIMUM_DIFFERENCE = "MAXIMUM_DIFFERENCE"
    MEAN_DIFFERENCE = "MEAN_DIFFERENCE"
    MINIMUM_DIFFERENCE = "MINIMUM_DIFFERENCE"


class RelativeVolumeMetric(str, Enum):
    COUNT_RATIO = "COUNT_RATIO"
    PERCENTAGE_RATIO = "PERCENTAGE_RATIO"


class Role(str, Enum):
    ADMIN = "ADMIN"
    ANONYMOUS = "ANONYMOUS"
    EDITOR = "EDITOR"
    GUEST = "GUEST"
    SUPER = "SUPER"
    VIEWER = "VIEWER"


class SourceState(str, Enum):
    BACKFILLING = "BACKFILLING"
    IDLE = "IDLE"
    INIT = "INIT"
    PENDING_BACKFILL = "PENDING_BACKFILL"
    POLLING = "POLLING"
    RUNNING = "RUNNING"
    STARTING = "STARTING"
    STOPPING = "STOPPING"


class StreamingSourceMessageFormat(str, Enum):
    AVRO = "AVRO"
    JSON = "JSON"
    PROTOBUF = "PROTOBUF"


class UserDeleteErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"


class UserUpdateErrorCode(str, Enum):
    UNKNOWN = "UNKNOWN"


class ValidatorState(str, Enum):
    BACKFILLING = "BACKFILLING"
    PENDING_BACKFILL = "PENDING_BACKFILL"
    PROCESSING = "PROCESSING"
    RUNNING = "RUNNING"


class VolumeMetric(str, Enum):
    COUNT = "COUNT"
    DUPLICATES_COUNT = "DUPLICATES_COUNT"
    DUPLICATES_PERCENTAGE = "DUPLICATES_PERCENTAGE"
    PERCENTAGE = "PERCENTAGE"
    UNIQUE_COUNT = "UNIQUE_COUNT"
    UNIQUE_PERCENTAGE = "UNIQUE_PERCENTAGE"


class WindowTimeUnit(str, Enum):
    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"
    MONTH = "MONTH"
    WEEK = "WEEK"
