---
name: openspec-contracts
description: |
  Govern when Hermes must create, verify, and execute within an OpenSpec contract.
  Use before any recurring, sensitive, external-facing, financial, irreversible, or unattended task.
license: MIT
compatibility: Requires openspec-mcp server.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.0.0"
---

OpenSpec Contracts for Hermes

Before acting on a sensitive task, Hermes must verify an approved contract exists and execute only within its constraints.

**When to propose a contract**

Propose a contract via `openspec.propose` when the task is any of the following:
- Recurring or scheduled.
- External-facing (sends messages, calls APIs, contacts vendors).
- Financial (spends money, modifies billing, changes subscriptions).
- Irreversible (deletions, cancellations, data loss).
- Likely to run unattended (no human in the loop at execution time).

If the user describes a one-off, read-only, internal task with no external impact, a contract is optional but still recommended for unattended execution.

**Explicit approval behavior**

Hermes must NOT infer approval from vague user replies such as "sure", "ok", "go ahead", or "do it". Approval is an explicit record with required metadata.

Required fields for every approval:
- `actor`: Who approved (email or identifier).
- `channel`: Where approval happened (`cli`, `slack`, `telegram`, `web`).
- `scope`: What is being approved (e.g., `execute_scheduled_task`).
- `constraints`: Execution boundaries (e.g., `max_cost_usd`, `allowed_tools`, `max_duration_minutes`).

If any required field is missing, Hermes must refuse execution and ask for explicit approval with complete metadata.

Hermes must also reject ambiguous constraints. If the user says "keep it cheap" without a numeric limit, Hermes must ask for a concrete constraint or propose a default and request confirmation.

**Execution handoff**

Before executing a contract-governed task, Hermes must:

1. Call `openspec.get_change(change_id)`.
2. Verify `status == "approved"`.
3. Load `approval.constraints` into the execution context.
4. Refuse execution if:
   - No approved contract exists.
   - The request exceeds the approved constraints.
   - The contract has expired (check `approval.expiration`).

If the contract is `proposed`, Hermes must not execute. It must inform the user that approval is required.
If the contract is `rejected`, Hermes must not execute. It must inform the user of the rejection reason and ask if they want to propose a revised contract.
If the contract is `archived`, Hermes must treat it as non-existent and require a new proposal.

**Scheduled task policy**

For `scheduled_task` contracts specifically:
- Respect the `allowed_tools` constraint. Do not use tools outside the approved list.
- Respect read-only declarations. If the contract says read-only, do not mutate state.
- Respect cost constraints. If estimated cost exceeds `max_cost_usd`, abort and alert.
- Respect time constraints. If estimated duration exceeds `max_duration_minutes`, abort and alert.
- Report outcomes through the approved alerting channels.
- Use the specified idempotency strategy to prevent duplicate work.

**Example conversation flow**

```
User: Every Monday at 9 AM, audit SaaS spend and alert if it goes up more than 15%.

Hermes: This is a recurring, external-facing task. I'll create an OpenSpec contract for it.
       [calls openspec.propose]
       Proposed contract `audit-saas-spend`.
       Requires approval before execution.

User: Approved.

Hermes: I need explicit approval metadata to proceed.
        Who is approving, through which channel, and what are the execution constraints?
        For example:
        - max_cost_usd: 50
        - allowed_tools: [stripe.read, spreadsheet.read]
        - alerting: [telegram]

User: I approve via CLI. Max cost $50. Read-only tools only. Alert on Telegram.

Hermes: [calls openspec.approve with actor, channel, scope, constraints]
        Approved. I will execute `audit-saas-spend` every Monday at 9 AM
        within the approved constraints.

[At execution time]
Hermes: [calls openspec.get_change("audit-saas-spend")]
        Status: approved. Constraints loaded.
        [executes within bounds]
        [alerts via Telegram with results]
```

**Guardrails**

- Never execute without verifying approval first.
- Never execute outside approved constraints.
- Never infer approval from informal language.
- Always load constraints into execution context before acting.
- Always check expiration before executing.
- If constraints are missing or ambiguous, ask for clarification rather than assuming defaults.
