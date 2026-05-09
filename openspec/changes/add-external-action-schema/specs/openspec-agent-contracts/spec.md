## MODIFIED Requirements

### Requirement: Contract Proposal
The system SHALL expose `openspec.propose` to create a new OpenSpec change for an agent contract.

#### Scenario: Propose scheduled task contract
- **WHEN** `openspec.propose` is called with type `scheduled_task`
- **THEN** the system creates a new change directory under `openspec/changes/<change_id>/`
- **AND** the system writes `proposal.md`
- **AND** the system writes `tasks.md`
- **AND** the system writes at least one spec artifact
- **AND** the system returns the change ID, status, artifact paths, and whether approval is required

#### Scenario: Propose external action contract
- **WHEN** `openspec.propose` is called with type `external_action`
- **THEN** the system validates the payload against `schemas/external-action.yaml`
- **AND** the system creates a new change directory under `openspec/changes/<change_id>/`
- **AND** the system writes `proposal.md`
- **AND** the system writes `tasks.md`
- **AND** the system writes at least one spec artifact
- **AND** the system returns the change ID, status, artifact paths, and whether approval is required

#### Scenario: Proposal conflicts with existing change
- **WHEN** `openspec.propose` is called for a change ID that already exists
- **THEN** the system rejects the request without overwriting existing artifacts

### Requirement: Additional No-Code Schemas (Future)
The system SHALL include placeholder schemas for `research` contracts for future phases.

#### Scenario: Research schema placeholder exists
- **WHEN** the repository is inspected
- **THEN** `schemas/future/research.yaml` defines required fields for research objective, scope, sources, methodology, deliverable, and acceptance criteria
- **AND** the system does not enforce validation against it in the current phase
