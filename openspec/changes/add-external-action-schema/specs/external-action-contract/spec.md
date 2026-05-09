## ADDED Requirements

### Requirement: External Action Schema Definition
The system SHALL define an `external_action` schema for agent operations that interact with external systems.

#### Scenario: Validate external action fields
- **WHEN** the system validates an external action contract
- **THEN** the contract requires objective, action, audience, channel, approval, constraints, rollback, and acceptance criteria

#### Scenario: External action schema file is active
- **WHEN** the repository is inspected
- **THEN** `schemas/external-action.yaml` defines the active schema
- **AND** the placeholder `schemas/future/external-action.yaml` is removed or deprecated

### Requirement: External Action Contract Proposal
The system SHALL expose `openspec.propose` to create a new OpenSpec change for an `external_action` contract.

#### Scenario: Propose external action contract
- **WHEN** `openspec.propose` is called with type `external_action`
- **THEN** the system validates the payload against `schemas/external-action.yaml`
- **AND** the system creates a new change directory under `openspec/changes/<change_id>/`
- **AND** the system writes `proposal.md`, `tasks.md`, and at least one spec artifact
- **AND** the system returns the change ID, status, artifact paths, and whether approval is required

#### Scenario: Reject invalid external action proposal
- **WHEN** `openspec.propose` is called with type `external_action` and a missing required field
- **THEN** the system rejects the request with a validation error
- **AND** no change directory is created

### Requirement: External Action Approval Safety
The system SHALL require explicit approval for external action contracts before execution.

#### Scenario: External action proposed but not approved
- **WHEN** an external action contract exists without an approval record
- **THEN** Hermes must not execute the external action

#### Scenario: External action approved with constraints
- **WHEN** Hermes executes against an approved external action contract with constraints
- **THEN** Hermes must stay within the approved constraints

### Requirement: Hermes Skill Enforcement
The system SHALL instruct Hermes to propose an external action contract before executing any external-facing operation.

#### Scenario: Hermes receives external-facing task
- **WHEN** Hermes receives a task involving email, Slack, payment, vendor contact, or any other external system mutation
- **THEN** the skill instructs Hermes to create an OpenSpec proposal with type `external_action`
- **AND** the skill instructs Hermes to wait for explicit approval before executing

#### Scenario: Hermes receives trivial internal task
- **WHEN** Hermes receives a simple low-risk internal request with no external side effects
- **THEN** the skill instructs Hermes to answer directly without creating an OpenSpec contract
