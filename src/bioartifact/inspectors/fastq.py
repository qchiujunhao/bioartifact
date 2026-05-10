from __future__ import annotations

import gzip
from pathlib import Path

from bioartifact.io import is_gzip, open_text, strip_newline
from bioartifact.models import ArtifactResult


def normalize_fastq_read_id(header: str) -> str:
    """Normalize common FASTQ mate suffixes for paired-end comparisons."""

    value = header.strip()
    if value.startswith("@"):
        value = value[1:]
    value = value.split()[0] if value else value
    if value.endswith(("/1", "/2")):
        value = value[:-2]
    return value


def inspect_fastq(path: Path) -> ArtifactResult:
    errors: list[str] = []
    warnings: list[str] = []
    record_count = 0
    total_bases = 0
    min_length: int | None = None
    max_length = 0
    gzip_encoded = False

    try:
        gzip_encoded = is_gzip(path)
        with open_text(path) as handle:
            line_number = 0
            while True:
                header = handle.readline()
                if header == "":
                    break
                line_number += 1
                if not header.strip():
                    if any(line.strip() for line in handle):
                        errors.append(
                            f"blank line found between FASTQ records near line {line_number}"
                        )
                    break
                sequence = handle.readline()
                plus = handle.readline()
                quality = handle.readline()
                line_number += 3

                if not sequence or not plus or not quality:
                    errors.append(f"incomplete FASTQ record ending near line {line_number}")
                    break

                header = strip_newline(header)
                sequence = strip_newline(sequence)
                plus = strip_newline(plus)
                quality = strip_newline(quality)
                record_count += 1

                if not header.startswith("@"):
                    errors.append(f"record {record_count} header does not start with @")
                if not plus.startswith("+"):
                    errors.append(f"record {record_count} separator does not start with +")
                if len(sequence) != len(quality):
                    errors.append(
                        f"record {record_count} sequence and quality lengths differ "
                        f"({len(sequence)} != {len(quality)})"
                    )

                read_length = len(sequence)
                total_bases += read_length
                min_length = read_length if min_length is None else min(min_length, read_length)
                max_length = max(max_length, read_length)
    except (OSError, EOFError, gzip.BadGzipFile) as exc:
        errors.append(f"could not read FASTQ: {exc}")

    if record_count == 0 and not errors:
        errors.append("no FASTQ records found")

    summary = {
        "records": record_count,
        "bases": total_bases,
        "min_read_length": min_length,
        "max_read_length": max_length if record_count else None,
        "mean_read_length": (total_bases / record_count) if record_count else None,
        "gzip": gzip_encoded,
    }

    return ArtifactResult(
        path=str(path),
        artifact_type="fastq",
        valid=not errors,
        summary=summary,
        warnings=warnings,
        errors=errors,
        usable_as=["sequencing_reads"] if not errors else [],
        suggested_next_steps=["read_qc", "alignment"] if not errors else [],
    )
