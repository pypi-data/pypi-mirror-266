from dataclasses import dataclass

from validio_sdk.graphql_client import GraphQLClientHttpError


@dataclass
class SourceSchemaReinference:
    source_names: set[str] | None

    def should_reinfer_schema_for_source(self, source_name: str) -> bool:
        if self.source_names is None:
            return False
        if len(self.source_names) == 0:  # ReInfer for all
            return True
        return source_name in self.source_names


def _sanitize_error(
    e: GraphQLClientHttpError,
    show_secrets: bool,
) -> Exception:
    if show_secrets:
        return e
    raise RuntimeError(
        f"API error: status code {e.status_code}: The error message has been "
        "suppressed because it potentially contains sensitive information; "
        "If you would like to view the error message, run again with --show-secrets"
    )
