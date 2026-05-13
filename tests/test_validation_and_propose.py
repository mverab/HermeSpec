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

VALID_EXTERNAL_ACTION = {
    "objective": "Notify team of critical alert via Slack.",
    "action": {
        "type": "send_message",
        "target": "#incidents",
        "description": "Post critical alert to incidents channel.",
    },
    "audience": "On-call engineers",
    "channel": "slack",
    "approval": {"required": True, "minimum_approvers": 1},
    "constraints": {"max_cost_usd": 0, "read_only": False},
    "rollback": {
        "possible": True,
        "procedure": "Delete the posted message if within 5 minutes.",
    },
    "acceptance": ["Message is posted to #incidents within 30 seconds."],
}


def test_validate_scheduled_task_requires_core_fields():
    payload = dict(VALID_SCHEDULED_TASK)
    payload.pop("trigger")

    with pytest.raises(OpenSpecMCPError) as exc:
        validate_contract_payload("scheduled_task", payload)

    assert exc.value.code == "SCHEMA_VALIDATION_FAILED"
    assert "trigger" in exc.value.detail["missing"]


def test_validate_external_action_requires_core_fields():
    payload = dict(VALID_EXTERNAL_ACTION)
    payload.pop("action")

    with pytest.raises(OpenSpecMCPError) as exc:
        validate_contract_payload("external_action", payload)

    assert exc.value.code == "SCHEMA_VALIDATION_FAILED"
    assert "action" in exc.value.detail["missing"]


def test_validate_external_action_rejects_missing_nested_action_field():
    payload = dict(VALID_EXTERNAL_ACTION)
    payload["action"] = {
        "type": "send_message",
        "target": "#incidents",
    }

    with pytest.raises(OpenSpecMCPError) as exc:
        validate_contract_payload("external_action", payload)

    assert exc.value.code == "SCHEMA_VALIDATION_FAILED"
    assert "action.description" in exc.value.detail["missing"]


def test_validate_external_action_requires_explicit_approval():
    payload = dict(VALID_EXTERNAL_ACTION)
    payload["approval"] = {"required": False, "minimum_approvers": 1}

    with pytest.raises(OpenSpecMCPError) as exc:
        validate_contract_payload("external_action", payload)

    assert exc.value.code == "SCHEMA_VALIDATION_FAILED"
    assert exc.value.detail["invalid"] == [
        {"path": "approval.required", "expected": [True], "actual": False}
    ]


def test_validate_scheduled_task_rejects_missing_nested_trigger_field():
    payload = dict(VALID_SCHEDULED_TASK)
    payload["trigger"] = {
        "mode": "cron",
        "schedule": "0 9 * * MON",
    }

    with pytest.raises(OpenSpecMCPError) as exc:
        validate_contract_payload("scheduled_task", payload)

    assert exc.value.code == "SCHEMA_VALIDATION_FAILED"
    assert "trigger.timezone" in exc.value.detail["missing"]


def test_validate_scheduled_task_rejects_missing_action_item_field():
    payload = dict(VALID_SCHEDULED_TASK)
    payload["actions"] = [
        {
            "id": "compare-spend",
            "description": "Compare this week spend against prior baseline.",
        }
    ]

    with pytest.raises(OpenSpecMCPError) as exc:
        validate_contract_payload("scheduled_task", payload)

    assert exc.value.code == "SCHEMA_VALIDATION_FAILED"
    assert "actions.0.allowed_tools" in exc.value.detail["missing"]


def test_schema_files_are_available():
    scheduled = load_schema("scheduled_task")
    external = load_schema("external_action")
    future_research = load_schema("future/research")

    assert scheduled["type"] == "scheduled_task"
    assert external["type"] == "external_action"
    assert external.get("status") != "future-placeholder"
    assert "properties" in external
    assert future_research["type"] == "research"


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


def test_propose_external_action_creates_all_required_artifacts(tmp_path):
    service = OpenSpecContractService(tmp_path)

    response = service.propose(
        ProposeRequest(
            title="Notify team of critical alert",
            description="Post critical alert to Slack #incidents.",
            type="external_action",
            change_id="notify-critical-alert",
            payload=VALID_EXTERNAL_ACTION,
        )
    )

    assert response.change_id == "notify-critical-alert"
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
        / "external-action"
        / "spec.md"
    ).exists()


def test_propose_external_action_rejects_missing_fields(tmp_path):
    service = OpenSpecContractService(tmp_path)
    payload = dict(VALID_EXTERNAL_ACTION)
    payload.pop("constraints")

    with pytest.raises(OpenSpecMCPError) as exc:
        service.propose(
            ProposeRequest(
                title="Notify team",
                description="Test missing fields.",
                type="external_action",
                change_id="missing-fields",
                payload=payload,
            )
        )

    assert exc.value.code == "SCHEMA_VALIDATION_FAILED"
    assert "constraints" in exc.value.detail["missing"]
    assert not (tmp_path / "openspec" / "changes" / "missing-fields").exists()


def test_propose_external_action_rejects_invalid_nested_payload_before_writing(
    tmp_path,
):
    service = OpenSpecContractService(tmp_path)
    payload = dict(VALID_EXTERNAL_ACTION)
    payload["action"] = {
        "type": "send_message",
        "target": "#incidents",
    }

    with pytest.raises(OpenSpecMCPError) as exc:
        service.propose(
            ProposeRequest(
                title="Notify team",
                description="Test missing nested fields.",
                type="external_action",
                change_id="missing-nested-fields",
                payload=payload,
            )
        )

    assert exc.value.code == "SCHEMA_VALIDATION_FAILED"
    assert "action.description" in exc.value.detail["missing"]
    assert not (tmp_path / "openspec" / "changes" / "missing-nested-fields").exists()


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
