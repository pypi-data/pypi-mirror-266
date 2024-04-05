"""Apply command implementation."""

from validio_sdk.resource._diff import GraphDiff
from validio_sdk.resource._resource import DiffContext
from validio_sdk.resource._server_resources import apply_updates_on_server
from validio_sdk.validio_client import ValidioAPIClient


async def apply(
    namespace: str,
    client: ValidioAPIClient,
    ctx: DiffContext,
    diff: GraphDiff,
    show_secrets: bool,
) -> None:
    """Applies the provided diff operations on the server."""
    await apply_updates_on_server(namespace, ctx, diff, client, show_secrets)
