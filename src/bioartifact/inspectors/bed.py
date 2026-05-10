from __future__ import annotations

from collections import Counter
from pathlib import Path

from bioartifact.io import open_text, strip_newline
from bioartifact.models import ArtifactResult


def _iter_interval_rows(path: Path) -> tuple[list[list[str]], list[str]]:
    rows: list[list[str]] = []
    errors: list[str] = []
    with open_text(path) as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = strip_newline(raw_line)
            if not line or line.startswith(("#", "track ", "browser ")):
                continue
            fields = line.split("\t")
            if len(fields) < 3:
                errors.append(f"line {line_number} has fewer than 3 BED columns")
                continue
            rows.append(fields)
    return rows, errors


def _coordinate_errors(rows: list[list[str]]) -> list[str]:
    errors: list[str] = []
    for index, fields in enumerate(rows, start=1):
        try:
            start = int(fields[1])
            end = int(fields[2])
        except ValueError:
            errors.append(f"row {index} has non-integer coordinates")
            continue
        if start < 0:
            errors.append(f"row {index} has negative start coordinate")
        if end < start:
            errors.append(f"row {index} has end before start")
    return errors


def _interval_summary(rows: list[list[str]]) -> dict[str, object]:
    chrom_counts = Counter(fields[0] for fields in rows)
    widths = []
    for fields in rows:
        try:
            widths.append(int(fields[2]) - int(fields[1]))
        except ValueError:
            continue
    return {
        "records": len(rows),
        "chromosomes": len(chrom_counts),
        "chromosome_counts": dict(sorted(chrom_counts.items())),
        "min_width": min(widths) if widths else None,
        "max_width": max(widths) if widths else None,
    }


def inspect_bed(path: Path) -> ArtifactResult:
    errors: list[str] = []
    try:
        rows, read_errors = _iter_interval_rows(path)
        errors.extend(read_errors)
        errors.extend(_coordinate_errors(rows))
    except OSError as exc:
        rows = []
        errors.append(f"could not read BED: {exc}")

    if not rows and not errors:
        errors.append("no BED records found")

    return ArtifactResult(
        path=str(path),
        artifact_type="bed",
        valid=not errors,
        summary=_interval_summary(rows),
        errors=errors,
        usable_as=["genomic_intervals"] if not errors else [],
        suggested_next_steps=["interval_intersection", "genome_browser_loading"]
        if not errors
        else [],
    )


def inspect_narrowpeak(path: Path) -> ArtifactResult:
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[list[str]] = []

    try:
        rows, read_errors = _iter_interval_rows(path)
        errors.extend(read_errors)
        errors.extend(_coordinate_errors(rows))
        for index, fields in enumerate(rows, start=1):
            if len(fields) < 10:
                errors.append(f"row {index} has fewer than 10 narrowPeak columns")
                continue
            try:
                score = int(fields[4])
            except ValueError:
                errors.append(f"row {index} has non-integer score")
            else:
                if score < 0 or score > 1000:
                    warnings.append(f"row {index} score is outside the conventional 0-1000 range")
            if fields[5] not in {"+", "-", "."}:
                errors.append(f"row {index} has invalid strand value")
            for column_index, column_name in ((6, "signalValue"), (7, "pValue"), (8, "qValue")):
                try:
                    float(fields[column_index])
                except ValueError:
                    errors.append(f"row {index} has non-numeric {column_name}")
            try:
                int(fields[9])
            except ValueError:
                errors.append(f"row {index} has non-integer peak offset")
    except OSError as exc:
        errors.append(f"could not read narrowPeak: {exc}")

    if not rows and not errors:
        errors.append("no narrowPeak records found")

    return ArtifactResult(
        path=str(path),
        artifact_type="narrowPeak",
        valid=not errors,
        summary=_interval_summary(rows) | {"required_columns": 10},
        warnings=warnings,
        errors=errors,
        usable_as=["genomic_intervals", "peak_calls"] if not errors else [],
        suggested_next_steps=["peak_annotation", "motif_analysis"] if not errors else [],
    )
