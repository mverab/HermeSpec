## Why

Hermes can run long-lived, recurring, external-facing, and tool-using workflows, but those workflows can drift if their intent, approval boundaries, and acceptance criteria live only in chat history. This change adds an OpenSpec-backed contract layer so sensitive agent work is proposed, reviewed, approved, and audited before execution.

The first use case is scheduled tasks because unattended recurrence is where hidden assumptions and unclear approval boundaries are most likely to become operational risk.

## What Changes

- Add an `openspec-mcp` server that exposes OpenSpec contract lifecycle operations over MCP.
- Add filesystem-backed contract creation, inspection, listing, approval, rejection, and archival.
- Add append-only approval and rejection records for auditability.
- Add a complete no-code schema and validation for `scheduled_task` contracts.
- Add initial schema files for `research` and `external_action` as placeholders for future phases.
- Add a Hermes skill named `openspec-contracts` that defines when Hermes should create a contract before acting.
- Add local examples and MCP configuration for integrating Hermes with the server.
- Keep automatic execution of OpenSpec changes out of scope for the MVP; Hermes executes only after approval and only within the approved contract.

## Capabilities

### New Capabilities

- `openspec-agent-contracts`: Contract lifecycle for agent work, including proposal, retrieval, listing, approval, rejection, archival, schema validation, Hermes skill behavior, and approval safety.

### Modified Capabilities

None.

## Impact

- New Python package under `src/openspec_mcp`.
- New MCP server entrypoint for local stdio usage.
- Active schema file under `schemas/scheduled-task.yaml`.
- Placeholder schema files under `schemas/future/`.
- New Hermes skill files under `hermes/skills/openspec-contracts/`.
- New examples under `examples/`.
- New tests covering filesystem safety, proposal generation, approval lifecycle with concurrent locking, listing, retrieval, and archival.
- Runtime dependencies: Python 3.11+, `uv`, MCP Python SDK, Node.js 20.19+, and OpenSpec CLI.
