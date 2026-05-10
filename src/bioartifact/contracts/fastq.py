from __future__ import annotations

from itertools import zip_longest
from pathlib import Path

from bioartifact.contracts.common import result
from bioartifact.inspectors.fastq import inspect_fastq, normalize_fastq_read_id
from bioartifact.io import open_text
from bioartifact.models import ContractResult, failed, passed


def validate_fastq(path: Path, **_: object) -> ContractResult:
    artifact = inspect_fastq(path)
    checks = [
        passed("readable", "FASTQ is readable")
        if artifact.valid
        else failed(
            "readable",
            "FASTQ is not structurally valid",
            remediation="Regenerate or repair the FASTQ file before using it downstream.",
            errors=artifact.errors,
        ),
        passed("records_present", "FASTQ contains records", records=artifact.summary["records"])
        if artifact.summary["records"] > 0
        else failed(
            "records_present",
            "FASTQ contains no records",
            remediation="Check that the workflow wrote reads to the expected FASTQ path.",
        ),
    ]

    if path.name.lower().endswith(".gz"):
        if artifact.summary.get("gzip"):
            checks.append(passed("valid_gzip", "gzip encoding is valid"))
        else:
            checks.append(
                failed(
                    "valid_gzip",
                    "file extension indicates gzip but gzip magic is absent",
                    remediation="Recompress the file with gzip or correct the filename extension.",
                )
            )

    if artifact.valid:
        checks.append(passed("sequence_quality_lengths", "all sequence and quality lengths match"))
    else:
        length_errors = [
            error for error in artifact.errors if "sequence and quality lengths differ" in error
        ]
        if length_errors:
            checks.append(
                failed(
                    "sequence_quality_lengths",
                    "one or more FASTQ records have mismatched sequence and quality lengths",
                    remediation="Regenerate the FASTQ or trim/filter with a tool that preserves sequence and quality synchronization.",
                    examples=length_errors[:5],
                )
            )

    return result(
        "fastq",
        checks,
        path=str(path),
        artifact_type=artifact.artifact_type,
        warnings=artifact.warnings,
        errors=artifact.errors,
    )


def _iter_fastq_ids(path: Path):
    with open_text(path) as handle:
        while True:
            header = handle.readline()
            if not header:
                break
            if not header.strip():
                break
            sequence = handle.readline()
            plus = handle.readline()
            quality = handle.readline()
            if not sequence or not plus or not quality:
                break
            yield normalize_fastq_read_id(header)


def validate_paired_fastq(
    path: Path, mate: str | Path | None = None, **_: object
) -> ContractResult:
    if mate is None:
        return result(
            "paired_fastq",
            [
                failed(
                    "mate_provided",
                    "paired_fastq contract requires --mate",
                    remediation="Pass the second FASTQ file with `--mate`.",
                )
            ],
            path=str(path),
            artifact_type="fastq",
        )

    mate_path = Path(mate)
    first = inspect_fastq(path)
    second = inspect_fastq(mate_path)
    checks = [
        passed("first_readable", "first FASTQ is valid")
        if first.valid
        else failed(
            "first_readable",
            "first FASTQ is invalid",
            remediation="Repair or regenerate the first mate FASTQ.",
            errors=first.errors,
        ),
        passed("second_readable", "second FASTQ is valid")
        if second.valid
        else failed(
            "second_readable",
            "second FASTQ is invalid",
            remediation="Repair or regenerate the second mate FASTQ.",
            errors=second.errors,
        ),
    ]

    first_records = first.summary.get("records", 0)
    second_records = second.summary.get("records", 0)
    if first_records == second_records:
        checks.append(passed("synchronized_read_counts", "FASTQ files contain equal read counts"))
    else:
        checks.append(
            failed(
                "synchronized_read_counts",
                "FASTQ files contain different read counts",
                remediation="Recreate the paired FASTQ files from the same synchronized filtering step.",
                first_records=first_records,
                second_records=second_records,
            )
        )

    if first.valid and second.valid:
        mismatches = []
        compared = 0
        for compared, (first_id, second_id) in enumerate(
            zip_longest(_iter_fastq_ids(path), _iter_fastq_ids(mate_path)),
            start=1,
        ):
            if first_id != second_id:
                mismatches.append(
                    {"record": compared, "first_id": first_id, "second_id": second_id}
                )
                if len(mismatches) >= 10:
                    break
        if mismatches:
            checks.append(
                failed(
                    "matching_read_ids",
                    "paired FASTQ read IDs differ",
                    remediation="Verify that R1 and R2 files belong to the same sample and filtering step.",
                    examples=mismatches,
                )
            )
        else:
            checks.append(
                passed("matching_read_ids", "paired FASTQ read IDs match", compared=compared)
            )

    return result(
        "paired_fastq",
        checks,
        path=str(path),
        artifact_type="fastq",
        warnings=first.warnings + second.warnings,
        errors=first.errors + second.errors,
    )
