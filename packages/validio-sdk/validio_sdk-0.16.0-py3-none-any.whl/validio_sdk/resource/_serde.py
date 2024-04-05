import inspect
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from camel_converter import to_snake

# We need validio_sdk in scope due to eval.
# ruff: noqa: F401
import validio_sdk

if TYPE_CHECKING:
    from validio_sdk.code._import import ImportContext
    from validio_sdk.resource._diffable import Diffable
    from validio_sdk.resource._resource import Resource

"""
These are fields in a node of the graph that contains links to the resource graph
itself or other internal fields that we don't need to serialise. We ignore these
during encoding.
"""
SKIPPED_INTERNAL_FIELD_NAMES = {
    "_resource_names_by_type",
    "_resource_graph",
    "_id",
    "_applied",
    "_namespace",
}

"""
Contains the type (unique hardcoded name) of the current node.
Allows us know how to decode that node.
"""
NODE_TYPE_FIELD_NAME = "_node_type"

"""Contains the child nodes for the current node in the graph."""
CHILDREN_FIELD_NAME = "_children"

"""Contains the config values of a resource when we encode that resource."""
CONFIG_FIELD_NAME = "config_field"

"""
These are fields in a node of the graph, that contain metadata as opposed to
actual configuration values. While we work with the graph (e.g. when
encoding/decoding, diffing etc.), we need special handling for them
whenever they show up.
"""
INTERNAL_FIELD_NAMES: set[str] = {
    NODE_TYPE_FIELD_NAME,
    CHILDREN_FIELD_NAME,
}.union(SKIPPED_INTERNAL_FIELD_NAMES)


def custom_resource_graph_encoder(obj: Any) -> None:
    if callable(getattr(obj, "_encode", None)):
        return obj._encode()
    raise RuntimeError(f"failed to encode graph: missing encoder for {obj}")


def _encode_resource(
    obj: "Resource", skip_fields: set[str] | None = None
) -> dict[str, object]:
    """
    Helper method to encode a node in the graph that corresponds to a Resource instance.

    :param obj: the node to be encoded
    :param skip_fields: These fields will ignored during encoding
    ...
    :returns: JSON compatible encoded value
    """
    # For the encoding, we group all actual config fields in it's dedicated section.
    # The config fields correspond to parameters that go into the Resource's constructor
    # so this lets us automatically decode the value back into the Resource using its
    # constructor.
    config_fields = {}
    # Internal fields are everything else that isn't config field. These are encoded
    # as is unless they have a custom encoder.
    internal_fields = {}

    skip_fields = (skip_fields or set({})).union(
        {
            # We will recursively encode the children so skip the field.
            CHILDREN_FIELD_NAME,
        }
    )
    for field, value in obj.__dict__.items():
        if field in skip_fields:
            continue

        if field in INTERNAL_FIELD_NAMES:
            internal_fields[field] = value
        else:
            config_fields[field] = (
                value._encode() if callable(getattr(value, "_encode", None)) else value
            )

    return without_skipped_internal_fields(
        {
            **internal_fields,
            CONFIG_FIELD_NAME: config_fields,
            **obj._encode_children(),
        }
    )


def get_children_node(obj: dict[str, dict[str, object]]) -> dict[str, object]:
    if CHILDREN_FIELD_NAME in obj:
        return obj[CHILDREN_FIELD_NAME]
    return {}


def without_skipped_internal_fields(
    obj: dict[str, dict[str, object]],
) -> dict[str, object]:
    """Remove the resource graph info from the object we want to serialize."""
    return {k: v for k, v in obj.items() if k not in SKIPPED_INTERNAL_FIELD_NAMES}


def with_resource_graph_info(obj: dict[str, object], g: object) -> dict[str, object]:
    """Adds back the resource graph info to the object we're deserializing."""
    return {**obj, "__internal__": g}


def _api_create_input_params(
    resource: "Resource",
    namespace: str,
    overrides: dict[str, Any] | None = None,
    skip_fields: set[str] | None = None,
) -> object:
    cls = eval(f"validio_sdk.graphql_client.{resource.__class__.__name__}CreateInput")
    overrides = overrides if overrides else {}
    skip_fields = {
        *set(overrides.keys()),
        *(skip_fields if skip_fields is not None else set({})),
        "name",
        "resource_name",
        "resource_namespace",
    }

    fields = list(inspect.signature(cls).parameters)
    name = resource.name
    return cls(
        **{
            **{
                to_snake(f): getattr(resource, to_snake(f))
                for f in fields
                if to_snake(f) not in skip_fields
            },
            **overrides,
            "name": name,
            "resource_name": name,
            "resource_namespace": namespace,
        }
    )


def _api_update_input_params(
    resource: "Resource",
    overrides: dict[str, Any] | None = None,
    skip_fields: set[str] | None = None,
) -> object:
    cls = eval(f"validio_sdk.graphql_client.{resource.__class__.__name__}UpdateInput")
    overrides = overrides if overrides else {}
    skip_fields = {
        *set(overrides.keys()),
        *(skip_fields if skip_fields is not None else set({})),
        "id",
    }

    fields = list(inspect.signature(cls).parameters)
    return cls(
        **{
            **{
                to_snake(f): getattr(resource, to_snake(f))
                for f in fields
                if to_snake(f) not in skip_fields
            },
            **overrides,
            "id": resource._must_id(),
        }
    )


@dataclass
class ImportValue:
    value: Any
    comment: str | None = None


def _import_resource_params(
    resource: "Diffable",
    skip_fields: set[str] | None = None,
) -> dict[str, ImportValue]:
    from validio_sdk.resource._resource import DiffContext

    skip_fields = skip_fields or set({})
    parent_resource_name_fields = {f"{f[:len(f)-1]}_name" for f in DiffContext.fields()}
    skip_fields = {*skip_fields, *parent_resource_name_fields}
    return {
        field: ImportValue(getattr(resource, field))
        for field in resource._all_fields()
        if field not in skip_fields
    }


def _import_value_repr(
    value: Any,
    indent_level: int,
    import_ctx: "ImportContext",
) -> str:
    from validio_sdk.resource._diffable import Diffable

    if isinstance(value, Diffable):
        value_repr = value._import_str(indent_level=indent_level, import_ctx=import_ctx)
    elif isinstance(value, Enum):
        value_repr = value.__str__()
    elif isinstance(value, list):
        # This code will basically just change how more complex types that
        # something simple than a list of stringsd is represented. Where this
        # works fine for strings:
        #
        # Obj(
        #     some_key=['foo','bar','baz'],
        # )
        #
        # It doesn't really look well when we do this for `Diffable` objects. It
        # would by default end up like this.
        #
        # Obj(
        #     complex=[AnotherObj(
        #         foo="bar",
        #     ),AnotherObj(
        #         foo="baz",
        #     )],
        # )
        #
        # This code will change that to look like this. That's all it does!
        #
        # Obj(
        #     complex=[
        #         AnotherObj(
        #             foo="bar",
        #         ),
        #         AnotherObj(
        #             foo="baz",
        #         ),
        #    ],
        # )
        if len(value) > 0 and isinstance(value[0], Diffable):
            base_indent = " " * Diffable._num_ident_spaces(indent_level)
            next_indent = " " * Diffable._num_ident_spaces(indent_level + 1)
            values = f",\n{next_indent}".join(
                [v._import_str(indent_level + 1, import_ctx) for v in value]
            )

            value_repr = f"[\n{next_indent}{values},\n{base_indent}]"
        else:
            values = ",".join(
                [_import_value_repr(v, indent_level, import_ctx) for v in value]
            )

            value_repr = f"[{values}]"
    else:
        value_repr = repr(value)

    return value_repr
