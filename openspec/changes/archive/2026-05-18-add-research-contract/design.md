## Context

The MVP agent contract system supports `scheduled_task` and `external_action` as validated schemas. A placeholder `research.yaml` exists under `schemas/future/` but is not loaded or enforced. Research tasks (market analysis, competitive intelligence, data gathering) carry significant scope and cost risk that a contract boundary should gate before Hermes executes them.

## Goals / Non-Goals

**Goals:**
- Promote `research` from placeholder to a validated, load-bearing schema.
- Extend `openspec.propose` to accept `type: research` with full field validation.
- Update the Hermes skill to mandate proposals for non-trivial research tasks.
- Maintain parity in test coverage with `scheduled_task` and `external_action`.

**Non-Goals:**
- Policy layer (approval expiration, automatic invalidation, RBAC) — out of scope.
- UI for contract review — out of scope.
- Real Hermes runtime integration testing — out of scope; remains simulated.
- Modifying `scheduled_task` or `external_action` behavior — no changes to existing schemas.

## Decisions

**1. Promote schema file rather than create a new one**
- Create `schemas/research.yaml` as the active schema and deprecate `schemas/future/research.yaml`.
- Rationale: The placeholder already has the right conceptual structure. Promoting signals continuity. Future schemas stay in `schemas/future/` until promoted.

**2. Reuse existing `validate_contract_payload` path**
- `validators.py` already loads schemas by type name. Adding `research` requires only a new YAML file and adding to `_ACTIVE_CONTRACT_TYPES`.
- Rationale: No new validation infrastructure. Consistent with existing types.

**3. Hermes skill rule: non-trivial research MUST propose**
- Added as a hard rule in `SKILL.md` alongside the existing scheduled task and external action rules.
- Rationale: The contract model is worthless if Hermes can bypass it for high-risk research tasks.

**4. Keep constraints opaque to the MCP layer**
- Constraints (e.g., `max_cost_usd`, `allowed_tools`) are stored and returned by `openspec.approve`, but the MCP does not interpret them.
- Rationale: The MCP is a boundary store, not an executor. Hermes interprets constraints at execution time.

## Risks / Trade-offs

- **[Risk] Schema promotion breaks references** → Mitigation: Update any internal docs or tests that reference `schemas/future/research.yaml` as the active path.
- **[Risk] Overly strict validation blocks legitimate edge cases** → Mitigation: Start with required-field validation only. Do not add semantic validators in this change.
- **[Trade-off] Hermes skill rules are advisory until real integration** → The skill instructs Hermes, but enforcement is only as strong as the skill loading. Acceptable for this phase.
