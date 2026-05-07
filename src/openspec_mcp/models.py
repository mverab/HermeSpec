from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProposeRequest:
    title: str
    description: str
    type: str
    change_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProposeResponse:
    change_id: str
    status: str
    path: str
    artifacts: dict[str, str]
    approval_required: bool


@dataclass(frozen=True)
class SpecArtifact:
    path: str
    content: str


@dataclass(frozen=True)
class ApprovalEvent:
    event_id: str
    change_id: str
    type: str  # "approval" or "rejection"
    actor: str
    channel: str
    timestamp: str
    scope: str | None = None
    constraints: dict[str, Any] | None = None
    expiration: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class ChangeArtifacts:
    change_id: str
    status: str
    path: str
    proposal: str
    tasks: str
    specs: list[SpecArtifact]
    approval: dict[str, Any] | None = None


@dataclass(frozen=True)
class ChangeSummary:
    change_id: str
    status: str
    path: str
    approval_required: bool
    approval: dict[str, Any] | None = None


@dataclass(frozen=True)
class ApproveRequest:
    change_id: str
    actor: str
    channel: str
    scope: str
    constraints: dict[str, Any] | None = None
    expiration: str | None = None


@dataclass(frozen=True)
class RejectRequest:
    change_id: str
    actor: str
    channel: str
    reason: str


@dataclass(frozen=True)
class ArchiveRequest:
    change_id: str
    actor: str


@dataclass(frozen=True)
class ApproveResponse:
    change_id: str
    status: str
    event_id: str
    timestamp: str


@dataclass(frozen=True)
class RejectResponse:
    change_id: str
    status: str
    event_id: str
    timestamp: str


@dataclass(frozen=True)
class ArchiveResponse:
    change_id: str
    archive_path: str
    timestamp: str
