# Phase Plan

This phase plan describes the development path for `bioartifact`, starting from
the initial public release and extending into longer-term package maintenance.
The phases are ordered by dependency and maturity rather than fixed calendar
dates.

The goal is to mature `bioartifact` from a useful first release into a reliable
artifact-validation layer for agents, workflow systems, benchmark platforms, and
reproducibility pipelines.

## Guiding Priorities

1. Keep the core lightweight and deterministic.
2. Make JSON outputs stable enough for downstream automation.
3. Validate structure and workflow compatibility, not biological interpretation.
4. Add format support conservatively, with fixtures and tests.
5. Demonstrate real workflow value before expanding the public API.
6. Keep long-term scope broad enough for community use, without making the core
   package heavy.

## Phase 1: Release Stabilization

Primary goal: make the first public release installable, understandable, and
safe to depend on experimentally.

Should do:

- Complete PyPI release publishing through GitHub Actions and PyPI Trusted
  Publishing.
- Confirm `pip install bioartifact` works on a clean environment.
- Add installation smoke tests to CI.
- Confirm GitHub Actions CI passes on the public repository.
- Add GitHub repository metadata: description, topics, license, and release
  notes.
- Review README, `SKILLS.md`, schemas, and CLI help for consistency.
- Create GitHub issues for known follow-up work instead of keeping plan
  items only in prose.
- Publish a small `0.1.1` patch release if first users find packaging or docs
  issues.

Can do:

- Add badges for PyPI, CI, license, and Python versions.
- Add a lightweight `docs/` directory if README starts becoming too long.

Exit criteria:

- Public repo is clean and professional.
- PyPI install works.
- Users can run `bioartifact inspect`, `validate`, `summarize`, `contracts`,
  `types`, and `validate-manifest` from the installed package.

## Phase 2: Schema And Contract Hardening

Primary goal: make outputs dependable for automated systems.

Should do:

- Treat `schema_version` and JSON schemas as part of the public interface.
- Add full JSON Schema validation tests for artifact, contract, summary,
  discovery, and manifest outputs.
- Add schemas for discovery and summary outputs.
- Define a compatibility policy for schema changes.
- Improve manifest validation diagnostics for missing files, wrong types,
  failed contracts, and invalid manifest structure.
- Add contract documentation pages or a generated contract reference.
- Add more negative fixtures for common workflow failures.

Can do:

- Add `bioartifact schema` CLI discovery for schema locations or schema JSON.
- Add machine-readable contract metadata with stable fields such as
  `required_arguments`, `artifact_types`, and `output_schema`.

Exit criteria:

- A workflow engine can pin `schema_version` and validate CLI JSON output.
- Contract behavior is documented enough for external users to rely on it.

## Phase 3: Format Depth And Optional Integrations

Primary goal: improve validation depth without making the base package heavy.

Should do:

- Improve BAM/SAM validation through optional `pysam` support.
- Add focused tests for the `bio` extra when `pysam` is installed.
- Decide how far VCF validation should go in the standard-library core.
- Add optional integration hooks for `samtools` and `bcftools` when installed.
- Add performance safeguards for large files, such as record limits, sampling
  controls, or explicit full-scan modes.
- Document which inspectors scan full files and which inspect headers or
  sampled records.

Can do:

- Add CRAM support through optional `pysam`.
- Evaluate BigWig, BigBed, and H5AD support, but only add them if fixtures and
  stable summaries are clear.

Exit criteria:

- Alignment and variant validation are more useful in real pipelines.
- Large-file behavior is predictable and documented.

## Phase 4: Workflow And Agent Use Cases

Primary goal: prove that `bioartifact` catches real workflow problems that file
existence checks miss.

Should do:

- Add one reproducible mini workflow using existing fixtures.
- Add an example manifest for a realistic sequencing workflow.
- Add examples for Snakemake, Nextflow, or Galaxy-style output validation.
- Add an agent-oriented example showing how JSON output gates downstream steps.
- Record failure cases where `bioartifact` catches malformed artifacts,
  unsatisfied contracts, or wrong output types.
- Add CLI examples that can be copied directly into CI jobs.

Can do:

- Add a small benchmark harness comparing file-existence checks versus
  `bioartifact` contract validation.
- Add a tutorial notebook or Markdown walkthrough.

Exit criteria:

- The project has at least one end-to-end example that demonstrates practical
  value beyond format parsing.

## Phase 5: Documentation, Adoption, And API Stability

Primary goal: make the project easier for external users to evaluate and adopt.

Should do:

- Review public API names and mark unstable interfaces clearly.
- Decide whether to keep the Python API minimal or add documented high-level
  helpers.
- Add documentation for extending inspectors and contracts.
- Add contribution guidelines for new formats and fixtures.
- Open issues labeled `good first issue`, `format-support`, `contract`, and
  `docs`.
- Gather feedback from at least one real workflow, benchmark, or agent
  evaluation use case.
- Prepare a `0.2.0` release if schema or manifest behavior has matured.

Can do:

- Add documentation site generation with MkDocs or Sphinx.
- Add coverage reporting if it helps maintain confidence.

Exit criteria:

- New contributors can understand how to add a format or contract.
- External users can judge stability and limitations quickly.

## Phase 6: Integration And Release Maturity

Primary goal: make `bioartifact` dependable enough for routine use in
automation, benchmarking, and reproducibility workflows.

Should do:

- Add versioned example outputs for each supported command.
- Add a documented compatibility policy for CLI flags, JSON fields, schemas,
  and contracts.
- Add release checklists for patch and minor releases.
- Add integration examples for CI systems and workflow runners.
- Add a small public gallery of passing and failing fixture cases.
- Decide which Python APIs are stable enough to document.
- Prepare a stable minor release after schema, manifest, and contract behavior
  have been exercised in real examples.

Can do:

- Add a documentation site if README and `SKILLS.md` are no longer enough.
- Add optional provenance metadata for workflow outputs.
- Add a small compatibility test suite that downstream projects can reuse.

Exit criteria:

- The repository has stable public releases, clear examples, reliable schemas,
  and enough integration guidance for external workflows to adopt the tool.

## Phase 7: Broader Artifact Coverage

Primary goal: expand the range of bioinformatics artifacts while preserving
clear contracts and small reproducible fixtures.

Should do:

- Add CRAM support through optional `pysam` integration.
- Add BigWig and BigBed inspection through optional dependencies.
- Add H5AD inspection for single-cell workflows with careful summary limits.
- Add domain-specific table profiles for common RNA-seq, ChIP-seq, ATAC-seq,
  and metagenomics outputs.
- Add MultiQC data-table extraction when structured files are available.
- Define what each new artifact type can and cannot validate.
- Require fixtures, negative examples, and schema coverage for every new format.

Can do:

- Evaluate mzML, mzIdentML, and proteomics table support.
- Evaluate RO-Crate metadata inspection if it helps workflow bundles.
- Add a formal proposal template for new artifact types.

Exit criteria:

- New format support is useful beyond extension detection.
- Optional integrations do not increase the default installation weight.

## Phase 8: Extension Architecture

Primary goal: let users add inspectors and contracts without modifying
`bioartifact` itself.

Should do:

- Design a stable plugin interface for third-party inspectors and contracts.
- Support Python entry points for external artifact types.
- Add a documented contract authoring guide.
- Add validation tests for third-party plugin registration.
- Add clear error messages when optional plugins are missing or incompatible.
- Keep the built-in registry deterministic and inspectable from the CLI.

Can do:

- Add `bioartifact plugin` discovery commands.
- Add template repositories for new inspector packages.
- Add compatibility tests that plugin authors can vendor or run in CI.

Exit criteria:

- External projects can maintain their own format support cleanly.
- The core package remains small while the ecosystem can grow.

## Phase 9: Workflow Ecosystem Integrations

Primary goal: make `bioartifact` easy to use from workflow systems, CI, and
benchmark platforms.

Should do:

- Add examples for Snakemake, Nextflow, CWL, WDL, and Galaxy-style validation.
- Add GitHub Actions examples for validating workflow outputs in CI.
- Add manifest examples for single-sample and multi-sample workflows.
- Add failure-mode examples that show how contracts prevent bad downstream
  steps.
- Document recommended exit-code handling for automation.
- Add compact JSON examples suitable for dashboards and benchmark logs.

Can do:

- Add reusable action or container images if demand appears.
- Add example benchmark tasks that compare expected and observed artifacts.
- Add integration notes for workflow provenance systems.

Exit criteria:

- A workflow author can adopt `bioartifact` without writing custom glue code.
- Benchmark systems can consume results directly as structured JSON.

## Phase 10: Performance, Scale, And Robustness

Primary goal: handle realistic file sizes predictably without sacrificing
determinism.

Should do:

- Define scan modes such as header-only, sampled, bounded, and full validation.
- Add explicit record and byte limits where full scans are expensive.
- Add streaming implementations for text formats where practical.
- Add memory and runtime tests for larger synthetic fixtures.
- Add regression tests for truncated gzip files, malformed records, empty files,
  and mixed-delimiter tables.
- Document performance behavior for each inspector.

Can do:

- Add optional parallel directory summarization.
- Add profiling benchmarks for common artifact types.
- Add cacheable file fingerprints for repeated validations.

Exit criteria:

- Large-file behavior is documented, bounded, and testable.
- Users can choose stronger validation intentionally when runtime cost matters.

## Phase 11: Provenance And Artifact Bundles

Primary goal: move from single-file inspection toward validating coherent
workflow output sets.

Should do:

- Extend manifests to support grouped artifacts, expected relationships, and
  required companion files.
- Add checksum and size metadata for reproducibility records.
- Add paired-output checks for common workflow products, such as BAM plus index,
  VCF plus index, peaks plus summits, and count matrix plus metadata.
- Add bundle summaries that describe a complete workflow output directory.
- Add machine-readable warnings for missing provenance or ambiguous artifacts.

Can do:

- Add lightweight provenance fields without depending on a workflow engine.
- Evaluate compatibility with RO-Crate or other research-object metadata.
- Add export examples for reproducibility reports.

Exit criteria:

- `bioartifact` can validate not only individual files, but also whether an
  output directory is coherent and usable.

## Phase 12: Governance, Sustainability, And Community

Primary goal: keep the project maintainable as scope and usage grow.

Should do:

- Define a release cadence and support policy.
- Add deprecation rules for CLI flags, contracts, and JSON fields.
- Maintain issue labels for formats, contracts, docs, bugs, and integrations.
- Add security and support guidance appropriate for a validation tool.
- Track user-requested formats and contracts in public issues.
- Keep examples, schemas, and fixture provenance synchronized with releases.
- Add contributor guidance for review expectations and test requirements.

Can do:

- Add a lightweight steering document if multiple contributors become active.
- Add published case studies after real workflows adopt the package.
- Add citation metadata and archival releases when the package reaches stable
  use.

Exit criteria:

- The project has a clear maintenance model, predictable releases, and a path
  for outside contributors to add meaningful support safely.

## Cross-Cutting Work

These items should continue throughout all phases:

- Keep tests fast and deterministic.
- Avoid heavy required dependencies.
- Keep fixtures small, documented, and reproducible.
- Prefer explicit limitations over overclaiming.
- Keep CLI JSON deterministic and stable.
- Use patch releases for packaging and documentation fixes.
- Use minor releases for new contracts, schemas, or artifact types.
