from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from bioartifact.detection import detect_artifact_type
from bioartifact.models import SCHEMA_VERSION


def summarize_directory(path: str | Path, *, recursive: bool = False) -> dict[str, Any]:
    """Summarize detected artifact types in a directory."""

    root = Path(path)
    if not root.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "path": str(root),
            "valid": False,
            "errors": ["directory does not exist"],
            "artifacts": [],
            "counts": {},
        }
    if not root.is_dir():
        return {
            "schema_version": SCHEMA_VERSION,
            "path": str(root),
            "valid": False,
            "errors": ["path is not a directory"],
            "artifacts": [],
            "counts": {},
        }

    iterator = root.rglob("*") if recursive else root.iterdir()
    artifacts = []
    counts: Counter[str] = Counter()

    for candidate in sorted(iterator):
        if not candidate.is_file():
            continue
        artifact_type = detect_artifact_type(candidate)
        if artifact_type == "unknown":
            continue
        artifacts.append(
            {
                "path": str(candidate),
                "type": artifact_type,
            }
        )
        counts[artifact_type] += 1

    return {
        "schema_version": SCHEMA_VERSION,
        "path": str(root),
        "valid": True,
        "errors": [],
        "artifacts": artifacts,
        "counts": dict(sorted(counts.items())),
    }
