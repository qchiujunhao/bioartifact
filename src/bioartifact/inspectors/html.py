from __future__ import annotations

import re
from pathlib import Path

from bioartifact.io import open_text
from bioartifact.models import ArtifactResult

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def inspect_html(path: Path) -> ArtifactResult:
    errors: list[str] = []
    warnings: list[str] = []
    title: str | None = None
    is_multiqc = False
    bytes_read = 0

    try:
        with open_text(path) as handle:
            content = handle.read(200_000)
            bytes_read = len(content.encode("utf-8", errors="replace"))
    except OSError as exc:
        content = ""
        errors.append(f"could not read HTML report: {exc}")

    lower_content = content.lower()
    if content and "<html" not in lower_content and "<!doctype html" not in lower_content:
        warnings.append("file does not contain an obvious HTML root element")

    match = TITLE_RE.search(content)
    if match:
        title = " ".join(match.group(1).split())
    is_multiqc = "multiqc" in lower_content
    usable_as = []
    if not errors:
        usable_as = ["report", "multiqc_report"] if is_multiqc else ["report"]

    return ArtifactResult(
        path=str(path),
        artifact_type="html",
        valid=not errors,
        summary={
            "title": title,
            "multiqc": is_multiqc,
            "bytes_sampled": bytes_read,
        },
        warnings=warnings,
        errors=errors,
        usable_as=usable_as,
        suggested_next_steps=["report_archival"] if not errors else [],
    )
