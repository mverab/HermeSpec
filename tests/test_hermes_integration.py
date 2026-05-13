import asyncio
import json

from openspec_mcp.server import build_server


def _json_result(content_blocks):
    return json.loads(content_blocks[0].text)


def test_hermes_full_flow_propose_approve_consume_constraints(monkeypatch, tmp_path):
    """Validate the full Hermes-MCP handoff:

    1. Hermes proposes a scheduled task contract.
    2. User approves with explicit constraints.
    3. Hermes calls get_change, verifies status is approved, and loads constraints.
    4. Execution must respect the boundaries defined in constraints.
    """
    monkeypatch.setenv("OPENSPEC_WORKSPACE", str(tmp_path))
    server = build_server()

    scheduled_task = {
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

    # Step 1: Propose
    propose_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.propose",
                {
                    "payload": {
                        "title": "Audit SaaS subscriptions weekly",
                        "description": "Audit SaaS spend every Monday.",
                        "type": "scheduled_task",
                        "change_id": "hermes-audit-flow",
                        "payload": scheduled_task,
                    }
                },
            )
        )
    )
    assert propose_result["status"] == "proposed"
    assert propose_result["approval_required"] is True

    # Step 2: Approve with explicit constraints
    constraints = {
        "max_cost_usd": 50,
        "allowed_tools": ["stripe.read"],
        "read_only": True,
        "max_duration_minutes": 30,
    }
    approve_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.approve",
                {
                    "payload": {
                        "change_id": "hermes-audit-flow",
                        "actor": "user@example.com",
                        "channel": "cli",
                        "scope": "execute_scheduled_task",
                        "constraints": constraints,
                    }
                },
            )
        )
    )
    assert approve_result["status"] == "approved"
    assert approve_result["event_id"]

    # Step 3: Hermes consumes change and verifies approval + constraints
    get_result = _json_result(
        asyncio.run(
            server.call_tool("openspec.get_change", {"change_id": "hermes-audit-flow"})
        )
    )

    # Approval status is surfaced
    assert get_result["status"] == "approval"
    assert get_result["approval"] is not None
    assert get_result["approval"]["status"] == "approval"

    # Constraints are preserved and accessible for boundary enforcement
    latest_event = get_result["approval"]["latest_event"]
    assert latest_event["constraints"] == constraints
    assert latest_event["scope"] == "execute_scheduled_task"
    assert latest_event["actor"] == "user@example.com"

    # Proposal and spec artifacts exist for boundary validation
    assert get_result["proposal"]
    assert get_result["tasks"]
    assert get_result["specs"]
    spec_paths = [spec["path"] for spec in get_result["specs"]]
    assert any("scheduled-task" in p for p in spec_paths)

    # Step 4: list_changes also reflects approved status
    list_result = _json_result(
        asyncio.run(server.call_tool("openspec.list_changes", {}))
    )
    assert len(list_result["changes"]) == 1
    listed = list_result["changes"][0]
    assert listed["change_id"] == "hermes-audit-flow"
    assert listed["status"] == "approval"
    assert listed["approval"]["status"] == "approval"
    assert listed["approval"]["latest_event"]["constraints"] == constraints


def test_hermes_rejects_ambiguous_approval_by_requiring_explicit_scope(
    monkeypatch, tmp_path
):
    """Hermes skill must reject vague approvals; the MCP layer enforces explicit scope."""
    monkeypatch.setenv("OPENSPEC_WORKSPACE", str(tmp_path))
    server = build_server()

    # Propose
    _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.propose",
                {
                    "payload": {
                        "title": "Test",
                        "description": "Test ambiguous approval.",
                        "type": "scheduled_task",
                        "change_id": "ambiguous-approval",
                        "payload": {
                            "objective": "Test.",
                            "trigger": {
                                "mode": "cron",
                                "schedule": "0 9 * * *",
                                "timezone": "UTC",
                            },
                            "preconditions": [],
                            "actions": [],
                            "idempotency": {"strategy": "none"},
                            "rollback": {"possible": False, "procedure": "none"},
                            "alerting": {
                                "channels": [],
                                "on_success": "none",
                                "on_failure": "none",
                            },
                            "acceptance": [],
                        },
                    }
                },
            )
        )
    )

    # Approve without scope should be rejected by the MCP service
    approve_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.approve",
                {
                    "payload": {
                        "change_id": "ambiguous-approval",
                        "actor": "user@example.com",
                        "channel": "cli",
                        "scope": "",
                    }
                },
            )
        )
    )
    assert approve_result["error"]["code"] == "MISSING_APPROVER"


def test_hermes_external_action_full_flow_propose_approve_consume_constraints(
    monkeypatch, tmp_path
):
    """Validate the full Hermes-MCP handoff for an external action:

    1. Hermes proposes an external action contract.
    2. User approves with explicit constraints.
    3. Hermes calls get_change, verifies status is approved, and loads constraints.
    4. Execution must respect the boundaries defined in constraints.
    """
    monkeypatch.setenv("OPENSPEC_WORKSPACE", str(tmp_path))
    server = build_server()

    external_action = {
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

    # Step 1: Propose
    propose_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.propose",
                {
                    "payload": {
                        "title": "Notify team of critical alert",
                        "description": "Post critical alert to Slack #incidents.",
                        "type": "external_action",
                        "change_id": "hermes-external-action-flow",
                        "payload": external_action,
                    }
                },
            )
        )
    )
    assert propose_result["status"] == "proposed"
    assert propose_result["approval_required"] is True

    # Step 2: Approve with explicit constraints
    constraints = {
        "max_cost_usd": 0,
        "allowed_channels": ["slack"],
        "allowed_targets": ["#incidents"],
        "read_only": False,
    }
    approve_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.approve",
                {
                    "payload": {
                        "change_id": "hermes-external-action-flow",
                        "actor": "user@example.com",
                        "channel": "cli",
                        "scope": "execute_external_action",
                        "constraints": constraints,
                    }
                },
            )
        )
    )
    assert approve_result["status"] == "approved"
    assert approve_result["event_id"]

    # Step 3: Hermes consumes change and verifies approval + constraints
    get_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.get_change", {"change_id": "hermes-external-action-flow"}
            )
        )
    )

    assert get_result["status"] == "approval"
    assert get_result["approval"] is not None
    assert get_result["approval"]["status"] == "approval"

    latest_event = get_result["approval"]["latest_event"]
    assert latest_event["constraints"] == constraints
    assert latest_event["scope"] == "execute_external_action"
    assert latest_event["actor"] == "user@example.com"

    assert get_result["proposal"]
    assert get_result["tasks"]
    assert get_result["specs"]
    spec_paths = [spec["path"] for spec in get_result["specs"]]
    assert any("external-action" in p for p in spec_paths)

    # Step 4: list_changes also reflects approved status
    list_result = _json_result(
        asyncio.run(server.call_tool("openspec.list_changes", {}))
    )
    assert len(list_result["changes"]) == 1
    listed = list_result["changes"][0]
    assert listed["change_id"] == "hermes-external-action-flow"
    assert listed["status"] == "approval"
    assert listed["approval"]["status"] == "approval"
    assert listed["approval"]["latest_event"]["constraints"] == constraints
