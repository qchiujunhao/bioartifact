# Changelog

All notable changes to `bioartifact` will be documented in this file.

## 0.1.0 - 2026-05-10

Initial release:

- Dependency-free inspection core with JSON-serializable result models.
- CLI commands for `inspect`, `validate`, `summarize`, `contracts`, `types`,
  and `validate-manifest`.
- JSON output by default for every command, with human-readable text available
  through `--human` or `--output human`.
- Inspectors for FASTQ, FASTA, SAM, BAM headers, VCF, BED, narrowPeak, GTF/GFF,
  CSV/TSV, and HTML reports.
- Contracts for FASTQ, paired FASTQ, sorted/indexed BAM, narrowPeak,
  differential-expression tables, and valid VCF.
- Schema-versioned JSON outputs and JSON schemas.
- Deterministic fixture suite for tests, documentation, and future JOSS examples.
- Manifest-based workflow output validation.
