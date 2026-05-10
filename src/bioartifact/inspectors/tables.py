from __future__ import annotations

import csv
from pathlib import Path

from bioartifact.io import open_text, strip_newline
from bioartifact.models import ArtifactResult


def _delimiter_for(path: Path, artifact_type: str) -> str:
    if artifact_type == "csv" or path.suffix.lower() == ".csv":
        return ","
    return "\t"


def inspect_table(path: Path, artifact_type: str | None = None) -> ArtifactResult:
    detected_type = artifact_type or ("csv" if path.suffix.lower() == ".csv" else "tsv")
    delimiter = _delimiter_for(path, detected_type)
    errors: list[str] = []
    warnings: list[str] = []
    columns: list[str] = []
    rows = 0
    missing_values = 0
    inconsistent_rows = 0

    try:
        with open_text(path) as handle:
            reader = csv.reader((strip_newline(line) for line in handle), delimiter=delimiter)
            for row_number, row in enumerate(reader, start=1):
                if row_number == 1:
                    columns = row
                    if not columns or all(column == "" for column in columns):
                        errors.append("table header is empty")
                    continue
                if not row:
                    continue
                rows += 1
                missing_values += sum(1 for value in row if value == "")
                if columns and len(row) != len(columns):
                    inconsistent_rows += 1
    except OSError as exc:
        errors.append(f"could not read table: {exc}")

    if not columns and not errors:
        errors.append("table has no header")
    if rows == 0 and not errors:
        warnings.append("table has a header but no data rows")
    if inconsistent_rows:
        errors.append(f"{inconsistent_rows} rows have a different column count from the header")

    summary = {
        "delimiter": delimiter,
        "rows": rows,
        "columns": columns,
        "column_count": len(columns),
        "missing_values": missing_values,
        "inconsistent_rows": inconsistent_rows,
    }

    return ArtifactResult(
        path=str(path),
        artifact_type=detected_type,
        valid=not errors,
        summary=summary,
        warnings=warnings,
        errors=errors,
        usable_as=["table"] if not errors else [],
        suggested_next_steps=["table_validation"] if not errors else [],
    )
