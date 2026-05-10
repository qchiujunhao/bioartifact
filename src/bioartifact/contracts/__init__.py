from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from bioartifact.contracts.alignment import validate_indexed_bam, validate_sorted_bam
from bioartifact.contracts.fastq import validate_fastq, validate_paired_fastq
from bioartifact.contracts.intervals import validate_narrowpeak
from bioartifact.contracts.tables import validate_de_table
from bioartifact.contracts.vcf import validate_valid_vcf
from bioartifact.models import ContractResult, failed

ContractValidator = Callable[..., ContractResult]

CONTRACTS: dict[str, ContractValidator] = {
    "de_table": validate_de_table,
    "fastq": validate_fastq,
    "indexed_bam": validate_indexed_bam,
    "narrowpeak": validate_narrowpeak,
    "paired_fastq": validate_paired_fastq,
    "sorted_bam": validate_sorted_bam,
    "valid_vcf": validate_valid_vcf,
}


def available_contracts() -> list[str]:
    """Return supported contract names."""

    return sorted(CONTRACTS)


def validate_artifact(path: str | Path, contract_name: str, **kwargs: Any) -> ContractResult:
    """Validate one artifact against a named contract."""

    validator = CONTRACTS.get(contract_name)
    if validator is None:
        return ContractResult(
            contract_name=contract_name,
            passed=False,
            path=str(path),
            checks=[
                failed(
                    "known_contract",
                    f"unknown contract '{contract_name}'",
                    remediation="Run `bioartifact contracts` and choose one of the listed contract names.",
                    available_contracts=available_contracts(),
                )
            ],
            errors=[f"unknown contract '{contract_name}'"],
        )
    return validator(Path(path), **kwargs)
