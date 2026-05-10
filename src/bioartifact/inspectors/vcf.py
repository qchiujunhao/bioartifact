from __future__ import annotations

import gzip
from pathlib import Path

from bioartifact.io import is_gzip, open_text, strip_newline
from bioartifact.models import ArtifactResult

REQUIRED_HEADER_COLUMNS = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO"]


def inspect_vcf(path: Path) -> ArtifactResult:
    errors: list[str] = []
    warnings: list[str] = []
    gzip_encoded = False
    metadata_lines = 0
    records = 0
    samples: list[str] = []
    has_column_header = False

    try:
        gzip_encoded = is_gzip(path)
        with open_text(path) as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = strip_newline(raw_line)
                if not line:
                    continue
                if line.startswith("##"):
                    metadata_lines += 1
                    continue
                if line.startswith("#CHROM"):
                    columns = line.split("\t")
                    has_column_header = True
                    if columns[:8] != REQUIRED_HEADER_COLUMNS:
                        errors.append("VCF column header does not contain required first 8 columns")
                    if len(columns) > 8:
                        if columns[8] != "FORMAT":
                            errors.append("sample columns are present but FORMAT column is missing")
                        samples = columns[9:]
                    continue
                if line.startswith("#"):
                    warnings.append(f"unrecognized header line at line {line_number}")
                    continue

                records += 1
                fields = line.split("\t")
                if len(fields) < 8:
                    errors.append(f"record {records} has fewer than 8 VCF columns")
                    continue
                try:
                    pos = int(fields[1])
                except ValueError:
                    errors.append(f"record {records} POS is not an integer")
                    continue
                if pos <= 0:
                    errors.append(f"record {records} POS is not positive")
                if not fields[3] or fields[3] == ".":
                    errors.append(f"record {records} REF is empty")
                if not fields[4] or fields[4] == ".":
                    errors.append(f"record {records} ALT is empty")
    except (OSError, EOFError, gzip.BadGzipFile) as exc:
        errors.append(f"could not read VCF: {exc}")

    if not has_column_header:
        errors.append("missing #CHROM column header")

    summary = {
        "metadata_lines": metadata_lines,
        "records": records,
        "samples": samples,
        "sample_count": len(samples),
        "gzip": gzip_encoded,
    }

    return ArtifactResult(
        path=str(path),
        artifact_type="vcf",
        valid=not errors,
        summary=summary,
        warnings=warnings,
        errors=errors,
        usable_as=["variants"] if not errors else [],
        suggested_next_steps=["variant_annotation", "variant_filtering"] if not errors else [],
    )
