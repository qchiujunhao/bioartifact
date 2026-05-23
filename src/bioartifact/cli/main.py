from __future__ import annotations

import argparse
import sys
from typing import Any

from bioartifact.contracts import available_contracts, validate_artifact
from bioartifact.inspectors import inspect_artifact
from bioartifact.json import dumps_json
from bioartifact.manifest import validate_manifest
from bioartifact.metadata import artifact_type_details, contract_details
from bioartifact.schema_registry import available_schema_names, get_schema, schema_details
from bioartifact.summarize import summarize_directory


def _print_payload(payload: dict[str, Any], args: argparse.Namespace) -> None:
    if _should_emit_json(args):
        print(dumps_json(payload))
        return

    for key, value in payload.items():
        if isinstance(value, list):
            print(f"{key}:")
            for item in value:
                print(f"  - {item}")
        elif isinstance(value, dict):
            print(f"{key}:")
            for nested_key, nested_value in value.items():
                print(f"  {nested_key}: {nested_value}")
        else:
            print(f"{key}: {value}")


def _should_emit_json(args: argparse.Namespace) -> bool:
    if getattr(args, "human", False):
        return False
    if getattr(args, "json", False):
        return True
    return getattr(args, "output", "json") != "human"


def _inspect(args: argparse.Namespace) -> int:
    result = inspect_artifact(args.path, artifact_type=args.type)
    _print_payload(result.to_dict(), args)
    return 0 if result.valid else 1


def _validate(args: argparse.Namespace) -> int:
    result = validate_artifact(args.path, args.contract, mate=args.mate)
    _print_payload(result.to_dict(), args)
    return 0 if result.passed else 1


def _summarize(args: argparse.Namespace) -> int:
    result = summarize_directory(args.path, recursive=args.recursive)
    _print_payload(result, args)
    return 0 if result["valid"] else 1


def _contracts(args: argparse.Namespace) -> int:
    _print_payload(contract_details(), args)
    return 0


def _types(args: argparse.Namespace) -> int:
    _print_payload(artifact_type_details(), args)
    return 0


def _validate_manifest(args: argparse.Namespace) -> int:
    result = validate_manifest(args.path, base_dir=args.base_dir)
    _print_payload(result, args)
    return 0 if result["passed"] else 1


def _schema(args: argparse.Namespace) -> int:
    payload = get_schema(args.name) if args.name else schema_details()
    _print_payload(payload, args)
    return 0


def _add_output_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--output",
        choices=["json", "human"],
        default="json",
        help="output mode; defaults to JSON",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit structured JSON output; this is the default"
    )
    parser.add_argument("--human", action="store_true", help="force human-readable output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bioartifact",
        description="Inspect and validate bioinformatics artifacts.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="inspect one artifact")
    inspect_parser.add_argument("path", help="artifact path")
    inspect_parser.add_argument("--type", help="override artifact type detection")
    _add_output_arguments(inspect_parser)
    inspect_parser.set_defaults(func=_inspect)

    validate_parser = subparsers.add_parser("validate", help="validate an artifact contract")
    validate_parser.add_argument("path", help="artifact path")
    validate_parser.add_argument(
        "--contract",
        required=True,
        choices=available_contracts(),
        help="contract name",
    )
    validate_parser.add_argument("--mate", help="mate FASTQ path for paired_fastq")
    _add_output_arguments(validate_parser)
    validate_parser.set_defaults(func=_validate)

    summarize_parser = subparsers.add_parser("summarize", help="summarize a directory")
    summarize_parser.add_argument("path", help="directory path")
    summarize_parser.add_argument("--recursive", action="store_true", help="scan recursively")
    _add_output_arguments(summarize_parser)
    summarize_parser.set_defaults(func=_summarize)

    contracts_parser = subparsers.add_parser("contracts", help="list supported contracts")
    _add_output_arguments(contracts_parser)
    contracts_parser.set_defaults(func=_contracts)

    types_parser = subparsers.add_parser("types", help="list supported artifact types")
    _add_output_arguments(types_parser)
    types_parser.set_defaults(func=_types)

    manifest_parser = subparsers.add_parser(
        "validate-manifest",
        help="validate expected workflow outputs from a JSON or YAML manifest",
    )
    manifest_parser.add_argument("path", help="manifest path")
    manifest_parser.add_argument(
        "--base-dir",
        help="base directory for relative output paths; defaults to the manifest directory",
    )
    _add_output_arguments(manifest_parser)
    manifest_parser.set_defaults(func=_validate_manifest)

    schema_parser = subparsers.add_parser("schema", help="list or print JSON schemas")
    schema_parser.add_argument(
        "name",
        nargs="?",
        choices=available_schema_names(),
        help="schema name to print; omit to list available schemas",
    )
    _add_output_arguments(schema_parser)
    schema_parser.set_defaults(func=_schema)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
