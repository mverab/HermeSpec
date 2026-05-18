# Expected Rejection: Competitor Research

If the user or system rejects the contract, Hermes calls `openspec.reject`:

```json
{
  "change_id": "competitor-research",
  "actor": "user@example.com",
  "channel": "cli",
  "reason": "Postpone until after the product launch next month."
}
```

Response from `openspec.reject`:

```json
{
  "change_id": "competitor-research",
  "status": "rejected",
  "event_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "timestamp": "2026-05-07T10:05:00Z"
}
```

Status after rejection (`openspec.get_change`):

```json
{
  "change_id": "competitor-research",
  "status": "rejection",
  "approval": {
    "status": "rejection",
    "latest_event": {
      "event_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
      "change_id": "competitor-research",
      "type": "rejection",
      "actor": "user@example.com",
      "channel": "cli",
      "timestamp": "2026-05-07T10:05:00Z",
      "scope": null,
      "constraints": null,
      "expiration": null,
      "reason": "Postpone until after the product launch next month."
    },
    "history_count": 2
  }
}
```

Hermes must refuse execution and inform the user of the rejection reason.
