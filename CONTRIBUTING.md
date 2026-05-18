# Contributing to HermeSpec

Thank you for your interest in contributing. This project follows a lightweight process.

## Development Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Install the OpenSpec CLI: `npm i -g @open-spec/cli`
3. Sync dependencies: `uv sync --all-groups`
4. Run tests: `uv run pytest`
5. Run the MCP server locally: `uv run openspec-mcp`

## Pull Request Guidelines

- Open a PR against `main`.
- Ensure `uv run pytest` passes before requesting review.
- Ensure `uv build` produces a valid wheel.
- Keep changes focused. One logical change per PR.
- Update tests when adding or modifying behavior.

## Code Style

- Follow existing conventions. The test suite is the source of truth.
- No external formatting tools are enforced; keep diffs minimal.

## Reporting Issues

Use [GitHub Issues](https://github.com/hermespec/hermespec/issues) for bugs, feature requests, and questions.
