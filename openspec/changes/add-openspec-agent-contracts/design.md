## Context

Hermes can interpret user intent, use tools, schedule recurring work, communicate through gateways, and retain memory. Those capabilities need a durable contract layer when a task is recurring, sensitive, external-facing, financial, irreversible, or likely to run unattended.

This project starts as a standalone repo named `HermeSpec`. The full MVP is complete after the core filesystem tools and approval lifecycle are implemented. It will provide an MCP server that creates and manages OpenSpec-style contracts while leaving execution to Hermes. OpenSpec remains the source of filesystem conventions and lifecycle vocabulary.

The repo is initially empty, so the design can establish the first project structure without migration from existing code.

## Goals / Non-Goals

**Goals:**

- Provide a local stdio MCP server named `openspec-mcp`.
- Support the lifecycle tools `openspec.propose`, `openspec.get_change`, `openspec.list_changes`, `openspec.approve`, `openspec.reject`, and `openspec.archive` by the end of the MVP.
- Generate OpenSpec artifacts for the first contract type, `scheduled_task`.
- Store approval and rejection history as append-only JSONL.
- Validate filesystem paths so all writes stay inside the configured workspace.
- Provide active schema validation and examples for `scheduled_task`.
- Provide placeholder schemas for future `research` and `external_action` contract types without enforcing them in the MVP.
- Provide a Hermes skill that defines when contracts are required before execution.

**Non-Goals:**

- Do not modify Hermes core.
- Do not modify OpenSpec core.
- Do not build a Codex plugin in the MVP.
- Do not execute arbitrary OpenSpec changes through MCP.
- Do not add remote storage, dashboard UI, multi-user RBAC, or semantic LLM validation.
- Do not allow approval to imply execution; execution remains Hermes-owned.

## Decisions

### Decision: Use file locking for the append-only approval log

The MVP will use a lockfile (`openspec/approvals.jsonl.lock`) with retry and exponential backoff to serialize writes to `approvals.jsonl`. This prevents partial interleaving when multiple MCP clients approve or reject concurrently.

Alternative considered: `fcntl.flock()`. It is simpler but fails on network filesystems and Windows. The lockfile approach is portable and can be replaced with SQLite later if event volume grows.

### Decision: Maintain a lightweight approval index

The JSONL remains the append-only source of truth, but the server will maintain `openspec/approvals.index.json` mapping `change_id → latest file offset`. The index is updated under the same lock as the JSONL append. Reads that need only the latest status use the index; reads that need full history scan the JSONL.

Alternative considered: mutable status files per change. Rejected because it duplicates state and weakens auditability.

### Decision: Use a fixed archive convention

Archival is implemented with the approval lifecycle, not in the foundation phase. It moves the change directory from `openspec/changes/<change_id>/` to `openspec/archive/<YYYY-MM-DD>/<change_id>/` and writes an `archive.record` file with actor and timestamp. This convention does not depend on the OpenSpec CLI, and `list_changes` excludes archives naturally by skipping the `archive/` directory.

### Decision: Define explicit Hermes-MCP execution handoff

Hermes does not execute automatically on approval. Instead, the `openspec-contracts` skill requires Hermes to:
1. Call `openspec.get_change` before acting on a sensitive task.
2. Verify `status == "approved"`.
3. Load the approval `constraints` into its execution context.
4. Refuse execution if no approved contract exists or if the request exceeds constraints.

This keeps enforcement in Hermes (out of MCP scope) but makes the contract boundary explicit and testable.

### Decision: Use structured error codes

All MCP tool errors return a consistent JSON object with `code`, `message`, and `detail`. Codes are stable strings such as `CHANGE_EXISTS`, `PATH_TRAVERSAL`, `MISSING_APPROVER`, and `NOT_FOUND`. This lets Hermes and other clients react programmatically instead of parsing human text.

### Decision: Use Python 3.11, `uv`, and the MCP Python SDK

Python keeps the MCP server small, testable, and easy to run locally with `uv run openspec-mcp`. The MCP SDK provides the tool transport and schema surface instead of hand-rolling protocol handling.

Alternative considered: TypeScript MCP server. TypeScript would align with Node-based OpenSpec CLI tooling, but it would add more runtime coupling to the CLI ecosystem and is not needed for the MVP.

### Decision: Use filesystem-first artifact generation

`openspec.propose` will create the OpenSpec change directory and write `proposal.md`, `tasks.md`, and spec artifacts directly under `openspec/changes/<change_id>/`. The OpenSpec CLI may be called for availability checks and archival compatibility, but artifact generation stays in the server so tests can verify exact output.

Alternative considered: drive all artifact creation through OpenSpec CLI subprocesses. That would mirror manual CLI usage, but it makes structured MCP responses and deterministic tests harder.

### Decision: Keep services separate from MCP transport

The MCP tool handlers will delegate to modules:

- `config.py` for environment configuration.
- `models.py` for request and response models.
- `filesystem.py` for safe paths, artifact reads, writes, listing, and archival.
- `approvals.py` for append-only approval and rejection records.
- `validators.py` for schema checks.
- `openspec_cli.py` for OpenSpec CLI checks.
- `server.py` for MCP registration and transport.

This separation allows most behavior to be tested without launching an MCP transport.

### Decision: Infer status from filesystem and approval log

The MVP will infer status as follows:

- `proposed` when a change exists without approval or rejection.
- `approved` when the latest relevant action is approval.
- `rejected` when the latest relevant action is rejection.
- `archived` when the change has moved to archive.

Alternative considered: write mutable status files into each change. That is simpler to query, but it weakens auditability and duplicates state already available from append-only records.

### Decision: Treat approvals as explicit records

Approvals and rejections will be written to `openspec/approvals.jsonl`. Each event will include the change ID, actor, channel, timestamp, action type, scope or reason, constraints, and optional expiration.

Approval APIs will reject missing actor metadata. Hermes must not infer approval from vague user replies.

### Decision: Limit MVP schema validation to `scheduled_task`

The repo will include schema files for `research` and `external_action` under `schemas/future/` as placeholders, but only `scheduled_task` has active validation, templates, and tests in the MVP. This removes incomplete surface area and prevents confusion about which contract types are ready for production use.

## Risks / Trade-offs

- OpenSpec CLI behavior may differ across versions -> Keep CLI calls narrow, check availability explicitly, and test filesystem behavior independently.
- Direct filesystem generation may drift from OpenSpec conventions -> Use the same directory structure and keep generated artifacts simple Markdown.
- Approval log inference can be ambiguous after repeated approvals and rejections -> Use latest event per change ID for MVP and preserve all prior events for audit.
- Concurrent approvals may corrupt JSONL -> Mitigated by lockfile with retry; monitor for lock contention under high concurrency.
- Hermes may execute outside the approved scope -> The Hermes skill must require explicit approval summaries and execution boundaries, but enforcement inside Hermes remains future work.
- Schemas may be too shallow for complex non-code tasks -> Start with minimum required fields and add semantic validation in a later phase.

## Approval Event Format

Each line in `openspec/approvals.jsonl` is a single JSON object:

```json
{
  "event_id": "uuid-v4",
  "change_id": "scheduled-saas-audit",
  "type": "approval",
  "actor": "user@example.com",
  "channel": "cli",
  "timestamp": "2026-05-06T12:00:00Z",
  "scope": "execute_scheduled_task",
  "constraints": { "max_cost_usd": 50 },
  "expiration": "2026-06-06T12:00:00Z",
  "reason": null
}
```

Required fields for every event: `event_id`, `change_id`, `type`, `actor`, `channel`, `timestamp`.
`type` is either `approval` or `rejection`. `constraints` and `expiration` are allowed only for approvals. `reason` is allowed only for rejections.

## Migration Plan

1. Initialize the Python repo in `/Users/mverab/HermeSpec`.
2. Add the MCP server package and unit tests.
3. Add schemas, Hermes skill, examples, and local MCP config.
4. Validate the scheduled SaaS audit example end to end.
5. Defer Codex plugin packaging and native Hermes hooks until the MCP + skill path is proven.

Rollback is filesystem-based: remove the MCP config from Hermes and stop using the generated contracts. Existing approval logs and OpenSpec artifacts remain readable Markdown and JSONL.

## Open Questions

- Should rejected changes require a new change ID for revision, or allow a revision marker under the same change ID?
- Which Hermes approval phrases should be configurable versus hard-coded in the skill?
- How much schema validation should happen at propose time versus before execution?
- Should the approval index be rebuilt automatically if it is detected as stale or missing?
- At what concurrency threshold should the lockfile be replaced with SQLite or another transactional store?
