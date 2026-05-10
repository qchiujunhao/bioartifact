from __future__ import annotations

import csv
from pathlib import Path

from bioartifact.contracts.common import result
from bioartifact.inspectors.tables import inspect_table
from bioartifact.io import open_text, strip_newline
from bioartifact.models import ContractResult, failed, passed

REQUIRED_DE_COLUMNS = ["gene", "log2FoldChange", "pvalue", "padj"]


def _delimiter_for(path: Path) -> str:
    return "," if path.suffix.lower() == ".csv" else "\t"


def validate_de_table(path: Path, **_: object) -> ContractResult:
    artifact_type = "csv" if path.suffix.lower() == ".csv" else "tsv"
    artifact = inspect_table(path, artifact_type=artifact_type)
    checks = [
        passed("readable", "table is readable")
        if artifact.valid
        else failed(
            "readable",
            "table is invalid",
            remediation="Repair the delimiter/header structure or regenerate the table.",
            errors=artifact.errors,
        ),
    ]

    columns = list(artifact.summary.get("columns", []))
    missing = [column for column in REQUIRED_DE_COLUMNS if column not in columns]
    if missing:
        checks.append(
            failed(
                "required_columns",
                "differential expression table is missing required columns",
                remediation="Include gene, log2FoldChange, pvalue, and padj columns with exact names.",
                missing=missing,
                required=REQUIRED_DE_COLUMNS,
            )
        )
    else:
        checks.append(passed("required_columns", "all required DE columns are present"))

    if not missing and artifact.valid:
        delimiter = _delimiter_for(path)
        gene_seen: set[str] = set()
        duplicate_genes: set[str] = set()
        pvalue_errors = 0
        padj_errors = 0
        empty_genes = 0

        with open_text(path) as handle:
            reader = csv.DictReader((strip_newline(line) for line in handle), delimiter=delimiter)
            for row in reader:
                gene = row.get("gene", "")
                if not gene:
                    empty_genes += 1
                elif gene in gene_seen:
                    duplicate_genes.add(gene)
                else:
                    gene_seen.add(gene)

                for column_name in ("pvalue", "padj"):
                    value = row.get(column_name, "")
                    try:
                        parsed = float(value)
                    except ValueError:
                        if column_name == "pvalue":
                            pvalue_errors += 1
                        else:
                            padj_errors += 1
                        continue
                    if parsed < 0 or parsed > 1:
                        if column_name == "pvalue":
                            pvalue_errors += 1
                        else:
                            padj_errors += 1

        if pvalue_errors:
            checks.append(
                failed(
                    "pvalue_range",
                    "pvalue contains non-numeric or out-of-range values",
                    remediation="Ensure pvalue entries are numeric values between 0 and 1.",
                    count=pvalue_errors,
                )
            )
        else:
            checks.append(passed("pvalue_range", "all pvalue entries are within [0, 1]"))

        if padj_errors:
            checks.append(
                failed(
                    "padj_range",
                    "padj contains non-numeric or out-of-range values",
                    remediation="Ensure adjusted p-values are numeric values between 0 and 1.",
                    count=padj_errors,
                )
            )
        else:
            checks.append(passed("padj_range", "all padj entries are within [0, 1]"))

        if empty_genes:
            checks.append(
                failed(
                    "gene_values",
                    "one or more rows have empty gene values",
                    remediation="Populate the gene identifier column before downstream analysis.",
                    count=empty_genes,
                )
            )
        elif duplicate_genes:
            checks.append(
                failed(
                    "unique_genes",
                    "duplicate gene values were found",
                    remediation="Collapse duplicate genes or use a unique feature identifier column.",
                    examples=sorted(duplicate_genes)[:10],
                )
            )
        else:
            checks.append(passed("unique_genes", "gene values are present and unique"))

    return result(
        "de_table",
        checks,
        path=str(path),
        artifact_type=artifact.artifact_type,
        warnings=artifact.warnings,
        errors=artifact.errors,
    )
