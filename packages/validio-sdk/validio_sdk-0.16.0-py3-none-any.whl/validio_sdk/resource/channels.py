"""Notification Channels."""

from typing import TYPE_CHECKING, Any, cast

from validio_sdk.graphql_client import ChannelDeleteInput
from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource._resource_graph import RESOURCE_GRAPH
from validio_sdk.resource._serde import (
    CONFIG_FIELD_NAME,
    _encode_resource,
    get_children_node,
    with_resource_graph_info,
)
from validio_sdk.validio_client import ValidioAPIClient

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class Channel(Resource):
    """A notification channel configuration.

    https://docs.validio.io/docs/channels
    """

    def __init__(self, name: str, __internal__: ResourceGraph | None = None) -> None:
        """
        Constructor.

        :param name: Unique resource name assigned to the destination
        :param __internal__: Should be left ignored. This is for internal usage only.
        """
        # Channels are at the root sub-graphs.
        g: ResourceGraph = __internal__ or RESOURCE_GRAPH
        super().__init__(name, g)

        self._resource_graph: ResourceGraph = g
        self._resource_graph._add_root(self)

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return set({})

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Channel"

    async def _api_delete(self, client: ValidioAPIClient) -> Any:
        response = await client.delete_channel(ChannelDeleteInput(id=self._must_id()))
        return self._check_graphql_response(
            response=response,
            method_name="channels",
            response_field=None,
        )

    def _encode(self) -> dict[str, object]:
        return _encode_resource(self)

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        cls: type,
        obj: dict[str, dict[str, object]],
        g: ResourceGraph,
    ) -> "Channel":
        from validio_sdk.resource.notification_rules import NotificationRule

        channel = cls(**with_resource_graph_info(obj[CONFIG_FIELD_NAME], g))

        # Decode notification rules
        children_obj = cast(dict[str, dict[str, object]], get_children_node(obj))
        notification_rules_obj = cast(
            dict[str, dict[str, object]],
            (
                children_obj[NotificationRule.__name__]
                if NotificationRule.__name__ in children_obj
                else {}
            ),
        )

        notification_rules = {}
        for rule_name, value in notification_rules_obj.items():
            rule = NotificationRule._decode(ctx, channel, value)
            notification_rules[rule_name] = rule
            ctx.notification_rules[rule_name] = rule

        if len(notification_rules) > 0:
            channel._children[NotificationRule.__name__] = cast(
                dict[str, Resource], notification_rules
            )

        return channel


class SlackChannel(Channel):
    """
    Configuration to send notifications to a Slack channel.

    https://docs.validio.io/docs/slack
    """

    def __init__(
        self,
        name: str,
        application_link_url: str,
        webhook_url: str,
        timezone: str | None = "UTC",
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param application_link_url: URL to your Validio application
            instance, used to send notifications.
        :param webhook_url: Webhook URL provided by Slack to the
            specified Slack channel.
        :param timezone: Timezone to display timestamps in the notifications in.
        """
        super().__init__(name, __internal__)
        self.application_link_url = application_link_url
        self.webhook_url = webhook_url

        if timezone is None:
            timezone = "UTC"

        self.timezone = timezone

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"application_link_url", "webhook_url", "timezone"}


class MsTeamsChannel(Channel):
    """
    Configuration to send notifications to a Microsoft Teams channel.

    https://docs.validio.io/docs/msteams
    """

    def __init__(
        self,
        name: str,
        application_link_url: str,
        webhook_url: str,
        timezone: str | None = "UTC",
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param application_link_url: URL to your Validio application
            instance, used to send notifications.
        :param webhook_url: Webhook URL provided by Microsoft Teams to the
            specified channel.
        :param timezone: Timezone to display timestamps in the notifications in.
        """
        super().__init__(name, __internal__)
        self.application_link_url = application_link_url
        self.webhook_url = webhook_url

        if timezone is None:
            timezone = "UTC"

        self.timezone = timezone

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"application_link_url", "webhook_url", "timezone"}


class WebhookChannel(Channel):
    """
    Configuration to send notifications to a webhook.

    https://docs.validio.io/docs/webhooks
    """

    def __init__(
        self,
        name: str,
        application_link_url: str,
        webhook_url: str,
        auth_header: str | None,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param application_link_url: URL to your Validio application
            instance, used to send notifications.
        :param webhook_url: Webhook URL to the specified HTTP endpoint.
        :param auth_header: Signature to include in the authorization
            header sent to the HTTP endpoint.
        """
        super().__init__(name, __internal__)
        self.application_link_url = application_link_url
        self.webhook_url = webhook_url
        self.auth_header = auth_header

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"application_link_url", "webhook_url", "auth_header"}
