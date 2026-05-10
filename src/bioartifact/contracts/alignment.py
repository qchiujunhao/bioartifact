from __future__ import annotations

from pathlib import Path

from bioartifact.contracts.common import result
from bioartifact.inspectors import inspect_artifact
from bioartifact.models import ContractResult, failed, passed


def validate_sorted_bam(path: Path, **_: object) -> ContractResult:
    artifact = inspect_artifact(path)
    checks = [
        passed("readable", "alignment artifact is readable")
        if artifact.valid
        else failed(
            "readable",
            "alignment artifact is not readable",
            remediation="Regenerate the alignment file or inspect the upstream aligner output.",
            errors=artifact.errors,
        ),
    ]

    if artifact.artifact_type not in {"bam", "sam"}:
        checks.append(
            failed(
                "artifact_type",
                "sorted_bam contract expects a BAM or SAM artifact",
                remediation="Provide a `.bam` or `.sam` alignment file for this contract.",
                artifact_type=artifact.artifact_type,
            )
        )
    else:
        checks.append(passed("artifact_type", "artifact is an alignment file"))

    if artifact.summary.get("sorted") is True:
        checks.append(passed("coordinate_sorted", "alignment is coordinate sorted"))
    else:
        checks.append(
            failed(
                "coordinate_sorted",
                "alignment is not declared coordinate sorted",
                remediation="Sort the alignment by coordinate, for example with `samtools sort`, then rerun validation.",
                sort_order=artifact.summary.get("sort_order"),
            )
        )

    return result(
        "sorted_bam",
        checks,
        path=str(path),
        artifact_type=artifact.artifact_type,
        warnings=artifact.warnings,
        errors=artifact.errors,
    )


def validate_indexed_bam(path: Path, **_: object) -> ContractResult:
    artifact = inspect_artifact(path)
    checks = [
        passed("readable", "BAM is readable")
        if artifact.valid
        else failed(
            "readable",
            "BAM is not readable",
            remediation="Regenerate the BAM file or check that it is BGZF-compressed BAM.",
            errors=artifact.errors,
        ),
    ]

    if artifact.artifact_type != "bam":
        checks.append(
            failed(
                "artifact_type",
                "indexed_bam contract expects a BAM artifact",
                remediation="Provide a `.bam` file for the indexed_bam contract.",
                artifact_type=artifact.artifact_type,
            )
        )
    else:
        checks.append(passed("artifact_type", "artifact is a BAM file"))

    if artifact.summary.get("index_present") is True:
        checks.append(passed("index_present", "BAM index was found"))
    else:
        checks.append(
            failed(
                "index_present",
                "no BAM index was found next to the BAM file",
                remediation="Create an index with `samtools index aligned.bam` or provide an adjacent `.bai`/`.csi` file.",
            )
        )

    return result(
        "indexed_bam",
        checks,
        path=str(path),
        artifact_type=artifact.artifact_type,
        warnings=artifact.warnings,
        errors=artifact.errors,
    )
