import importlib.metadata
import tomllib

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


@pytest.mark.parametrize(
    "approvals_setting",
    [
        "../approvals.jsonl",
        "/tmp/openspec-approvals.jsonl",
    ],
)
def test_config_rejects_approvals_file_outside_workspace(
    monkeypatch, tmp_path, approvals_setting
):
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("OPENSPEC_WORKSPACE", str(workspace))
    monkeypatch.setenv("OPENSPEC_AGENT_CONTRACTS_APPROVALS_FILE", approvals_setting)

    with pytest.raises(OpenSpecMCPError) as exc:
        load_config()

    assert exc.value.code == "PATH_TRAVERSAL"
    assert exc.value.detail["workspace"] == str(workspace.resolve())


def test_cli_availability_returns_structured_error_for_missing_binary(tmp_path):
    cli = OpenSpecCLI(bin_name="definitely-missing-openspec-bin", workspace=tmp_path)

    with pytest.raises(OpenSpecMCPError) as exc:
        cli.ensure_available()

    assert exc.value.code == "OPENSPEC_CLI_UNAVAILABLE"
    assert "definitely-missing-openspec-bin" in exc.value.message


def _get_console_scripts():
    """Return console scripts declared in pyproject.toml."""
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    return pyproject["project"]["scripts"]


def test_openspec_mcp_entry_point_is_declared():
    scripts = _get_console_scripts()
    assert "openspec-mcp" in scripts
    assert scripts["openspec-mcp"] == "openspec_mcp.server:main"


def test_hermespec_mcp_entry_point_is_declared():
    scripts = _get_console_scripts()
    assert "hermespec-mcp" in scripts
    assert scripts["hermespec-mcp"] == "openspec_mcp.server:main"


def test_both_entry_points_resolve_to_same_module():
    scripts = _get_console_scripts()
    assert scripts["openspec-mcp"] == scripts["hermespec-mcp"]


def test_installed_entry_points_match_pyproject():
    """If the package is installed, verify entry points match pyproject.toml."""
    try:
        dist = importlib.metadata.distribution("hermespec")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("hermespec not installed (run uv sync)")

    eps = dist.entry_points
    scripts = {ep.name: ep.value for ep in eps if ep.group == "console_scripts"}

    assert "openspec-mcp" in scripts
    assert "hermespec-mcp" in scripts
    assert scripts["openspec-mcp"] == "openspec_mcp.server:main"
    assert scripts["hermespec-mcp"] == "openspec_mcp.server:main"
