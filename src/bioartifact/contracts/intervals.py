from __future__ import annotations

from pathlib import Path

from bioartifact.contracts.common import result
from bioartifact.inspectors.bed import inspect_narrowpeak
from bioartifact.models import ContractResult, failed, passed


def validate_narrowpeak(path: Path, **_: object) -> ContractResult:
    artifact = inspect_narrowpeak(path)
    checks = [
        passed("readable", "narrowPeak file is readable")
        if artifact.valid
        else failed(
            "readable",
            "narrowPeak file is invalid",
            remediation="Regenerate the peak caller output or validate that the file is tab-delimited narrowPeak.",
            errors=artifact.errors,
        ),
    ]

    records = artifact.summary.get("records", 0)
    if records:
        checks.append(passed("records_present", "narrowPeak contains records", records=records))
    else:
        checks.append(
            failed(
                "records_present",
                "narrowPeak contains no records",
                remediation="Check that peak calling completed and wrote peaks to the expected path.",
            )
        )

    column_errors = [error for error in artifact.errors if "fewer than 10" in error]
    if column_errors:
        checks.append(
            failed(
                "required_columns",
                "one or more rows have fewer than 10 columns",
                remediation="Use a narrowPeak output, not a BED3/BED6 peak file, or choose a BED-oriented contract.",
                examples=column_errors,
            )
        )
    else:
        checks.append(passed("required_columns", "all rows contain required narrowPeak columns"))

    coordinate_errors = [
        error
        for error in artifact.errors
        if "coordinate" in error or "end before start" in error or "negative start" in error
    ]
    if coordinate_errors:
        checks.append(
            failed(
                "coordinates_valid",
                "one or more rows contain invalid genomic coordinates",
                remediation="Ensure starts are non-negative integers and ends are greater than or equal to starts.",
                examples=coordinate_errors,
            )
        )
    else:
        checks.append(passed("coordinates_valid", "all genomic coordinates are valid"))

    return result(
        "narrowpeak",
        checks,
        path=str(path),
        artifact_type=artifact.artifact_type,
        warnings=artifact.warnings,
        errors=artifact.errors,
    )
