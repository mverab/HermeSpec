from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    workspace: Path
    openspec_bin: str
    telemetry: bool
    approvals_file: Path


def _truthy(value: str | None) -> bool:
    return value in {"1", "true", "TRUE", "yes", "YES", "on", "ON"}


def load_config() -> Config:
    workspace = Path(os.environ.get("OPENSPEC_WORKSPACE", ".")).expanduser().resolve()
    openspec_bin = os.environ.get("OPENSPEC_BIN", "openspec")
    approvals_setting = os.environ.get("OPENSPEC_AGENT_CONTRACTS_APPROVALS_FILE", "openspec/approvals.jsonl")
    approvals_path = Path(approvals_setting).expanduser()
    if not approvals_path.is_absolute():
        approvals_path = workspace / approvals_path

    return Config(
        workspace=workspace,
        openspec_bin=openspec_bin,
        telemetry=_truthy(os.environ.get("OPENSPEC_TELEMETRY", "0")),
        approvals_file=approvals_path,
    )
