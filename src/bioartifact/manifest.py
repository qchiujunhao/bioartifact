from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bioartifact.contracts import validate_artifact
from bioartifact.inspectors import inspect_artifact
from bioartifact.models import SCHEMA_VERSION


def _resolve_path(value: str | Path, base_dir: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base_dir / path


def _resolve_contract_args(raw_args: Any, base_dir: Path, entry: dict[str, Any]) -> dict[str, Any]:
    contract_args = dict(raw_args) if isinstance(raw_args, dict) else {}
    if "mate" in entry:
        contract_args["mate"] = _resolve_path(str(entry["mate"]), base_dir)
    elif "mate" in contract_args:
        contract_args["mate"] = _resolve_path(str(contract_args["mate"]), base_dir)
    return contract_args


def _load_manifest(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"could not read manifest: {exc}"]

    try:
        if path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore[import-not-found]
            except ImportError:
                return None, [
                    "YAML manifest support requires PyYAML; use JSON or install the optional YAML dependency"
                ]
            payload = yaml.safe_load(text)
        else:
            payload = json.loads(text)
    except Exception as exc:
        return None, [f"could not parse manifest: {exc}"]

    if not isinstance(payload, dict):
        return None, ["manifest root must be an object"]
    return payload, []


def validate_manifest(path: str | Path, *, base_dir: str | Path | None = None) -> dict[str, Any]:
    """Validate expected workflow outputs declared in a JSON or YAML manifest."""

    manifest_path = Path(path)
    resolved_base = Path(base_dir) if base_dir is not None else manifest_path.parent
    resolved_base = resolved_base.resolve()

    manifest, load_errors = _load_manifest(manifest_path)
    if manifest is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "manifest": str(manifest_path),
            "base_dir": str(resolved_base),
            "passed": False,
            "summary": {
                "expected": 0,
                "passed": 0,
                "failed": 0,
                "missing": 0,
            },
            "outputs": [],
            "errors": load_errors,
        }

    outputs = manifest.get("outputs")
    if not isinstance(outputs, list):
        return {
            "schema_version": SCHEMA_VERSION,
            "manifest": str(manifest_path),
            "base_dir": str(resolved_base),
            "passed": False,
            "summary": {
                "expected": 0,
                "passed": 0,
                "failed": 0,
                "missing": 0,
            },
            "outputs": [],
            "errors": ["manifest must contain an `outputs` array"],
        }

    records: list[dict[str, Any]] = []
    missing = 0
    passed_count = 0

    for index, entry in enumerate(outputs, start=1):
        if not isinstance(entry, dict):
            records.append(
                {
                    "name": f"output_{index}",
                    "path": None,
                    "expected_type": None,
                    "passed": False,
                    "inspection": None,
                    "type_check": {
                        "passed": False,
                        "message": "manifest output entry must be an object",
                    },
                    "contract": None,
                    "requirements": [],
                    "errors": ["manifest output entry must be an object"],
                }
            )
            continue

        raw_path = entry.get("path")
        name = str(entry.get("name") or raw_path or f"output_{index}")
        expected_type = entry.get("type") or entry.get("artifact_type")
        contract_name = entry.get("contract")

        if not raw_path:
            records.append(
                {
                    "name": name,
                    "path": None,
                    "expected_type": expected_type,
                    "passed": False,
                    "inspection": None,
                    "type_check": {
                        "passed": False,
                        "message": "manifest output is missing `path`",
                    },
                    "contract": None,
                    "requirements": [],
                    "errors": ["manifest output is missing `path`"],
                }
            )
            continue

        artifact_path = _resolve_path(str(raw_path), resolved_base)
        inspection = inspect_artifact(artifact_path)
        if not artifact_path.exists():
            missing += 1

        type_passed = expected_type is None or inspection.artifact_type == expected_type
        if type_passed:
            type_message = "artifact type matches manifest expectation"
        else:
            type_message = (
                f"expected artifact type {expected_type!r}, detected {inspection.artifact_type!r}"
            )

        contract_payload = None
        contract_passed = True
        contract_args = _resolve_contract_args(entry.get("contract_args"), resolved_base, entry)

        if contract_name:
            contract_result = validate_artifact(artifact_path, str(contract_name), **contract_args)
            contract_payload = contract_result.to_dict()
            contract_passed = contract_result.passed

        requirements = _validate_requirements(entry.get("requires"), artifact_path, resolved_base)
        requirements_passed = all(requirement["passed"] for requirement in requirements)

        output_passed = inspection.valid and type_passed and contract_passed and requirements_passed
        if output_passed:
            passed_count += 1

        records.append(
            {
                "name": name,
                "path": str(artifact_path),
                "expected_type": expected_type,
                "passed": output_passed,
                "inspection": inspection.to_dict(),
                "type_check": {
                    "passed": type_passed,
                    "message": type_message,
                },
                "contract": contract_payload,
                "requirements": requirements,
                "errors": []
                if output_passed
                else _manifest_record_errors(
                    inspection_valid=inspection.valid,
                    type_passed=type_passed,
                    contract_passed=contract_passed,
                    requirements_passed=requirements_passed,
                ),
            }
        )

    failed_count = len(records) - passed_count
    return {
        "schema_version": SCHEMA_VERSION,
        "manifest": str(manifest_path),
        "base_dir": str(resolved_base),
        "passed": failed_count == 0,
        "summary": {
            "expected": len(records),
            "passed": passed_count,
            "failed": failed_count,
            "missing": missing,
        },
        "outputs": records,
        "errors": [],
    }


def _manifest_record_errors(
    *,
    inspection_valid: bool,
    type_passed: bool,
    contract_passed: bool,
    requirements_passed: bool,
) -> list[str]:
    errors = []
    if not inspection_valid:
        errors.append("inspection failed")
    if not type_passed:
        errors.append("artifact type mismatch")
    if not contract_passed:
        errors.append("contract failed")
    if not requirements_passed:
        errors.append("requirement failed")
    return errors


def _validate_requirements(
    raw_requirements: Any,
    artifact_path: Path,
    base_dir: Path,
) -> list[dict[str, Any]]:
    if raw_requirements is None:
        return []
    if isinstance(raw_requirements, (str, dict)):
        requirement_entries = [raw_requirements]
    elif isinstance(raw_requirements, list):
        requirement_entries = raw_requirements
    else:
        return [
            {
                "name": "requires",
                "path": None,
                "expected_type": None,
                "passed": False,
                "exists": False,
                "inspection": None,
                "type_check": None,
                "contract": None,
                "errors": ["manifest `requires` field must be a string, object, or array"],
            }
        ]

    records = []
    for index, requirement in enumerate(requirement_entries, start=1):
        records.append(_validate_requirement(requirement, index, artifact_path, base_dir))
    return records


def _validate_requirement(
    requirement: Any,
    index: int,
    artifact_path: Path,
    base_dir: Path,
) -> dict[str, Any]:
    if isinstance(requirement, str):
        raw_path = requirement
        name = requirement
        expected_type = None
        contract_name = None
        contract_args: dict[str, Any] = {}
    elif isinstance(requirement, dict):
        raw_path = requirement.get("path")
        suffix = requirement.get("suffix")
        name = str(requirement.get("name") or raw_path or suffix or f"requirement_{index}")
        expected_type = requirement.get("type") or requirement.get("artifact_type")
        contract_name = requirement.get("contract")
        contract_args = _resolve_contract_args(
            requirement.get("contract_args"), base_dir, requirement
        )

        if raw_path is None and suffix is not None:
            raw_path = f"{artifact_path}{suffix}"
    else:
        return {
            "name": f"requirement_{index}",
            "path": None,
            "expected_type": None,
            "passed": False,
            "exists": False,
            "inspection": None,
            "type_check": None,
            "contract": None,
            "errors": ["manifest requirement entry must be a string or object"],
        }

    if not raw_path:
        return {
            "name": name,
            "path": None,
            "expected_type": expected_type,
            "passed": False,
            "exists": False,
            "inspection": None,
            "type_check": None,
            "contract": None,
            "errors": ["manifest requirement is missing `path` or `suffix`"],
        }

    requirement_path = _resolve_path(str(raw_path), base_dir)
    exists = requirement_path.exists()
    if not exists:
        return {
            "name": name,
            "path": str(requirement_path),
            "expected_type": expected_type,
            "passed": False,
            "exists": False,
            "inspection": None,
            "type_check": None,
            "contract": None,
            "errors": ["required file missing"],
        }

    inspection_payload = None
    type_check = None
    type_passed = True
    if expected_type is not None or contract_name:
        inspection = inspect_artifact(requirement_path)
        inspection_payload = inspection.to_dict()
        type_passed = expected_type is None or inspection.artifact_type == expected_type
        if expected_type is not None:
            type_check = {
                "passed": type_passed,
                "message": "required artifact type matches manifest expectation"
                if type_passed
                else f"expected artifact type {expected_type!r}, detected {inspection.artifact_type!r}",
            }
    contract_payload = None
    contract_passed = True
    if contract_name:
        contract_result = validate_artifact(requirement_path, str(contract_name), **contract_args)
        contract_payload = contract_result.to_dict()
        contract_passed = contract_result.passed

    passed = exists and type_passed and contract_passed
    errors = []
    if not type_passed:
        errors.append("artifact type mismatch")
    if not contract_passed:
        errors.append("contract failed")

    return {
        "name": name,
        "path": str(requirement_path),
        "expected_type": expected_type,
        "passed": passed,
        "exists": True,
        "inspection": inspection_payload,
        "type_check": type_check,
        "contract": contract_payload,
        "errors": errors,
    }
