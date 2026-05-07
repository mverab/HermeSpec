# HermeSpec

HermeSpec provides an OpenSpec-backed contract layer for long-running AI agents.

The MVP implements the full contract lifecycle for scheduled tasks:

- `openspec.propose` — create a contract with artifacts.
- `openspec.get_change` — retrieve a contract and its current approval status.
- `openspec.list_changes` — list active contracts.
- `openspec.approve` — record explicit approval with constraints.
- `openspec.reject` — record rejection with reason.
- `openspec.archive` — move completed contracts to archive.

Hermes integration includes a skill (`hermes/skills/openspec-contracts/SKILL.md`) that defines when contracts are required, how to verify approval, and how to execute within approved constraints.

## Requirements

- Python 3.11+
- `uv`
- Node.js 20.19+
- OpenSpec CLI available as `openspec`

## Development

Install dependencies and run tests:

```bash
uv run pytest
```

Run the MCP server locally:

```bash
uv run openspec-mcp
```

## Configuration

The server reads:

- `OPENSPEC_WORKSPACE`, default `.`
- `OPENSPEC_BIN`, default `openspec`
- `OPENSPEC_TELEMETRY`, default `0`
- `OPENSPEC_AGENT_CONTRACTS_APPROVALS_FILE`, default `openspec/approvals.jsonl`

## Hermes Integration

See `hermes/mcp-config.example.json` for an example MCP client configuration that connects Hermes to the `openspec-mcp` server.

See `hermes/skills/openspec-contracts/SKILL.md` for the Hermes skill that governs contract-based execution.
