## 1. Schema Promotion

- [x] 1.1 Create `schemas/research.yaml` with required fields: objective, scope, sources, methodology, deliverable, acceptance, and full property definitions.
- [x] 1.2 Deprecate `schemas/future/research.yaml` and point it to the active schema path.
- [x] 1.3 Update `validators.py` to load `research` from the active schema path and validate payloads.

## 2. MCP Service Extension

- [x] 2.1 Extend `OpenSpecContractService.propose` to accept `type: research` and route to artifact generation.
- [x] 2.2 Add `research` spec artifact template in `service.py`.
- [x] 2.3 Verify `openspec.propose` returns `approval_required: true` for `research`.

## 3. Tests

- [x] 3.1 Add unit tests for `research` schema loading and required-field validation.
- [x] 3.2 Add integration test for successful `openspec.propose` with `type: research`.
- [x] 3.3 Add integration test for rejected `openspec.propose` with missing required fields.
- [x] 3.4 Add Hermes integration test simulating: propose research -> approve with constraints -> get_change -> verify constraints.
- [x] 3.5 Add Hermes skill test verifying research policy is present in SKILL.md.
- [x] 3.6 Run full test suite and confirm all tests pass.

## 4. Hermes Skill Update

- [x] 4.1 Add rule to `hermes/skills/openspec-contracts/SKILL.md`: non-trivial research tasks MUST propose with `type: research`.
- [x] 4.2 Add example conversation in SKILL.md for research approval flow.

## 5. Living Docs Update

- [x] 5.1 Update `README.md` to list `research` as an active contract type.
- [x] 5.2 Update `openspec/specs/openspec-agent-contracts/spec.md` to reflect `research` as active.
- [x] 5.3 Create `openspec/specs/research-contract/spec.md` with requirements analogous to external-action-contract.
- [x] 5.4 Update `openspec/config.yaml` context to mention `research` as an MVP contract.
- [x] 5.5 Update `docs/release/mvp-readiness.md` to include `research` in Current MVP Scope.

## 6. OpenSpec CLI Install Documentation

- [x] 6.1 Add `npm i -g @open-spec/cli` to README Requirements section.

## 7. Final Verification

- [x] 7.1 Run `uv run pytest` and confirm all tests pass.
- [x] 7.2 Run `uv build` and confirm build exits 0.
