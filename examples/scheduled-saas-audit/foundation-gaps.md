# Foundation Gaps

Fase 1 implemented proposal, retrieval, listing, scheduled task validation, and filesystem safety.

Fase 2 implemented the approval and rejection event log, approval index, archive execution with archive records, and concurrent write safety.

Fase 3 implemented the Hermes skill, MCP configuration, and example approval/rejection flows.

All foundation and lifecycle gaps from Fase 1 have been resolved. The following remain for future phases:

- Native Hermes hooks for automatic skill loading and constraint enforcement.
- Codex plugin packaging.
- Multi-user RBAC.
- Semantic LLM validation.
- Remote storage backend.
- Dashboard UI.
- Execution telemetry.
- Constraint enforcement at the MCP server layer.
- `openspec.validate` as a standalone tool.
- `openspec.diff` and `openspec.update_task` tools.
