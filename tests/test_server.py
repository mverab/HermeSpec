import asyncio
import json

import pytest

from openspec_mcp.server import build_server


def _json_result(content_blocks):
    return json.loads(content_blocks[0].text)


def test_server_builds_with_core_tools():
    server = build_server()

    assert server.name == "openspec-mcp"

    tools = asyncio.run(server.list_tools())

    assert [tool.name for tool in tools] == [
        "openspec.propose",
        "openspec.get_change",
        "openspec.list_changes",
        "openspec.approve",
        "openspec.reject",
        "openspec.archive",
    ]


def test_server_core_tools_execute_against_workspace(monkeypatch, tmp_path):
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

    propose_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.propose",
                {
                    "payload": {
                        "title": "Audit SaaS subscriptions weekly",
                        "description": "Audit SaaS spend every Monday.",
                        "type": "scheduled_task",
                        "change_id": "audit-saas-subscriptions-weekly",
                        "payload": scheduled_task,
                    }
                },
            )
        )
    )
    list_result = _json_result(
        asyncio.run(server.call_tool("openspec.list_changes", {}))
    )
    get_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.get_change", {"change_id": "audit-saas-subscriptions-weekly"}
            )
        )
    )

    assert propose_result["change_id"] == "audit-saas-subscriptions-weekly"
    assert list_result["changes"][0]["change_id"] == "audit-saas-subscriptions-weekly"
    assert get_result["change_id"] == "audit-saas-subscriptions-weekly"


def test_server_lifecycle_propose_approve_reject_archive(monkeypatch, tmp_path):
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

    # Propose
    propose_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.propose",
                {
                    "payload": {
                        "title": "Audit SaaS subscriptions weekly",
                        "description": "Audit SaaS spend every Monday.",
                        "type": "scheduled_task",
                        "change_id": "lifecycle-audit",
                        "payload": scheduled_task,
                    }
                },
            )
        )
    )
    assert propose_result["status"] == "proposed"

    # Get (proposed)
    get_result = _json_result(
        asyncio.run(
            server.call_tool("openspec.get_change", {"change_id": "lifecycle-audit"})
        )
    )
    assert get_result["status"] == "proposed"
    assert get_result["approval"] is None

    # Approve
    approve_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.approve",
                {
                    "payload": {
                        "change_id": "lifecycle-audit",
                        "actor": "user@example.com",
                        "channel": "cli",
                        "scope": "execute_scheduled_task",
                        "constraints": {"max_cost_usd": 50},
                    }
                },
            )
        )
    )
    assert approve_result["status"] == "approved"
    assert approve_result["event_id"]

    # Get (approved)
    get_result = _json_result(
        asyncio.run(
            server.call_tool("openspec.get_change", {"change_id": "lifecycle-audit"})
        )
    )
    assert get_result["status"] == "approved"
    assert get_result["approval"]["status"] == "approval"

    # List shows approved
    list_result = _json_result(
        asyncio.run(server.call_tool("openspec.list_changes", {}))
    )
    assert list_result["changes"][0]["status"] == "approved"

    # Archive
    archive_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.archive",
                {
                    "payload": {
                        "change_id": "lifecycle-audit",
                        "actor": "user@example.com",
                    }
                },
            )
        )
    )
    assert archive_result["archive_path"]

    # Get (not found after archive)
    get_result = _json_result(
        asyncio.run(
            server.call_tool("openspec.get_change", {"change_id": "lifecycle-audit"})
        )
    )
    assert get_result["error"]["code"] == "NOT_FOUND"


def test_server_archive_rejects_unapproved_change(monkeypatch, tmp_path):
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
        "actions": [],
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
    _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.propose",
                {
                    "payload": {
                        "title": "Audit SaaS subscriptions weekly",
                        "description": "Audit SaaS spend every Monday.",
                        "type": "scheduled_task",
                        "change_id": "unapproved-archive",
                        "payload": scheduled_task,
                    }
                },
            )
        )
    )

    archive_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.archive",
                {
                    "payload": {
                        "change_id": "unapproved-archive",
                        "actor": "user@example.com",
                    }
                },
            )
        )
    )

    assert archive_result["error"]["code"] == "ARCHIVE_NOT_ALLOWED"
    assert (tmp_path / "openspec" / "changes" / "unapproved-archive").exists()


def test_server_archive_rejects_rejected_change(monkeypatch, tmp_path):
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
        "actions": [],
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
    _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.propose",
                {
                    "payload": {
                        "title": "Audit SaaS subscriptions weekly",
                        "description": "Audit SaaS spend every Monday.",
                        "type": "scheduled_task",
                        "change_id": "rejected-archive",
                        "payload": scheduled_task,
                    }
                },
            )
        )
    )
    _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.reject",
                {
                    "payload": {
                        "change_id": "rejected-archive",
                        "actor": "user@example.com",
                        "channel": "cli",
                        "reason": "Not approved.",
                    }
                },
            )
        )
    )

    archive_result = _json_result(
        asyncio.run(
            server.call_tool(
                "openspec.archive",
                {
                    "payload": {
                        "change_id": "rejected-archive",
                        "actor": "user@example.com",
                    }
                },
            )
        )
    )

    assert archive_result["error"]["code"] == "ARCHIVE_NOT_ALLOWED"
    assert (tmp_path / "openspec" / "changes" / "rejected-archive").exists()


@pytest.mark.parametrize(
    "tool_name,payload",
    [
        ("openspec.get_change", {"change_id": "../../../etc/passwd"}),
        (
            "openspec.approve",
            {
                "payload": {
                    "change_id": "../escape",
                    "actor": "user@example.com",
                    "channel": "cli",
                    "scope": "execute_scheduled_task",
                }
            },
        ),
        (
            "openspec.reject",
            {
                "payload": {
                    "change_id": "/absolute/path",
                    "actor": "user@example.com",
                    "channel": "cli",
                    "reason": "No.",
                }
            },
        ),
        (
            "openspec.archive",
            {
                "payload": {
                    "change_id": "bad--name",
                    "actor": "user@example.com",
                }
            },
        ),
    ],
)
def test_server_rejects_path_traversal_at_tool_boundary(
    monkeypatch, tmp_path, tool_name, payload
):
    monkeypatch.setenv("OPENSPEC_WORKSPACE", str(tmp_path))
    server = build_server()

    result = _json_result(asyncio.run(server.call_tool(tool_name, payload)))

    assert result["error"]["code"] == "INVALID_CHANGE_ID"
