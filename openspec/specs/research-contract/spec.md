# research-contract Specification

## Purpose
Define the active `research` contract type for agent-led research tasks.
The contract captures objective, scope, sources, methodology, deliverable format,
and acceptance criteria so Hermes can wait for explicit approval before
performing non-trivial research work.

## Requirements
### Requirement: Research Schema Definition
The system SHALL define a `research` schema for agent-led research contracts.

#### Scenario: Validate research fields
- **WHEN** the system validates a research contract
- **THEN** the contract requires objective, scope, sources, methodology, deliverable, and acceptance criteria

#### Scenario: Research schema file is active
- **WHEN** the repository is inspected
- **THEN** `schemas/research.yaml` defines the active schema
- **AND** the placeholder `schemas/future/research.yaml` is deprecated

### Requirement: Research Contract Proposal
The system SHALL expose `openspec.propose` to create a new OpenSpec change for a `research` contract.

#### Scenario: Propose research contract
- **WHEN** `openspec.propose` is called with type `research`
- **THEN** the system validates the payload against `schemas/research.yaml`
- **AND** the system creates a new change directory under `openspec/changes/<change_id>/`
- **AND** the system writes `proposal.md`, `tasks.md`, and at least one spec artifact
- **AND** the system returns the change ID, status, artifact paths, and whether approval is required

#### Scenario: Reject invalid research proposal
- **WHEN** `openspec.propose` is called with type `research` and a missing required field
- **THEN** the system rejects the request with a validation error
- **AND** no change directory is created

### Requirement: Research Approval Safety
The system SHALL require explicit approval for research contracts before execution.

#### Scenario: Research proposed but not approved
- **WHEN** a research contract exists without an approval record
- **THEN** Hermes must not execute the research

#### Scenario: Research approved with constraints
- **WHEN** Hermes executes against an approved research contract with constraints
- **THEN** Hermes must stay within the approved constraints

### Requirement: Hermes Skill Enforcement
The system SHALL instruct Hermes to propose a research contract before executing any non-trivial research task.

#### Scenario: Hermes receives research task
- **WHEN** Hermes receives a task involving market analysis, competitive intelligence, technical evaluation, or data gathering
- **THEN** the skill instructs Hermes to create an OpenSpec proposal with type `research`
- **AND** the skill instructs Hermes to wait for explicit approval before executing

#### Scenario: Hermes receives trivial internal task
- **WHEN** Hermes receives a simple low-risk internal request with no research burden
- **THEN** the skill instructs Hermes to answer directly without creating an OpenSpec contract
