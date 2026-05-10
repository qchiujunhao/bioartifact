from __future__ import annotations

import gzip
from pathlib import Path

from bioartifact.io import is_gzip, open_text, strip_newline
from bioartifact.models import ArtifactResult


def inspect_fasta(path: Path) -> ArtifactResult:
    errors: list[str] = []
    warnings: list[str] = []
    sequence_count = 0
    current_length = 0
    lengths: list[int] = []
    gzip_encoded = False

    try:
        gzip_encoded = is_gzip(path)
        with open_text(path) as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = strip_newline(raw_line)
                if not line:
                    continue
                if line.startswith(">"):
                    if sequence_count > 0:
                        lengths.append(current_length)
                    sequence_count += 1
                    current_length = 0
                    continue
                if sequence_count == 0:
                    errors.append(
                        f"sequence data found before first FASTA header at line {line_number}"
                    )
                    break
                current_length += len(line.strip())
        if sequence_count > 0:
            lengths.append(current_length)
    except (OSError, EOFError, gzip.BadGzipFile) as exc:
        errors.append(f"could not read FASTA: {exc}")

    if sequence_count == 0 and not errors:
        errors.append("no FASTA records found")
    if any(length == 0 for length in lengths):
        warnings.append("one or more FASTA records have zero sequence length")

    total_bases = sum(lengths)
    summary = {
        "sequences": sequence_count,
        "bases": total_bases,
        "min_sequence_length": min(lengths) if lengths else None,
        "max_sequence_length": max(lengths) if lengths else None,
        "mean_sequence_length": (total_bases / len(lengths)) if lengths else None,
        "gzip": gzip_encoded,
    }

    return ArtifactResult(
        path=str(path),
        artifact_type="fasta",
        valid=not errors,
        summary=summary,
        warnings=warnings,
        errors=errors,
        usable_as=["reference_sequences", "sequences"] if not errors else [],
        suggested_next_steps=["index_reference", "sequence_alignment"] if not errors else [],
    )
