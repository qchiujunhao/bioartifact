"""Agent-friendly inspection and validation of bioinformatics artifacts."""

from bioartifact.contracts import available_contracts, validate_artifact
from bioartifact.detection import detect_artifact_type
from bioartifact.inspectors import inspect_artifact
from bioartifact.manifest import validate_manifest
from bioartifact.metadata import artifact_type_details, contract_details
from bioartifact.models import ArtifactResult, CheckResult, ContractResult
from bioartifact.summarize import summarize_directory

__all__ = [
    "ArtifactResult",
    "CheckResult",
    "ContractResult",
    "available_contracts",
    "artifact_type_details",
    "contract_details",
    "detect_artifact_type",
    "inspect_artifact",
    "summarize_directory",
    "validate_artifact",
    "validate_manifest",
]

__version__ = "0.1.0"
