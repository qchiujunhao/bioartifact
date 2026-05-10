from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from bioartifact.detection import detect_artifact_type
from bioartifact.inspectors.alignment import inspect_bam, inspect_sam
from bioartifact.inspectors.bed import inspect_bed, inspect_narrowpeak
from bioartifact.inspectors.fasta import inspect_fasta
from bioartifact.inspectors.fastq import inspect_fastq
from bioartifact.inspectors.gtf import inspect_gff, inspect_gtf
from bioartifact.inspectors.html import inspect_html
from bioartifact.inspectors.tables import inspect_table
from bioartifact.inspectors.vcf import inspect_vcf
from bioartifact.models import ArtifactResult

Inspector = Callable[[Path], ArtifactResult]

INSPECTORS: dict[str, Inspector] = {
    "bam": inspect_bam,
    "bed": inspect_bed,
    "csv": lambda path: inspect_table(path, artifact_type="csv"),
    "fasta": inspect_fasta,
    "fastq": inspect_fastq,
    "gff": inspect_gff,
    "gtf": inspect_gtf,
    "html": inspect_html,
    "narrowPeak": inspect_narrowpeak,
    "sam": inspect_sam,
    "tsv": lambda path: inspect_table(path, artifact_type="tsv"),
    "vcf": inspect_vcf,
}


def inspect_artifact(path: str | Path, artifact_type: str | None = None) -> ArtifactResult:
    """Inspect one artifact path and return a JSON-serializable result."""

    artifact_path = Path(path)
    detected_type = artifact_type or detect_artifact_type(artifact_path)

    if not artifact_path.exists():
        return ArtifactResult(
            path=str(artifact_path),
            artifact_type=detected_type,
            valid=False,
            errors=["file does not exist"],
        )
    if not artifact_path.is_file():
        return ArtifactResult(
            path=str(artifact_path),
            artifact_type=detected_type,
            valid=False,
            errors=["path is not a file"],
        )

    inspector = INSPECTORS.get(detected_type)
    if inspector is None:
        return ArtifactResult(
            path=str(artifact_path),
            artifact_type="unknown",
            valid=False,
            warnings=["artifact type could not be detected from extension"],
        )
    return inspector(artifact_path)
