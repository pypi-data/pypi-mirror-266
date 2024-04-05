import pytest

from validio_sdk.graphql_client import (
    NumericDistributionMetric,
    NumericMetric,
    WindowTimeUnit,
)
from validio_sdk.resource import FieldSelector
from validio_sdk.resource._diff import (
    DiffContext,
    GraphDiff,
    ResourceUpdate,
    ResourceUpdates,
    _diff_resource_graph,
)
from validio_sdk.resource._errors import ManifestConfigurationError
from validio_sdk.resource._resource import ResourceGraph
from validio_sdk.resource.channels import Channel, SlackChannel
from validio_sdk.resource.credentials import Credential, DemoCredential
from validio_sdk.resource.filters import NullFilter
from validio_sdk.resource.notification_rules import (
    Conditions,
    NotificationRule,
    SourceNotificationRuleCondition,
)
from validio_sdk.resource.segmentations import Segmentation
from validio_sdk.resource.sources import DemoSource, Source
from validio_sdk.resource.thresholds import DynamicThreshold
from validio_sdk.resource.validators import (
    NumericDistributionValidator,
    NumericValidator,
    Reference,
    Validator,
)
from validio_sdk.resource.windows import TumblingWindow, Window


def _add_namespace(namespace: str, ctx: DiffContext) -> None:
    for f in DiffContext.fields():
        for r in getattr(ctx, f).values():
            r._namespace = namespace


def create_diff_context(
    credentials: dict[str, Credential] | None = None,
    channels: dict[str, Channel] | None = None,
    sources: dict[str, Source] | None = None,
    windows: dict[str, Window] | None = None,
    segmentations: dict[str, Segmentation] | None = None,
    validators: dict[str, Validator] | None = None,
    notification_rules: dict[str, NotificationRule] | None = None,
) -> DiffContext:
    return DiffContext(
        credentials=credentials or {},
        channels=channels or {},
        sources=sources or {},
        windows=windows or {},
        segmentations=segmentations or {},
        validators=validators or {},
        notification_rules=notification_rules or {},
    )


def create_resource_updates(
    credentials: dict[str, ResourceUpdate] | None = None,
    channels: dict[str, ResourceUpdate] | None = None,
    sources: dict[str, ResourceUpdate] | None = None,
    windows: dict[str, ResourceUpdate] | None = None,
    segmentations: dict[str, ResourceUpdate] | None = None,
    validators: dict[str, ResourceUpdate] | None = None,
    notification_rules: dict[str, ResourceUpdate] | None = None,
) -> ResourceUpdates:
    return ResourceUpdates(
        credentials=credentials or {},
        channels=channels or {},
        sources=sources or {},
        windows=windows or {},
        segmentations=segmentations or {},
        validators=validators or {},
        notification_rules=notification_rules or {},
    )


def create_graph_diff(
    to_create: DiffContext | None = None,
    to_delete: DiffContext | None = None,
    to_update: ResourceUpdates | None = None,
) -> GraphDiff:
    return GraphDiff(
        to_create=to_create or DiffContext(),
        to_delete=to_delete or DiffContext(),
        to_update=to_update or create_resource_updates(),
    )


# ruff: noqa: PLR0915
def test_diff_should_detect_create_update_delete_operations_on_resources() -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential("c1", manifest_g)
    manifest_s1 = DemoSource("s1", manifest_c1)
    manifest_s2 = DemoSource("s2", manifest_c1)  # To be created
    manifest_seg1 = Segmentation("seg1", manifest_s1, ["city"])
    manifest_seg2 = Segmentation("seg2", manifest_s1, ["gender"])  # To be created
    manifest_w1 = TumblingWindow("w1", manifest_s1, "d", 1, WindowTimeUnit.DAY)
    manifest_w2 = TumblingWindow(
        "w2", manifest_s1, "d", 2, WindowTimeUnit.DAY
    )  # To be created
    manifest_w3 = TumblingWindow(
        "w3",
        manifest_s1,
        "d",
        3,
        WindowTimeUnit.DAY,
    )  # Update
    manifest_v1 = NumericValidator(
        "v1", manifest_w1, manifest_seg1, NumericMetric.MAX, "a"
    )
    manifest_v2 = NumericValidator(
        "v2",
        manifest_w1,
        manifest_seg1,
        NumericMetric.MEAN,
        "b",
    )  # To be created
    manifest_ch1 = SlackChannel("ch1", "app", "web", "tz", manifest_g)
    manifest_ch2 = SlackChannel("ch2", "app", "web", "tz", manifest_g)  # To be created
    manifest_ch3 = SlackChannel("ch3", "app", "web", None, manifest_g)  # To be updated
    manifest_cond1 = Conditions(
        source_condition=SourceNotificationRuleCondition([manifest_s1])
    )
    manifest_r1 = NotificationRule("r1", manifest_ch1, manifest_cond1)
    manifest_r2 = NotificationRule("r2", manifest_ch1, manifest_cond1)  # To be created
    manifest_r3 = NotificationRule("r3", manifest_ch1, manifest_cond1)  # To be updated

    server_c1 = DemoCredential("c1", server_g)
    server_s1 = DemoSource("s1", server_c1)
    server_s3 = DemoSource("s3", server_c1)  # To be deleted
    server_seg1 = Segmentation("seg1", server_s1, ["city"])
    server_seg3 = Segmentation("seg3", server_s1, ["country"])  # To be deleted
    server_w1 = TumblingWindow("w1", server_s1, "d", 1, WindowTimeUnit.DAY)
    server_w3 = TumblingWindow("w3", server_s1, "d", 4, WindowTimeUnit.DAY)
    server_w4 = TumblingWindow(
        "w4", server_s1, "d", 5, WindowTimeUnit.DAY
    )  # To be deleted
    server_v1 = NumericValidator("v1", server_w1, server_seg1, NumericMetric.MAX, "a")
    server_v3 = NumericValidator(
        "v3", server_w1, server_seg1, NumericMetric.MAX, "d"
    )  # Delete
    server_ch1 = SlackChannel("ch1", "app", "web", "tz", server_g)
    server_ch3 = SlackChannel("ch3", "app", "web", "tz", server_g)
    server_ch4 = SlackChannel("ch4", "app", "web", "tz", server_g)  # To be deleted
    server_cond1 = Conditions(
        source_condition=SourceNotificationRuleCondition([manifest_s1])
    )
    server_r1 = NotificationRule("r1", server_ch1, server_cond1)
    server_r3 = NotificationRule("r3", server_ch1, None)
    server_r4 = NotificationRule("r4", server_ch1, server_cond1)  # To be deleted

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        sources={
            manifest_s1.name: manifest_s1,
            manifest_s2.name: manifest_s2,
        },
        segmentations={
            manifest_seg1.name: manifest_seg1,
            manifest_seg2.name: manifest_seg2,
        },
        windows={
            manifest_w1.name: manifest_w1,
            manifest_w2.name: manifest_w2,
            manifest_w3.name: manifest_w3,
        },
        validators={
            manifest_v1.name: manifest_v1,
            manifest_v2.name: manifest_v2,
        },
        channels={
            manifest_ch1.name: manifest_ch1,
            manifest_ch2.name: manifest_ch2,
            manifest_ch3.name: manifest_ch3,
        },
        notification_rules={
            manifest_r1.name: manifest_r1,
            manifest_r2.name: manifest_r2,
            manifest_r3.name: manifest_r3,
        },
    )

    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        sources={
            server_s1.name: server_s1,
            server_s3.name: server_s3,
        },
        segmentations={
            server_seg1.name: server_seg1,
            server_seg3.name: server_seg3,
        },
        windows={
            server_w1.name: server_w1,
            server_w3.name: server_w3,
            server_w4.name: server_w4,
        },
        validators={
            server_v1.name: server_v1,
            server_v3.name: server_v3,
        },
        channels={
            server_ch1.name: server_ch1,
            server_ch3.name: server_ch3,
            server_ch4.name: server_ch4,
        },
        notification_rules={
            server_r1.name: server_r1,
            server_r3.name: server_r3,
            server_r4.name: server_r4,
        },
    )

    expected = create_graph_diff(
        to_create=DiffContext(
            sources={manifest_s2.name: manifest_s2},
            segmentations={manifest_seg2.name: manifest_seg2},
            windows={manifest_w2.name: manifest_w2},
            validators={manifest_v2.name: manifest_v2},
            channels={manifest_ch2.name: manifest_ch2},
            notification_rules={manifest_r2.name: manifest_r2},
        ),
        to_delete=DiffContext(
            sources={server_s3.name: server_s3},
            segmentations={server_seg3.name: server_seg3},
            windows={server_w4.name: server_w4},
            validators={server_v3.name: server_v3},
            channels={server_ch4.name: server_ch4},
            notification_rules={server_r4.name: server_r4},
        ),
        to_update=create_resource_updates(
            windows={
                manifest_w3.name: ResourceUpdate(
                    manifest_w3,
                    server_w3,
                )
            },
            channels={
                manifest_ch3.name: ResourceUpdate(
                    manifest_ch3,
                    server_ch3,
                ),
            },
            notification_rules={
                manifest_r3.name: ResourceUpdate(
                    manifest_r3,
                    server_r3,
                )
            },
        ),
    )

    _add_namespace(namespace, server_ctx)
    assert expected == _diff_resource_graph(namespace, manifest_ctx, server_ctx)


@pytest.mark.parametrize(
    ("filter_field", "reference_filter_field", "offset", "expect_update"),
    [
        ("age", "age10", 2, False),
        ("age2", "age10", 2, True),
        ("age", "age10", 3, True),
        ("age", "age", 2, True),
    ],
)
def test_diff_should_detect_updates_on_nested_objects(
    filter_field: FieldSelector,
    reference_filter_field: FieldSelector,
    offset: int,
    expect_update: bool,
) -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential("c1", manifest_g)
    manifest_s1 = DemoSource("s1", manifest_c1)
    manifest_seg1 = Segmentation("seg1", manifest_s1, ["city"])
    manifest_w1 = TumblingWindow("w1", manifest_s1, "d", 1, WindowTimeUnit.DAY)

    manifest_v = NumericDistributionValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        threshold=DynamicThreshold(2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        filter=NullFilter(field=filter_field),
        reference=Reference(
            manifest_s1,
            manifest_w1,
            1,
            offset,
            NullFilter(field=reference_filter_field),
        ),
    )

    server_c1 = DemoCredential("c1", server_g)
    server_s1 = DemoSource("s1", server_c1)
    server_seg1 = Segmentation("seg1", server_s1, ["city"])
    server_w1 = TumblingWindow("w1", server_s1, "d", 1, WindowTimeUnit.DAY)
    server_v = NumericDistributionValidator(
        name="v1",
        window=server_w1,
        segmentation=server_seg1,
        threshold=DynamicThreshold(2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        filter=NullFilter(field="age"),
        reference=Reference(server_s1, server_w1, 1, 2, NullFilter(field="age10")),
    )

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        sources={manifest_s1.name: manifest_s1},
        segmentations={manifest_seg1.name: manifest_seg1},
        windows={manifest_w1.name: manifest_w1},
        validators={manifest_v.name: manifest_v},
    )
    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        sources={server_s1.name: server_s1},
        segmentations={server_seg1.name: server_seg1},
        windows={server_w1.name: server_w1},
        validators={server_v.name: server_v},
    )

    expected = create_graph_diff(
        to_update=create_resource_updates(
            validators=(
                {
                    manifest_v.name: ResourceUpdate(
                        manifest_v,
                        server_v,
                    ),
                }
                if expect_update
                else {}
            ),
        )
    )

    _add_namespace(namespace, server_ctx)
    assert expected == _diff_resource_graph(namespace, manifest_ctx, server_ctx)


def test_diff_should_reject_update_on_immutable_field() -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential("c1", manifest_g)
    manifest_s1 = DemoSource("s1", manifest_c1)
    manifest_s2 = DemoSource("s2", manifest_c1)

    server_c1 = DemoCredential("c1", server_g)
    server_s1 = DemoSource("s1", server_c1)
    server_s2 = DemoSource("s2", server_c1)

    # Differing sources on the same segmentation should be rejected.
    manifest_seg1 = Segmentation("seg1", manifest_s2, ["city"])
    server_seg1 = Segmentation("seg1", server_s1, ["city"])

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        sources={manifest_s1.name: manifest_s1, manifest_s2.name: manifest_s2},
        segmentations={manifest_seg1.name: manifest_seg1},
    )
    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        sources={server_s1.name: server_s1, server_s2.name: server_s2},
        segmentations={server_seg1.name: server_seg1},
    )

    _add_namespace(namespace, server_ctx)
    with pytest.raises(ManifestConfigurationError) as err:
        _diff_resource_graph(namespace, manifest_ctx, server_ctx)

    assert "field 'source_name' is immutable" in str(err)
