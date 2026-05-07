import pytest

from openspec_mcp.errors import OpenSpecMCPError
from openspec_mcp.filesystem import OpenSpecWorkspace, validate_change_id


def test_validate_change_id_accepts_kebab_case():
    assert validate_change_id("audit-saas-subscriptions") == "audit-saas-subscriptions"


@pytest.mark.parametrize("change_id", ["../escape", "/absolute", "Bad_Name", "bad--name", "bad.thing", ""])
def test_validate_change_id_rejects_unsafe_values(change_id):
    with pytest.raises(OpenSpecMCPError) as exc:
        validate_change_id(change_id)

    assert exc.value.code == "INVALID_CHANGE_ID"


def test_create_change_rejects_conflicts(tmp_path):
    workspace = OpenSpecWorkspace(tmp_path)

    workspace.create_change("audit-saas")

    with pytest.raises(OpenSpecMCPError) as exc:
        workspace.create_change("audit-saas")

    assert exc.value.code == "CHANGE_EXISTS"


def test_list_changes_excludes_archive_directory(tmp_path):
    workspace = OpenSpecWorkspace(tmp_path)
    workspace.create_change("active-change")
    (tmp_path / "openspec" / "changes" / "archive").mkdir(parents=True)
    (tmp_path / "openspec" / "changes" / "archive" / "old-change").mkdir()

    changes = workspace.list_changes()

    assert [change.change_id for change in changes] == ["active-change"]


def test_read_change_artifacts_returns_proposal_tasks_and_specs(tmp_path):
    workspace = OpenSpecWorkspace(tmp_path)
    change_dir = workspace.create_change("audit-saas")
    (change_dir / "proposal.md").write_text("proposal", encoding="utf-8")
    (change_dir / "tasks.md").write_text("tasks", encoding="utf-8")
    spec_dir = change_dir / "specs" / "scheduled-task"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("spec", encoding="utf-8")

    change = workspace.read_change("audit-saas")

    assert change.proposal == "proposal"
    assert change.tasks == "tasks"
    assert change.specs[0].content == "spec"


def test_archive_path_uses_fixed_convention(tmp_path):
    workspace = OpenSpecWorkspace(tmp_path)

    path = workspace.archive_path("audit-saas", date="2026-05-06")

    assert path == tmp_path / "openspec" / "archive" / "2026-05-06" / "audit-saas"
