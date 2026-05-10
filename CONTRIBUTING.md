# Contributing

`bioartifact` is early-stage software. Contributions should preserve the core
scope: lightweight, deterministic, machine-readable inspection and validation of
bioinformatics artifacts.

## Development Setup

Create an isolated environment and install the package:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

On systems where Python is not externally managed, `python -m pip install -e
".[dev]"` is also sufficient.

## Checks

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

Run linting:

```bash
ruff check .
```

Run formatting before submitting broad edits:

```bash
ruff format .
```

## Adding Inspectors

When adding an artifact type:

1. Add conservative extension detection.
2. Add an independent inspector module.
3. Return an `ArtifactResult` with deterministic summary fields.
4. Avoid heavy runtime dependencies unless they are optional extras.
5. Add valid and invalid fixtures when practical.
6. Add unit tests and CLI examples.

Inspectors should validate structure and compatibility, not scientific
interpretation.

## Adding Contracts

When adding a contract:

1. Add a named validator under `src/bioartifact/contracts/`.
2. Register it in the contract registry.
3. Emit named `CheckResult` entries with useful messages and remediation hints.
4. Add a fixture-backed passing test and at least one failing test.
5. Document the contract in the README and `SKILLS.md`.

## Pull Request Guidance

Keep pull requests focused. Include the command output for tests and linting in
the PR description. For behavior changes, include before/after JSON examples.

