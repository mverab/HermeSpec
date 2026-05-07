## ADDED Requirements

### Requirement: MCP Server Availability
The system SHALL provide an MCP server named `openspec-mcp` that exposes OpenSpec agent contract tools over MCP.

#### Scenario: Server starts with dependencies installed
- **WHEN** the MCP server is started in an environment with Python 3.11+ and project dependencies installed
- **THEN** the server exposes the OpenSpec contract lifecycle tools

#### Scenario: OpenSpec CLI is unavailable
- **WHEN** an OpenSpec tool requires the OpenSpec CLI and the configured binary cannot be found
- **THEN** the system returns a structured error that identifies the missing OpenSpec CLI dependency

### Requirement: Contract Proposal
The system SHALL expose `openspec.propose` to create a new OpenSpec change for an agent contract.

#### Scenario: Propose scheduled task contract
- **WHEN** `openspec.propose` is called with type `scheduled_task`
- **THEN** the system creates a new change directory under `openspec/changes/<change_id>/`
- **AND** the system writes `proposal.md`
- **AND** the system writes `tasks.md`
- **AND** the system writes at least one spec artifact
- **AND** the system returns the change ID, status, artifact paths, and whether approval is required

#### Scenario: Proposal conflicts with existing change
- **WHEN** `openspec.propose` is called for a change ID that already exists
- **THEN** the system rejects the request without overwriting existing artifacts

### Requirement: Change Retrieval
The system SHALL expose `openspec.get_change` to retrieve active change artifacts and approval metadata.

#### Scenario: Retrieve known change
- **WHEN** `openspec.get_change` is called for an existing active change
- **THEN** the system returns proposal content, tasks content, spec artifacts, current status, and approval metadata

#### Scenario: Retrieve unknown change
- **WHEN** `openspec.get_change` is called for a change ID that does not exist
- **THEN** the system returns a not found error

### Requirement: Change Listing
The system SHALL expose `openspec.list_changes` to list active OpenSpec agent contract changes.

#### Scenario: List active changes
- **WHEN** `openspec.list_changes` is called
- **THEN** the system returns changes under `openspec/changes`
- **AND** the result excludes archived changes
- **AND** each change includes its change ID, path, status, and approval requirement

### Requirement: Contract Approval
The system SHALL expose `openspec.approve` to record explicit approval for a change.

#### Scenario: Approve contract
- **WHEN** `openspec.approve` is called with change ID, approver, approval channel, approval scope, and constraints
- **THEN** the system appends an approval event to the approval log
- **AND** the change is considered approved

#### Scenario: Approval missing approver
- **WHEN** `openspec.approve` is called without approver metadata
- **THEN** the system rejects the request

#### Scenario: Approval includes constraints
- **WHEN** `openspec.approve` is called with execution constraints
- **THEN** the system preserves those constraints in the approval event

### Requirement: Contract Rejection
The system SHALL expose `openspec.reject` to record explicit rejection for a change.

#### Scenario: Reject contract
- **WHEN** `openspec.reject` is called with change ID, rejecting actor, and reason
- **THEN** the system appends a rejection event to the approval log
- **AND** the change is considered rejected

### Requirement: Contract Archival
The system SHALL expose `openspec.archive` to archive completed or activated changes.

#### Scenario: Archive known change
- **WHEN** `openspec.archive` is called for an existing approved or completed change
- **THEN** the system archives the change
- **AND** the system returns the archive path

#### Scenario: Archive unknown change
- **WHEN** `openspec.archive` is called for a change ID that does not exist
- **THEN** the system returns a not found error

### Requirement: Scheduled Task Schema
The system SHALL define a `scheduled_task` schema for recurring or scheduled agent operations.

#### Scenario: Validate scheduled task fields
- **WHEN** the system validates a scheduled task contract
- **THEN** the contract requires objective, trigger, preconditions, actions, idempotency, rollback, alerting, and acceptance criteria

### Requirement: Additional No-Code Schemas (Future)
The system SHALL include placeholder schemas for `research` and `external_action` contracts for future phases.

#### Scenario: Research schema placeholder exists
- **WHEN** the repository is inspected
- **THEN** `schemas/future/research.yaml` defines required fields for research objective, scope, sources, methodology, deliverable, and acceptance criteria
- **AND** the system does not enforce validation against it in the MVP

#### Scenario: External action schema placeholder exists
- **WHEN** the repository is inspected
- **THEN** `schemas/future/external-action.yaml` defines required fields for objective, action, audience, channel, approval, constraints, rollback, and acceptance criteria
- **AND** the system does not enforce validation against it in the MVP

### Requirement: Hermes Skill
The system SHALL provide a Hermes skill named `openspec-contracts`.

#### Scenario: Hermes receives recurring sensitive task
- **WHEN** Hermes receives a non-trivial recurring, external-facing, financial, irreversible, multi-channel, memory-affecting, or unattended task
- **THEN** the skill instructs Hermes to create an OpenSpec proposal before execution

#### Scenario: Hermes receives trivial task
- **WHEN** Hermes receives a simple low-risk request
- **THEN** the skill instructs Hermes to answer directly without creating an OpenSpec contract

### Requirement: Approval Safety
The system SHALL distinguish proposal, approval, and execution.

#### Scenario: Contract proposed but not approved
- **WHEN** a contract exists without an approval record
- **THEN** Hermes must not execute the scheduled task

#### Scenario: Contract approved with constraints
- **WHEN** Hermes executes against an approved contract with constraints
- **THEN** Hermes must stay within the approved constraints

### Requirement: Filesystem Safety
The system SHALL restrict all contract file operations to the configured OpenSpec workspace.

#### Scenario: Path traversal rejected
- **WHEN** any MCP tool receives a malicious change ID containing path traversal
- **THEN** the system rejects the request before reading or writing files

### Requirement: Approval Auditability
The system SHALL maintain append-only approval and rejection history.

#### Scenario: Approval history is inspectable
- **WHEN** approval or rejection actions occur
- **THEN** each action is recorded as one JSON object per line in `openspec/approvals.jsonl`
