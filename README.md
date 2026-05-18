# HermeSpec

HermeSpec provides an OpenSpec-backed contract layer for long-running AI agents.

The MVP implements the OpenSpec contract lifecycle for three active contract types:

- `scheduled_task` - recurring or scheduled agent operations.
- `external_action` - external-facing mutations such as email, Slack, payments,
  vendor contact, or API writes.
- `research` - agent-led research contracts covering market analysis, competitive
  intelligence, technical evaluation, or data gathering.

The MCP server exposes:

- `openspec.propose` - create a contract with artifacts.
- `openspec.get_change` - retrieve a contract and its current approval status.
- `openspec.list_changes` - list active contracts.
- `openspec.approve` - record explicit approval with constraints.
- `openspec.reject` - record rejection with reason.
- `openspec.archive` - move completed contracts to archive.

`scheduled_task`, `external_action`, and `research` payloads are validated before
artifacts are created.

Hermes integration includes a skill (`hermes/skills/openspec-contracts/SKILL.md`) that defines when contracts are required, how to verify approval, and how to execute within approved constraints.

## Requirements

- Python 3.11+
- `uv`
- Node.js 20.19+
- OpenSpec CLI installed separately and available as `openspec`

Install the OpenSpec CLI globally:

```bash
npm i -g @open-spec/cli
```

## Development

Install dependencies:

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

Run the MCP server locally:

```bash
uv run openspec-mcp
```

Run packaging verification:

```bash
uv build
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

## MVP Ship Gate

Before an MVP ship decision, verify:

- `uv run pytest` exits 0.
- `uv build` exits 0.
- README scope matches the active contract types: `scheduled_task`, `external_action`, and `research`.
- Living spec Purpose sections are concrete and no longer contain archived-change placeholders.
- Any worker team uses 3-5 workers with disjoint write ownership.
