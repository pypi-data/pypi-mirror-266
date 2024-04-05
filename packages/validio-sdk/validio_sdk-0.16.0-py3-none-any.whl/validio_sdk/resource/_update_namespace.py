from camel_converter import to_snake

from validio_sdk.graphql_client.input_types import ResourceNamespaceUpdateInput
from validio_sdk.resource._diff import DiffContext
from validio_sdk.resource._resource import Resource
from validio_sdk.resource._server_resources import load_resources
from validio_sdk.validio_client import ValidioAPIClient

_max_recursion_depth = 20


async def get_resources_to_move(
    namespace: str,
    client: ValidioAPIClient,
    resources_obj_raw: dict[str, list[str]] | None,
) -> dict[str, dict[str, Resource]]:
    server_ctx = await load_resources(namespace=namespace, client=client)

    if resources_obj_raw:
        resources_obj = {k: set(v) for k, v in resources_obj_raw.items()}
    else:
        resources_obj = {
            k: set(getattr(server_ctx, k).keys()) for k in server_ctx.fields()
        }

    resources_to_move: dict[str, dict[str, Resource]] = {}
    resource_topo_order = DiffContext.fields_topological_order()
    for parent_resource_type, children_types in resource_topo_order:
        if resources_obj_raw is not None and parent_resource_type not in resources_obj:
            continue

        parent_resource_names = resources_obj[parent_resource_type]
        for parent_resource_name in parent_resource_names:
            visit_resource(
                server_ctx=server_ctx,
                resource_topo_order=resource_topo_order,
                resources_to_move=resources_to_move,
                resource_type=parent_resource_type,
                resource=find_resource_in_server_list(
                    server_ctx=server_ctx,
                    resource_type=parent_resource_type,
                    resource_name=parent_resource_name,
                ),
                depth=0,
            )

    return resources_to_move


def visit_resource(
    server_ctx: DiffContext,
    resource_topo_order: list[tuple[str, list[str]]],
    resources_to_move: dict[str, dict[str, Resource]],
    resource_type: str,
    resource: Resource,
    depth: int,
) -> None:
    if depth > _max_recursion_depth:
        # Safeguard. We don't have deep parent-child relationships
        raise Exception("BUG: max recursion depth exceeded")

    # Flag the resource to be moved.
    if resource_type not in resources_to_move:
        resources_to_move[resource_type] = {}
    resources_to_move[resource_type][resource.name] = resource

    # Get all children resources for the resource and flag them to be moved as well.
    children_types = next(
        (
            children_types
            for (parent_type, children_types) in resource_topo_order
            if parent_type == resource_type
        ),
        None,
    )

    if not children_types:
        return

    for child_resource_type in children_types:
        children_resources = get_children_resources_to_move(
            server_ctx=server_ctx,
            parent_resource_class_name=resource.resource_class_name().lower(),
            parent_resource_name=resource.name,
            child_resource_type=child_resource_type,
        )
        for child_resource in children_resources:
            visit_resource(
                server_ctx=server_ctx,
                resource_topo_order=resource_topo_order,
                resources_to_move=resources_to_move,
                resource_type=child_resource_type,
                resource=child_resource,
                depth=depth + 1,
            )


def find_resource_in_server_list(
    server_ctx: DiffContext,
    resource_type: str,
    resource_name: str,
) -> Resource:
    resources = getattr(server_ctx, resource_type)
    for name, r in resources.items():
        if name == resource_name:
            return r
    raise Exception(f"{resource_type} '{resource_name}' not found in namespace")


def get_children_resources_to_move(
    server_ctx: DiffContext,
    parent_resource_class_name: str,
    parent_resource_name: str,
    child_resource_type: str,
) -> list[Resource]:
    """Returns the names of the children of the specified type
    that belong to the parent.
    """
    child_resources = getattr(server_ctx, child_resource_type)
    # e.g 'credentials' => 'credential_name'
    parent_name_field = f"{parent_resource_class_name}_name"
    return [
        r
        for r in child_resources.values()
        if getattr(r, parent_name_field) == parent_resource_name
    ]


async def apply_move(
    namespace: str,
    client: ValidioAPIClient,
    target_namespace: str,
    resources_to_move: dict[str, dict[str, Resource]],
) -> None:
    for resource_type, _ in DiffContext.fields_topological_order():
        if resource_type not in resources_to_move:
            continue
        for name, resource in resources_to_move[resource_type].items():
            method_name = f"update_{to_snake(resource.resource_class_name())}_namespace"
            method_fn = client.__getattribute__(method_name)
            response = await method_fn(
                ResourceNamespaceUpdateInput(
                    new_resource_namespace=target_namespace,
                    resource_name=name,
                    resource_namespace=namespace,
                )
            )
            if len(response.errors) > 0:
                raise RuntimeError(
                    f"operation '{method_name}' failed for "
                    f"resource {resource.__class__.__name__}(name={name}): "
                    f"{response.errors}"
                )
