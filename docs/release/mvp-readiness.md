# MVP Readiness Audit

This audit covers release documentation, package metadata, OpenSpec project
metadata, and living spec Purpose sections. It does not assess source, tests,
Hermes skill content, examples, or schemas beyond references needed to identify
release blockers.

## Current MVP Scope

- Active contract types: `scheduled_task`, `external_action`, `research`.
- Lifecycle tools: `openspec.propose`, `openspec.get_change`,
  `openspec.list_changes`, `openspec.approve`, `openspec.reject`,
  `openspec.archive`.
- Execution remains out of scope for `openspec-mcp`; Hermes executes only after
  explicit approval and within approved constraints.

## Ship Decision Checks

- `uv run pytest -q` must exit 0.
- `uv build` must exit 0.
- README must describe all active contract types.
- `openspec/config.yaml` must define operational project context and measurable
  artifact rules.
- Living specs must have concrete Purpose sections, not archived-change
  placeholders.
- Coordinated agent work should use 3-5 workers with disjoint ownership.

## Packaging Metadata

- `pyproject.toml` declares the package name (`hermespec`), version, README,
  Python version, dependencies, two console scripts (`openspec-mcp` and
  `hermespec-mcp`), pytest paths, and Hatchling build backend.
- Author, project URLs, and MIT license metadata are declared and point to the
  public repository at `https://github.com/mverab/HermeSpec`.
- Keywords include MCP, AI agents, approvals, governance, and developer tooling.
- Classifiers include AI/ML topics in addition to standard development status
  and Python version markers.

## Blockers And Risks

- No docs/spec/package metadata blocker remains.
- Risk: OpenSpec CLI installation remains external to this package. The README
  includes `npm i -g @fission-ai/openspec@latest` as the canonical install command.
- Risk: Package is not yet published to PyPI. Install is via `git clone` +
  `uv sync` as documented.
