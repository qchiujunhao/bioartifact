# Changelog

All notable changes to `bioartifact` will be documented in this file.

## Unreleased

- Added `bioartifact schema` for schema catalog discovery and named JSON schema
  output.
- Added public JSON schemas for directory summaries, contract discovery,
  artifact type discovery, and schema catalog output.
- Added manifest `requires` checks for required companion files, such as BAM and
  VCF indexes.
- Added requirement-level aggregate counts under manifest
  `summary.requirements`.
- Added machine-readable `required_arguments`, `optional_arguments`, and
  `output_schema` fields to contract discovery output.
- Tightened public JSON schemas so `schema_version` is validated as the current
  schema version constant.
- Added a static project website under `docs/` with a GitHub Pages deployment
  workflow.
- Refined the project website layout for a cleaner, less cluttered presentation.

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
- Deterministic fixture suite for tests, documentation, and future publication examples.
- Manifest-based workflow output validation.
