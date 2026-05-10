from __future__ import annotations

from collections.abc import Iterable

from bioartifact.models import CheckResult, ContractResult


def result(
    contract_name: str,
    checks: Iterable[CheckResult],
    *,
    path: str | None = None,
    artifact_type: str | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
) -> ContractResult:
    check_list = list(checks)
    return ContractResult(
        contract_name=contract_name,
        passed=all(check.status != "fail" for check in check_list),
        checks=check_list,
        path=path,
        artifact_type=artifact_type,
        warnings=warnings or [],
        errors=errors or [],
    )
