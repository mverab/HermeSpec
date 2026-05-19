# HermeSpec

> Approval contracts for long-running AI agents. Propose, approve, execute.

[![CI](https://github.com/mverab/HermeSpec/actions/workflows/ci.yml/badge.svg)](https://github.com/mverab/HermeSpec/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## What is HermeSpec?

HermeSpec is an MCP server that forces AI agents to ask permission before taking risky actions.

When an agent wants to send an email, charge a credit card, post to Slack, or run a scheduled task, it must first **propose a contract** describing exactly what it plans to do. A human reviews and either **approves** (with constraints), **rejects**, or **leaves it pending**. The agent only proceeds after explicit approval.

All proposals, approvals, rejections, and completions are recorded in an audit log.

## How it works

```
┌─────────────┐     propose      ┌─────────────┐
│  AI Agent   │ ────────────────→ │  HermeSpec  │
│ (MCP client)│                   │   Server    │
└─────────────┘                   └──────┬──────┘
       ↑                                 │
       │    approve / reject / constrain │
       └─────────────────────────────────┘
                          human
```

1. **Agent proposes** a contract via `openspec.propose`
2. **Human approves** via `openspec.approve` (with optional constraints)
3. **Agent executes** within the approved bounds
4. **Agent archives** the contract via `openspec.archive` when done

## Quickstart

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for Python dependency management
- Node.js 20.19+ (for the OpenSpec CLI dependency)

### Install

```bash
# 1. Clone the repo
git clone https://github.com/mverab/HermeSpec.git
cd HermeSpec

# 2. Install Python dependencies
uv sync --all-groups

# 3. Install the OpenSpec CLI
npm i -g @fission-ai/openspec@latest
```

### Start the server

```bash
uv run hermespec-mcp
```

The server speaks [Model Context Protocol](https://modelcontextprotocol.io) and exposes six tools for the contract lifecycle.

### Propose and approve a contract

An agent proposes a contract:

```json
{
  "tool": "openspec.propose",
  "arguments": {
    "change_type": "external_action",
    "title": "Notify team of critical alert",
    "artifacts": [
      {
        "path": "alerts/2026-05-18-critical.md",
        "purpose": "Alert documentation for the incident"
      }
    ],
    "payload": {
      "action": "send_slack_message",
      "channel": "#incidents",
      "message": "Database replication lag exceeded 30s on primary."
    }
  }
}
```

The server returns a contract ID. A human reviews and approves:

```json
{
  "tool": "openspec.approve",
  "arguments": {
    "id": "<contract-id>",
    "constraints": {
      "channels": ["#incidents", "#oncall"],
      "max_mentions": 5
    }
  }
}
```

The agent checks approval via `openspec.get_change`, executes the action within constraints, then archives:

```json
{
  "tool": "openspec.archive",
  "arguments": {
    "id": "<contract-id>"
  }
}
```

## Contract Types

HermeSpec validates payloads for three contract types:

| Type | Use Case | Example |
|------|----------|---------|
| `scheduled_task` | Recurring or one-time operations | Security audits, data freshness checks |
| `external_action` | External-facing mutations | Send email, post to Slack, call API |
| `research` | Bounded research tasks | Competitive analysis, technical evaluation |

Each type has a JSON Schema that validates the payload before the contract is created.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `openspec.propose` | Create a new contract with artifacts and payload |
| `openspec.get_change` | Retrieve a contract and its current approval status |
| `openspec.list_changes` | List all active (non-archived) contracts |
| `openspec.approve` | Record explicit approval with optional constraints |
| `openspec.reject` | Record rejection with a reason |
| `openspec.archive` | Move a completed contract to the archive |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENSPEC_WORKSPACE` | `.` | Working directory for contracts and artifacts |
| `OPENSPEC_BIN` | `openspec` | Path to the OpenSpec CLI |
| `OPENSPEC_TELEMETRY` | `0` | Emit lightweight operational metrics (`1` to enable) |
| `OPENSPEC_AGENT_CONTRACTS_APPROVALS_FILE` | `openspec/approvals.jsonl` | Path to the approvals log |

## Example Flows

Full examples for each contract type:

| Contract Type | Example |
|---------------|---------|
| `scheduled_task` | [Weekly SaaS Security Audit](examples/scheduled-saas-audit/) |
| `external_action` | [Notify Critical Alert](examples/notify-critical-alert/) |
| `research` | [Competitor Research](examples/competitor-research/) |

Each example includes:

- `request.md` — the original task request
- `expected-proposal.md` — what the agent should propose
- `expected-approval-summary.md` — what an approver would see
- `expected-rejection.md` — what a rejection looks like

## Hermes Integration

HermeSpec includes a Hermes skill that defines when contracts are required, how to verify approval, and how to execute within approved constraints.

- **MCP config:** [`hermes/mcp-config.example.json`](hermes/mcp-config.example.json)
- **Skill definition:** [`hermes/skills/openspec-contracts/SKILL.md`](hermes/skills/openspec-contracts/SKILL.md)

## Development

```bash
# Install all dependencies including dev tools
uv sync --all-groups

# Run the test suite
uv run pytest -q

# Run the MCP server locally
uv run hermespec-mcp

# Build the package
uv build
```

## License

[MIT](LICENSE)
