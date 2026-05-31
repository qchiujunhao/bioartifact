# bioartifact

`bioartifact` is a lightweight Python package and command-line tool for inspecting and
validating bioinformatics output files in deterministic, machine-readable form.

The project targets AI agents, workflow systems, benchmark platforms, and
reproducibility pipelines that need to answer practical questions:

- What kind of artifact was generated?
- Is the artifact structurally readable?
- What basic properties does it contain?
- Does it satisfy a declared contract?
- Is it usable as input to a downstream workflow step?

The package focuses on structure and compatibility, not biological interpretation.

## Motivation

AI agents, workflow engines, and benchmark systems increasingly need to make
automated decisions about bioinformatics outputs. Traditional tools are strong
at format-specific parsing, command-line statistics, or human-readable QC
reports, but they do not provide a small unified layer for asking: "Was the
expected artifact produced, is it structurally usable, and does it satisfy the
contract for the next step?"

`bioartifact` fills that layer with deterministic JSON outputs and named
contracts. It is designed to complement tools such as `samtools`, `bcftools`,
FastQC, MultiQC, and workflow engines, not replace them.

## Current Status

This repository contains:

- extension-based artifact detection
- structured dataclass result models
- JSON-serializable inspection results
- a dependency-free CLI built on `argparse`
- inspectors for FASTQ, FASTA, SAM, BAM headers, VCF, BED, narrowPeak, GTF/GFF,
  generic CSV/TSV tables, and HTML reports
- contracts for FASTQ, paired FASTQ, sorted/indexed BAM, narrowPeak,
  differential-expression tables, and valid VCF
- schema-versioned JSON outputs
- CLI discovery commands for supported artifact types, contracts, and schemas
- manifest-based workflow output validation
- directory summarization
- unit tests and CI configuration

The core has no runtime dependencies. Optional extras can be added for richer
format support without making the base installation heavy.

## Installation

From PyPI:

```bash
pip install bioartifact
```

From a checkout for local development:

```bash
python -m pip install -e .
```

For development:

```bash
python -m pip install -e ".[dev]"
pre-commit install
```

Optional richer BAM/SAM support:

```bash
pip install "bioartifact[bio]"
```

From a checkout, use `python -m pip install -e ".[bio]"`.

## CLI Examples

Inspect an artifact:

```bash
bioartifact inspect sample.fastq
```

Validate a named contract:

```bash
bioartifact validate peaks.narrowPeak --contract narrowpeak
```

Validate paired FASTQ files:

```bash
bioartifact validate sample_R1.fastq.gz --contract paired_fastq --mate sample_R2.fastq.gz
```

Summarize a directory:

```bash
bioartifact summarize outputs/ --recursive
```

List supported contracts and artifact types:

```bash
bioartifact contracts
bioartifact types
```

`bioartifact contracts` includes machine-readable metadata for each contract,
including supported artifact types, required arguments such as `mate`, and the
schema name emitted by validation results.

List available JSON schemas or print a named schema:

```bash
bioartifact schema
bioartifact schema artifact_result
```

Validate all expected outputs declared in a manifest:

```bash
bioartifact validate-manifest workflow_manifest.json
```

Agent-facing CLI usage guidance is available in [SKILLS.md](SKILLS.md).
The development phase plan is available in [PHASE_PLAN.md](PHASE_PLAN.md).

## Output Modes

The CLI emits structured JSON by default for every command. This is intentional:
`bioartifact` is agent-first, and the default output should be deterministic and
machine-readable regardless of whether a command runs in a terminal, a PTY, CI,
or a captured subprocess.

This means agents and workflow systems do not need to pass an output-format
flag. Humans can opt into text output when desired.

For deterministic overrides:

```bash
bioartifact inspect sample.fastq --output human
bioartifact inspect sample.fastq --human
```

The `--json` flag is still accepted for compatibility, but JSON is already the
default.

## Quickstart With Fixtures

The repository includes small synthetic fixture files that can be used without
downloading external data:

```bash
PYTHONPATH=src python -m bioartifact inspect tests/fixtures/variants.vcf.gz
PYTHONPATH=src python -m bioartifact validate tests/fixtures/peaks.narrowPeak --contract narrowpeak
PYTHONPATH=src python -m bioartifact validate tests/fixtures/reads_R1.fastq --contract paired_fastq --mate tests/fixtures/reads_R2.fastq
PYTHONPATH=src python -m bioartifact validate-manifest tests/fixtures/workflow_manifest.pass.json
```

## Python API

```python
from bioartifact import inspect_artifact, validate_artifact

artifact = inspect_artifact("sample.vcf.gz")
print(artifact.to_dict())

contract = validate_artifact("peaks.narrowPeak", "narrowpeak")
print(contract.to_dict())
```

## Design Principles

- Agent-first: deterministic, structured, JSON-serializable output.
- Lightweight: useful with a single command and no workflow engine.
- Modular: each inspector and contract is independent.
- Contract-oriented: validate structure, compatibility, and required properties.
- Conservative: report limitations explicitly instead of inferring scientific meaning.

## Supported Artifact Types

Initial detection and inspection support:

- FASTQ / FASTQ.GZ
- FASTA / FASTA.GZ
- SAM
- BAM header inspection, with optional `pysam` statistics when installed
- VCF / VCF.GZ
- BED
- narrowPeak
- GTF / GFF / GFF3
- CSV / TSV
- HTML / MultiQC HTML

## Inspection Methods

`bioartifact inspect` first detects the artifact type from the filename extension,
then runs a format-specific structural inspector. Inspectors are conservative:
they report whether a file is readable and structurally compatible with the
expected format, but they do not infer biological correctness.

| Artifact type | Detection | Inspection approach | Summary fields |
| --- | --- | --- | --- |
| FASTQ / FASTQ.GZ | `.fastq`, `.fq`, `.fastq.gz`, `.fq.gz` | Opens plain text or gzip input, reads four-line FASTQ records, checks `@` headers, `+` separators, incomplete records, and sequence/quality length equality. | record count, base count, min/max/mean read length, gzip flag |
| FASTA / FASTA.GZ | `.fasta`, `.fa`, `.fna`, and gzip variants | Opens plain text or gzip input, checks that sequence data follows FASTA headers, counts records, and records sequence lengths. | sequence count, base count, min/max/mean sequence length, gzip flag |
| SAM | `.sam` | Parses SAM text headers and alignment rows, checks that alignment records have at least 11 columns, parses flags, extracts references from `@SQ`, and detects coordinate sorting from `@HD SO:coordinate`. | alignment count, mapped/unmapped counts, references, sort order, flag counts |
| BAM | `.bam` | Reads the BGZF/gzip BAM header directly, checks the `BAM\1` magic header, parses header text and reference dictionary, detects sort order, and checks for adjacent `.bai`/`.csi` indexes. If `pysam` is installed, indexed BAM read statistics are also attempted. | references, reference names, sort order, index presence, optional mapped/unmapped counts |
| VCF / VCF.GZ | `.vcf`, `.vcf.gz` | Opens plain text or gzip input, checks metadata/header structure, validates required first 8 VCF columns, detects sample columns, and checks basic record fields such as positive `POS`, non-empty `REF`, and non-empty `ALT`. | metadata line count, variant record count, sample names, sample count, gzip flag |
| BED | `.bed` | Reads tab-delimited interval rows, ignores comments and browser/track lines, checks at least 3 columns, integer coordinates, non-negative starts, and `end >= start`. | record count, chromosome count, per-chromosome counts, min/max interval width |
| narrowPeak | `.narrowPeak` | Applies BED coordinate checks plus ENCODE narrowPeak structure checks: at least 10 columns, integer score, valid strand, numeric signal/p/q columns, and integer peak offset. | record count, chromosome counts, min/max width, required column count |
| GTF | `.gtf` | Parses 9-column GTF rows, validates positive coordinates, summarizes feature types, and extracts `gene_id` and `transcript_id` attributes when present. | record count, feature counts, gene count, transcript count |
| GFF / GFF3 | `.gff`, `.gff3` | Parses 9-column GFF rows, validates positive coordinates, summarizes feature types, and extracts `ID` attributes for gene-like records where available. | record count, feature counts, gene count, transcript count |
| CSV / TSV | `.csv`, `.tsv`, `.tab` | Uses Python's CSV parser with delimiter inferred from extension, reads the header, counts rows/columns, tracks empty cells, and rejects rows with inconsistent column counts. | delimiter, row count, column names, column count, missing values, inconsistent rows |
| HTML / MultiQC HTML | `.html`, `.htm` | Samples the report text, checks for an HTML root/doctype marker, extracts the `<title>`, and detects MultiQC-like reports by searching for `multiqc`. | title, MultiQC flag, sampled byte count |

The current BAM inspector intentionally keeps the default installation light by
parsing the BAM header without requiring `pysam`. Installing `bioartifact[bio]`
enables optional `pysam`-based statistics for indexed BAM files.

## Supported Contracts

- `fastq`
- `paired_fastq`
- `sorted_bam`
- `indexed_bam`
- `narrowpeak`
- `de_table`
- `valid_vcf`

## Contract Reference

| Contract | Expected input | Behavior | Common limitation | Example |
| --- | --- | --- | --- | --- |
| `fastq` | FASTQ or FASTQ.GZ | Checks readability, gzip integrity when applicable, record presence, and sequence/quality length equality. | Does not run per-base quality QC. | `bioartifact validate reads.fastq.gz --contract fastq` |
| `paired_fastq` | R1 FASTQ plus `--mate` R2 FASTQ | Checks both files, read-count synchronization, and normalized read ID matching. | Does not infer mates automatically. | `bioartifact validate R1.fastq.gz --contract paired_fastq --mate R2.fastq.gz` |
| `sorted_bam` | BAM or SAM | Checks readability and whether the alignment header declares coordinate sorting. | Does not prove record-level sort order without deeper parsing. | `bioartifact validate aligned.bam --contract sorted_bam` |
| `indexed_bam` | BAM | Checks readability and adjacent `.bai` or `.csi` presence. | Does not verify full index correctness. | `bioartifact validate aligned.bam --contract indexed_bam` |
| `narrowpeak` | narrowPeak | Checks required 10-column structure and interval coordinates. | Does not judge peak-calling quality. | `bioartifact validate peaks.narrowPeak --contract narrowpeak` |
| `de_table` | CSV or TSV | Checks required DE columns, p-value ranges, and duplicate/empty genes. | Assumes exact column names. | `bioartifact validate de_table.tsv --contract de_table` |
| `valid_vcf` | VCF or VCF.GZ | Checks header, required columns, basic records, and sample column structure. | Does not replace `bcftools` validation. | `bioartifact validate variants.vcf.gz --contract valid_vcf` |

## Manifest Validation

Use `validate-manifest` when a workflow run should produce multiple expected
artifacts. Relative paths are resolved against the manifest directory unless
`--base-dir` is provided.

Minimal JSON manifest:

```json
{
  "outputs": [
    {
      "name": "peaks",
      "path": "peaks.narrowPeak",
      "type": "narrowPeak",
      "contract": "narrowpeak"
    },
    {
      "name": "paired_reads",
      "path": "reads_R1.fastq.gz",
      "type": "fastq",
      "contract": "paired_fastq",
      "mate": "reads_R2.fastq.gz"
    },
    {
      "name": "alignment",
      "path": "aligned.bam",
      "type": "bam",
      "contract": "sorted_bam",
      "requires": [
        {
          "name": "bam_index",
          "suffix": ".bai"
        }
      ]
    }
  ]
}
```

Use `requires` for companion files that must exist before downstream workflow
steps can safely run. A requirement can provide an explicit `path`, or a
`suffix` appended to the artifact path. Requirement objects may also include
`type`, `contract`, and `contract_args` when the companion should be inspected
or validated as a supported artifact. Manifest summaries include requirement
counts under `summary.requirements`.

Run:

```bash
bioartifact validate-manifest workflow_manifest.json
```

YAML manifests are supported when `PyYAML` is installed, for example with
`python -m pip install -e ".[manifest]"`.

## JSON Output Reference

All structured CLI outputs include `schema_version`. The current schema version
is `1.0.0`.

- Artifact inspection schema: [schemas/artifact_result.schema.json](schemas/artifact_result.schema.json)
- Contract validation schema: [schemas/contract_result.schema.json](schemas/contract_result.schema.json)
- Manifest validation schema: [schemas/manifest_result.schema.json](schemas/manifest_result.schema.json)
- Directory summary schema: [schemas/summary_result.schema.json](schemas/summary_result.schema.json)
- Contract discovery schema: [schemas/contracts.schema.json](schemas/contracts.schema.json)
- Artifact type discovery schema: [schemas/artifact_types.schema.json](schemas/artifact_types.schema.json)
- Schema catalog schema: [schemas/schema_catalog.schema.json](schemas/schema_catalog.schema.json)

The same schemas are available from the installed CLI:

```bash
bioartifact schema
bioartifact schema contract_result
```

Schema files are intended to be part of the user-facing interface for the `1.x`
line. Additive fields may be introduced in minor releases; breaking output
changes require a new major schema version.

## CLI Exit Codes

- `0`: the requested inspection, validation, summary, discovery, or manifest
  validation succeeded.
- `1`: inspection or validation failed, a manifest did not pass, or the input
  path/manifest was invalid.

Warnings do not cause a non-zero exit code unless a required structural check or
contract check fails.

## Development

Run the standard-library test suite:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Run the configured developer checks after installing dev dependencies:

```bash
ruff check .
pytest
```

## Releasing

PyPI publishing is handled by GitHub Actions through PyPI Trusted Publishing.
For the first release, create a pending publisher on PyPI with:

- PyPI project name: `bioartifact`
- Owner: `qchiujunhao`
- Repository name: `bioartifact`
- Workflow name: `release.yml`
- Environment name: `pypi`

After the pending publisher is configured, publish a GitHub Release from a
version tag such as `v0.1.0`. The `Release` workflow will build the package and
publish it to PyPI. Manual `workflow_dispatch` is available from GitHub Actions
only for retrying a release if needed.

## Reproducible Fixtures

The repository includes a small fixture suite under `tests/fixtures/` with
versioned FASTA, FASTQ, FASTQ.GZ, SAM, BAM, VCF, VCF.GZ, BED, narrowPeak, GTF,
TSV, and HTML report examples. These files are synthetic but structurally valid,
small enough for CI, and documented with provenance notes so they can support
examples in documentation and publication materials.

Binary fixtures are deterministic and can be regenerated with:

```bash
python tests/fixtures/scripts/build_binary_fixtures.py
```
