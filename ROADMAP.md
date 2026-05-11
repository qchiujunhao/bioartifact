# Six-Month Roadmap

This roadmap covers the first six months of development for `bioartifact`,
starting from the initial public release.

The goal is to mature `bioartifact` from a useful first release into a reliable
artifact-validation layer for agents, workflow systems, benchmark platforms, and
reproducibility pipelines.

## Guiding Priorities

1. Keep the core lightweight and deterministic.
2. Make JSON outputs stable enough for downstream automation.
3. Validate structure and workflow compatibility, not biological interpretation.
4. Add format support conservatively, with fixtures and tests.
5. Demonstrate real workflow value before pursuing JOSS submission.

## Month 1: Release Stabilization

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
- Create GitHub issues for known follow-up work instead of keeping roadmap
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

## Month 2: Schema And Contract Hardening

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

## Month 3: Format Depth And Optional Integrations

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

## Month 4: Workflow And Agent Use Cases

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

## Month 5: Documentation, Adoption, And API Stability

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

## Month 6: JOSS Readiness

Primary goal: decide whether the project has enough maturity and evidence for
JOSS submission.

Should do:

- Write a clear statement of need.
- Add comparison text covering `pysam`, `samtools`, `bcftools`, FastQC,
  MultiQC, workflow engines, and schema-only validation.
- Add `paper.md` and `paper.bib` using the JOSS template.
- Add `CITATION.cff` with real author metadata.
- Archive a stable release on Zenodo and record the DOI.
- Add any required authorship, contribution, and reproducibility disclosures
  for the target venue.
- Confirm the submitted version matches the archived release.

Can do:

- Submit only after there is public development history, a stable release, and
  evidence of real use.
- Delay JOSS if the project still lacks external usage or a convincing workflow
  case study.

Exit criteria:

- The repository has stable public releases, real examples, clear comparison
  text, and enough usage evidence to support a JOSS submission.

## Cross-Cutting Work

These items should continue throughout the six months:

- Keep tests fast and deterministic.
- Avoid heavy required dependencies.
- Keep fixtures small, documented, and reproducible.
- Prefer explicit limitations over overclaiming.
- Keep CLI JSON deterministic and stable.
- Use patch releases for packaging and documentation fixes.
- Use minor releases for new contracts, schemas, or artifact types.
