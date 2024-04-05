"""Validator configuration."""

import json
from abc import ABC
from typing import TYPE_CHECKING, Any, cast

from validio_sdk.graphql_client import (
    CategoricalDistributionMetric,
    NumericAnomalyMetric,
    NumericDistributionMetric,
    NumericMetric,
    ReferenceSourceConfigCreateInput,
    ReferenceSourceConfigUpdateInput,
    RelativeTimeMetric,
    RelativeVolumeMetric,
    SourceConfigCreateInput,
    SourceConfigUpdateInput,
    VolumeMetric,
)
from validio_sdk.resource import FieldSelector
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._errors import ManifestConfigurationError
from validio_sdk.resource._field_selector import (
    FromFieldSelector,
    SelectorWithFieldName,
)
from validio_sdk.resource._resource import Resource
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    _api_create_input_params,
    _api_update_input_params,
    _encode_resource,
)
from validio_sdk.resource.filters import Filter
from validio_sdk.resource.segmentations import Segmentation
from validio_sdk.resource.sources import (
    DemoSource,
    ObjectStorageSource,
    Source,
    StreamSource,
)
from validio_sdk.resource.thresholds import DynamicThreshold, Threshold
from validio_sdk.resource.windows import (
    FileWindow,
    GlobalWindow,
    TumblingWindow,
    Window,
)
from validio_sdk.scalars import JsonFilterExpression, JsonPointer
from validio_sdk.validio_client import ValidioAPIClient

if TYPE_CHECKING:
    from validio_sdk.code._import import ImportContext
    from validio_sdk.resource._diff import DiffContext


class Reference(Diffable):
    """
    Represents configuration for reference validators.

    See the Validio docs for more info on reference configuration
    https://docs.validio.io/docs/reference-source-config
    """

    def __init__(
        self,
        source: Source,
        window: Window,
        history: int,
        offset: int,
        filter: Filter | None = None,
    ):
        """
        Constructor.

        :param source: The reference source to attach the validator to. (immutable)
        :param window: The window in the reference source to attach the
            validator to. (immutable)
        :param history: Over how many windows metric will be calculated
            for the reference source
        :param offset: By how many windows in the past the reference
            calculation is shifted.
        :param filter: Optional filter on the data processed from the
            reference source.
        """
        self.source_name = source.name
        self.window_name = window.name
        self.history = history
        self.offset = offset
        self.filter = filter

    def _immutable_fields(self) -> set[str]:
        return {"source_name", "window_name"}

    def _mutable_fields(self) -> set[str]:
        return {"history", "offset"}

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        return {"filter": self.filter}

    def _import_str(
        self,
        indent_level: int,
        import_ctx: "ImportContext",
        inits: list[tuple[str, Any, str | None]] | None = None,
    ) -> str:
        inits = list(inits or [])
        source = import_ctx.get_variable(Source, self.source_name)
        window = import_ctx.get_variable(Window, self.window_name)
        inits = [*inits, ("source", source, None), ("window", window, None)]
        return super()._import_str(
            indent_level=indent_level,
            import_ctx=import_ctx,
            inits=inits,
        )

    def _reference_source_config_create_input(
        self, ctx: "DiffContext"
    ) -> ReferenceSourceConfigCreateInput:
        source_id = ctx.sources[self.source_name]._must_id()
        window_id = ctx.windows[self.window_name]._must_id()
        return ReferenceSourceConfigCreateInput(
            # type: ignore[call-arg]
            source_id=source_id,
            # type: ignore[call-arg]
            window_id=window_id,
            filter=cast(
                JsonFilterExpression | None,
                self.filter._api_create_input() if self.filter else None,
            ),
            offset=self.offset,
            history=self.history,
        )

    def _reference_source_config_update_input(self) -> ReferenceSourceConfigUpdateInput:
        return ReferenceSourceConfigUpdateInput(
            filter=cast(
                JsonFilterExpression | None,
                self.filter._api_create_input() if self.filter else None,
            ),
            offset=self.offset,
            history=self.history,
        )

    def _encode(self) -> dict[str, object]:
        return json.loads(
            json.dumps(
                self.__dict__,
                default=lambda o: o._encode(),
            )
        )

    @staticmethod
    def _decode(
        obj: dict[str, Any],
        all_sources: dict[str, Source],
        all_windows: dict[str, Window],
    ) -> "Reference":
        source_name = obj["source_name"]
        window_name = obj["window_name"]
        if source_name not in all_sources:
            raise RuntimeError(
                f"invalid configuration: no such reference source {source_name}"
            )
        if window_name not in all_windows:
            raise RuntimeError(
                f"invalid configuration: no such reference window {source_name}"
            )

        source = all_sources[source_name]
        window = all_windows[window_name]
        filter_ = (
            Filter._decode(obj["filter"]) if "filter" in obj and obj["filter"] else None
        )

        # Remove the fields that are not compatible with the constructor.
        # We have the objects themselves now, so they will be repopulated by
        # the constructor accordingly.
        obj = {k: v for k, v in obj.items() if k not in {"source_name", "window_name"}}

        return Reference(
            **{
                **obj,
                "source": source,
                "window": window,
                "filter": filter_,
            }
        )  # type:ignore


class Validator(Resource, ABC):
    """Base class for a validator resources.

    https://docs.validio.io/docs/validators
    """

    def __init__(
        self,
        name: str,
        window: Window,
        segmentation: Segmentation,
        threshold: Threshold,
        filter: Filter | None = None,
        reference: Reference | None = None,
        initialize_with_backfill: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the validator. (immutable)
        :param window: The window to attach the validator to. (immutable)
        :param segmentation: The segmentation to attach the validator to. (immutable)
        :param threshold: A threshold configuration to attach to the validator.
            Note: While a threshold's configuration can be updated, it is not
            possible to change the threshold type after the validator has been
            created.
        :param filter: Optional filter to attach to the validator.
            https://docs.validio.io/docs/validators#filters
        :param reference: Configuration for reference validators
        :param initialize_with_backfill: If set to true, will wait for an
            explicit source backfill before the validator can start
            processing data.
            https://docs.validio.io/docs/validators#backfill
        """
        super().__init__(name, window._resource_graph)

        if window.source_name != segmentation.source_name:
            raise ManifestConfigurationError(
                f"invalid {self.__class__.__name__} validator '{name}': "
                f"window source '{window.source_name}' does not match "
                f"segmentation source '{segmentation.source_name}'"
            )

        source = window._resource_graph._find_source(window.source_name)
        if not source:
            raise RuntimeError(
                f"invalid {self.__class__.__name__} validator '{name}': "
                f"missing source '{window.source_name}' for window '{window.name}'"
            )

        _validate_source_window_compatibility(source, window)

        self.source_name: str = source.name
        self.window_name: str = window.name
        self.segmentation_name: str = segmentation.name
        self.filter = filter
        self.threshold = threshold
        self.reference = reference
        self.initialize_with_backfill: bool = initialize_with_backfill

        source.add(name, self)

    def _maybe_set_field_selector(
        self, field_name: str, field: JsonPointer | FieldSelector
    ) -> str:
        if isinstance(field, str):
            return field

        self._field_selector = SelectorWithFieldName(
            field_name=field_name,
            field_selector=field,
        )
        return "<UNRESOLVED>"

    def _maybe_set_reference_field_selector(
        self,
        field_name: str,
        field: JsonPointer | FromFieldSelector,
        source_field_name: str,
        source_field_value: JsonPointer | FieldSelector,
    ) -> str:
        if isinstance(field, str):
            return field

        if not isinstance(source_field_value, FieldSelector):
            raise ManifestConfigurationError(
                f"invalid configuration for validator {self.name}: source field"
                f" {source_field_name} (value={source_field_value}) does not use a"
                " field selector; reference field can only be used with a matching"
                " source field selector"
            )

        self._reference_field_selector = {"field_name": field_name}
        return "<UNRESOLVED>"

    def _validate_reference_filter_no_field_selector(self) -> None:
        if (
            self.reference
            and self.reference.filter
            and hasattr(self.reference.filter, "_field_selector")
        ):
            raise ManifestConfigurationError(
                f"invalid {self.__class__.__name__} '{self.name}': "
                "field selector not allowed in a reference filter configuration"
            )

    def _validate_unique_field_selector(self) -> None:
        if (
            hasattr(self, "_field_selector")
            and self.filter
            and hasattr(self.filter, "_field_selector")
        ):
            raise ManifestConfigurationError(
                f"invalid {self.__class__.__name__} '{self.name}': "
                "field selector cannot be used in both source field "
                "and filter at the same time "
            )

        self._validate_reference_filter_no_field_selector()

    def _validate_no_field_selector(self) -> None:
        position = None
        if hasattr(self, "_field_selector"):
            position = f"field '{self._field_selector.field_name}'"
        elif self.filter and hasattr(self.filter, "_field_selector"):
            position = "filter configuration"

        if position:
            raise ManifestConfigurationError(
                f"invalid {self.__class__.__name__} '{self.name}': "
                f"field selector not allowed in {position}"
            )

        self._validate_reference_filter_no_field_selector()

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        objects: dict[str, Diffable | list[Diffable] | None] = {
            "filter": self.filter,
            "threshold": self.threshold,
        }
        if self.reference:
            objects["reference"] = self.reference

        return objects

    def _immutable_fields(self) -> set[str]:
        fields = {
            "window_name",
            "segmentation_name",
        }

        if not isinstance(self, FreshnessValidator):
            fields.add("metric")

        return fields

    def _mutable_fields(self) -> set[str]:
        return set({})

    def _ignored_fields(self) -> set[str]:
        return {
            # initialize_with_backfill is treated as a hint on the backend.
            # So what the client sets is not necessarily what the server will
            # return back. The field is also unused after validator creation
            # so that it doesn't matter to diff it. So we ignore it always.
            "initialize_with_backfill",
        }

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Validator"

    def _source_config_create_input(
        self, ctx: "DiffContext"
    ) -> SourceConfigCreateInput:
        source_id = ctx.sources[self.source_name]._id.value
        segmentation_id = ctx.segmentations[self.segmentation_name]._id.value
        window_id = ctx.windows[self.window_name]._id.value
        return SourceConfigCreateInput(
            # type: ignore[call-arg]
            source_id=source_id,
            # type: ignore[call-arg]
            segmentation_id=segmentation_id,
            # type: ignore[call-arg]
            window_id=window_id,
            filter=self._filter_api_create_input(),
        )

    def _source_config_update_input(self) -> SourceConfigUpdateInput:
        return SourceConfigUpdateInput(filter=self._filter_api_create_input())

    def _filter_api_create_input(self) -> Any | None:
        return self.filter._api_create_input() if self.filter else None

    def _api_create_input(self, namespace: str, ctx: "DiffContext") -> Any:
        overrides: dict[str, Any] = {
            "source_config": self._source_config_create_input(ctx)
        }
        if self.reference is not None:
            overrides[
                "reference_source_config"
            ] = self.reference._reference_source_config_create_input(ctx)

        return {
            "input": _api_create_input_params(
                self, namespace=namespace, overrides=overrides
            ),
            "threshold": self.threshold._api_create_input(),
        }

    def _api_update_input(self, _namespace: str, _: "DiffContext") -> Any:
        overrides: dict[str, Any] = {
            "source_config": self._source_config_update_input()
        }
        if self.reference is not None:
            overrides[
                "reference_source_config"
            ] = self.reference._reference_source_config_update_input()

        return _api_update_input_params(
            self,
            overrides=overrides,
        )

    async def _api_delete(self, client: ValidioAPIClient) -> Any:
        """Validator api is different from other resources since it is batched."""
        response = await client.delete_validators([self._must_id()])
        return self._check_graphql_response(
            response=response,
            method_name="delete_validators",
            response_field=None,
        )

    def _encode(self) -> dict[str, object]:
        return _encode_resource(
            self, skip_fields=({"reference"} if self.reference is None else set({}))
        )

    @staticmethod
    def _decode_pending(ctx: "DiffContext") -> None:
        for name, (cls, obj) in ctx.pending_validators_raw.items():
            config_obj = obj[CONFIG_FIELD_NAME]
            window_name = config_obj["window_name"]
            segmentation_name = config_obj["segmentation_name"]

            if window_name not in ctx.windows:
                raise RuntimeError(
                    f"failed to decode validator {name}: missing window {window_name}"
                )
            if segmentation_name not in ctx.segmentations:
                raise RuntimeError(
                    f"failed to decode validator {name}: missing segmentation"
                    f" {segmentation_name}"
                )

            window = ctx.windows[window_name]
            segmentation = ctx.segmentations[segmentation_name]

            ctx.validators[name] = Validator._decode(
                ctx, cls, obj, window, segmentation
            )

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        cls: type,
        obj: dict[str, Any],
        window: Window,
        segmentation: Segmentation,
    ) -> "Validator":
        obj = {
            k: v
            for k, v in obj[CONFIG_FIELD_NAME].items()
            if k
            not in {
                # Drop fields here that are not part of the constructor.
                # They will be reinitialized by the constructor.
                "source_name",
                "window_name",
                "segmentation_name",
            }
        }

        threshold = Threshold._decode(obj["threshold"])

        reference = (
            Reference._decode(obj["reference"], ctx.sources, ctx.windows)
            if "reference" in obj and obj["reference"]
            else None
        )

        filter_ = (
            Filter._decode(obj["filter"]) if "filter" in obj and obj["filter"] else None
        )

        # If the validator uses a field selector, then replace the corresponding
        # field with the selector - since they are both the same field from the
        # constructor's pov.
        FieldSelector._replace(obj)

        # Similarly, if the validator uses a reference field selector, replace it.
        if "_reference_field_selector" in obj:
            selector_obj = obj["_reference_field_selector"]
            obj[selector_obj["field_name"]] = FieldSelector.reference()
            del obj["_reference_field_selector"]

        return cls(
            **{
                **obj,
                "window": window,
                "segmentation": segmentation,
                "threshold": threshold,
                "filter": filter_,
                **({"reference": reference} if reference else {}),
            }
        )


class NumericValidator(Validator):
    """A Numeric validator resource.

    https://docs.validio.io/docs/numeric
    """

    def __init__(
        self,
        name: str,
        window: Window,
        segmentation: Segmentation,
        metric: NumericMetric,
        source_field: JsonPointer | FieldSelector,
        threshold: Threshold = DynamicThreshold(3),
        filter: Filter | None = None,
        initialize_with_backfill: bool = False,
    ):
        """
        Constructor.

        :param source_field: Field to monitor. (immutable)
        :param metric: Metric type for the validator. (immutable)
        """
        super().__init__(
            name=name,
            window=window,
            segmentation=segmentation,
            threshold=threshold,
            filter=filter,
            initialize_with_backfill=initialize_with_backfill,
        )

        self.metric = (
            metric if isinstance(metric, NumericMetric) else NumericMetric(metric)
        )
        self.metric = metric
        self.source_field: str = self._maybe_set_field_selector(
            "source_field", source_field
        )

        self._validate_unique_field_selector()

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "source_field",
                "metric",
            },
        }


class VolumeValidator(Validator):
    """A Volume validator resource.

    https://docs.validio.io/docs/volume
    """

    def __init__(
        self,
        name: str,
        window: Window,
        segmentation: Segmentation,
        metric: VolumeMetric,
        source_fields: list[str] | None = None,
        threshold: Threshold = DynamicThreshold(3),
        filter: Filter | None = None,
        initialize_with_backfill: bool = False,
        # Deprecated.
        optional_source_field: JsonPointer | FieldSelector | None = None,
    ):
        """
        Constructor.

        :param source_fields: List of fields for the DUPLICATES and UNIQUE metrics.
        :param metric: Metric type for the validator. (immutable)
        :param optional_source_field: Deprecated. (immutable)
        """
        super().__init__(
            name=name,
            window=window,
            segmentation=segmentation,
            threshold=threshold,
            filter=filter,
            initialize_with_backfill=initialize_with_backfill,
        )

        self.metric = (
            metric if isinstance(metric, VolumeMetric) else VolumeMetric(metric)
        )

        self.optional_source_field: str | None = None
        if optional_source_field:
            self.optional_source_field = self._maybe_set_field_selector(
                "optional_source_field", optional_source_field
            )

        self.source_fields = source_fields if source_fields else []

        self._validate_unique_field_selector()

    def __getattr__(self, name: str) -> str | None:
        """Getter for field aliases."""
        # source_field is called optional_source_field on the api input
        if name == "source_field":
            return self.optional_source_field
        raise AttributeError

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{"optional_source_field", "source_fields", "metric"},
        }


class NumericDistributionValidator(Validator):
    """A Numeric distribution validator resource.

    https://docs.validio.io/docs/numeric-distribution
    """

    def __init__(
        self,
        name: str,
        window: Window,
        segmentation: Segmentation,
        metric: NumericDistributionMetric,
        source_field: JsonPointer | FieldSelector,
        reference_source_field: JsonPointer | FromFieldSelector,
        reference: Reference,
        threshold: Threshold = DynamicThreshold(3),
        filter: Filter | None = None,
        initialize_with_backfill: bool = False,
    ):
        """
        Constructor.

        :param source_field: Field to monitor. (immutable)
        :param reference_source_field: Reference field to compare against. (immutable)
        :param metric: Metric type for the validator. (immutable)
        """
        super().__init__(
            name=name,
            window=window,
            segmentation=segmentation,
            threshold=threshold,
            reference=reference,
            filter=filter,
            initialize_with_backfill=initialize_with_backfill,
        )

        self.metric = (
            metric
            if isinstance(metric, NumericDistributionMetric)
            else NumericDistributionMetric(metric)
        )

        self.source_field: str = self._maybe_set_field_selector(
            "source_field", source_field
        )
        self.reference_source_field: str = self._maybe_set_reference_field_selector(
            "reference_source_field",
            reference_source_field,
            "source_field",
            source_field,
        )

        self._validate_unique_field_selector()

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "source_field",
                "reference_source_field",
            },
        }


class CategoricalDistributionValidator(Validator):
    """A Categorical distribution validator resource.

    https://docs.validio.io/docs/categorical-distribution
    """

    def __init__(
        self,
        name: str,
        window: Window,
        segmentation: Segmentation,
        metric: CategoricalDistributionMetric,
        source_field: JsonPointer | FieldSelector,
        reference_source_field: JsonPointer | FromFieldSelector,
        reference: Reference,
        threshold: Threshold = DynamicThreshold(3),
        filter: Filter | None = None,
        initialize_with_backfill: bool = False,
    ):
        """
        Constructor.

        :param source_field: Field to monitor. (immutable)
        :param reference_source_field: Reference field to
            compare against. (immutable)
        :param metric: Metric type for the validator. (immutable)
        """
        super().__init__(
            name=name,
            window=window,
            segmentation=segmentation,
            threshold=threshold,
            reference=reference,
            filter=filter,
            initialize_with_backfill=initialize_with_backfill,
        )

        self.metric = (
            metric
            if isinstance(metric, CategoricalDistributionMetric)
            else CategoricalDistributionMetric(metric)
        )

        self.source_field: str = self._maybe_set_field_selector(
            "source_field", source_field
        )
        self.reference_source_field: str = self._maybe_set_reference_field_selector(
            "reference_source_field",
            reference_source_field,
            "source_field",
            source_field,
        )

        self._validate_unique_field_selector()

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "source_field",
                "reference_source_field",
            },
        }


class NumericAnomalyValidator(Validator):
    """A Numeric anomaly validator resource.

    https://docs.validio.io/docs/numeric-anomaly
    """

    def __init__(
        self,
        name: str,
        window: Window,
        segmentation: Segmentation,
        metric: NumericAnomalyMetric,
        source_field: JsonPointer | FieldSelector,
        reference_source_field: JsonPointer | FromFieldSelector,
        reference: Reference,
        sensitivity: float,
        minimum_absolute_difference: float,
        minimum_relative_difference_percent: float,
        minimum_reference_datapoints: float | None = None,
        threshold: Threshold = DynamicThreshold(3),
        filter: Filter | None = None,
        initialize_with_backfill: bool = False,
    ):
        """
        Constructor.

        :param source_field: Field to monitor. (immutable)
        :param reference_source_field: Reference field to
            compare against. (immutable)
        :param metric: Metric type for the validator. (immutable)
        """
        super().__init__(
            name=name,
            window=window,
            segmentation=segmentation,
            threshold=threshold,
            reference=reference,
            filter=filter,
            initialize_with_backfill=initialize_with_backfill,
        )

        self.metric: str = (
            metric
            if isinstance(metric, NumericAnomalyMetric)
            else NumericAnomalyMetric(metric)
        )
        self.sensitivity = sensitivity
        self.minimum_absolute_difference = minimum_absolute_difference
        self.minimum_relative_difference_percent = minimum_relative_difference_percent
        self.minimum_reference_datapoints = minimum_reference_datapoints

        self.source_field: str = self._maybe_set_field_selector(
            "source_field", source_field
        )
        self.reference_source_field: str = self._maybe_set_reference_field_selector(
            "reference_source_field",
            reference_source_field,
            "source_field",
            source_field,
        )

        self._validate_unique_field_selector()

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "source_field",
                "reference_source_field",
                "sensitivity",
                "minimum_absolute_difference",
                "minimum_relative_difference_percent",
                "minimum_reference_datapoints",
            },
        }


class RelativeVolumeValidator(Validator):
    """A Relative volume validator resource.

    https://docs.validio.io/docs/relative-volume
    """

    def __init__(
        self,
        name: str,
        window: Window,
        segmentation: Segmentation,
        metric: RelativeVolumeMetric,
        reference: Reference,
        optional_source_field: JsonPointer | None = None,
        optional_reference_source_field: JsonPointer | None = None,
        threshold: Threshold = DynamicThreshold(3),
        filter: Filter | None = None,
        initialize_with_backfill: bool = False,
    ):
        """
        Constructor.

        :param optional_source_field: Field to monitor. (immutable)
        :param optional_reference_source_field: Reference field
            to compare against. (immutable)
        :param metric: Metric type for the validator. (immutable)
        """
        super().__init__(
            name=name,
            window=window,
            segmentation=segmentation,
            threshold=threshold,
            reference=reference,
            filter=filter,
            initialize_with_backfill=initialize_with_backfill,
        )

        self.metric: str = (
            metric
            if isinstance(metric, RelativeVolumeMetric)
            else RelativeVolumeMetric(metric)
        )
        self.optional_source_field = optional_source_field
        self.optional_reference_source_field = optional_reference_source_field

        self._validate_no_field_selector()

    def __getattr__(self, name: str) -> str | None:
        """Getter for field aliases."""
        # optional_source_field is called source_field on the api input
        if name == "source_field":
            return self.optional_source_field

        # optional_reference_source_field is called reference_source_field
        # on the api input
        if name == "reference_source_field":
            return self.optional_reference_source_field

        raise AttributeError

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "optional_source_field",
                "optional_reference_source_field",
            },
        }


class RelativeTimeValidator(Validator):
    """A Relative time validator resource.

    https://docs.validio.io/docs/relative-time
    """

    def __init__(
        self,
        name: str,
        window: Window,
        segmentation: Segmentation,
        metric: RelativeTimeMetric,
        source_field_minuend: JsonPointer,
        source_field_subtrahend: JsonPointer,
        threshold: Threshold = DynamicThreshold(3),
        filter: Filter | None = None,
        initialize_with_backfill: bool = False,
    ):
        """
        Constructor.

        :param source_field_minuend: Timestamp field to monitor. (immutable)
        :param source_field_subtrahend: Reference timestamp to subtract. (immutable)
        :param metric: Metric type for the validator. (immutable)
        """
        super().__init__(
            name=name,
            window=window,
            segmentation=segmentation,
            threshold=threshold,
            filter=filter,
            initialize_with_backfill=initialize_with_backfill,
        )

        self.metric: str = (
            metric
            if isinstance(metric, RelativeTimeMetric)
            else RelativeTimeMetric(metric)
        )
        self.source_field_minuend = source_field_minuend
        self.source_field_subtrahend = source_field_subtrahend

        self._validate_no_field_selector()

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "source_field_minuend",
                "source_field_subtrahend",
            },
        }


class FreshnessValidator(Validator):
    """A Freshness validator resource.

    https://docs.validio.io/docs/freshness
    """

    def __init__(
        self,
        name: str,
        window: TumblingWindow,
        segmentation: Segmentation,
        threshold: Threshold = DynamicThreshold(3),
        filter: Filter | None = None,
        initialize_with_backfill: bool = False,
        optional_source_field: JsonPointer | None = None,
    ):
        """Constructor."""
        super().__init__(
            name=name,
            window=window,
            segmentation=segmentation,
            threshold=threshold,
            filter=filter,
            initialize_with_backfill=initialize_with_backfill,
        )

        self.optional_source_field = optional_source_field

        self._validate_no_field_selector()

    def __getattr__(self, name: str) -> str | None:
        """Getter for field aliases."""
        # optional_source_field is called source_field on the api input
        if name == "source_field":
            return self.optional_source_field

        raise AttributeError

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "optional_source_field",
            },
        }


def _validate_source_window_compatibility(source: Source, window: Window) -> None:
    """
    Validate source and window compatibility.

    To avoid creating a partial configuration and bail out once the creating of
    the validator is done we do some pre validation of combination we know is
    invalid.
    """
    is_demo_source = isinstance(source, DemoSource)
    is_stream_source = issubclass(source.__class__, StreamSource)
    is_object_storage_source = issubclass(source.__class__, ObjectStorageSource)
    is_warehouse_source = (
        not is_stream_source and not is_object_storage_source and not is_demo_source
    )

    if (isinstance(window, FileWindow) and not is_object_storage_source) or (
        isinstance(window, GlobalWindow) and not is_warehouse_source
    ):
        raise ManifestConfigurationError(
            f"invalid window '{window.__class__.__name__}' on source type "
            f"'{source.__class__.__name__}'"
        )


VALIDATOR_CLASSES: set[type] = {
    NumericAnomalyValidator,
    NumericValidator,
    NumericDistributionValidator,
    VolumeValidator,
    RelativeTimeValidator,
    FreshnessValidator,
    CategoricalDistributionValidator,
    RelativeVolumeValidator,
}
