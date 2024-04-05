import copy
import dataclasses
from dataclasses import dataclass
from typing import Any, Optional, TypeVar, cast

from camel_converter import to_snake

from validio_sdk.exception import ValidioError
from validio_sdk.graphql_client import CredentialSecretChanged, GraphQLClientHttpError
from validio_sdk.resource._diff_util import must_find_source
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._errors import (
    ManifestConfigurationError,
    max_resource_depth_exceeded,
    rejected_update_exception,
    updated_resource_type_mismatch_exception,
)
from validio_sdk.resource._field_selector import SelectorWithFieldName
from validio_sdk.resource._resource import DiffContext, Resource
from validio_sdk.resource._util import SourceSchemaReinference, _sanitize_error
from validio_sdk.resource.credentials import Credential
from validio_sdk.resource.sources import Source
from validio_sdk.validio_client import ValidioAPIClient

R = TypeVar("R", bound=Resource)

"""
When we descend into nested objects, we set a limit on how deep we go.
Otherwise, in a bad manifest configuration or due to a bug in our code, we
could enter a cycle.
"""
MAX_RESOURCE_DEPTH = 15


@dataclass
class ResourceUpdate:
    """
    Represents a resource that has an update. It contains the concrete class
    of the resource (e.g. TumblingWindow), followed by a representation of the
    manifest and server's version of the resource respectively.
    """

    manifest: Resource
    server: Resource
    secrets_changed: bool = False


@dataclass
class ResourceUpdates:
    """Resources to update. Grouped by type."""

    credentials: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    channels: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    sources: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    windows: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    segmentations: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    validators: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    notification_rules: dict[str, ResourceUpdate] = dataclasses.field(
        default_factory=dict
    )
    identity_providers: dict[str, ResourceUpdate] = dataclasses.field(
        default_factory=dict
    )
    users: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)


@dataclass
class GraphDiff:
    to_create: DiffContext
    to_delete: DiffContext
    to_update: ResourceUpdates

    def num_creates(self) -> int:
        return self.size(self.to_create)

    def num_deletes(self) -> int:
        return self.size(self.to_delete)

    def num_updates(self) -> int:
        return self.size(self.to_update)

    def num_operations(self) -> int:
        return self.num_creates() + self.num_deletes() + self.num_updates()

    @staticmethod
    def size(obj: Any) -> int:
        count = 0
        for f in DiffContext.fields():
            count += len(getattr(obj, f))
        return count


async def diff_resource_graph(
    namespace: str,
    client: ValidioAPIClient,
    schema_reinference: SourceSchemaReinference,
    show_secrets: bool,
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
) -> GraphDiff:
    partial_diff = _diff_resource_graph(
        namespace=namespace,
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        for_validators=False,
    )

    # Enrich resource_graph. We do this before expanding field selectors
    # because the latter depends on the schema for all sources being present.
    await enrich_resource_graph(
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        graph=partial_diff,
        client=client,
        schema_reinference=schema_reinference,
        show_secrets=show_secrets,
    )

    # Expand field selector for validators.
    expand_validator_field_selectors(manifest_ctx)

    # Now after expanding field selectors, we can diff validators.
    validators_diff = _diff_resource_graph(
        namespace=namespace,
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        for_validators=True,
    )

    final_diff = partial_diff
    final_diff.to_create.validators = validators_diff.to_create.validators
    final_diff.to_update.validators = validators_diff.to_update.validators
    final_diff.to_delete.validators = validators_diff.to_delete.validators

    return final_diff


def expand_validator_field_selectors(manifest_ctx: DiffContext) -> None:
    for name in list(manifest_ctx.validators.keys()):
        template = manifest_ctx.validators[name]

        source_field_selector: SelectorWithFieldName | None = getattr(
            template, "_field_selector", None
        )
        reference_field_selector: dict[str, str] | None = getattr(
            template, "_reference_field_selector", None
        )
        filter_field_selector: SelectorWithFieldName | None = (
            getattr(template.filter, "_field_selector", None)
            if template.filter
            else None
        )

        if source_field_selector:
            field_selector = source_field_selector
        elif filter_field_selector:
            field_selector = filter_field_selector
        else:
            continue

        source = must_find_source(manifest_ctx, template.source_name)
        if source.jtd_schema is None:
            # If we have no schema then it means we're doing a diff where the
            # source's credential has not yet been created - which means we can't
            # do schema inference. As a result, we can't yet expand the selector.
            continue

        if source_field_selector:
            delattr(template, "_field_selector")
        if reference_field_selector:
            delattr(template, "_reference_field_selector")
        if filter_field_selector:
            delattr(template.filter, "_field_selector")

        # Remove the placeholder validator.
        del manifest_ctx.validators[name]

        fields = field_selector.field_selector._get_matching_fields(
            cast(Any, source.jtd_schema)
        )

        # We don't want to deep copy the entire resource graph
        resource_graph = template._resource_graph
        template._resource_graph = None  # type: ignore
        for field in fields:
            validator = copy.deepcopy(template)
            validator._resource_graph = resource_graph

            resource_name = validator.name % {"field": field}
            validator.name = resource_name

            if source_field_selector:
                setattr(validator, field_selector.field_name, field)

            if reference_field_selector:
                setattr(validator, reference_field_selector["field_name"], field)

            if filter_field_selector:
                setattr(
                    validator.filter,
                    field_selector.field_name,
                    field,
                )

            manifest_ctx.validators[resource_name] = validator


def _diff_resource_graph(
    namespace: str,
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    for_validators: bool | None = None,
) -> GraphDiff:
    fns = [
        (compute_creates, DiffContext),
        (compute_deletes, DiffContext),
        (compute_updates, ResourceUpdates),
    ]
    diffs = []
    fields = DiffContext.fields()
    for diff_fn, cls in fns:
        diff_by_resource = {}
        for field in fields:
            include_diff = (
                True
                if for_validators is None
                else (field == "validators") == for_validators
            )
            if not include_diff:
                continue
            diff_by_resource[field] = diff_fn(
                namespace, getattr(manifest_ctx, field), getattr(server_ctx, field)
            )
        diffs.append(cls(**diff_by_resource))

    return GraphDiff(to_create=diffs[0], to_delete=diffs[1], to_update=diffs[2])


def compute_creates(
    namespace: str, manifest_resources: dict[str, R], server_resources: dict[str, R]
) -> dict[str, R]:
    creates = {}
    for name, resource in manifest_resources.items():
        if name in server_resources:
            _check_namespace(namespace, server_resources[name])
            continue
        creates[name] = resource
    return creates


def compute_deletes(
    namespace: str, manifest_resources: dict[str, R], server_resources: dict[str, R]
) -> dict[str, R]:
    deletes = {}
    for name, resource in server_resources.items():
        if namespace != resource._must_namespace():
            # Only work on resources in the configured namespace.
            continue

        if name not in manifest_resources:
            deletes[name] = resource

    return deletes


def compute_updates(
    namespace: str, manifest_resources: dict[str, R], server_resources: dict[str, R]
) -> dict[str, ResourceUpdate]:
    diffs = {}

    for name, manifest in manifest_resources.items():
        if name not in server_resources:
            continue

        server = server_resources[name]
        _check_namespace(namespace, server)

        d = diff(manifest, server, 0, manifest, server)
        if d:
            diffs[name] = d

    return diffs


# ruff: noqa: PLR0911,PLR0912
def diff(
    manifest_object: Diffable,
    server_object: Diffable,
    curr_depth: int,
    manifest_resource: Resource,
    server_resource: Resource,
) -> ResourceUpdate | None:
    """
    Compares the current (manifest) resource against a provided server version
    of that resource. None is returned if there are no changes between the two
    resources. If there is at least one change, then a diff is returned which
    contains a representation of the full manifest and server side resource.
    """
    if curr_depth > MAX_RESOURCE_DEPTH:
        raise max_resource_depth_exceeded(manifest_resource.name)

    # If the server resource has a different type, this is an invalid update.
    # e.g. we can't switch a window from tumbling to fixed batch. The window
    # needs to be re-created if that's the desired outcome.
    if not isinstance(server_object, manifest_object.__class__):
        raise updated_resource_type_mismatch_exception(
            manifest_resource.name, manifest_object, server_object
        )

    # Check for any disallowed updates. e.g. we can't switch the
    # source id of a validator.
    for field in manifest_object._immutable_fields():
        manifest = getattr(manifest_object, field)
        server = getattr(server_object, field)
        if manifest != server:
            raise rejected_update_exception(
                manifest_resource.name, field, manifest, server
            )

    # If any valid field changes, then mark the resource as having a diff.
    for field in manifest_object._mutable_fields():
        manifest = getattr(manifest_object, field)
        server = getattr(server_object, field)
        if manifest == server:
            continue

        # Whenever we find there's a change to make, grab all fields on both
        # resource versions so that we can present them as a diff.
        # Regardless of at what depth we find a change, the diff we present will always
        # start from the root resource itself. We pass those objects around for this
        # purpose.
        return ResourceUpdate(manifest_resource, server_resource)

    # No changes yet. Next, descend into the nested fields. If we find any
    # changes, then mark _this_ resource as changed.
    server_nested_objects = server_object._nested_objects()
    for field, manifest in manifest_object._nested_objects().items():
        server = server_nested_objects[field]

        # No possible change if both are unset.
        if manifest is None and server is None:
            continue

        # If exactly one of them is None, then we definitely have a change.
        if manifest is None or server is None:
            return ResourceUpdate(manifest_resource, server_resource)

        if isinstance(server, list) != isinstance(manifest, list):
            return ResourceUpdate(manifest_resource, server_resource)

        if isinstance(server, list) and isinstance(manifest, list):
            if len(server) != len(manifest):
                return ResourceUpdate(manifest_resource, server_resource)

            for i in range(len(server) - 1):
                # Descend into both objects to diff.
                collected_diff = diff(
                    manifest[i],
                    server[i],
                    curr_depth + 1,
                    manifest_resource,
                    server_resource,
                )

                if collected_diff:
                    # The returned diff is that of the full resource (not
                    # just the nested object that had a change). So we can
                    # exit with it.
                    return collected_diff

            continue

        # Descend into both objects to diff.
        collected_diff = diff(
            manifest, server, curr_depth + 1, manifest_resource, server_resource
        )
        if collected_diff:
            # The returned diff is that of the full resource (not
            # just the nested object that had a change). So we can
            # exit with it.
            return collected_diff

    # No update to make
    return None


async def enrich_resource_graph(
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    graph: GraphDiff,
    client: ValidioAPIClient,
    schema_reinference: SourceSchemaReinference,
    show_secrets: bool,
) -> None:
    """
    Now that we have a graph and done a diff, some values are unknown and need to
    be resolved before we can get a full picture of changes and start making api
    requests to create/update things. This function fetches missing info from the
    server and updates resources in the graph as needed.
    """
    # For the resources we update, resolve the ids in the manifest objects. We have
    # the info in the equivalent server object.
    for f in DiffContext.fields():
        manifest_resources = getattr(manifest_ctx, f)
        server_resources = getattr(server_ctx, f)
        for name, server_resource in server_resources.items():
            if name in manifest_resources:
                manifest_resource = manifest_resources[name]
                manifest_resource._id.value = server_resource._must_id()

    # Since source jtd schemas can be managed automatically, we do not include
    # them in the actual diff process since they are not necessarily known yet.
    # Instead, here we explicitly check for any updates.
    await check_for_source_schema_changes(
        manifest_ctx, server_ctx, graph, client, schema_reinference
    )

    # Check if any credential secrets has changed and add them to the diff.
    # They're excluded by default.
    await check_for_credential_secret_changes(
        manifest_ctx, server_ctx, graph, client, show_secrets
    )


async def check_for_source_schema_changes(
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    graph: GraphDiff,
    client: ValidioAPIClient,
    schema_reinference: SourceSchemaReinference,
) -> None:
    # For sources that are to be created and don't have a schema, we
    # need to infer a schema for them to use in the create request.
    for name, source in graph.to_create.sources.items():
        if source.jtd_schema is None:
            await infer_schema_for_source(manifest_ctx, source, client)

    # For sources that are to be updated, if there is no schema specified
    # in the manifest, then assign it the schema of the server version.
    # Or if we were asked to re-infer the schema, then do that instead.
    for name, r in graph.to_update.sources.items():
        assert isinstance(r.manifest, Source)
        assert isinstance(r.server, Source)

        manifest_source = r.manifest
        reinfer = schema_reinference.should_reinfer_schema_for_source(name)
        if manifest_source.jtd_schema is None:
            if reinfer:
                await infer_schema_for_source(manifest_ctx, manifest_source, client)
            else:
                manifest_source.jtd_schema = r.server.jtd_schema

    # For unchanged sources, check if there is a schema diff now that all schemas
    # have been resolved. If we find a diff, flag the source as updated.
    unchanged_sources = {
        name: s
        for name, s in manifest_ctx.sources.items()
        if s.name not in graph.to_create.sources
        and s.name not in graph.to_update.sources
        and s.name not in graph.to_delete.sources
    }

    for name, server_source in server_ctx.sources.items():
        if name not in unchanged_sources:
            continue

        manifest_source = unchanged_sources[name]

        reinfer = schema_reinference.should_reinfer_schema_for_source(name)
        if manifest_source.jtd_schema is None and reinfer:
            await infer_schema_for_source(manifest_ctx, manifest_source, client)

        if (
            manifest_source.jtd_schema is not None
            and manifest_source.jtd_schema != server_source.jtd_schema
        ):
            # The 'manifest' and 'server' version of the resource can be the same here
            # since there is no difference between the two (only change is the secret).
            graph.to_update.sources[name] = ResourceUpdate(
                manifest_source, server_source
            )

        # Ensure the source has a schema in case we need it in a field selector.
        if manifest_source.jtd_schema is None:
            manifest_source.jtd_schema = server_source.jtd_schema


async def infer_schema_for_source(
    manifest_ctx: DiffContext,
    source: Source,
    client: ValidioAPIClient,
) -> None:
    credential = manifest_ctx.credentials[source.credential_name]
    # If we don't yet have an ID (credential has not yet been created),
    # we can't do schema inference. So schema will be unknown in the diff.
    if credential._id.value is None:
        return
    await source._api_infer_schema(credential, client)


async def check_for_credential_secret_changes(
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    graph: GraphDiff,
    client: ValidioAPIClient,
    show_secrets: bool,
) -> None:
    """
    To be able to always compute if we have any diff for our credentials we want
    to call the API to figure this out otherwise we wouldn't show a change in
    the secret if other fields were changed.

    TODO(VR-3095): The API should return a list of changed fields so we can be
    more granular in our diff. Currently we will mark *all* secret fields as
    changed.
    """
    # If it's a delete it won't exist in `manifest_ctx` so it will be skipped.
    for name, manifest_resource in manifest_ctx.credentials.items():
        # If it's an add it won't exist in `server_ctx` so it will be skipped.
        server_resource = server_ctx.credentials.get(name)
        if not server_resource:
            continue

        secret_fields = manifest_resource._secret_fields()
        if not secret_fields:
            continue

        has_changed = await _credential_secret_change(
            client, secret_fields, manifest_resource, show_secrets
        )

        if not has_changed:
            continue

        # Flag the credential for secrets changed if any so we can show it in
        # the diff.
        graph.to_update.credentials[name] = ResourceUpdate(
            manifest_resource, server_resource, secrets_changed=has_changed
        )


async def _credential_secret_change(
    client: ValidioAPIClient,
    secret_fields: set[str],
    credential: Credential,
    show_secrets: bool = False,
) -> bool:
    # We need to import the validio_sdk module due to the `eval`
    # ruff: noqa: F401
    import validio_sdk

    method_name = f"{to_snake(credential.__class__.__name__)}_secret_changed"
    cls = eval(
        f"validio_sdk.graphql_client.input_types.{credential.__class__.__name__}SecretChangedInput"
    )

    try:
        response = cast(
            CredentialSecretChanged,
            await client.__getattribute__(method_name)(
                cls(
                    **{
                        "id": credential._must_id(),
                        **{f: getattr(credential, f) for f in secret_fields},
                    }
                )
            ),
        )
    except GraphQLClientHttpError as e:
        raise _sanitize_error(e, show_secrets)

    if len(response.errors) > 0:
        raise RuntimeError(
            f"operation '{method_name}' failed for Credential {credential.name}: "
            f"{response.errors}"
        )

    return response.has_changed or False


def _check_namespace(namespace: str, server_resource: Resource) -> None:
    server_namespace = server_resource._must_namespace()
    if namespace != server_namespace:
        raise ManifestConfigurationError(
            f"resource {server_resource.__class__.__name__} '{server_resource.name}' "
            "does not belong to the current namespace; "
            f"resource namespace = {server_namespace}; current namespace = {namespace}"
        )
