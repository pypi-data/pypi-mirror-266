"""Filters configuration."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Union

from validio_sdk.resource import FieldSelector
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._field_selector import SelectorWithFieldName
from validio_sdk.resource._serde import NODE_TYPE_FIELD_NAME

if TYPE_CHECKING:
    from validio_sdk.scalars import JsonPointer


class Filter(Diffable):
    """
    Base class for a filter configuration.

    https://docs.validio.io/docs/filters
    """

    @property
    def _node_type(self) -> str:
        return self.__class__.__name__

    def _maybe_set_field_selector(
        self, field_name: str, field: Union["JsonPointer", FieldSelector]
    ) -> str:
        if isinstance(field, str):
            return field

        self._field_selector = SelectorWithFieldName(
            field_name=field_name,
            field_selector=field,
        )
        return "<UNRESOLVED>"

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return set(self.__dict__.keys())

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        return {}

    def _encode(self) -> dict[str, object]:
        data = self.__dict__
        data["_node_type"] = self._node_type

        return data

    @staticmethod
    def _decode(obj: dict[str, Any]) -> "Filter":
        cls = eval(obj[NODE_TYPE_FIELD_NAME])
        FieldSelector._replace(obj)
        return cls(**{k: v for k, v in obj.items() if k != NODE_TYPE_FIELD_NAME})

    def _api_create_input(self) -> dict[str, object]:
        return {
            "__typename": f"{self.__class__.__name__}Expression",
            **self.__dict__,
        }


class BooleanFilterOperator(str, Enum):
    """
    Configures the behavior of a Boolean filter.

    IS_TRUE: Allow values equal to TRUE
    IS_FALSE: Allow values equal to FALSE
    """

    IS_TRUE = "IS_TRUE"
    IS_FALSE = "IS_FALSE"


@dataclass
class BooleanFilter(Filter):
    """A Boolean filter configuration.

    https://docs.validio.io/docs/filters#boolean-filter
    """

    field: str | FieldSelector
    operator: BooleanFilterOperator

    def __post_init__(self) -> None:
        """Post init for filter."""
        self.field = self._maybe_set_field_selector("field", self.field)
        if not isinstance(self.operator, BooleanFilterOperator):
            self.operator = BooleanFilterOperator(self.operator)


class NullFilterOperator(str, Enum):
    """
    Configures the behavior of a Null filter.

    IS: Filter in NULL values
    IS_NOT: Filter in Non-NULL values
    """

    IS = "IS"
    IS_NOT = "IS_NOT"


@dataclass
class NullFilter(Filter):
    """A Null filter configuration.

    https://docs.validio.io/docs/filters#null
    """

    field: str | FieldSelector
    operator: NullFilterOperator = NullFilterOperator.IS

    def __post_init__(self) -> None:
        """Post init for filter."""
        self.field = self._maybe_set_field_selector("field", self.field)
        if not isinstance(self.operator, NullFilterOperator):
            self.operator = NullFilterOperator(self.operator)


class EnumFilterOperator(str, Enum):
    """
    Configures the behavior of an Enum filter.

    ALLOW: Allow values in the enum
    DENY: Deny values in the enum
    """

    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass
class EnumFilter(Filter):
    """An Enum filter configuration.

    https://docs.validio.io/docs/filters#enum
    """

    field: str | FieldSelector
    values: list[str]
    operator: EnumFilterOperator = EnumFilterOperator.ALLOW

    def __post_init__(self) -> None:
        """Post init for filter."""
        self.field = self._maybe_set_field_selector("field", self.field)
        if not isinstance(self.operator, EnumFilterOperator):
            self.operator = EnumFilterOperator(self.operator)


class StringFilterOperator(str, Enum):
    """
    Configures the behavior of a String filter.

    IS_EMPTY: The string is empty
    IS_NOT_EMPTY: The string is not empty
    CONTAINS: The string contains
    DOES_NOT_CONTAIN: The string does not contain
    STARTS_WITH: The string is prefixed with
    ENDS_WITH: The string is suffixed with
    IS_EXACTLY: Exact match of full string
    REGEX: Regular expressions
    """

    IS_EMPTY = "IS_EMPTY"
    IS_NOT_EMPTY = "IS_NOT_EMPTY"
    CONTAINS = "CONTAINS"
    DOES_NOT_CONTAIN = "DOES_NOT_CONTAIN"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    IS_EXACTLY = "IS_EXACTLY"
    REGEX = "REGEX"


@dataclass
class StringFilter(Filter):
    """A String filter configuration.

    https://docs.validio.io/docs/filters#string
    """

    field: str | FieldSelector
    value: str | None
    operator: StringFilterOperator

    def __post_init__(self) -> None:
        """Post init for filter."""
        self.field = self._maybe_set_field_selector("field", self.field)
        if not isinstance(self.operator, StringFilterOperator):
            self.operator = StringFilterOperator(self.operator)


class ThresholdFilterOperator(str, Enum):
    """
    Configures the behavior of a String filter.

    EQUAL: The value equals (==)
    NOT_EQUAL: The value does not equal (!=)
    LESS_THAN: The value is less than (<)
    LESS_THAN_OR_EQUAL: The value is less than or equal (<=)
    GREATER_THAN: The value is greater than (>)
    GREATER_THAN_OR_EQUAL: The value is greater than or equal (>=)
    """

    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS"
    LESS_THAN_OR_EQUAL = "LESS_EQUAL"
    GREATER_THAN = "GREATER"
    GREATER_THAN_OR_EQUAL = "GREATER_EQUAL"


@dataclass
class ThresholdFilter(Filter):
    """A Threshold filter configuration.

    https://docs.validio.io/docs/filters#threshold-filter
    """

    field: str | FieldSelector
    value: float
    operator: ThresholdFilterOperator

    def __post_init__(self) -> None:
        """Post init for filter."""
        self.field = self._maybe_set_field_selector("field", self.field)
        if not isinstance(self.operator, ThresholdFilterOperator):
            self.operator = ThresholdFilterOperator(self.operator)
