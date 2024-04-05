"""Plan command implementation."""

import json
import os
import pathlib
import subprocess
import sys
from enum import Enum
from typing import Any

from validio_sdk.code import scaffold
from validio_sdk.code.settings import dump_graph_var, graph_preamble_var
from validio_sdk.graphql_client import GraphQLClientHttpError
from validio_sdk.resource._diff import GraphDiff, diff_resource_graph
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._resource import DiffContext, Resource, ResourceGraph
from validio_sdk.resource._server_resources import load_resources
from validio_sdk.resource._util import SourceSchemaReinference
from validio_sdk.resource.credentials import Credential
from validio_sdk.validio_client import ValidioAPIClient


async def plan(
    namespace: str,
    client: ValidioAPIClient,
    directory: pathlib.Path,
    schema_reinference: SourceSchemaReinference,
    destroy: bool,
    no_capture: bool,
    show_secrets: bool,
) -> tuple[GraphDiff, DiffContext]:
    """Computes a diff between the manifest program and the live server resources."""
    try:
        manifest_ctx = (
            _get_manifest_graph(directory, no_capture) if not destroy else DiffContext()
        )
        server_ctx = await load_resources(namespace, client)

        diff = await diff_resource_graph(
            namespace=namespace,
            client=client,
            schema_reinference=schema_reinference,
            show_secrets=show_secrets,
            manifest_ctx=manifest_ctx,
            server_ctx=server_ctx,
        )

        return diff, manifest_ctx
    except GraphQLClientHttpError as e:
        raise RuntimeError(f"API error: ({e.status_code}: {e.response.json()})")


def _get_manifest_graph(directory: pathlib.Path, no_capture: bool) -> DiffContext:
    """Runs the manifest program and captures its output into a ResourceGraph."""
    process_env = os.environ.copy()
    process_env[dump_graph_var] = "1"
    child = subprocess.run(
        [sys.executable, directory / scaffold.main_file_name],
        cwd=directory,
        env=process_env,
        capture_output=True,
        text=True,
        check=False,
    )

    if child.returncode != 0:
        _dump_child_stderr(child)
        sys.exit(child.returncode)

    raw_output: str = child.stdout
    (_graph, ctx, captured_output) = _extract_resource_graph(raw_output, child)
    if no_capture and captured_output:
        print(captured_output)

    return ctx


def _dump_child_stderr(child: subprocess.CompletedProcess) -> None:
    print(child.stderr, file=sys.stderr)
    print(
        f"{scaffold.main_file_name} terminated with a non-zero exit code",
        file=sys.stderr,
    )


# Parse the graph from the child program's output. Returns also any captured stdout
# of the child program.
def _extract_resource_graph(
    raw_output: str,
    child: subprocess.CompletedProcess,
) -> tuple[ResourceGraph, DiffContext, str]:
    preamble_start_idx: int = raw_output.find(graph_preamble_var)
    if preamble_start_idx < 0:
        return ResourceGraph(), DiffContext(), ""

    std_output = raw_output[:preamble_start_idx]

    graph_str = raw_output[preamble_start_idx + len(graph_preamble_var) :].strip()
    if len(graph_str) == 0:
        _dump_child_stderr(child)
        raise RuntimeError(
            "BUG(internal): missing resource graph from manifest program"
        )

    try:
        graph_json = json.loads(graph_str)
    except Exception as e:
        # We wrap the error here, because otherwise the exception thrown by
        # JSON parser can be cryptic if it lands in the terminal on its own.
        raise RuntimeError(f"failed to load resource graph output JSON: {e}")

    graph, ctx = ResourceGraph._decode(graph_json)
    return graph, ctx, std_output


# ruff: noqa: PLR0912
def _create_resource_diff_object(
    r: Resource | dict,
    show_secrets: bool,
    rewrites: dict[str, Any] | None = None,
    secrets_changed: bool = False,
    is_manifest: bool = False,
) -> dict[str, object]:
    if rewrites is None:
        rewrites = {}

    data = r.__dict__ if isinstance(r, Resource) else r

    diff_object = {}
    for k, v in data.items():
        if k.startswith("_"):
            continue

        if k in rewrites:
            diff_object[k] = rewrites[k]
        elif isinstance(v, Resource | dict):
            diff_object[k] = _create_resource_diff_object(v, show_secrets)
        elif hasattr(v, "__dict__") and not isinstance(v, Enum):
            diff_object[k] = _create_resource_diff_object(v.__dict__, show_secrets)
        elif isinstance(v, list):
            if len(v) == 0 or not isinstance(v[0], Diffable):
                diff_object[k] = v
                continue

            items = []
            for item in v:
                items.append(_create_resource_diff_object(item.__dict__, show_secrets))

            diff_object[k] = items
        else:
            diff_object[k] = v

    # Mask any sensitive info if requested.
    if not show_secrets and isinstance(r, Credential):
        secret_fields = r._secret_fields()
        if secret_fields:
            for field in secret_fields:
                if secrets_changed and not is_manifest:
                    diff_object[field] = "REDACTED-PREVIOUS"
                else:
                    diff_object[field] = "REDACTED"

    return diff_object
