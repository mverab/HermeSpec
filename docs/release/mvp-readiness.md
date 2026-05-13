# MVP Readiness Audit

This audit covers release documentation, package metadata, OpenSpec project
metadata, and living spec Purpose sections. It does not assess source, tests,
Hermes skill content, examples, or schemas beyond references needed to identify
release blockers.

## Current MVP Scope

- Active contract types: `scheduled_task`, `external_action`.
- Future placeholder: `research`.
- Lifecycle tools: `openspec.propose`, `openspec.get_change`,
  `openspec.list_changes`, `openspec.approve`, `openspec.reject`,
  `openspec.archive`.
- Execution remains out of scope for `openspec-mcp`; Hermes executes only after
  explicit approval and within approved constraints.

## Ship Decision Checks

- `uv run pytest` must exit 0.
- `uv build` must exit 0.
- README must describe both active contract types.
- `openspec/config.yaml` must define operational project context and measurable
  artifact rules.
- Living specs must have concrete Purpose sections, not archived-change
  placeholders.
- Coordinated agent work should use 3-5 workers with disjoint ownership.

## Packaging Metadata

- `pyproject.toml` declares the package name, version, README, Python version,
  dependencies, console script, pytest paths, and Hatchling build backend.
- No author, project URL, or license metadata is declared. That is not patched
  here because the repository does not include authoritative values for those
  fields.

## Blockers And Risks

- No docs/spec/package metadata blocker remains in Worker 4's owned scope.
- Risk: OpenSpec CLI installation remains external to this package. The README
  requires `openspec` on `PATH`, but does not prescribe how to install it.
