from __future__ import annotations

from collections import Counter
from pathlib import Path

from bioartifact.io import open_text, strip_newline
from bioartifact.models import ArtifactResult


def _parse_attributes(raw_attributes: str, artifact_type: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    if artifact_type == "gtf":
        for part in raw_attributes.strip().rstrip(";").split(";"):
            part = part.strip()
            if not part or " " not in part:
                continue
            key, value = part.split(" ", 1)
            attributes[key] = value.strip().strip('"')
        return attributes

    for part in raw_attributes.strip().split(";"):
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        attributes[key] = value
    return attributes


def _inspect_gtf_like(path: Path, artifact_type: str) -> ArtifactResult:
    errors: list[str] = []
    feature_counts: Counter[str] = Counter()
    gene_ids: set[str] = set()
    transcript_ids: set[str] = set()
    records = 0

    try:
        with open_text(path) as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = strip_newline(raw_line)
                if not line or line.startswith("#"):
                    continue
                fields = line.split("\t")
                if len(fields) != 9:
                    errors.append(f"line {line_number} does not contain 9 columns")
                    continue
                records += 1
                feature_counts[fields[2]] += 1
                try:
                    start = int(fields[3])
                    end = int(fields[4])
                except ValueError:
                    errors.append(f"line {line_number} has non-integer coordinates")
                    continue
                if start <= 0:
                    errors.append(f"line {line_number} start is not positive")
                if end < start:
                    errors.append(f"line {line_number} end is before start")
                attributes = _parse_attributes(fields[8], artifact_type)
                if "gene_id" in attributes:
                    gene_ids.add(attributes["gene_id"])
                if "transcript_id" in attributes:
                    transcript_ids.add(attributes["transcript_id"])
                if "ID" in attributes and fields[2].lower() == "gene":
                    gene_ids.add(attributes["ID"])
    except OSError as exc:
        errors.append(f"could not read {artifact_type.upper()}: {exc}")

    if records == 0 and not errors:
        errors.append(f"no {artifact_type.upper()} records found")

    return ArtifactResult(
        path=str(path),
        artifact_type=artifact_type,
        valid=not errors,
        summary={
            "records": records,
            "feature_counts": dict(sorted(feature_counts.items())),
            "gene_count": len(gene_ids),
            "transcript_count": len(transcript_ids),
        },
        errors=errors,
        usable_as=["genome_annotation"] if not errors else [],
        suggested_next_steps=["feature_counting", "annotation_filtering"] if not errors else [],
    )


def inspect_gtf(path: Path) -> ArtifactResult:
    return _inspect_gtf_like(path, "gtf")


def inspect_gff(path: Path) -> ArtifactResult:
    return _inspect_gtf_like(path, "gff")
