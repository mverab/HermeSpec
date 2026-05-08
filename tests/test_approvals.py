import json
import threading

import pytest

from openspec_mcp.approvals import (
    _acquire_lock,
    _release_lock,
    append_event,
    build_approval_event,
    build_rejection_event,
    get_history,
    get_latest_status,
)
from openspec_mcp.errors import OpenSpecMCPError


def test_build_approval_event_requires_actor_channel_scope():
    with pytest.raises(OpenSpecMCPError) as exc:
        build_approval_event("audit", actor="", channel="cli", scope="execute")
    assert exc.value.code == "MISSING_APPROVER"
    assert "actor" in exc.value.detail["missing"]

    with pytest.raises(OpenSpecMCPError) as exc:
        build_approval_event("audit", actor="user", channel="", scope="execute")
    assert "channel" in exc.value.detail["missing"]

    with pytest.raises(OpenSpecMCPError) as exc:
        build_approval_event("audit", actor="user", channel="cli", scope="")
    assert "scope" in exc.value.detail["missing"]


def test_build_rejection_event_requires_actor_channel_reason():
    with pytest.raises(OpenSpecMCPError) as exc:
        build_rejection_event("audit", actor="", channel="cli", reason="no")
    assert exc.value.code == "MISSING_REJECTION_METADATA"
    assert "actor" in exc.value.detail["missing"]

    with pytest.raises(OpenSpecMCPError) as exc:
        build_rejection_event("audit", actor="user", channel="", reason="no")
    assert "channel" in exc.value.detail["missing"]

    with pytest.raises(OpenSpecMCPError) as exc:
        build_rejection_event("audit", actor="user", channel="cli", reason="")
    assert "reason" in exc.value.detail["missing"]


def test_append_event_creates_jsonl_and_index(tmp_path):
    approvals_file = tmp_path / "approvals.jsonl"
    event = build_approval_event(
        "audit-saas",
        actor="user@example.com",
        channel="cli",
        scope="execute",
        constraints={"max_cost_usd": 50},
    )
    append_event(approvals_file, event)

    assert approvals_file.exists()
    lines = approvals_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["change_id"] == "audit-saas"
    assert parsed["type"] == "approval"

    index_path = approvals_file.with_suffix(".jsonl.index.json")
    assert index_path.exists()
    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert "audit-saas" in index
    assert index["audit-saas"]["event"]["scope"] == "execute"


def test_approve_reject_updates_status(tmp_path):
    approvals_file = tmp_path / "approvals.jsonl"

    approve_event = build_approval_event("audit", actor="a", channel="cli", scope="run")
    append_event(approvals_file, approve_event)

    status = get_latest_status(approvals_file, "audit")
    assert status is not None
    assert status["status"] == "approval"

    reject_event = build_rejection_event(
        "audit", actor="a", channel="cli", reason="nope"
    )
    append_event(approvals_file, reject_event)

    status = get_latest_status(approvals_file, "audit")
    assert status["status"] == "rejection"


def test_get_history_returns_all_events(tmp_path):
    approvals_file = tmp_path / "approvals.jsonl"
    append_event(
        approvals_file,
        build_approval_event("audit", actor="a", channel="cli", scope="run"),
    )
    append_event(
        approvals_file,
        build_rejection_event("audit", actor="a", channel="cli", reason="nope"),
    )
    append_event(
        approvals_file,
        build_approval_event("other", actor="b", channel="cli", scope="run"),
    )

    history = get_history(approvals_file, "audit")
    assert len(history) == 2
    assert history[0].type == "approval"
    assert history[1].type == "rejection"


def test_index_rebuilds_if_missing(tmp_path):
    approvals_file = tmp_path / "approvals.jsonl"
    append_event(
        approvals_file,
        build_approval_event("audit", actor="a", channel="cli", scope="run"),
    )

    index_path = approvals_file.with_suffix(".jsonl.index.json")
    index_path.unlink()

    status = get_latest_status(approvals_file, "audit")
    assert status is not None
    assert status["status"] == "approval"


def test_concurrent_appends_do_not_corrupt_jsonl(tmp_path):
    approvals_file = tmp_path / "approvals.jsonl"
    change_ids = [f"change-{i}" for i in range(10)]
    errors: list[Exception] = []

    def append_for(change_id: str) -> None:
        try:
            event = build_approval_event(
                change_id, actor="a", channel="cli", scope="run"
            )
            append_event(approvals_file, event, max_retries=20, base_delay=0.01)
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=append_for, args=(cid,)) for cid in change_ids]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent append errors: {errors}"

    lines = approvals_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 10
    for line in lines:
        parsed = json.loads(line)
        assert "event_id" in parsed
        assert "timestamp" in parsed

    index_path = approvals_file.with_suffix(".jsonl.index.json")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert len(index) == 10


def test_lock_timeout_raises_error(tmp_path):
    lock_path = tmp_path / "test.lock"
    lock_path.touch()

    with pytest.raises(OpenSpecMCPError) as exc:
        _acquire_lock(lock_path, max_retries=2, base_delay=0.01)

    assert exc.value.code == "LOCK_TIMEOUT"
    _release_lock(lock_path)
