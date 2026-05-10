from __future__ import annotations

from pathlib import Path

from bioartifact.contracts.common import result
from bioartifact.inspectors.vcf import inspect_vcf
from bioartifact.models import ContractResult, failed, passed


def validate_valid_vcf(path: Path, **_: object) -> ContractResult:
    artifact = inspect_vcf(path)
    checks = [
        passed("readable", "VCF is readable")
        if artifact.valid
        else failed(
            "readable",
            "VCF is invalid",
            remediation="Regenerate the VCF or validate it with a format-specific VCF tool before downstream use.",
            errors=artifact.errors,
        ),
    ]

    if "missing #CHROM column header" in artifact.errors:
        checks.append(
            failed(
                "header_present",
                "VCF is missing the #CHROM column header",
                remediation="Write a complete VCF header before variant records.",
            )
        )
    else:
        checks.append(passed("header_present", "VCF contains the #CHROM column header"))

    if artifact.summary.get("records", 0) > 0:
        checks.append(
            passed(
                "records_present",
                "VCF contains variant records",
                records=artifact.summary["records"],
            )
        )
    else:
        checks.append(
            failed(
                "records_present",
                "VCF contains no variant records",
                remediation="Confirm the variant caller produced records or handle the no-variant case explicitly.",
            )
        )

    sample_count = artifact.summary.get("sample_count", 0)
    if sample_count:
        checks.append(
            passed("sample_columns", "VCF contains sample columns", sample_count=sample_count)
        )
    else:
        checks.append(
            passed("sample_columns", "VCF is valid without sample columns", sample_count=0)
        )

    return result(
        "valid_vcf",
        checks,
        path=str(path),
        artifact_type=artifact.artifact_type,
        warnings=artifact.warnings,
        errors=artifact.errors,
    )
