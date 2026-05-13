from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .errors import OpenSpecMCPError


def load_schema(schema_name: str, schemas_root: Path | None = None) -> dict[str, Any]:
    root = schemas_root or Path(__file__).resolve().parents[2] / "schemas"
    filename = (
        "scheduled-task.yaml"
        if schema_name == "scheduled_task"
        else "external-action.yaml"
        if schema_name == "external_action"
        else f"{schema_name}.yaml"
    )
    path = root / filename
    if not path.exists():
        raise OpenSpecMCPError(
            "SCHEMA_NOT_FOUND",
            f"Schema not found: {schema_name}",
            {"schema": schema_name},
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise OpenSpecMCPError(
            "SCHEMA_INVALID",
            f"Schema is invalid: {schema_name}",
            {"schema": schema_name},
        )
    return data


_SCHEMA_REQUIRED_FIELDS: dict[str, list[str]] = {
    "scheduled_task": [
        "objective",
        "trigger",
        "preconditions",
        "actions",
        "idempotency",
        "rollback",
        "alerting",
        "acceptance",
    ],
    "external_action": [
        "objective",
        "action",
        "audience",
        "channel",
        "approval",
        "constraints",
        "rollback",
        "acceptance",
    ],
}


def validate_contract_payload(contract_type: str, payload: dict[str, Any]) -> None:
    required = _SCHEMA_REQUIRED_FIELDS.get(contract_type)
    if required is None:
        raise OpenSpecMCPError(
            "UNSUPPORTED_CONTRACT_TYPE",
            f"Contract type is not active in the MVP: {contract_type}",
            {"type": contract_type},
        )

    missing = [field for field in required if field not in payload]
    if missing:
        raise OpenSpecMCPError(
            "SCHEMA_VALIDATION_FAILED",
            f"{contract_type.replace('_', ' ').title()} payload is missing required fields.",
            {"missing": missing},
        )
