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


_ACTIVE_CONTRACT_TYPES = {"scheduled_task", "external_action", "research"}

_PYTHON_TYPES = {
    "array": list,
    "boolean": bool,
    "integer": int,
    "object": dict,
    "string": str,
}


def validate_contract_payload(contract_type: str, payload: dict[str, Any]) -> None:
    if contract_type not in _ACTIVE_CONTRACT_TYPES:
        raise OpenSpecMCPError(
            "UNSUPPORTED_CONTRACT_TYPE",
            f"Contract type is not active in the MVP: {contract_type}",
            {"type": contract_type},
        )

    schema = load_schema(contract_type)
    missing: list[str] = []
    invalid: list[dict[str, Any]] = []
    _validate_node(schema, payload, path="", missing=missing, invalid=invalid)

    if missing or invalid:
        detail: dict[str, Any] = {}
        if missing:
            detail["missing"] = missing
        if invalid:
            detail["invalid"] = invalid
        raise OpenSpecMCPError(
            "SCHEMA_VALIDATION_FAILED",
            f"{contract_type.replace('_', ' ').title()} payload does not match schema.",
            detail,
        )


def _validate_node(
    schema: dict[str, Any],
    value: Any,
    *,
    path: str,
    missing: list[str],
    invalid: list[dict[str, Any]],
) -> None:
    expected_type = schema.get("type")
    if expected_type in _PYTHON_TYPES and not _matches_type(value, expected_type):
        invalid.append(
            {
                "path": path or "$",
                "expected": expected_type,
                "actual": type(value).__name__,
            }
        )
        return

    enum = schema.get("enum")
    if enum is not None and value not in enum:
        invalid.append({"path": path or "$", "expected": enum, "actual": value})
        return

    if isinstance(value, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_node(
                    item_schema,
                    item,
                    path=_join_path(path, str(index)),
                    missing=missing,
                    invalid=invalid,
                )
        return

    if not isinstance(value, dict):
        return

    required = schema.get("required", [])
    for field in required:
        if field not in value:
            missing.append(_join_path(path, field))

    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return

    for field, child_schema in properties.items():
        if field not in value or not isinstance(child_schema, dict):
            continue
        _validate_node(
            child_schema,
            value[field],
            path=_join_path(path, field),
            missing=missing,
            invalid=invalid,
        )


def _join_path(parent: str, child: str) -> str:
    return f"{parent}.{child}" if parent else child


def _matches_type(value: Any, expected_type: str) -> bool:
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, _PYTHON_TYPES[expected_type])
