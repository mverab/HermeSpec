import json

import pytest

from openspec_mcp.errors import OpenSpecMCPError
from openspec_mcp.filesystem import OpenSpecWorkspace


def test_archive_moves_change_and_creates_record(tmp_path):
    workspace = OpenSpecWorkspace(tmp_path)
    workspace.create_change("audit-saas")

    archive_path = workspace.archive_change("audit-saas", actor="user@example.com")

    assert not (tmp_path / "openspec" / "changes" / "audit-saas").exists()
    assert archive_path.exists()
    assert (archive_path / "archive.record").exists()

    record = json.loads((archive_path / "archive.record").read_text(encoding="utf-8"))
    assert record["change_id"] == "audit-saas"
    assert record["actor"] == "user@example.com"
    assert "timestamp" in record


def test_archive_excludes_from_list_changes(tmp_path):
    workspace = OpenSpecWorkspace(tmp_path)
    workspace.create_change("active-change")
    workspace.create_change("to-archive")
    workspace.archive_change("to-archive", actor="user")

    changes = workspace.list_changes()
    assert [c.change_id for c in changes] == ["active-change"]


def test_archive_rejects_unknown_change(tmp_path):
    workspace = OpenSpecWorkspace(tmp_path)

    with pytest.raises(OpenSpecMCPError) as exc:
        workspace.archive_change("missing", actor="user")

    assert exc.value.code == "NOT_FOUND"


def test_archive_rejects_duplicate_archive_same_day(tmp_path):
    workspace = OpenSpecWorkspace(tmp_path)
    workspace.create_change("audit-saas")
    workspace.archive_change("audit-saas", actor="user")

    workspace.create_change("audit-saas")
    with pytest.raises(OpenSpecMCPError) as exc:
        workspace.archive_change("audit-saas", actor="user")

    assert exc.value.code == "ARCHIVE_EXISTS"
