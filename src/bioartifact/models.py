from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

JsonDict = dict[str, Any]
SCHEMA_VERSION = "1.0.0"


@dataclass(slots=True)
class ArtifactResult:
    """Structured result returned by artifact inspectors."""

    path: str
    artifact_type: str
    valid: bool
    schema_version: str = SCHEMA_VERSION
    summary: JsonDict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    usable_as: list[str] = field(default_factory=list)
    suggested_next_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(slots=True)
class CheckResult:
    """One named pass/warn/fail check inside a contract result."""

    name: str
    status: str
    message: str = ""
    details: JsonDict = field(default_factory=dict)
    remediation: str | None = None

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass(slots=True)
class ContractResult:
    """Structured result returned by contract validators."""

    contract_name: str
    passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    path: str | None = None
    artifact_type: str | None = None
    schema_version: str = SCHEMA_VERSION
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> JsonDict:
        return {
            "schema_version": self.schema_version,
            "contract": self.contract_name,
            "passed": self.passed,
            "path": self.path,
            "artifact_type": self.artifact_type,
            "checks": [check.to_dict() for check in self.checks],
            "warnings": self.warnings,
            "errors": self.errors,
        }


def passed(
    name: str, message: str = "", remediation: str | None = None, **details: Any
) -> CheckResult:
    return CheckResult(
        name=name, status="pass", message=message, details=details, remediation=remediation
    )


def failed(
    name: str, message: str = "", remediation: str | None = None, **details: Any
) -> CheckResult:
    return CheckResult(
        name=name, status="fail", message=message, details=details, remediation=remediation
    )


def warned(
    name: str, message: str = "", remediation: str | None = None, **details: Any
) -> CheckResult:
    return CheckResult(
        name=name, status="warn", message=message, details=details, remediation=remediation
    )
