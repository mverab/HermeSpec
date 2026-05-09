## Why

The `scheduled_task` schema validates read-only, internal operations, but the contract model only proves its value when it gates high-risk actions. `external_action` covers writes to external systems (email, Slack, payments, vendor contact) where unapproved execution has real blast radius. Promoting the placeholder to a validated schema is the next load-bearing step before scaling the MCP to policy layers or Hermes real integration.

## What Changes

- Promote `schemas/future/external-action.yaml` from placeholder to fully validated schema with required fields: objective, action, audience, channel, approval, constraints, rollback, acceptance.
- Add `openspec.propose` support for `type: external_action` with field-level validation.
- Add Hermes skill rule: external-facing actions MUST propose before execution.
- Add tests for valid/invalid external action proposals.
- Archive current change and update spec after completion.

## Capabilities

### New Capabilities
- `external-action-contract`: Contract schema and validation for agent actions that interact with external systems.

### Modified Capabilities
- `openspec-agent-contracts`: Extend `openspec.propose` to accept `external_action` as a valid contract type with schema validation.

## Impact

- `src/openspec_mcp/validators.py`: Add `external_action` schema loading and validation.
- `src/openspec_mcp/service.py`: Extend `propose` to handle `external_action` payloads.
- `schemas/external-action.yaml`: Promote from `schemas/future/` to active schema.
- `hermes/skills/openspec-contracts/SKILL.md`: Add rule requiring proposal for external actions.
- Tests: Add validation and integration tests for external action proposals.
