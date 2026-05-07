## Fase 1: Core MCP + Filesystem Foundation

Fase 1 is a foundation slice only. It is not spec-complete by itself; the MVP contract is satisfied after Fase 2 adds approval, rejection, and archive lifecycle behavior.

### 1. Project Setup

- [x] 1.1 Initialize the repo with `pyproject.toml`, Python 3.11 metadata, `uv` support, and package configuration for `openspec_mcp`.
- [x] 1.2 Add runtime dependencies for the MCP Python SDK and YAML/schema handling.
- [x] 1.3 Add development dependencies for `pytest` and test coverage.
- [x] 1.4 Create the source package layout under `src/openspec_mcp/`.
- [x] 1.5 Add a README covering prerequisites, installation, local MCP usage, and MVP scope.

### 2. Configuration and OpenSpec CLI

- [x] 2.1 Implement environment-based config loading for `OPENSPEC_WORKSPACE`, `OPENSPEC_BIN`, `OPENSPEC_TELEMETRY`, and `OPENSPEC_AGENT_CONTRACTS_APPROVALS_FILE`.
- [x] 2.2 Implement an OpenSpec CLI wrapper that checks binary availability without executing user-controlled shell commands.
- [x] 2.3 Add structured error types with stable `code` fields for missing dependencies, invalid input, conflicts, not found changes, and filesystem safety failures.
- [x] 2.4 Add tests for config defaults, environment overrides, and OpenSpec CLI unavailable behavior.

### 3. Filesystem Safety Layer

- [x] 3.1 Implement safe workspace path resolution that rejects path traversal and absolute change IDs.
- [x] 3.2 Implement canonical change ID validation for kebab-case slugs.
- [x] 3.3 Implement change directory creation without overwriting existing changes.
- [x] 3.4 Implement artifact reads for proposal, tasks, and spec files.
- [x] 3.5 Implement active change listing that excludes archived changes.
- [x] 3.6 Implement archive path resolution helpers without moving changes yet.
- [x] 3.7 Add tests for path traversal rejection, conflict prevention, listing, reading, and archive path resolution.

### 4. Proposal Generation

- [x] 4.1 Implement scheduled task proposal artifact templates.
- [x] 4.2 Implement scheduled task spec artifact templates.
- [x] 4.3 Implement scheduled task implementation checklist templates.
- [x] 4.4 Implement `openspec.propose` service logic that creates all required artifacts in one operation.
- [x] 4.5 Validate `change_id` (kebab-case, no conflict) and required schema fields at propose time.
- [x] 4.6 Return structured artifact paths and approval requirement metadata from proposal creation.
- [x] 4.7 Add unit tests for successful scheduled task proposal generation, existing change conflicts, and invalid inputs.

### 5. MCP Server Tools (Core)

- [x] 5.1 Implement the MCP server entrypoint in `src/openspec_mcp/server.py`.
- [x] 5.2 Register `openspec.propose`.
- [x] 5.3 Register `openspec.get_change`.
- [x] 5.4 Register `openspec.list_changes`.
- [x] 5.5 Add a smoke test that verifies the server module imports and registers core tools.
- [x] 5.6 Add integration tests that exercise propose, get, and list through the MCP tool layer.

### 6. Schemas and Validation (MVP)

- [x] 6.1 Add `schemas/scheduled-task.yaml` with required scheduled task fields.
- [x] 6.2 Implement minimal schema loading and required-field validation for `scheduled_task`.
- [x] 6.3 Add `schemas/future/research.yaml` as a placeholder schema without active validation.
- [x] 6.4 Add `schemas/future/external-action.yaml` as a placeholder schema without active validation.
- [x] 6.5 Add tests for scheduled task validation and schema file availability.

### 7. Examples and Foundation Validation

- [x] 7.1 Add the scheduled SaaS audit example request.
- [x] 7.2 Add the expected generated proposal example.
- [x] 7.3 Validate the local service flow for propose, get change, and list using tests.
- [x] 7.4 Document observed foundation gaps before approval lifecycle work.

### 8. Final Verification (Fase 1)

- [x] 8.1 Run the full test suite.
- [x] 8.2 Run formatting or linting if configured.
- [x] 8.3 Run `openspec status --change add-openspec-agent-contracts`.
- [x] 8.4 Confirm all apply-required artifacts are complete.

---

## Fase 2: Approval Lifecycle and MVP Completion

### 9. Approval and Rejection Log

- [x] 9.1 Define approval and rejection event models with `event_id`, `change_id`, `type`, `actor`, `channel`, `timestamp`, `scope`, `constraints`, `expiration`, and `reason`.
- [x] 9.2 Implement append-only JSONL writes to `openspec/approvals.jsonl`.
- [x] 9.3 Implement file locking (`openspec/approvals.jsonl.lock`) with retry and exponential backoff.
- [x] 9.4 Implement `openspec/approvals.index.json` for latest-status lookup by `change_id`.
- [x] 9.5 Reject approval requests that omit approver, channel, or scope metadata.
- [x] 9.6 Preserve approval constraints and optional expiration metadata.
- [x] 9.7 Add tests for approval, rejection, repeated events, missing metadata, JSONL parsing, and concurrent writes.

### 10. MCP Server Tools (Approval)

- [x] 10.1 Register `openspec.approve`.
- [x] 10.2 Register `openspec.reject`.
- [x] 10.3 Register `openspec.archive` with approval/completion gating.
- [x] 10.4 Update `openspec.get_change` to include current status and approval metadata.
- [x] 10.5 Update `openspec.list_changes` to include status and approval requirement per change.
- [x] 10.6 Implement archival to `openspec/archive/<YYYY-MM-DD>/<change_id>/` with an `archive.record` metadata file.
- [x] 10.7 Add integration tests for the full approval lifecycle: propose → approve → get → reject → get → list.
- [x] 10.8 Add tests for archive behavior on approved vs non-approved changes.
- [x] 10.9 Add the expected archive record example.

---

## Fase 3: Hermes Integration

### 11. Hermes Integration Assets

- [ ] 11.1 Create `hermes/skills/openspec-contracts/SKILL.md`.
- [ ] 11.2 Define rules for when Hermes must propose before acting.
- [ ] 11.3 Define explicit approval behavior and ambiguous approval rejection.
- [ ] 11.4 Define the Hermes-MCP execution handoff: get_change → verify approved → load constraints → execute within bounds.
- [ ] 11.5 Define scheduled task policy in the skill.
- [ ] 11.6 Add example conversations for scheduled task approval flow.
- [ ] 11.7 Add `hermes/mcp-config.example.json` for local stdio MCP configuration.

### 12. Examples and End-to-End Validation

- [ ] 12.1 Add the expected approval summary example.
- [ ] 12.2 Add the expected rejection example with reason.
- [ ] 12.3 Validate the full flow: propose → approve → Hermes skill consumes constraints → execution respects boundaries.
- [ ] 12.4 Document observed integration gaps and future phases.

### 13. Final Verification (Fase 3)

- [ ] 13.1 Run the full test suite including approval and integration tests.
- [ ] 13.2 Run formatting or linting if configured.
- [ ] 13.3 Confirm all Fase 2 and Fase 3 artifacts are complete.
