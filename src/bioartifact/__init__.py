"""Agent-friendly inspection and validation of bioinformatics artifacts."""

from bioartifact.contracts import available_contracts, validate_artifact
from bioartifact.detection import detect_artifact_type
from bioartifact.inspectors import inspect_artifact
from bioartifact.manifest import validate_manifest
from bioartifact.metadata import artifact_type_details, contract_details
from bioartifact.models import ArtifactResult, CheckResult, ContractResult
from bioartifact.schema_registry import available_schema_names, get_schema, schema_details
from bioartifact.summarize import summarize_directory

__all__ = [
    "ArtifactResult",
    "CheckResult",
    "ContractResult",
    "available_contracts",
    "artifact_type_details",
    "available_schema_names",
    "contract_details",
    "detect_artifact_type",
    "get_schema",
    "inspect_artifact",
    "schema_details",
    "summarize_directory",
    "validate_artifact",
    "validate_manifest",
]

__version__ = "0.1.0"
