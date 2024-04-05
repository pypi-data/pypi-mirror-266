import dataclasses
import inspect
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, TypeVar, cast

from camel_converter import to_snake

# We need validio_sdk in scope due to eval.
# ruff: noqa: F401
import validio_sdk
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._serde import (
    NODE_TYPE_FIELD_NAME,
    ImportValue,
    _api_create_input_params,
    _api_update_input_params,
    _import_resource_params,
    _import_value_repr,
    without_skipped_internal_fields,
)
from validio_sdk.validio_client import ValidioAPIClient

if TYPE_CHECKING:
    from validio_sdk.code._import import ImportContext
    from validio_sdk.resource.channels import Channel
    from validio_sdk.resource.credentials import Credential
    from validio_sdk.resource.notification_rules import NotificationRule
    from validio_sdk.resource.segmentations import Segmentation
    from validio_sdk.resource.sources import Source
    from validio_sdk.resource.validators import Validator
    from validio_sdk.resource.windows import Window

R = TypeVar("R", bound="Resource")


@dataclass
class DiffContext:
    """
    Caches all objects of a graph to make it easier to
    revisit them at a later point. e.g. to compare two graphs.
    """

    credentials: dict[str, "Credential"] = dataclasses.field(default_factory=dict)
    channels: dict[str, "Channel"] = dataclasses.field(default_factory=dict)
    sources: dict[str, "Source"] = dataclasses.field(default_factory=dict)
    windows: dict[str, "Window"] = dataclasses.field(default_factory=dict)
    segmentations: dict[str, "Segmentation"] = dataclasses.field(default_factory=dict)
    validators: dict[str, "Validator"] = dataclasses.field(default_factory=dict)
    notification_rules: dict[str, "NotificationRule"] = dataclasses.field(
        default_factory=dict
    )

    # Validators objects that are yet to be decoded
    pending_validators_raw: dict[str, tuple[type, dict[str, Any]]] = dataclasses.field(
        default_factory=dict
    )

    @staticmethod
    def fields() -> list[str]:
        return [
            f
            for f in list(inspect.signature(DiffContext).parameters)
            if f != "pending_validators_raw"
        ]

    @staticmethod
    def fields_topological_order() -> list[tuple[str, list[str]]]:
        """Returns the fields but with their parent-child dependency encoded."""
        fields: list[tuple[str, list[str]]] = [
            # Channels need to come before sources because notification rules
            # have references to sources.
            ("channels", ["notification_rules"]),
            ("credentials", ["sources"]),
            ("sources", ["windows", "segmentations", "validators"]),
            ("windows", []),
            ("segmentations", []),
            ("validators", []),
            ("notification_rules", []),
        ]
        # Sanity check that this doesn't go out of sync
        parents = {parent for (parent, _) in fields}
        expected = set(DiffContext.fields())
        if parents != expected:
            raise Exception(f"DiffContext fields mismatch {parents} != {expected}")
        return fields


class ResourceID:
    """
    ResourceID represents the id of a resource.

    This value is potentially unknown until after the configuration has been fully
    provisioned. So it acts like a future/promise where it starts out as unknown
    and eventually will be resolved with a concrete value.
    """

    _node_type = "_id"

    def __init__(self) -> None:
        self.value: str | None = None
        """Eventually contains the concrete value assigned to the resource"""

        self._node_type = ResourceID._node_type

    @staticmethod
    def _encode() -> None:
        # Resource ID is never populated before we write the graph out.
        # So no need to include the empty object value in the graph output. When we
        # deserialize back from json, each resource will re-initialize its IDs with
        # empty values again.
        return None


class Resource(Diffable):
    """
    Dataclass representing a resource object.

    All resources are derived from this base. It tracks the dependency
    between resources.
    """

    def __init__(self, name: str, __internal__: "ResourceGraph"):
        self._id: ResourceID = ResourceID()
        self._namespace: str | None = None
        self._node_type: str = self.__class__.__name__

        self.name = name

        # Split by resource type. e.g a Source will have different children sets
        # per resource type (window, segmentation, validators)
        # { "Window": {"w1": {}, "w2": {}}, "Segmentation": {"seg1": {}} }
        self._children = cast(
            dict[str, dict[str, Resource]],
            {
                # This is a type violation as a workaround so that we know
                # how to deserialize the value.
                NODE_TYPE_FIELD_NAME: "_children",
            },
        )

        # The graph must always come from the parent. Except for the root
        # node type (Credential) which will explicitly set a default if none
        # was provided.
        self._resource_graph: ResourceGraph = __internal__

        # Flags whether this resource has been applied (created/deleted/updated)
        # on the server.
        self._applied = False

    def _must_id(self) -> str:
        if self._id.value is None:
            raise RuntimeError(
                f"resource {self.__class__.__name__}(name={self.name}) "
                "has unresolved ID"
            )

        return self._id.value

    def _must_namespace(self) -> str:
        if self._namespace is None:
            raise RuntimeError(
                f"resource {self.__class__.__name__}(name={self.name}) "
                "has unresolved namespace"
            )

        return self._namespace

    # Adds the specified resource as a 'child' of the self resource.
    def add(self, resource_name: str, child: "Resource") -> None:
        self._resource_graph.allocate_resource_name(resource_name, child)

        child_type: str = child.resource_class_name()
        if child_type not in self._children:
            self._children[child_type] = {}

        # No need to do a duplicate check here - since a duplicate name
        # will have failed when we allocated the resource name.
        self._children[child_type][resource_name] = child

    def _encode_children(self) -> dict[str, dict[str, object]]:
        children = {
            k: (
                v._encode()  # type:ignore
                if callable(getattr(v, "_encode", None))
                else v
            )
            for k, v in self._children.items()
        }

        # If the node has no children, then skip deserializing the object.
        # This makes the encoded graph smaller - (e.g. validators are the most
        # common elements in the graph with 10s of thousands of them, and they
        # don't have children)
        if list(children.keys()) == [NODE_TYPE_FIELD_NAME]:
            return {}

        return {"_children": children}

    def _nested_objects(self) -> dict[str, Optional["Diffable | list[Diffable]"]]:
        return {}

    def _api_create_response_field_name(self) -> str:
        return to_snake(self.resource_class_name())

    def _api_delete_method_name(self) -> str:
        return to_snake(self.resource_class_name())

    async def _api_create(
        self, namespace: str, client: ValidioAPIClient, ctx: "DiffContext"
    ) -> str:
        """
        Create the resource, and resolve's the current instance with
        the ID assigned that was assigned by the server.
        """
        create_input = self._api_create_input(namespace, ctx)
        payload = await self._api_create_or_update("create", client, create_input)
        id_ = payload.id
        self._id.value = id_
        return id_

    async def _api_update(
        self, namespace: str, client: ValidioAPIClient, ctx: "DiffContext"
    ) -> None:
        """Perform api call to update the resource."""
        from validio_sdk.resource.validators import Validator

        update_input = self._api_update_input(namespace, ctx)
        await self._api_create_or_update("update", client, update_input)

        if not isinstance(self, Validator):
            return

        # For validators, update the threshold as well. Those have
        # an explicit update api.
        resource_snake_case = to_snake(self.threshold.__class__.__name__)
        method_name = f"update_validator_with_{resource_snake_case}"
        method_fn = client.__getattribute__(method_name)

        response = await method_fn(self.threshold._api_update_input(self._must_id()))
        self._check_graphql_response(
            response=response,
            method_name=method_name,
            response_field=None,
        )

    async def _api_delete(self, client: ValidioAPIClient) -> Any:
        """Api method to delete this resource."""
        method_name = f"delete_{self._api_delete_method_name()}"
        method_fn = client.__getattribute__(method_name)
        response = await method_fn(self._id.value)
        return self._check_graphql_response(
            response=response,
            method_name=method_name,
            response_field=None,
        )

    async def _api_create_or_update(
        self, verb: str, client: ValidioAPIClient, api_input: Any | None
    ) -> Any:
        from validio_sdk.resource.validators import Validator

        """
        Perform api call to create or update the resource.
        """
        # Resource names map, for the most part, directly to the equivalent
        # graphql operation. So we strive to use the same logic for all resource
        # types, by templating the operation name and parameters.

        # e.g GcpBigQuerySource
        class_name = self.__class__.__name__
        # => gcp_big_query_source
        resource_snake_case = to_snake(class_name)

        # Validators end with `_with_dynamic_threshold_` on their create apis.
        method_suffix = (
            f"_with_{to_snake(self.threshold.__class__.__name__)}"
            if isinstance(self, Validator) and verb == "create"
            else ""
        )
        # => create_gcp_big_query_source
        method_name = f"{verb}_{resource_snake_case}{method_suffix}"
        method_fn = client.__getattribute__(method_name)
        # => source
        response_field = self._api_create_response_field_name()

        if isinstance(api_input, dict):
            response = await method_fn(**api_input)
        else:
            response = await method_fn(api_input)

        return self._check_graphql_response(
            response=response,
            method_name=method_name,
            response_field=response_field,
        )

    def _check_graphql_response(
        self,
        response: Any,
        method_name: str,
        response_field: str | None,
    ) -> Any:
        if len(response.errors) > 0:
            raise RuntimeError(
                f"operation '{method_name}' failed for "
                f"resource {self.__class__.__name__}(name={self.name}): "
                f"{response.errors}"
            )

        if response_field is None:
            return None

        payload = response.__getattribute__(response_field)
        if payload is None:
            raise RuntimeError(
                f"operation '{method_name}' failed for '"
                f"resource {self.__class__.__name__}(name={self.name}): '"
                "missing response body"
            )

        return payload

    def _api_create_input(self, namespace: str, _: "DiffContext") -> Any:
        """
        Returns the graphql input(s) to create this resource
        Returned value can either be the <Resource>CreateInput instance or
        if the create api takes in several arguments, then a dict[str, <Input>]
        that will be passed to the api.

        Default behavior (which should be overriden in most resource types) takes
        all fields on the resource, assumes that the field names match 1-1 with the
        corresponding input.
        """
        return _api_create_input_params(self, namespace)

    def _api_update_input(self, _namespace: str, _: "DiffContext") -> Any:
        """
        Similar to _api_create_input. Returns the graphql input(s) to
        update this resource.
        """
        return _api_update_input_params(self)

    def _import_str(
        self,
        indent_level: int,
        import_ctx: "ImportContext",
        inits: list[tuple[str, Any, str | None]] | None = None,
    ) -> str:
        params = [("name", repr(self.name), None), *list(inits or [])]

        for field, import_value in self._import_params().items():
            params.append(
                (
                    field,
                    _import_value_repr(
                        import_value.value, indent_level + 1, import_ctx
                    ),
                    import_value.comment,
                ),
            )

        return self._write_import_str(indent_level=indent_level, inits=params)

    def _import_params(self) -> dict[str, ImportValue]:
        return _import_resource_params(resource=self)

    @abstractmethod
    def resource_class_name(self) -> str:
        """What type of resource this is. (e.g. Window, Segmentation etc)."""

    @abstractmethod
    def _encode(self) -> dict[str, object]:
        """Encode the resource as json."""


class ResourceGraph:
    """
    ResourceGraph represents configuration as a graph of resources.

    A node in the graph represents an instance (identified by the resource name)
    of some resource like Window, Validator etc. and connected to that node are
    any child nodes - e.g. a Credential node will have child nodes of type
    Source, while a Source node will have child nodes of type Window,
    Segmentation, Validator.

    The Resource graph is the canonical datastructure that we work with - both
    the configuration as described from the user's code, as well as the configuration
    that exists on the server side at a given point in time, are represented by
    this graph.
    A node in the graph contains not only the configuration for the represented
    resource, but also internal metadata which we use to track dependency
    relationships that maintain the graph, as well as fields that are pending
    resolved values (waiting for concrete value from the API server).
    This enables us to do operations on it like diffing, dependency resolving etc.
    """

    _sub_graph_node_type = "sub_graph"

    def __init__(self) -> None:
        # Root nodes of each subgraph grouped by type. This contains resources
        # like credentials, channels that are at the top of our dependency trees
        self.sub_graphs = cast(
            # { "Credential": { "c1": { DemoCredential }, "c2": { GcpCredential } }
            dict[str, dict[str, Resource]],
            {
                # This is a type violation as a workaround so that we know
                # how to deserialize the value.
                NODE_TYPE_FIELD_NAME: ResourceGraph._sub_graph_node_type
            },
        )

        # Resource names are unique per resource type. This is used to track duplicate
        # names assignments to resources.
        self._resource_names_by_type: dict[str, set[str]] = {}

    # Remembers that this name is in use for the specified resource type.
    # Throws an error if the specified name has been previously used.
    # the resource type.
    def allocate_resource_name(self, resource_name: str, resource: "Resource") -> None:
        resource_type: str = resource.resource_class_name()
        if resource_type not in self._resource_names_by_type:
            self._resource_names_by_type[resource_type] = set({})

        if resource_name in self._resource_names_by_type[resource_type]:
            raise RuntimeError(
                f"duplicate name '{resource_name}' for type '{resource_type}'; resource"
                " names should be unique for the same resource type"
            )

        self._resource_names_by_type[resource_type].add(resource_name)

    def _add_root(self, resource: "Resource") -> None:
        """Adds a node to the root of a subgraph. Essentially creating
        a new subgraph.
        """
        self.allocate_resource_name(resource.name, resource)
        resource_class_name = resource.resource_class_name()
        if resource_class_name not in self.sub_graphs:
            self.sub_graphs[resource_class_name] = {}
        self.sub_graphs[resource_class_name][resource.name] = resource

    def _find_source(self, source_name: str) -> Optional["Source"]:
        from validio_sdk.resource.credentials import Credential
        from validio_sdk.resource.sources import Source

        if Credential.__name__ not in self.sub_graphs:
            return None

        for credential in self.sub_graphs[Credential.__name__].values():
            if Source.__name__ not in credential._children:
                continue
            if source_name not in credential._children[Source.__name__]:
                continue
            return cast(Source, credential._children[Source.__name__][source_name])

        return None

    def _encode(self) -> dict[str, object]:
        return without_skipped_internal_fields(self.__dict__)

    @staticmethod
    def _decode(obj: dict[str, dict[str, Any]]) -> tuple["ResourceGraph", DiffContext]:
        from validio_sdk.resource.channels import Channel
        from validio_sdk.resource.credentials import Credential
        from validio_sdk.resource.validators import Validator

        # We decode a graph in two passes.
        # The first pass through the input does not decode
        # validators - this bit is where we transition into a non-linear
        # DAG structure because a validator can have several parents (it's
        # target, reference source). So we need to resolve all potential sources
        # before we can resolve validators in the second pass.
        g = ResourceGraph()

        ctx = DiffContext()

        # Pass 1 - decode credentials, channels, etc. which are at the 'root'
        # level and descends onto child resources.
        ResourceGraph._decode_root(obj, ctx, g, Credential, "credentials")
        # We decode the channels graph after the credentials one - since notification
        # rules depend on sources - so that the sources are resolved by the time decode
        # the rules.
        ResourceGraph._decode_root(obj, ctx, g, Channel, "channels")

        # Pass 2 Decode validators.
        Validator._decode_pending(ctx)

        return g, ctx

    @staticmethod
    def _decode_root(
        obj: dict[str, dict[str, Any]],
        ctx: DiffContext,
        g: "ResourceGraph",
        resource_cls: type,
        resource_module_name: str,
    ) -> None:
        if resource_cls.__name__ not in obj["sub_graphs"]:
            return

        sub_graphs = obj["sub_graphs"][resource_cls.__name__]
        for k, v in sub_graphs.items():
            if k == NODE_TYPE_FIELD_NAME:
                continue

            cls = eval(
                f"validio_sdk.resource.{resource_module_name}.{v[NODE_TYPE_FIELD_NAME]}"
            )
            resource = cast(Any, resource_cls)._decode(ctx, cls, v, g)

            resources = getattr(ctx, resource_module_name)
            resources[resource.name] = resource
