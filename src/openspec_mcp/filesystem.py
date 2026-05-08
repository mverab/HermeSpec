from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .errors import OpenSpecMCPError
from .models import ChangeArtifacts, ChangeSummary, SpecArtifact

CHANGE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_change_id(change_id: str) -> str:
    if not CHANGE_ID_PATTERN.fullmatch(change_id):
        raise OpenSpecMCPError(
            "INVALID_CHANGE_ID",
            "Change ID must be kebab-case using lowercase letters, numbers, and single hyphens.",
            {"change_id": change_id},
        )
    return change_id


@dataclass(frozen=True)
class OpenSpecWorkspace:
    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", self.root.expanduser().resolve())

    @property
    def changes_dir(self) -> Path:
        return self.root / "openspec" / "changes"

    @property
    def archive_dir(self) -> Path:
        return self.root / "openspec" / "archive"

    def _ensure_inside_root(self, path: Path) -> Path:
        resolved = path.resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError as exc:
            raise OpenSpecMCPError(
                "PATH_TRAVERSAL",
                "Resolved path escapes the configured OpenSpec workspace.",
                {"path": str(path), "workspace": str(self.root)},
            ) from exc
        return resolved

    def change_path(self, change_id: str) -> Path:
        valid_id = validate_change_id(change_id)
        return self._ensure_inside_root(self.changes_dir / valid_id)

    def create_change(self, change_id: str) -> Path:
        path = self.change_path(change_id)
        if path.exists():
            raise OpenSpecMCPError(
                "CHANGE_EXISTS",
                f"Change already exists: {change_id}",
                {"change_id": change_id, "path": str(path)},
            )
        path.mkdir(parents=True)
        return path

    def list_changes(self) -> list[ChangeSummary]:
        if not self.changes_dir.exists():
            return []

        summaries: list[ChangeSummary] = []
        for path in sorted(self.changes_dir.iterdir()):
            if not path.is_dir() or path.name == "archive":
                continue
            validate_change_id(path.name)
            summaries.append(
                ChangeSummary(
                    change_id=path.name,
                    status="proposed",
                    path=str(path),
                    approval_required=True,
                )
            )
        return summaries

    def read_change(self, change_id: str) -> ChangeArtifacts:
        path = self.change_path(change_id)
        if not path.exists():
            raise OpenSpecMCPError(
                "NOT_FOUND", f"Change not found: {change_id}", {"change_id": change_id}
            )

        specs: list[SpecArtifact] = []
        specs_dir = path / "specs"
        if specs_dir.exists():
            for spec_path in sorted(specs_dir.glob("**/*.md")):
                safe_spec = self._ensure_inside_root(spec_path)
                specs.append(
                    SpecArtifact(
                        path=str(safe_spec),
                        content=safe_spec.read_text(encoding="utf-8"),
                    )
                )

        return ChangeArtifacts(
            change_id=change_id,
            status="proposed",
            path=str(path),
            proposal=self._read_optional(path / "proposal.md"),
            tasks=self._read_optional(path / "tasks.md"),
            specs=specs,
            approval=None,
        )

    def archive_path(self, change_id: str, date: str) -> Path:
        valid_id = validate_change_id(change_id)
        return self._ensure_inside_root(self.archive_dir / date / valid_id)

    def _read_optional(self, path: Path) -> str:
        safe_path = self._ensure_inside_root(path)
        if not safe_path.exists():
            return ""
        return safe_path.read_text(encoding="utf-8")

    def archive_change(self, change_id: str, actor: str) -> Path:
        source = self.change_path(change_id)
        if not source.exists():
            raise OpenSpecMCPError(
                "NOT_FOUND", f"Change not found: {change_id}", {"change_id": change_id}
            )

        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        dest = self.archive_path(change_id, date)
        if dest.exists():
            raise OpenSpecMCPError(
                "ARCHIVE_EXISTS",
                f"Change is already archived for {date}: {change_id}",
                {"change_id": change_id, "archive_path": str(dest)},
            )

        dest.mkdir(parents=True)
        for item in source.iterdir():
            shutil.move(str(item), str(dest / item.name))
        source.rmdir()

        record = {
            "change_id": change_id,
            "actor": actor,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "original_path": str(source),
            "archive_path": str(dest),
        }
        (dest / "archive.record").write_text(
            json.dumps(record, indent=2), encoding="utf-8"
        )

        return dest
