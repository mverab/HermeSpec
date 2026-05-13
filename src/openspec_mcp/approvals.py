from __future__ import annotations

import json
import os
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import OpenSpecMCPError
from .models import ApprovalEvent


def _acquire_lock(
    lock_path: Path, max_retries: int = 5, base_delay: float = 0.05
) -> None:
    """Acquire a lockfile using atomic O_CREAT|O_EXCL with exponential backoff."""
    for attempt in range(max_retries):
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL)
            os.close(fd)
            return
        except FileExistsError:
            if attempt == max_retries - 1:
                raise OpenSpecMCPError(
                    "LOCK_TIMEOUT",
                    f"Could not acquire lock after {max_retries} attempts: {lock_path}",
                    {"lock_path": str(lock_path)},
                )
            delay = base_delay * (2**attempt) + random.random() * 0.01
            time.sleep(delay)


def _release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _index_path(approvals_file: Path) -> Path:
    return approvals_file.with_suffix(".jsonl.index.json")


def _load_index(index_path: Path) -> dict[str, Any]:
    if not index_path.exists():
        return {}
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _save_index(index_path: Path, data: dict[str, Any]) -> None:
    index_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _scan_jsonl_for_change_id(
    approvals_file: Path, change_id: str
) -> list[ApprovalEvent]:
    events: list[ApprovalEvent] = []
    if not approvals_file.exists():
        return events
    with approvals_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                if raw.get("change_id") == change_id:
                    events.append(ApprovalEvent(**raw))
            except (json.JSONDecodeError, TypeError):
                continue
    return events


def append_event(
    approvals_file: Path,
    event: ApprovalEvent,
    max_retries: int = 5,
    base_delay: float = 0.05,
) -> None:
    lock_path = approvals_file.with_suffix(".jsonl.lock")
    _acquire_lock(lock_path, max_retries=max_retries, base_delay=base_delay)
    try:
        approvals_file.parent.mkdir(parents=True, exist_ok=True)

        offset = approvals_file.stat().st_size if approvals_file.exists() else 0
        with approvals_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.__dict__, separators=(",", ":")) + "\n")
            f.flush()

        index_path = _index_path(approvals_file)
        index = _load_index(index_path)
        previous = index.get(event.change_id)
        history_count = 1
        if isinstance(previous, dict) and isinstance(
            previous.get("history_count"), int
        ):
            history_count = previous["history_count"] + 1
        index[event.change_id] = {
            "offset": offset,
            "event": event.__dict__,
            "history_count": history_count,
        }
        _save_index(index_path, index)
    finally:
        _release_lock(lock_path)


def get_history(approvals_file: Path, change_id: str) -> list[ApprovalEvent]:
    return _scan_jsonl_for_change_id(approvals_file, change_id)


def get_latest_status(
    approvals_file: Path,
    change_id: str,
) -> dict[str, Any] | None:
    index_path = _index_path(approvals_file)
    index = _load_index(index_path)

    entry = index.get(change_id)
    if entry and isinstance(entry.get("event"), dict):
        event = ApprovalEvent(**entry["event"])
        history_count = entry.get("history_count")
        if not isinstance(history_count, int):
            history_count = len(_scan_jsonl_for_change_id(approvals_file, change_id))
        return {
            "status": event.type,
            "latest_event": event,
            "history_count": history_count,
        }

    events = _scan_jsonl_for_change_id(approvals_file, change_id)
    if not events:
        return None

    latest = events[-1]
    return {
        "status": latest.type,
        "latest_event": latest,
        "history_count": len(events),
    }


def build_approval_event(
    change_id: str,
    actor: str,
    channel: str,
    scope: str,
    constraints: dict[str, Any] | None = None,
    expiration: str | None = None,
) -> ApprovalEvent:
    missing = []
    if not actor:
        missing.append("actor")
    if not channel:
        missing.append("channel")
    if not scope:
        missing.append("scope")
    if missing:
        raise OpenSpecMCPError(
            "MISSING_APPROVER",
            f"Approval request is missing required metadata: {', '.join(missing)}.",
            {"missing": missing},
        )

    return ApprovalEvent(
        event_id=str(uuid.uuid4()),
        change_id=change_id,
        type="approval",
        actor=actor,
        channel=channel,
        timestamp=_now_iso(),
        scope=scope,
        constraints=constraints,
        expiration=expiration,
        reason=None,
    )


def build_rejection_event(
    change_id: str,
    actor: str,
    channel: str,
    reason: str,
) -> ApprovalEvent:
    missing = []
    if not actor:
        missing.append("actor")
    if not channel:
        missing.append("channel")
    if not reason:
        missing.append("reason")
    if missing:
        raise OpenSpecMCPError(
            "MISSING_REJECTION_METADATA",
            f"Rejection request is missing required metadata: {', '.join(missing)}.",
            {"missing": missing},
        )

    return ApprovalEvent(
        event_id=str(uuid.uuid4()),
        change_id=change_id,
        type="rejection",
        actor=actor,
        channel=channel,
        timestamp=_now_iso(),
        scope=None,
        constraints=None,
        expiration=None,
        reason=reason,
    )
