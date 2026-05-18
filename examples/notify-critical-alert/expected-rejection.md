# Expected Rejection: Notify Critical Alert

If the user or system rejects the contract, Hermes calls `openspec.reject`:

```json
{
  "change_id": "notify-critical-alert",
  "actor": "user@example.com",
  "channel": "cli",
  "reason": "Use PagerDuty instead of Slack for P0 alerts."
}
```

Response from `openspec.reject`:

```json
{
  "change_id": "notify-critical-alert",
  "status": "rejected",
  "event_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "timestamp": "2026-05-07T10:05:00Z"
}
```

Status after rejection (`openspec.get_change`):

```json
{
  "change_id": "notify-critical-alert",
  "status": "rejection",
  "approval": {
    "status": "rejection",
    "latest_event": {
      "event_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
      "change_id": "notify-critical-alert",
      "type": "rejection",
      "actor": "user@example.com",
      "channel": "cli",
      "timestamp": "2026-05-07T10:05:00Z",
      "scope": null,
      "constraints": null,
      "expiration": null,
      "reason": "Use PagerDuty instead of Slack for P0 alerts."
    },
    "history_count": 2
  }
}
```

Hermes must refuse execution and inform the user of the rejection reason.
