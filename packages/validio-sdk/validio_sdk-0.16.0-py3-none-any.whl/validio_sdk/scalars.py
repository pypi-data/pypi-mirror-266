"""Scalars used in our GraphQL schemas."""

from dataclasses import fields
from datetime import datetime
from enum import Enum
from typing import Union

from validio_sdk import (
    BooleanFilter,
    EnumFilter,
    NullFilter,
    StringFilter,
    ThresholdFilter,
)

ValidioId = str
CredentialId = ValidioId
SegmentationId = ValidioId
SourceId = ValidioId
ValidatorId = ValidioId
WindowId = ValidioId

CronExpression = str

# Raw JSON, used for filters
JsonFilterExpression = Union[
    BooleanFilter, EnumFilter, NullFilter, StringFilter, ThresholdFilter
]

# JTD schema definition
JsonTypeDefinition = dict

# A JSONPath expression specifying a field within a datapoint.
# Examples:
#   user.address.street for nested structures.
#   name to select a non-nested field called `name`.
JsonPointer = str


def serialize_json_filter_expression(value: JsonFilterExpression) -> dict:
    """
    Serialize filter type to JSON.

    Convert a typed filter to JSON. Since they use enums for operators the
    operator value will be used.

    :param value: The typed filter
    :returns: A dictionary for the filter
    """
    data = {"__typename": f"{value._node_type}Expression"}

    for field in fields(value):
        v = getattr(value, field.name)
        if isinstance(v, Enum):
            data[field.name] = v.value
        elif field.type in [float, int, str]:
            # Convert for known types. Even with type hint's it's possible to
            # set a float value to a string f.ex. and that will serialize the
            # request faulty making the backend not accept the request.
            data[field.name] = field.type(v)
        else:
            data[field.name] = v

    return data


def serialize_rfc3339_datetime(value: datetime) -> datetime:
    """
    Adds TZINFO if not present to a Python Datetime object so that it conforms to the
    RFC3339 standard that is accepted by the platform.

    :param value: The datetime object
    :returns: A tz-aware datetime object
    """
    if value.tzinfo:
        return value

    return value.astimezone()
