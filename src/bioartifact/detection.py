from __future__ import annotations

from pathlib import Path

KNOWN_ARTIFACT_TYPES = {
    "bam",
    "bed",
    "csv",
    "fasta",
    "fastq",
    "gff",
    "gtf",
    "html",
    "narrowPeak",
    "sam",
    "tsv",
    "vcf",
}


def detect_artifact_type(path: str | Path) -> str:
    """Return the artifact type inferred from a filename.

    The detector is intentionally conservative and extension-based. Inspectors
    still validate the structure before an artifact is considered valid.
    """

    name = Path(path).name
    lower_name = name.lower()

    if lower_name.endswith((".fastq.gz", ".fq.gz", ".fastq", ".fq")):
        return "fastq"
    if lower_name.endswith((".fasta.gz", ".fa.gz", ".fna.gz", ".fasta", ".fa", ".fna")):
        return "fasta"
    if lower_name.endswith(".vcf.gz") or lower_name.endswith(".vcf"):
        return "vcf"
    if lower_name.endswith(".narrowpeak"):
        return "narrowPeak"
    if lower_name.endswith(".bed"):
        return "bed"
    if lower_name.endswith(".bam"):
        return "bam"
    if lower_name.endswith(".sam"):
        return "sam"
    if lower_name.endswith(".gtf"):
        return "gtf"
    if lower_name.endswith((".gff", ".gff3")):
        return "gff"
    if lower_name.endswith(".csv"):
        return "csv"
    if lower_name.endswith((".tsv", ".tab")):
        return "tsv"
    if lower_name.endswith((".html", ".htm")):
        return "html"
    return "unknown"
