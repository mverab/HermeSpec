import pytest

from openspec_mcp.errors import OpenSpecMCPError
from openspec_mcp.models import ProposeRequest
from openspec_mcp.service import OpenSpecContractService
from openspec_mcp.validators import load_schema, validate_contract_payload


VALID_SCHEDULED_TASK = {
    "objective": "Audit SaaS subscriptions weekly.",
    "trigger": {
        "mode": "cron",
        "schedule": "0 9 * * MON",
        "timezone": "America/Merida",
    },
    "preconditions": ["Billing exports are available."],
    "actions": [
        {
            "id": "compare-spend",
            "description": "Compare this week spend against prior baseline.",
            "allowed_tools": ["stripe.read"],
        }
    ],
    "idempotency": {"strategy": "Use week start as dedupe key."},
    "rollback": {
        "possible": False,
        "procedure": "Read-only task; no rollback required.",
    },
    "alerting": {
        "channels": ["telegram"],
        "on_success": "alert_if_threshold_crossed",
        "on_failure": "always_alert",
    },
    "acceptance": ["Report when spend increases more than 15%."],
}


def test_validate_scheduled_task_requires_core_fields():
    payload = dict(VALID_SCHEDULED_TASK)
    payload.pop("trigger")

    with pytest.raises(OpenSpecMCPError) as exc:
        validate_contract_payload("scheduled_task", payload)

    assert exc.value.code == "SCHEMA_VALIDATION_FAILED"
    assert "trigger" in exc.value.detail["missing"]


def test_schema_files_are_available():
    scheduled = load_schema("scheduled_task")
    future_research = load_schema("future/research")
    future_external_action = load_schema("future/external-action")

    assert scheduled["type"] == "scheduled_task"
    assert future_research["type"] == "research"
    assert future_external_action["type"] == "external_action"


def test_propose_creates_all_required_artifacts(tmp_path):
    service = OpenSpecContractService(tmp_path)

    response = service.propose(
        ProposeRequest(
            title="Audit SaaS subscriptions weekly",
            description="Audit SaaS spend every Monday and alert if it increases more than 15%.",
            type="scheduled_task",
            change_id="audit-saas-subscriptions-weekly",
            payload=VALID_SCHEDULED_TASK,
        )
    )

    assert response.change_id == "audit-saas-subscriptions-weekly"
    assert response.status == "proposed"
    assert response.approval_required is True
    assert (
        tmp_path / "openspec" / "changes" / response.change_id / "proposal.md"
    ).exists()
    assert (
        tmp_path / "openspec" / "changes" / response.change_id / "tasks.md"
    ).exists()
    assert (
        tmp_path
        / "openspec"
        / "changes"
        / response.change_id
        / "specs"
        / "scheduled-task"
        / "spec.md"
    ).exists()


def test_get_and_list_change_after_propose(tmp_path):
    service = OpenSpecContractService(tmp_path)
    service.propose(
        ProposeRequest(
            title="Audit SaaS subscriptions weekly",
            description="Audit SaaS spend every Monday.",
            type="scheduled_task",
            change_id="audit-saas-subscriptions-weekly",
            payload=VALID_SCHEDULED_TASK,
        )
    )

    change = service.get_change("audit-saas-subscriptions-weekly")
    changes = service.list_changes()

    assert change.change_id == "audit-saas-subscriptions-weekly"
    assert "Audit SaaS subscriptions weekly" in change.proposal
    assert [item.change_id for item in changes] == ["audit-saas-subscriptions-weekly"]
