from __future__ import annotations

import json
from functools import cache
from importlib import resources
from typing import Any

from bioartifact.exceptions import BioartifactError
from bioartifact.models import SCHEMA_VERSION

SCHEMA_PACKAGE = "bioartifact.schema_files"

SCHEMA_METADATA: list[dict[str, str]] = [
    {
        "name": "artifact_result",
        "title": "ArtifactResult",
        "file": "artifact_result.schema.json",
        "description": "JSON schema for bioartifact inspect output.",
    },
    {
        "name": "contract_result",
        "title": "ContractResult",
        "file": "contract_result.schema.json",
        "description": "JSON schema for bioartifact validate output.",
    },
    {
        "name": "manifest_result",
        "title": "ManifestResult",
        "file": "manifest_result.schema.json",
        "description": "JSON schema for bioartifact validate-manifest output.",
    },
    {
        "name": "summary_result",
        "title": "SummaryResult",
        "file": "summary_result.schema.json",
        "description": "JSON schema for bioartifact summarize output.",
    },
    {
        "name": "artifact_types",
        "title": "ArtifactTypes",
        "file": "artifact_types.schema.json",
        "description": "JSON schema for bioartifact types output.",
    },
    {
        "name": "contracts",
        "title": "Contracts",
        "file": "contracts.schema.json",
        "description": "JSON schema for bioartifact contracts output.",
    },
    {
        "name": "schema_catalog",
        "title": "SchemaCatalog",
        "file": "schema_catalog.schema.json",
        "description": "JSON schema for bioartifact schema output.",
    },
]

_SCHEMA_BY_NAME = {schema["name"]: schema for schema in SCHEMA_METADATA}


class SchemaError(BioartifactError):
    """Raised when a requested schema is unavailable."""


def available_schema_names() -> list[str]:
    """Return stable names for JSON schemas exposed by the CLI."""

    return sorted(_SCHEMA_BY_NAME)


def schema_details() -> dict[str, Any]:
    """Return schema catalog metadata for CLI discovery."""

    return {
        "schema_version": SCHEMA_VERSION,
        "schemas": [
            dict(schema) for schema in sorted(SCHEMA_METADATA, key=lambda item: item["name"])
        ],
    }


@cache
def get_schema(name: str) -> dict[str, Any]:
    """Return a packaged JSON schema by stable schema name."""

    metadata = _SCHEMA_BY_NAME.get(name)
    if metadata is None:
        known = ", ".join(available_schema_names())
        msg = f"unknown schema {name!r}; expected one of: {known}"
        raise SchemaError(msg)

    schema_path = resources.files(SCHEMA_PACKAGE).joinpath(metadata["file"])
    return json.loads(schema_path.read_text(encoding="utf-8"))
