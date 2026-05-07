# Expected Approval Summary: Scheduled SaaS Audit

After the user provides explicit approval metadata, Hermes calls `openspec.approve`:

```json
{
  "change_id": "audit-saas-subscriptions-weekly",
  "actor": "user@example.com",
  "channel": "cli",
  "scope": "execute_scheduled_task",
  "constraints": {
    "max_cost_usd": 50,
    "allowed_tools": ["stripe.read", "spreadsheet.read"],
    "read_only": true,
    "alerting": ["telegram"]
  },
  "expiration": "2026-06-06T12:00:00Z"
}
```

Response from `openspec.approve`:

```json
{
  "change_id": "audit-saas-subscriptions-weekly",
  "status": "approved",
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-05-07T10:00:00Z"
}
```

Status after approval (`openspec.get_change`):

```json
{
  "change_id": "audit-saas-subscriptions-weekly",
  "status": "approval",
  "approval": {
    "status": "approval",
    "latest_event": {
      "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "change_id": "audit-saas-subscriptions-weekly",
      "type": "approval",
      "actor": "user@example.com",
      "channel": "cli",
      "timestamp": "2026-05-07T10:00:00Z",
      "scope": "execute_scheduled_task",
      "constraints": {
        "max_cost_usd": 50,
        "allowed_tools": ["stripe.read", "spreadsheet.read"],
        "read_only": true,
        "alerting": ["telegram"]
      },
      "expiration": "2026-06-06T12:00:00Z",
      "reason": null
    },
    "history_count": 1
  }
}
```
