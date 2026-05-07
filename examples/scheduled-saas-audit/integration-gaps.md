# Integration Gaps

Fases 1–3 implement the full MVP contract lifecycle: proposal, retrieval, listing, approval, rejection, archival, schema validation, Hermes skill behavior, and approval safety.

The following remain for future phases:

- **Native Hermes hooks**: Automatic skill loading and enforcement inside Hermes core rather than via manual skill invocation.
- **Codex plugin packaging**: A native OpenSpec plugin for Codex that wraps the MCP tools.
- **Multi-user RBAC**: Role-based access control for who can propose, approve, or archive.
- **Semantic LLM validation**: Use an LLM to validate that a proposed contract is coherent, complete, and safe before allowing approval.
- **Remote storage**: Move from filesystem-backed storage to a database or object store for multi-node deployments.
- **Dashboard UI**: A web interface for browsing changes, approvals, and audit history.
- **Execution telemetry**: Log actual execution cost, duration, and outcome back to the contract for compliance reporting.
- **Constraint enforcement in MCP**: Optionally enforce constraints (e.g., allowed_tools) at the MCP server layer rather than relying solely on Hermes.
