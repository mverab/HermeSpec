## Context

The MVP agent contract system supports `scheduled_task` as the only validated no-code schema. A placeholder `external-action.yaml` exists under `schemas/future/` but is not loaded or enforced. External actions (sending emails, posting to Slack, initiating payments) carry higher blast radius than read-only scheduled tasks because they mutate external state. The contract boundary must validate these before Hermes ever executes them.

## Goals / Non-Goals

**Goals:**
- Promote `external_action` from placeholder to a validated, load-bearing schema.
- Extend `openspec.propose` to accept `type: external_action` with full field validation.
- Update the Hermes skill to mandate proposals for external-facing actions.
- Maintain parity in test coverage with `scheduled_task`.

**Non-Goals:**
- Policy layer (approval expiration, automatic invalidation, RBAC) — out of scope.
- UI for contract review — out of scope.
- Real Hermes runtime integration testing — out of scope; remains simulated.
- Modifying `scheduled_task` behavior — no changes to existing schema.

## Decisions

**1. Promote schema file rather than create a new one**
- Move `schemas/future/external-action.yaml` to `schemas/external-action.yaml`.
- Rationale: The placeholder already has the right conceptual structure. Promoting signals continuity. Future schemas stay in `schemas/future/` until promoted.

**2. Reuse existing `validate_contract_payload` path**
- `validators.py` already loads schemas by type name. Adding `external_action` requires only a new YAML file and a type mapping entry.
- Rationale: No new validation infrastructure. Consistent with `scheduled_task`.

**3. Hermes skill rule: external-facing actions MUST propose**
- Added as a hard rule in `SKILL.md` alongside the existing scheduled task rule.
- Rationale: The contract model is worthless if Hermes can bypass it for high-risk actions.

**4. Keep constraints opaque to the MCP layer**
- Constraints (e.g., `max_cost_usd`, `allowed_channels`) are stored and returned by `openspec.approve`, but the MCP does not interpret them.
- Rationale: The MCP is a boundary store, not an executor. Hermes interprets constraints at execution time.

## Risks / Trade-offs

- **[Risk] Schema promotion breaks references** → Mitigation: Update any internal docs or tests that reference `schemas/future/external-action.yaml`. Search before moving.
- **[Risk] Overly strict validation blocks legitimate edge cases** → Mitigation: Start with required-field validation only. Do not add semantic validators (e.g., "email must be valid format") in this change.
- **[Trade-off] Hermes skill rules are advisory until real integration** → The skill instructs Hermes, but enforcement is only as strong as the skill loading. Acceptable for this phase.
