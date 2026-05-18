# Expected Approval Summary: Competitor Research

After the user provides explicit approval metadata, Hermes calls `openspec.approve`:

```json
{
  "change_id": "competitor-research",
  "actor": "user@example.com",
  "channel": "cli",
  "scope": "execute_research",
  "constraints": {
    "max_cost_usd": 0,
    "allowed_tools": ["web_search", "read_document"],
    "read_only": true,
    "max_sources": 10
  }
}
```

Response from `openspec.approve`:

```json
{
  "change_id": "competitor-research",
  "status": "approved",
  "event_id": "e5f6a7b8-c9d0-1234-efab-345678901234",
  "timestamp": "2026-05-07T10:00:00Z"
}
```

Status after approval (`openspec.get_change`):

```json
{
  "change_id": "competitor-research",
  "status": "approval",
  "approval": {
    "status": "approval",
    "latest_event": {
      "event_id": "e5f6a7b8-c9d0-1234-efab-345678901234",
      "change_id": "competitor-research",
      "type": "approval",
      "actor": "user@example.com",
      "channel": "cli",
      "timestamp": "2026-05-07T10:00:00Z",
      "scope": "execute_research",
      "constraints": {
        "max_cost_usd": 0,
        "allowed_tools": ["web_search", "read_document"],
        "read_only": true,
        "max_sources": 10
      },
      "expiration": null,
      "reason": null
    },
    "history_count": 1
  }
}
```

## Execution transcript requirements

At execution time Hermes must call `openspec.get_change("competitor-research")`, verify `status: "approval"`, then surface measurable proof before claiming completion:

```json
{
  "change_id": "competitor-research",
  "verified_status": "approval",
  "constraints_loaded": {
    "max_cost_usd": 0,
    "allowed_tools": ["web_search", "read_document"],
    "read_only": true,
    "max_sources": 10
  },
  "deliverable_path": "docs/research/competitor-matrix.md",
  "competitors_covered": 3,
  "sources_used": 7,
  "acceptance_criteria_evidence": [
    {
      "criterion": "Matrix covers at least 3 competitors.",
      "evidence": "Matrix includes Competitor A, Competitor B, and Competitor C."
    }
  ],
  "channels_used": [],
  "tools_used": ["web_search", "read_document"],
  "mutations_performed": []
}
```
