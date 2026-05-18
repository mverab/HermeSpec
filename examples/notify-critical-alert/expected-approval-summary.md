# Expected Approval Summary: Notify Critical Alert

After the user provides explicit approval metadata, Hermes calls `openspec.approve`:

```json
{
  "change_id": "notify-critical-alert",
  "actor": "user@example.com",
  "channel": "cli",
  "scope": "execute_external_action",
  "constraints": {
    "max_cost_usd": 0,
    "allowed_channels": ["#incidents"],
    "allowed_tools": ["slack.post_message"],
    "read_only": false
  }
}
```

Response from `openspec.approve`:

```json
{
  "change_id": "notify-critical-alert",
  "status": "approved",
  "event_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "timestamp": "2026-05-07T10:00:00Z"
}
```

Status after approval (`openspec.get_change`):

```json
{
  "change_id": "notify-critical-alert",
  "status": "approval",
  "approval": {
    "status": "approval",
    "latest_event": {
      "event_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "change_id": "notify-critical-alert",
      "type": "approval",
      "actor": "user@example.com",
      "channel": "cli",
      "timestamp": "2026-05-07T10:00:00Z",
      "scope": "execute_external_action",
      "constraints": {
        "max_cost_usd": 0,
        "allowed_channels": ["#incidents"],
        "allowed_tools": ["slack.post_message"],
        "read_only": false
      },
      "expiration": null,
      "reason": null
    },
    "history_count": 1
  }
}
```

## Execution transcript requirements

At execution time Hermes must call `openspec.get_change("notify-critical-alert")`, verify `status: "approval"`, then surface measurable proof before claiming completion:

```json
{
  "change_id": "notify-critical-alert",
  "verified_status": "approval",
  "constraints_loaded": {
    "max_cost_usd": 0,
    "allowed_channels": ["#incidents"],
    "allowed_tools": ["slack.post_message"],
    "read_only": false
  },
  "message_posted_to": "#incidents",
  "message_timestamp": "2026-05-07T10:00:05Z",
  "message_includes_severity": true,
  "message_includes_service": true,
  "message_includes_runbook": true,
  "acceptance_criteria_evidence": [
    {
      "criterion": "Message is posted to #incidents within 30 seconds.",
      "evidence": "Posted at 2026-05-07T10:00:05Z (5s after approval)."
    }
  ],
  "channels_used": ["#incidents"],
  "tools_used": ["slack.post_message"],
  "mutations_performed": ["slack.post_message"]
}
```
