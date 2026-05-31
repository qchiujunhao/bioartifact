from __future__ import annotations

from typing import Any

from bioartifact.models import SCHEMA_VERSION

ARTIFACT_TYPE_DETAILS: list[dict[str, Any]] = [
    {
        "name": "bam",
        "extensions": [".bam"],
        "description": "Binary alignment/map file; header inspection is available without pysam.",
        "usable_as": ["read_alignment"],
    },
    {
        "name": "bed",
        "extensions": [".bed"],
        "description": "BED genomic interval file.",
        "usable_as": ["genomic_intervals"],
    },
    {
        "name": "csv",
        "extensions": [".csv"],
        "description": "Comma-delimited table.",
        "usable_as": ["table"],
    },
    {
        "name": "fasta",
        "extensions": [".fasta", ".fa", ".fna", ".fasta.gz", ".fa.gz", ".fna.gz"],
        "description": "FASTA sequence file.",
        "usable_as": ["reference_sequences", "sequences"],
    },
    {
        "name": "fastq",
        "extensions": [".fastq", ".fq", ".fastq.gz", ".fq.gz"],
        "description": "FASTQ sequencing reads.",
        "usable_as": ["sequencing_reads"],
    },
    {
        "name": "gff",
        "extensions": [".gff", ".gff3"],
        "description": "GFF/GFF3 genome annotation.",
        "usable_as": ["genome_annotation"],
    },
    {
        "name": "gtf",
        "extensions": [".gtf"],
        "description": "GTF genome annotation.",
        "usable_as": ["genome_annotation"],
    },
    {
        "name": "html",
        "extensions": [".html", ".htm"],
        "description": "HTML report, including MultiQC-like reports.",
        "usable_as": ["report"],
    },
    {
        "name": "narrowPeak",
        "extensions": [".narrowPeak"],
        "description": "ENCODE narrowPeak peak-call interval file.",
        "usable_as": ["genomic_intervals", "peak_calls"],
    },
    {
        "name": "sam",
        "extensions": [".sam"],
        "description": "SAM text alignment file.",
        "usable_as": ["read_alignment"],
    },
    {
        "name": "tsv",
        "extensions": [".tsv", ".tab"],
        "description": "Tab-delimited table.",
        "usable_as": ["table"],
    },
    {
        "name": "vcf",
        "extensions": [".vcf", ".vcf.gz"],
        "description": "Variant call format file.",
        "usable_as": ["variants"],
    },
]


CONTRACT_DETAILS: list[dict[str, Any]] = [
    {
        "name": "de_table",
        "description": "Validate a differential-expression table with gene, log2FoldChange, pvalue, and padj columns.",
        "artifact_types": ["csv", "tsv"],
        "arguments": [],
        "required_arguments": [],
        "optional_arguments": [],
        "output_schema": "contract_result",
    },
    {
        "name": "fastq",
        "description": "Validate FASTQ readability, gzip integrity when applicable, record presence, and sequence/quality length agreement.",
        "artifact_types": ["fastq"],
        "arguments": [],
        "required_arguments": [],
        "optional_arguments": [],
        "output_schema": "contract_result",
    },
    {
        "name": "indexed_bam",
        "description": "Validate that a BAM file is readable and has an adjacent .bai or .csi index.",
        "artifact_types": ["bam"],
        "arguments": [],
        "required_arguments": [],
        "optional_arguments": [],
        "output_schema": "contract_result",
    },
    {
        "name": "narrowpeak",
        "description": "Validate required narrowPeak columns and genomic coordinate structure.",
        "artifact_types": ["narrowPeak"],
        "arguments": [],
        "required_arguments": [],
        "optional_arguments": [],
        "output_schema": "contract_result",
    },
    {
        "name": "paired_fastq",
        "description": "Validate two FASTQ files have equal read counts and matching normalized read IDs.",
        "artifact_types": ["fastq"],
        "arguments": ["mate"],
        "required_arguments": ["mate"],
        "optional_arguments": [],
        "output_schema": "contract_result",
    },
    {
        "name": "sorted_bam",
        "description": "Validate that a BAM or SAM artifact is declared coordinate sorted.",
        "artifact_types": ["bam", "sam"],
        "arguments": [],
        "required_arguments": [],
        "optional_arguments": [],
        "output_schema": "contract_result",
    },
    {
        "name": "valid_vcf",
        "description": "Validate VCF header presence, required columns, basic record fields, and sample column structure.",
        "artifact_types": ["vcf"],
        "arguments": [],
        "required_arguments": [],
        "optional_arguments": [],
        "output_schema": "contract_result",
    },
]


def artifact_type_details() -> dict[str, Any]:
    """Return supported artifact type metadata for CLI discovery."""

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_types": ARTIFACT_TYPE_DETAILS,
    }


def contract_details() -> dict[str, Any]:
    """Return supported contract metadata for CLI discovery."""

    return {
        "schema_version": SCHEMA_VERSION,
        "contracts": CONTRACT_DETAILS,
    }
