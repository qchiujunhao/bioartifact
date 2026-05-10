from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from bioartifact import inspect_artifact, validate_manifest
from bioartifact.cli.main import main

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TtyStringIO(StringIO):
    def isatty(self) -> bool:
        return True


def assert_matches_schema(
    testcase: unittest.TestCase, payload: object, schema: dict, path: str = "$"
) -> None:
    if "enum" in schema:
        testcase.assertIn(payload, schema["enum"], path)

    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        if payload is None and "null" in schema_type:
            return
        non_null_types = [value for value in schema_type if value != "null"]
        testcase.assertTrue(
            any(_matches_type(payload, value) for value in non_null_types),
            f"{path} does not match any allowed type {schema_type}",
        )
    elif isinstance(schema_type, str):
        testcase.assertTrue(_matches_type(payload, schema_type), f"{path} is not {schema_type}")

    if schema_type == "object" or (isinstance(schema_type, list) and "object" in schema_type):
        testcase.assertIsInstance(payload, dict, path)
        payload_dict = payload if isinstance(payload, dict) else {}
        required = set(schema.get("required", []))
        testcase.assertLessEqual(required, set(payload_dict), f"{path} is missing required keys")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            testcase.assertLessEqual(
                set(payload_dict),
                set(properties),
                f"{path} contains keys not declared by the schema",
            )
        for key, value in payload_dict.items():
            if key in properties:
                assert_matches_schema(testcase, value, properties[key], f"{path}.{key}")

    if schema_type == "array" or (isinstance(schema_type, list) and "array" in schema_type):
        testcase.assertIsInstance(payload, list, path)
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(payload if isinstance(payload, list) else []):
                assert_matches_schema(testcase, item, item_schema, f"{path}[{index}]")


def _matches_type(payload: object, schema_type: str) -> bool:
    if schema_type == "null":
        return payload is None
    if schema_type == "string":
        return isinstance(payload, str)
    if schema_type == "boolean":
        return isinstance(payload, bool)
    if schema_type == "integer":
        return isinstance(payload, int) and not isinstance(payload, bool)
    if schema_type == "object":
        return isinstance(payload, dict)
    if schema_type == "array":
        return isinstance(payload, list)
    return True


def run_cli_json(args: list[str]) -> tuple[int, dict]:
    stdout = StringIO()
    with redirect_stdout(stdout):
        code = main(args)
    return code, json.loads(stdout.getvalue())


class CliManifestAndSchemaTests(unittest.TestCase):
    def test_discovery_commands_emit_schema_versioned_json(self) -> None:
        contract_code, contracts_payload = run_cli_json(["contracts"])
        self.assertEqual(contract_code, 0)
        self.assertIn("schema_version", contracts_payload)
        self.assertIn("fastq", {contract["name"] for contract in contracts_payload["contracts"]})

        types_code, types_payload = run_cli_json(["types"])
        self.assertEqual(types_code, 0)
        self.assertIn("schema_version", types_payload)
        self.assertIn(
            "vcf", {artifact_type["name"] for artifact_type in types_payload["artifact_types"]}
        )

    def test_default_output_emits_json_for_non_interactive_stdout(self) -> None:
        code, payload = run_cli_json(["inspect", str(FIXTURES / "variants.vcf")])
        self.assertEqual(code, 0)
        self.assertEqual(payload["artifact_type"], "vcf")

    def test_default_output_emits_json_even_for_interactive_stdout(self) -> None:
        stdout = TtyStringIO()
        with redirect_stdout(stdout):
            code = main(["inspect", str(FIXTURES / "variants.vcf")])

        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["artifact_type"], "vcf")

    def test_human_output_can_be_forced_for_non_interactive_stdout(self) -> None:
        stdout = StringIO()
        with redirect_stdout(stdout):
            code = main(["inspect", str(FIXTURES / "variants.vcf"), "--human"])

        self.assertEqual(code, 0)
        output = stdout.getvalue()
        self.assertIn("artifact_type: vcf", output)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(output)

    def test_json_output_can_be_forced_explicitly(self) -> None:
        stdout = StringIO()
        with redirect_stdout(stdout):
            code = main(["inspect", str(FIXTURES / "variants.vcf"), "--output", "json"])

        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["artifact_type"], "vcf")

    def test_cli_failure_exit_code_and_remediation(self) -> None:
        code, payload = run_cli_json(
            ["validate", str(FIXTURES / "invalid" / "bad.fastq"), "--contract", "fastq"]
        )
        self.assertEqual(code, 1)
        self.assertEqual(payload["schema_version"], "1.0.0")
        failed_checks = [check for check in payload["checks"] if check["status"] == "fail"]
        self.assertTrue(failed_checks)
        self.assertTrue(any(check["remediation"] for check in failed_checks))

    def test_manifest_validation_passes_for_fixture_manifest(self) -> None:
        result = validate_manifest(FIXTURES / "workflow_manifest.pass.json")
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["schema_version"], "1.0.0")
        self.assertEqual(result["summary"], {"expected": 5, "passed": 5, "failed": 0, "missing": 0})

        code, payload = run_cli_json(
            ["validate-manifest", str(FIXTURES / "workflow_manifest.pass.json")]
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["passed"])

    def test_manifest_validation_fails_for_missing_bad_and_wrong_type_outputs(self) -> None:
        result = validate_manifest(FIXTURES / "workflow_manifest.fail.json")
        self.assertFalse(result["passed"])
        self.assertEqual(result["summary"]["expected"], 3)
        self.assertEqual(result["summary"]["failed"], 3)
        self.assertEqual(result["summary"]["missing"], 1)

        errors_by_name = {record["name"]: record["errors"] for record in result["outputs"]}
        self.assertIn("inspection failed", errors_by_name["missing_vcf"])
        self.assertIn("contract failed", errors_by_name["bad_fastq"])
        self.assertIn("artifact type mismatch", errors_by_name["wrong_type"])

    def test_missing_unknown_override_and_malformed_gzip_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            missing = inspect_artifact(root / "missing.fastq")
            self.assertFalse(missing.valid)
            self.assertEqual(missing.to_dict()["schema_version"], "1.0.0")

            unknown_path = root / "notes.md"
            unknown_path.write_text("not an artifact\n", encoding="utf-8")
            unknown = inspect_artifact(unknown_path)
            self.assertFalse(unknown.valid)
            self.assertEqual(unknown.artifact_type, "unknown")

            directory_result = inspect_artifact(root)
            self.assertFalse(directory_result.valid)
            self.assertIn("path is not a file", directory_result.errors)

            override_path = root / "reads.txt"
            override_path.write_text("@r1\nACGT\n+\nFFFF\n", encoding="utf-8")
            overridden = inspect_artifact(override_path, artifact_type="fastq")
            self.assertTrue(overridden.valid)
            self.assertEqual(overridden.artifact_type, "fastq")

            malformed_gzip = root / "bad.fastq.gz"
            malformed_gzip.write_bytes(b"\x1f\x8bnot-a-valid-gzip-stream")
            malformed = inspect_artifact(malformed_gzip)
            self.assertFalse(malformed.valid)
            self.assertTrue(malformed.errors)

    def test_json_payloads_have_schema_required_keys(self) -> None:
        artifact_schema = json.loads((ROOT / "schemas" / "artifact_result.schema.json").read_text())
        contract_schema = json.loads((ROOT / "schemas" / "contract_result.schema.json").read_text())
        manifest_schema = json.loads((ROOT / "schemas" / "manifest_result.schema.json").read_text())

        _, artifact = run_cli_json(["inspect", str(FIXTURES / "variants.vcf")])
        _, contract = run_cli_json(
            ["validate", str(FIXTURES / "peaks.narrowPeak"), "--contract", "narrowpeak"]
        )
        _, manifest = run_cli_json(
            ["validate-manifest", str(FIXTURES / "workflow_manifest.pass.json")]
        )

        assert_matches_schema(self, artifact, artifact_schema)
        assert_matches_schema(self, contract, contract_schema)
        assert_matches_schema(self, manifest, manifest_schema)


if __name__ == "__main__":
    unittest.main()
