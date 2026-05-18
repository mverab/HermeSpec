## Why

The `scheduled_task` and `external_action` schemas validate recurring and external-facing operations, but the contract model does not yet cover research tasks. `research` contracts govern agent-led market analysis, competitive intelligence, technical evaluation, and data gathering where unapproved execution risks information quality, scope creep, and cost overruns. Promoting the placeholder to a validated schema is the next load-bearing step before scaling the MCP to policy layers or Hermes real integration.

## What Changes

- Promote `schemas/future/research.yaml` from placeholder to fully validated active schema with required fields: objective, scope, sources, methodology, deliverable, acceptance.
- Add `openspec.propose` support for `type: research` with field-level validation.
- Add Hermes skill rule: non-trivial research tasks MUST propose before execution.
- Add tests for valid/invalid research proposals.
- Archive current change and update spec after completion.

## Capabilities

### New Capabilities
- `research-contract`: Contract schema and validation for agent-led research tasks.

### Modified Capabilities
- `openspec-agent-contracts`: Extend `openspec.propose` to accept `research` as a valid contract type with schema validation.

## Impact

- `src/openspec_mcp/validators.py`: Add `research` to active contract types and schema loading.
- `src/openspec_mcp/service.py`: Extend `propose` to handle `research` payloads and generate spec artifacts.
- `schemas/research.yaml`: Promote from `schemas/future/` to active schema.
- `hermes/skills/openspec-contracts/SKILL.md`: Add rule requiring proposal for non-trivial research tasks.
- Tests: Add validation and integration tests for research proposals.
- Living docs: Update README, openspec-agent-contracts spec, and mvp-readiness audit.
