import pytest

from openspec_mcp.config import load_config
from openspec_mcp.errors import OpenSpecMCPError
from openspec_mcp.openspec_cli import OpenSpecCLI


def test_config_defaults_to_current_workspace(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENSPEC_WORKSPACE", raising=False)
    monkeypatch.delenv("OPENSPEC_BIN", raising=False)
    monkeypatch.delenv("OPENSPEC_AGENT_CONTRACTS_APPROVALS_FILE", raising=False)

    config = load_config()

    assert config.workspace == tmp_path.resolve()
    assert config.openspec_bin == "openspec"
    assert config.approvals_file == tmp_path / "openspec" / "approvals.jsonl"


def test_config_uses_environment_overrides(monkeypatch, tmp_path):
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("OPENSPEC_WORKSPACE", str(workspace))
    monkeypatch.setenv("OPENSPEC_BIN", "custom-openspec")
    monkeypatch.setenv(
        "OPENSPEC_AGENT_CONTRACTS_APPROVALS_FILE", "logs/approvals.jsonl"
    )

    config = load_config()

    assert config.workspace == workspace.resolve()
    assert config.openspec_bin == "custom-openspec"
    assert config.approvals_file == workspace / "logs" / "approvals.jsonl"


def test_cli_availability_returns_structured_error_for_missing_binary(tmp_path):
    cli = OpenSpecCLI(bin_name="definitely-missing-openspec-bin", workspace=tmp_path)

    with pytest.raises(OpenSpecMCPError) as exc:
        cli.ensure_available()

    assert exc.value.code == "OPENSPEC_CLI_UNAVAILABLE"
    assert "definitely-missing-openspec-bin" in exc.value.message
