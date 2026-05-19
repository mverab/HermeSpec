# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Added `hermespec-mcp` console script as a preferred alias for `openspec-mcp`.
- Public repository polish: rewritten README with product positioning, badges, quickstart, and example flows.
- Added AI/ML classifiers and expanded keywords in packaging metadata.

### Changed

- README rewritten for public product presentation with clear value proposition and quickstart.
- `CONTRIBUTING.md` aligned with current development commands.
- Project URLs in `pyproject.toml` corrected to `https://github.com/mverab/HermeSpec`.

## [0.1.0] - 2026-05-18

### Added

- Initial MCP server implementation with six contract lifecycle tools: `propose`, `get_change`, `list_changes`, `approve`, `reject`, `archive`.
- Three active contract types with schema validation: `scheduled_task`, `external_action`, and `research`.
- Hermes integration skill (`hermes/skills/openspec-contracts/SKILL.md`) for contract-based execution.
- Example flows for all three contract types under `examples/`.
- OpenSpec change archive with three completed proposals.
- Living specifications for agent contracts, external actions, and research.
