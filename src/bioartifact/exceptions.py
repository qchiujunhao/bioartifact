class BioartifactError(Exception):
    """Base exception for bioartifact failures."""


class UnsupportedArtifactError(BioartifactError):
    """Raised when an artifact type is not supported."""


class InspectionError(BioartifactError):
    """Raised when an artifact cannot be inspected."""


class ContractError(BioartifactError):
    """Raised when a contract cannot be evaluated."""
