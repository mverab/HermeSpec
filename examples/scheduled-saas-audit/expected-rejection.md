# Expected Rejection: Scheduled SaaS Audit

If the user or system rejects the contract, Hermes calls `openspec.reject`:

```json
{
  "change_id": "audit-saas-subscriptions-weekly",
  "actor": "user@example.com",
  "channel": "cli",
  "reason": "Budget freeze for Q2. Revisit in Q3."
}
```

Response from `openspec.reject`:

```json
{
  "change_id": "audit-saas-subscriptions-weekly",
  "status": "rejected",
  "event_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "timestamp": "2026-05-07T10:05:00Z"
}
```

Status after rejection (`openspec.get_change`):

```json
{
  "change_id": "audit-saas-subscriptions-weekly",
  "status": "rejection",
  "approval": {
    "status": "rejection",
    "latest_event": {
      "event_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "change_id": "audit-saas-subscriptions-weekly",
      "type": "rejection",
      "actor": "user@example.com",
      "channel": "cli",
      "timestamp": "2026-05-07T10:05:00Z",
      "scope": null,
      "constraints": null,
      "expiration": null,
      "reason": "Budget freeze for Q2. Revisit in Q3."
    },
    "history_count": 2
  }
}
```

Hermes must refuse execution and inform the user of the rejection reason.
