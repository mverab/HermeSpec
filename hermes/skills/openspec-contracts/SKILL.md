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
- Non-trivial research (market analysis, competitive intelligence, technical evaluation, data gathering).
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
2. Verify `status == "approved"` and `approval.latest_event.type == "approval"`.
3. Load `approval.latest_event.constraints` into the execution context.
4. Refuse execution if:
   - No approved contract exists.
   - The request exceeds the approved constraints.
   - The contract has expired (check `approval.latest_event.expiration`).

The immediate response from `openspec.approve` may say `status: "approved"`, but execution MUST use the later `openspec.get_change` result and verify the latest approval event. Hermes must not execute from the approval response alone.

If the contract is `proposed`, Hermes must not execute. It must inform the user that approval is required.
If the contract is `rejected`, Hermes must not execute. It must inform the user of the rejection reason and ask if they want to propose a revised contract.
If the contract is `archived`, Hermes must treat it as non-existent and require a new proposal.

**Research policy**

For `research` contracts specifically (market analysis, competitive intelligence, technical evaluation, data gathering):
- Hermes MUST propose a `research` contract before executing any non-trivial research task.
- Hermes MUST wait for explicit approval with `scope: execute_research` before executing the research.
- Respect the `allowed_tools` constraint. Do not use tools outside the approved list.
- Respect the `forbidden_tools` constraint. Do not use explicitly forbidden tools.
- Respect scope boundaries. Stay within `scope.included` and avoid `scope.excluded` topics.
- Deliver the output to the agreed `deliverable.location` in the specified `deliverable.format`.
- Report progress through approved alerting channels.

**External action policy**

For `external_action` contracts specifically (email, Slack, Telegram, payments, vendor contact, API writes):
- Hermes MUST propose an `external_action` contract before executing any external-facing mutation.
- Hermes MUST wait for explicit approval with `scope: execute_external_action` before executing the mutation.
- Respect the `allowed_channels` constraint. Do not send messages through unapproved channels.
- Respect the `allowed_targets` constraint. Do not contact recipients or systems outside the approved list.
- Respect cost constraints. If estimated cost exceeds `max_cost_usd`, abort and alert.
- Respect the `rollback` procedure. If the action fails, execute the approved rollback plan if possible.
- Report outcomes through the approved alerting channels.
- If the contract declares `read_only: false`, confirm the user understands the mutation before executing.

**Scheduled task policy**

For `scheduled_task` contracts specifically:
- Respect the `allowed_tools` constraint. Do not use tools outside the approved list.
- Respect read-only declarations. If the contract says read-only, do not mutate state.
- Respect cost constraints. If estimated cost exceeds `max_cost_usd`, abort and alert.
- Respect time constraints. If estimated duration exceeds `max_duration_minutes`, abort and alert.
- Report outcomes through the approved alerting channels.
- Use the specified idempotency strategy to prevent duplicate work.

**Parallel agent governance**

If Hermes delegates any contract-governed work to parallel agents, Hermes MUST assign disjoint ownership before delegation. Each agent handoff must name:
- The contract ID and relevant approval constraints.
- The files, systems, channels, or data ranges the agent owns.
- The files, systems, channels, or data ranges the agent must not touch.
- The clear deliverables and evidence each agent must return.

Hermes MUST refuse to run parallel agents when ownership overlaps, deliverables are ambiguous, or the contract does not permit delegation.

**Transcript proof and goal conditions**

Hermes MUST surface measurable proof in the transcript before claiming a scheduled task or external action satisfied its goal conditions. The transcript must include:
- Contract ID and verified approval status.
- Constraints loaded from `approval.latest_event.constraints`.
- Tools, channels, targets, files, or systems actually used.
- The acceptance criteria and the observed metric or artifact that proves each criterion.
- Any skipped action, abort, rollback, or alert with the constraint or failure that caused it.

Hermes must not mark a contract-governed task complete from intent, tool invocation, or a message-send attempt alone. Completion requires observed evidence tied to the contract acceptance criteria.

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
        Status: approved. Latest event type: approval. Constraints loaded.
        [executes within bounds]
        [alerts via Telegram with measured spend delta and acceptance evidence]
```

**Example external action conversation flow**

```
User: Post a critical alert to #incidents on Slack when the error rate spikes.

Hermes: This is an external-facing action. I'll create an OpenSpec contract for it.
       [calls openspec.propose with type: external_action]
       Proposed contract `notify-critical-alert`.
       Requires approval before execution.

User: Approved.

Hermes: I need explicit approval metadata to proceed.
        Who is approving, through which channel, and what are the execution constraints?
        For example:
        - allowed_channels: [slack]
        - allowed_targets: [#incidents]
        - max_cost_usd: 0

User: I approve via CLI. Only Slack, only #incidents. No cost.

Hermes: [calls openspec.approve with actor, channel, scope, constraints]
        Approved. I will post critical alerts to #incidents only
        within the approved constraints.

[At execution time]
Hermes: [calls openspec.get_change("notify-critical-alert")]
        Status: approved. Latest event type: approval. Constraints loaded.
        [posts to #incidents only]
        [reports message ID, target, channel, and acceptance evidence]
```

**Example research conversation flow**

```
User: Research the top 3 competitors in the real-time collaboration space and produce a comparison matrix.

Hermes: This is a non-trivial research task. I'll create an OpenSpec contract for it.
       [calls openspec.propose with type: research]
       Proposed contract `competitor-research-collaboration`.
       Requires approval before execution.

User: Approved.

Hermes: I need explicit approval metadata to proceed.
        Who is approving, through which channel, and what are the execution constraints?
        For example:
        - max_cost_usd: 10
        - allowed_tools: [web_search, read_document]
        - max_duration_minutes: 60

User: I approve via CLI. Max cost $10. Search and read tools only. Max 60 minutes.

Hermes: [calls openspec.approve with actor, channel, scope, constraints]
        Approved. I will execute the research within the approved constraints
        and deliver the comparison matrix.

[At execution time]
Hermes: [calls openspec.get_change("competitor-research-collaboration")]
        Status: approved. Latest event type: approval. Constraints loaded.
        [executes research within scope boundaries]
        [reports evidence of acceptance criteria met]
```

**Guardrails**

- Never execute without verifying approval first.
- Never execute outside approved constraints.
- Never infer approval from informal language.
- Always load constraints into execution context before acting.
- Always check expiration before executing.
- If constraints are missing or ambiguous, ask for clarification rather than assuming defaults.
- Never claim goal completion without measurable transcript proof tied to acceptance criteria.
