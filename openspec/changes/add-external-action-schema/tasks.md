## 1. Schema Promotion

- [ ] 1.1 Move `schemas/future/external-action.yaml` to `schemas/external-action.yaml` and confirm it defines required fields: objective, action, audience, channel, approval, constraints, rollback, acceptance.
- [ ] 1.2 Update `validators.py` to load `external_action` from the active schema path.
- [ ] 1.3 Add validation in `validators.py` that rejects `external_action` payloads missing any required top-level field.

## 2. MCP Service Extension

- [ ] 2.1 Extend `OpenSpecContractService.propose` to accept `type: external_action` and route to the same artifact generation flow as `scheduled_task`.
- [ ] 2.2 Add `external_action` proposal and spec artifact templates in `service.py`.
- [ ] 2.3 Verify `openspec.propose` returns `approval_required: true` for `external_action`.

## 3. Tests

- [ ] 3.1 Add unit tests for `external_action` schema loading and required-field validation.
- [ ] 3.2 Add integration test for successful `openspec.propose` with `type: external_action`.
- [ ] 3.3 Add integration test for rejected `openspec.propose` with missing required fields.
- [ ] 3.4 Add Hermes integration test simulating: propose external action → approve with constraints → get_change → verify constraints.
- [ ] 3.5 Run full test suite and confirm coverage does not drop below 94%.

## 4. Hermes Skill Update

- [ ] 4.1 Add rule to `hermes/skills/openspec-contracts/SKILL.md`: external-facing actions (email, Slack, payment, vendor contact) MUST propose with `type: external_action`.
- [ ] 4.2 Add example conversation in SKILL.md for external action approval flow.

## 5. Final Verification

- [ ] 5.1 Run `uv run pytest` and confirm all tests pass.
- [ ] 5.2 Run `uv run pytest --cov=openspec_mcp --cov-report=term-missing` and confirm coverage.
- [ ] 5.3 Run `openspec status --change add-external-action-schema` and confirm all artifacts complete.
- [ ] 5.4 Archive the change with `openspec archive --change add-external-action-schema`.
