# bioartifact CLI Skill

Use this guide when an agent needs to inspect, validate, or summarize
bioinformatics workflow artifacts with the `bioartifact` command-line tool.

## When To Use

Use `bioartifact` when you need machine-readable evidence about generated files:

- determine an artifact type from a path
- check whether a file is structurally readable
- extract basic format properties as JSON
- validate a file against a named downstream contract
- summarize artifact types inside an output directory

Do not use `bioartifact` to decide biological correctness, statistical validity,
or scientific interpretation. It checks structure, compatibility, and basic
usability.

## Setup

Install from PyPI:

```bash
pip install bioartifact
```

From the repository root during development:

```bash
python -m pip install -e .
```

If the active Python environment is externally managed, create a virtual
environment first:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
```

For richer BAM statistics on indexed BAM files:

```bash
pip install "bioartifact[bio]"
```

From a checkout, use `python -m pip install -e ".[bio]"`.

During development without installation, use:

```bash
PYTHONPATH=src python -m bioartifact ...
```

## Output Mode

The CLI emits structured JSON by default for every command. This is intentional:
agents should not need output-format flags, and JSON should not depend on
whether the runner uses pipes, captured subprocesses, or a PTY.

Do not add output-format flags in normal agent workflows. Use `--human` or
`--output human` only when a human-readable view is explicitly requested.

## Core Commands

Inspect one artifact:

```bash
bioartifact inspect path/to/artifact
```

Validate one artifact against a contract:

```bash
bioartifact validate path/to/artifact --contract CONTRACT
```

Validate paired FASTQ files:

```bash
bioartifact validate reads_R1.fastq.gz --contract paired_fastq --mate reads_R2.fastq.gz
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

List available JSON schemas or print one schema:

```bash
bioartifact schema
bioartifact schema artifact_result
```

Validate a workflow manifest:

```bash
bioartifact validate-manifest workflow_manifest.json
```

Use manifest `requires` entries for required companion files, such as BAM or VCF
indexes:

```json
{
  "outputs": [
    {
      "name": "alignment",
      "path": "aligned.bam",
      "type": "bam",
      "contract": "sorted_bam",
      "requires": [{ "name": "bam_index", "suffix": ".bai" }]
    }
  ]
}
```

## Agent Workflow

1. Start with `bioartifact summarize OUTPUT_DIR --recursive` when the
   workflow produced a directory of unknown outputs.
2. Run `bioartifact inspect FILE` on each expected output file.
3. Run `bioartifact validate FILE --contract CONTRACT` for files that
   must satisfy downstream requirements.
4. Use `bioartifact validate-manifest MANIFEST.json` when expected
   outputs and contracts are already declared.
5. Treat non-zero exit codes as validation failures and inspect the JSON
   `errors`, `warnings`, and failed `checks`.
6. Report the JSON evidence or a concise summary of it. Do not hide failures.

## Choosing Contracts

| Need | Contract | Required command shape |
| --- | --- | --- |
| FASTQ is structurally usable | `fastq` | `bioartifact validate reads.fastq.gz --contract fastq` |
| Paired FASTQ files are synchronized | `paired_fastq` | `bioartifact validate R1.fastq.gz --contract paired_fastq --mate R2.fastq.gz` |
| BAM/SAM is declared coordinate sorted | `sorted_bam` | `bioartifact validate aligned.bam --contract sorted_bam` |
| BAM has a nearby `.bai` or `.csi` index | `indexed_bam` | `bioartifact validate aligned.bam --contract indexed_bam` |
| Peak calls satisfy narrowPeak structure | `narrowpeak` | `bioartifact validate peaks.narrowPeak --contract narrowpeak` |
| Differential expression table has required columns and valid p-values | `de_table` | `bioartifact validate de_table.tsv --contract de_table` |
| VCF has required header/records | `valid_vcf` | `bioartifact validate variants.vcf.gz --contract valid_vcf` |

## Reading JSON Output

Inspection output has this shape:

```json
{
  "schema_version": "1.0.0",
  "path": "sample.bam",
  "artifact_type": "bam",
  "valid": true,
  "summary": {},
  "warnings": [],
  "errors": [],
  "usable_as": [],
  "suggested_next_steps": []
}
```

Contract output has this shape:

```json
{
  "schema_version": "1.0.0",
  "contract": "narrowpeak",
  "passed": true,
  "path": "peaks.narrowPeak",
  "artifact_type": "narrowPeak",
  "checks": [
    {
      "name": "coordinates_valid",
      "status": "pass",
      "message": "all genomic coordinates are valid",
      "details": {},
      "remediation": null
    }
  ],
  "warnings": [],
  "errors": []
}
```

For agent decisions:

- `valid: true` means the inspector found no structural errors.
- `passed: true` means all contract checks avoided `fail`.
- `warnings` are limitations or non-fatal issues.
- `errors` are structural failures or unreadable input problems.
- Failed checks contain the most useful reason to route, retry, or stop.
- `remediation` gives an agent-oriented next action when a check fails.

## File-Type Inspection Summary

- FASTQ: checks four-line records, headers, separators, gzip readability, and
  sequence/quality length equality.
- FASTA: checks headers before sequence data and reports sequence counts and
  lengths.
- SAM: parses headers and alignment rows, counts mapped/unmapped reads, and
  detects `SO:coordinate`.
- BAM: parses the BGZF/gzip BAM header, references, sort order, and adjacent
  index files; optional `pysam` adds indexed read statistics.
- VCF: checks metadata/header lines, required columns, sample columns, positive
  positions, and non-empty REF/ALT fields.
- BED: checks tabular interval rows and coordinate validity.
- narrowPeak: checks BED-like coordinates plus required 10-column narrowPeak
  fields.
- GTF/GFF: checks 9-column annotation rows, coordinates, feature counts, and
  common IDs.
- CSV/TSV: checks headers, row/column consistency, missing values, and basic
  table shape.
- HTML: detects basic HTML structure, title, and MultiQC-like reports.

## Reproducible Examples

The repository includes small synthetic fixtures under `tests/fixtures/`.
Use them for smoke tests, examples, and manuscript demonstrations:

```bash
PYTHONPATH=src python -m bioartifact inspect tests/fixtures/variants.vcf.gz
PYTHONPATH=src python -m bioartifact validate tests/fixtures/peaks.narrowPeak --contract narrowpeak
PYTHONPATH=src python -m bioartifact validate tests/fixtures/reads_R1.fastq --contract paired_fastq --mate tests/fixtures/reads_R2.fastq
PYTHONPATH=src python -m bioartifact summarize tests/fixtures --recursive
PYTHONPATH=src python -m bioartifact validate-manifest tests/fixtures/workflow_manifest.pass.json
```

## Failure Handling

If validation fails:

1. Read `errors` and failed `checks`.
2. Confirm the path and artifact type are what the workflow expected.
3. If the artifact type is `unknown`, check the filename extension first.
4. If a compressed file fails, verify gzip/BGZF integrity.
5. If a contract fails but inspection passes, the file may be structurally
   readable but unsuitable for the downstream step.
6. In workflow automation, stop or route to remediation when a required contract
   has `passed: false`.
