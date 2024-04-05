"""Notification rule configuration."""

from typing import TYPE_CHECKING, Any

from validio_sdk.graphql_client import (
    BaseModel,
    NotificationRuleDeleteInput,
)
from validio_sdk.graphql_client.enums import IncidentSeverity, IssueTypename
from validio_sdk.graphql_client.fragments import (
    NotificationRuleDetailsConditionsOwnerNotificationRuleCondition,
    NotificationRuleDetailsConditionsSegmentNotificationRuleCondition,
    NotificationRuleDetailsConditionsSeverityNotificationRuleCondition,
    NotificationRuleDetailsConditionsSourceNotificationRuleCondition,
    NotificationRuleDetailsConditionsTagNotificationRuleCondition,
    NotificationRuleDetailsConditionsTypeNotificationRuleCondition,
)
from validio_sdk.graphql_client.input_types import (
    NotificationRuleConditionCreateInput,
    OwnerNotificationRuleConditionCreateInput,
    SegmentFieldInput,
    SegmentNotificationRuleConditionCreateInput,
    SeverityNotificationRuleConditionCreateInput,
    SourceNotificationRuleConditionCreateInput,
    TagCreateInput,
    TagNotificationRuleConditionCreateInput,
    TypeNotificationRuleConditionCreateInput,
)
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._resource import Resource
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    NODE_TYPE_FIELD_NAME,
    _api_create_input_params,
    _api_update_input_params,
    _encode_resource,
)
from validio_sdk.resource.channels import Channel
from validio_sdk.resource.sources import Source
from validio_sdk.validio_client import ValidioAPIClient

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class Conditions(Diffable):
    """Conditions used for notification rules."""

    def __init__(
        self,
        owner_condition: "OwnerNotificationRuleCondition | None" = None,
        segment_conditions: list["SegmentNotificationRuleCondition"] | None = None,
        severity_condition: "SeverityNotificationRuleCondition | None" = None,
        source_condition: "SourceNotificationRuleCondition | None" = None,
        tag_conditions: list["TagNotificationRuleCondition"] | None = None,
        type_condition: "TypeNotificationRuleCondition | None" = None,
    ) -> None:
        """Constructor."""
        self._node_type = self.__class__.__name__

        self.owner_condition = owner_condition
        self.segment_conditions = segment_conditions
        self.severity_condition = severity_condition
        self.source_condition = source_condition
        self.tag_conditions = tag_conditions
        self.type_condition = type_condition

    def _immutable_fields(self) -> set[str]:
        return set()

    def _mutable_fields(self) -> set[str]:
        return set()

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        # For some reason mypy doesn't recognize <Type>Condition -> Condition ->
        # Diffable as fulfiling the Diffable type.
        objects: dict[str, Diffable | list[Diffable] | None] = {  # type: ignore
            "owner_condition": self.owner_condition,
            "segment_conditions": self.segment_conditions,  # type: ignore
            "severity_condition": self.severity_condition,
            "source_condition": self.source_condition,
            "tag_conditions": self.tag_conditions,  # type: ignore
            "type_condition": self.type_condition,
        }

        return objects

    def _encode(self) -> dict[str, object]:
        return self.__dict__

    @staticmethod
    def _decode(ctx: "DiffContext", obj: dict[str, Any]) -> "Conditions":
        cls = eval(obj[NODE_TYPE_FIELD_NAME])

        args = {}
        for k, v in obj.items():
            if v is None:
                continue

            if k == NODE_TYPE_FIELD_NAME:
                continue

            if isinstance(v, list):
                values = []
                for value_element in v:
                    condition_cls = eval(value_element[NODE_TYPE_FIELD_NAME])
                    values.append(condition_cls._decode(ctx, value_element))

                args[k] = values
            else:
                condition_cls = eval(v[NODE_TYPE_FIELD_NAME])
                args[k] = condition_cls._decode(ctx, v)

        return cls(**args)

    def _create_input(self, ctx: "DiffContext") -> NotificationRuleConditionCreateInput:
        conditions = NotificationRuleConditionCreateInput()
        if self.owner_condition is not None:
            conditions.owner_condition = OwnerNotificationRuleConditionCreateInput(
                owners=self.owner_condition.owners
            )

        if self.severity_condition is not None:
            conditions.severity_condition = (
                SeverityNotificationRuleConditionCreateInput(
                    severities=self.severity_condition.severities
                )
            )

        if self.source_condition is not None:
            conditions.source_condition = SourceNotificationRuleConditionCreateInput(
                sources=[
                    ctx.sources[source_name]._must_id()
                    for source_name in self.source_condition.sources
                ]
            )

        if self.type_condition is not None:
            conditions.type_condition = TypeNotificationRuleConditionCreateInput(
                types=self.type_condition.types
            )

        if self.segment_conditions is not None:
            conditions.segment_conditions = [
                (
                    SegmentNotificationRuleConditionCreateInput(
                        segments=[
                            SegmentFieldInput(field=k, value=v)
                            for k, v in segment_condition.segments.items()
                        ]
                    )
                )
                for segment_condition in self.segment_conditions
            ]

        if self.tag_conditions is not None:
            conditions.tag_conditions = [
                (
                    TagNotificationRuleConditionCreateInput(
                        tags=[
                            TagCreateInput(key=k, value=v)
                            for k, v in tag_condition.tags.items()
                        ]
                    )
                )
                for tag_condition in self.tag_conditions
            ]

        return conditions

    def _api_create_input(self, ctx: "DiffContext") -> BaseModel:
        return self._create_input(ctx)

    def _api_update_input(self, ctx: "DiffContext") -> BaseModel:
        return self._create_input(ctx)

    @classmethod
    def _new_from_api(
        cls: type["Conditions"],
        api_conditions: list[
            NotificationRuleDetailsConditionsTypeNotificationRuleCondition
            | NotificationRuleDetailsConditionsOwnerNotificationRuleCondition
            | NotificationRuleDetailsConditionsSegmentNotificationRuleCondition
            | NotificationRuleDetailsConditionsSeverityNotificationRuleCondition
            | NotificationRuleDetailsConditionsSourceNotificationRuleCondition
            | NotificationRuleDetailsConditionsTagNotificationRuleCondition
            | NotificationRuleDetailsConditionsTypeNotificationRuleCondition
        ],
    ) -> "Conditions":
        """
        Create a new Conditions from API response.

        Input for creating and updating conditions for a notification rules in
        the API is a typed struct with fields for each condition type. Some of
        them might occur several times and is a list where others are just plain
        values.

        Output from the API however lists conditions as an array with elements
        being one conditions per row. This includes both across different
        condition types, f.ex. source conditions and type conditions are two
        different elements, but also for each condition that is represented as a
        list on the input, f.ex. each tag or segment will be returned as
        separate elements.

        This method will convert the API response and the expanded array for
        conditions to a `Conditions` type which is the same as the
        representation for create and update.
        """
        conditions = cls()
        for condition in api_conditions:
            match condition.typename__:
                case "OwnerNotificationRuleCondition":
                    conditions.owner_condition = OwnerNotificationRuleCondition(
                        owners=[x.id for x in condition.config.owners]  # type: ignore
                    )
                case "SegmentNotificationRuleCondition":
                    if conditions.segment_conditions is None:
                        conditions.segment_conditions = []

                    conditions.segment_conditions.append(
                        SegmentNotificationRuleCondition(
                            segments={
                                x.field: x.value
                                for x in condition.config.segments  # type: ignore
                            }
                        )
                    )
                case "SeverityNotificationRuleCondition":
                    conditions.severity_condition = SeverityNotificationRuleCondition(
                        severities=condition.config.severities  # type: ignore
                    )
                case "SourceNotificationRuleCondition":
                    conditions.source_condition = SourceNotificationRuleCondition(
                        sources=condition.config.sources  # type: ignore
                    )
                case "TagNotificationRuleCondition":
                    if conditions.tag_conditions is None:
                        conditions.tag_conditions = []

                    conditions.tag_conditions.append(
                        TagNotificationRuleCondition(
                            tags={
                                x.key: x.value
                                for x in condition.config.tags  # type: ignore
                            }
                        )
                    )
                case "TypeNotificationRuleCondition":
                    conditions.type_condition = TypeNotificationRuleCondition(
                        types=condition.config.types  # type: ignore
                    )

        return conditions


class NotificationRuleCondition(Diffable):
    """A condition for notification rules."""

    def __init__(self) -> None:
        """Base class for all notification rule conditions."""
        self._node_type = self.__class__.__name__

    def _immutable_fields(self) -> set[str]:
        return set()

    def _mutable_fields(self) -> set[str]:
        return set()

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        return {}

    def _encode(self) -> dict[str, Any]:
        return self.__dict__

    @staticmethod
    def _decode(_: "DiffContext", obj: dict[str, Any]) -> "NotificationRuleCondition":
        cls = eval(obj[NODE_TYPE_FIELD_NAME])
        return cls(**{k: v for k, v in obj.items() if k != NODE_TYPE_FIELD_NAME})


class OwnerNotificationRuleCondition(NotificationRuleCondition):
    """A condition for owners."""

    def __init__(self, owners: list[str]):
        """
        Constructor.

        :param owners: User IDs in uuid format. Will send notification for
        reasources owned by these users.
        """
        super().__init__()

        from uuid import UUID

        # Ensure we only try to work with valid UUIDs.
        for owner in owners:
            try:
                UUID(owner)
            except ValueError:
                raise Exception("owner must be id of type uuid")

        self.owners = owners
        self.owners.sort()

    def _mutable_fields(self) -> set[str]:
        return {"owners"}


class SegmentNotificationRuleCondition(NotificationRuleCondition):
    """A condition for segments."""

    def __init__(self, segments: dict[str, str]):
        """
        Constructor.

        :param segments: Key value pairs of field and field values for segments
        to send notifications for.
        """
        super().__init__()
        self.segments = segments

    def _mutable_fields(self) -> set[str]:
        return {"segments"}


class SeverityNotificationRuleCondition(NotificationRuleCondition):
    """A condition for severity."""

    def __init__(
        self,
        severities: list[IncidentSeverity],
    ):
        """
        Constructor.

        :param severities: List of severities to send notifications for.
        """
        super().__init__()
        self.severities = [
            (
                severity
                if isinstance(severity, IncidentSeverity)
                else IncidentSeverity(severity)
            )
            for severity in severities
        ]
        self.severities.sort()

    def _mutable_fields(self) -> set[str]:
        return {"severities"}


class SourceNotificationRuleCondition(NotificationRuleCondition):
    """A condition for sources."""

    def __init__(self, sources: list[Source]):
        """
        Constructor.

        :param sources: List of sources to send notifications for.
        """
        super().__init__()
        self.sources = [source.name for source in sources]
        self.sources.sort()

    def _mutable_fields(self) -> set[str]:
        return {"sources"}

    @staticmethod
    def _decode(
        ctx: "DiffContext", obj: dict[str, Any]
    ) -> "SourceNotificationRuleCondition":
        sources = [ctx.sources[source] for source in obj["sources"]]
        return SourceNotificationRuleCondition(sources=sources)


class TagNotificationRuleCondition(NotificationRuleCondition):
    """A condition for tags."""

    def __init__(self, tags: dict[str, str]):
        """
        Constructor.

        :param tags: Key value pairs of tags to send notifications for.
        """
        super().__init__()
        self.tags = tags

    def _mutable_fields(self) -> set[str]:
        return {"tags"}


class TypeNotificationRuleCondition(NotificationRuleCondition):
    """A condition for sources."""

    def __init__(
        self,
        types: list[IssueTypename],
    ):
        """
        Constructor.

        :param types: A list of event types to send notifications for.
        """
        super().__init__()
        self.types = [
            (type_ if isinstance(type_, IssueTypename) else IssueTypename(type_))
            for type_ in types
        ]
        self.types.sort()

    def _mutable_fields(self) -> set[str]:
        return {"types"}


class NotificationRule(Resource):
    """
    A notification rule.

    https://docs.validio.io/docs/notifications
    """

    def __init__(
        self,
        name: str,
        channel: Channel,
        conditions: Conditions | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the window
        :param channel: The channel to attach the rule to
        :param conditions: List of conditions for the notification rule.
        """
        super().__init__(name, channel._resource_graph)

        self.channel_name = channel.name

        # If conditions wasn't set, set it to an empty `Conditions` with all
        # fields to `None` to not have to account for `None`-ness of the field.
        self.conditions = conditions or Conditions()

        channel.add(name, self)

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        objects: dict[str, Diffable | list[Diffable] | None] = {
            "conditions": self.conditions,
        }

        return objects

    def _immutable_fields(self) -> set[str]:
        return {"channel_name"}

    def _mutable_fields(self) -> set[str]:
        return set()

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "NotificationRule"

    def _api_create_response_field_name(self) -> str:
        return "notification_rule"

    def _api_create_input(self, namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            namespace=namespace,
            overrides={
                "channel_id": ctx.channels[self.channel_name]._must_id(),
                "conditions": self.conditions._api_create_input(ctx),
            },
            skip_fields={"sources", "notification_typenames"},
        )

    def _api_update_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_update_input_params(
            self,
            overrides={
                "conditions": self.conditions._api_update_input(ctx),
            },
            skip_fields={"channel_id", "sources", "notification_typenames"},
        )

    async def _api_delete(self, client: ValidioAPIClient) -> Any:
        response = await client.delete_notification_rule(
            NotificationRuleDeleteInput(id=self._must_id())
        )
        return self._check_graphql_response(
            response=response,
            method_name="delete_notification_rule",
            response_field=None,
        )

    def _encode(self) -> dict[str, object]:
        # Drop fields here that are not part of the constructor for when
        # we deserialize back. They will be reinitialized by the constructor.
        return _encode_resource(self, skip_fields={"channel_name"})

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        channel: Channel,
        obj: dict[str, Any],
    ) -> "NotificationRule":
        obj = obj[CONFIG_FIELD_NAME]
        conditions = Conditions._decode(ctx, obj["conditions"])

        return NotificationRule(
            **{
                **obj,
                "channel": channel,
                "conditions": conditions,
            }
        )  # type: ignore
