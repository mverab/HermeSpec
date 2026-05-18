from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path

from . import approvals
from .config import Config
from .filesystem import OpenSpecWorkspace, validate_change_id
from .models import (
    ApproveRequest,
    ApproveResponse,
    ArchiveRequest,
    ArchiveResponse,
    ChangeArtifacts,
    ChangeSummary,
    ProposeRequest,
    ProposeResponse,
    RejectRequest,
    RejectResponse,
)
from .validators import validate_contract_payload


def slugify_title(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return validate_change_id(slug)


def _normalize_status(raw: str) -> str:
    if raw == "approval":
        return "approved"
    if raw == "rejection":
        return "rejected"
    return raw


class OpenSpecContractService:
    def __init__(self, workspace: str | Path, config: Config | None = None):
        self.workspace = OpenSpecWorkspace(Path(workspace))
        self.config = config

    def propose(self, request: ProposeRequest) -> ProposeResponse:
        change_id = validate_change_id(
            request.change_id or slugify_title(request.title)
        )
        validate_contract_payload(request.type, request.payload)

        change_dir = self.workspace.create_change(change_id)
        spec_dir = change_dir / "specs" / request.type.replace("_", "-")
        spec_dir.mkdir(parents=True)

        proposal_path = change_dir / "proposal.md"
        tasks_path = change_dir / "tasks.md"
        spec_path = spec_dir / "spec.md"

        proposal_path.write_text(self._proposal_template(request), encoding="utf-8")
        tasks_path.write_text(self._tasks_template(), encoding="utf-8")
        if request.type == "scheduled_task":
            spec_path.write_text(
                self._scheduled_task_spec_template(request), encoding="utf-8"
            )
        elif request.type == "external_action":
            spec_path.write_text(
                self._external_action_spec_template(request), encoding="utf-8"
            )
        elif request.type == "research":
            spec_path.write_text(
                self._research_spec_template(request), encoding="utf-8"
            )
        else:
            from .errors import OpenSpecMCPError
            raise OpenSpecMCPError(
                "UNSUPPORTED_CONTRACT_TYPE",
                f"Contract type is not active in the MVP: {request.type}",
                {"type": request.type},
            )

        return ProposeResponse(
            change_id=change_id,
            status="proposed",
            path=str(change_dir),
            artifacts={
                "proposal": str(proposal_path),
                "tasks": str(tasks_path),
                "specs": str(spec_dir),
            },
            approval_required=True,
        )

    def get_change(self, change_id: str) -> ChangeArtifacts:
        artifacts = self.workspace.read_change(validate_change_id(change_id))
        approval_info = self._get_approval_info(change_id)
        return ChangeArtifacts(
            change_id=artifacts.change_id,
            status=_normalize_status(approval_info.get("status", "proposed"))
            if approval_info
            else "proposed",
            path=artifacts.path,
            proposal=artifacts.proposal,
            tasks=artifacts.tasks,
            specs=artifacts.specs,
            approval=approval_info,
        )

    def list_changes(self) -> list[ChangeSummary]:
        summaries = self.workspace.list_changes()
        enriched: list[ChangeSummary] = []
        for summary in summaries:
            approval_info = self._get_approval_info(summary.change_id)
            enriched.append(
                ChangeSummary(
                    change_id=summary.change_id,
                    status=_normalize_status(approval_info.get("status", "proposed"))
                    if approval_info
                    else "proposed",
                    path=summary.path,
                    approval_required=summary.approval_required,
                    approval=approval_info,
                )
            )
        return enriched

    def approve(self, request: ApproveRequest) -> ApproveResponse:
        change_id = validate_change_id(request.change_id)
        _ = self.workspace.read_change(change_id)

        event = approvals.build_approval_event(
            change_id=change_id,
            actor=request.actor,
            channel=request.channel,
            scope=request.scope,
            constraints=request.constraints,
            expiration=request.expiration,
        )
        approvals.append_event(self._approvals_file, event)

        return ApproveResponse(
            change_id=change_id,
            status="approved",
            event_id=event.event_id,
            timestamp=event.timestamp,
        )

    def reject(self, request: RejectRequest) -> RejectResponse:
        change_id = validate_change_id(request.change_id)
        _ = self.workspace.read_change(change_id)

        event = approvals.build_rejection_event(
            change_id=change_id,
            actor=request.actor,
            channel=request.channel,
            reason=request.reason,
        )
        approvals.append_event(self._approvals_file, event)

        return RejectResponse(
            change_id=change_id,
            status="rejected",
            event_id=event.event_id,
            timestamp=event.timestamp,
        )

    def archive(self, request: ArchiveRequest) -> ArchiveResponse:
        change_id = validate_change_id(request.change_id)
        archive_path = self.workspace.archive_change(change_id, actor=request.actor)

        from datetime import datetime, timezone

        return ArchiveResponse(
            change_id=change_id,
            archive_path=str(archive_path),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def propose_dict(self, payload: dict) -> dict:
        response = self.propose(ProposeRequest(**payload))
        return asdict(response)

    def get_change_dict(self, change_id: str) -> dict:
        return asdict(self.get_change(change_id))

    def list_changes_dict(self) -> dict:
        return {"changes": [asdict(change) for change in self.list_changes()]}

    def approve_dict(self, payload: dict) -> dict:
        return asdict(self.approve(ApproveRequest(**payload)))

    def reject_dict(self, payload: dict) -> dict:
        return asdict(self.reject(RejectRequest(**payload)))

    def archive_dict(self, payload: dict) -> dict:
        return asdict(self.archive(ArchiveRequest(**payload)))

    @property
    def _approvals_file(self) -> Path:
        if self.config is not None:
            return self.config.approvals_file
        return self.workspace.root / "openspec" / "approvals.jsonl"

    def _get_approval_info(self, change_id: str) -> dict | None:
        return approvals.get_latest_status(self._approvals_file, change_id)

    def _proposal_template(self, request: ProposeRequest) -> str:
        return (
            f"# {request.title}\n\n"
            "## Summary\n\n"
            f"{request.description}\n\n"
            "## Contract Type\n\n"
            f"`{request.type}`\n\n"
            "## Approval\n\n"
            "Approval is required before execution.\n"
        )

    def _tasks_template(self) -> str:
        return (
            "# Tasks\n\n"
            "- [ ] Review generated contract artifacts.\n"
            "- [ ] Request explicit user approval before execution.\n"
            "- [ ] Execute only within the approved contract boundaries.\n"
        )

    def _scheduled_task_spec_template(self, request: ProposeRequest) -> str:
        trigger = request.payload["trigger"]
        return (
            "# Scheduled Task Contract\n\n"
            "## Objective\n\n"
            f"{request.payload['objective']}\n\n"
            "## Trigger\n\n"
            f"- Mode: `{trigger['mode']}`\n"
            f"- Schedule: `{trigger['schedule']}`\n"
            f"- Timezone: `{trigger['timezone']}`\n\n"
            "## Acceptance\n\n"
            + "\n".join(f"- {item}" for item in request.payload["acceptance"])
            + "\n"
        )

    def _external_action_spec_template(self, request: ProposeRequest) -> str:
        action = request.payload["action"]
        return (
            "# External Action Contract\n\n"
            "## Objective\n\n"
            f"{request.payload['objective']}\n\n"
            "## Action\n\n"
            f"- Type: `{action['type']}`\n"
            f"- Target: `{action['target']}`\n"
            f"- Description: {action['description']}\n\n"
            "## Audience\n\n"
            f"{request.payload['audience']}\n\n"
            "## Channel\n\n"
            f"{request.payload['channel']}\n\n"
            "## Constraints\n\n"
            f"{request.payload['constraints']}\n\n"
            "## Acceptance\n\n"
            + "\n".join(f"- {item}" for item in request.payload["acceptance"])
            + "\n"
        )

    def _research_spec_template(self, request: ProposeRequest) -> str:
        scope = request.payload["scope"]
        sources = request.payload["sources"]
        methodology = request.payload["methodology"]
        deliverable = request.payload["deliverable"]
        return (
            "# Research Contract\n\n"
            "## Objective\n\n"
            f"{request.payload['objective']}\n\n"
            "## Scope\n\n"
            "### Included\n"
            + "\n".join(f"- {item}" for item in scope["included"])
            + "\n\n### Excluded\n"
            + "\n".join(f"- {item}" for item in scope["excluded"])
            + "\n\n## Sources\n\n"
            + "\n".join(
                f"- `{s['type']}`: {s['identifier']}"
                for s in sources
            )
            + "\n\n## Methodology\n\n"
            f"- Approach: {methodology['approach']}\n"
            f"- Allowed tools: {', '.join(methodology['allowed_tools'])}\n\n"
            "## Deliverable\n\n"
            f"- Format: `{deliverable['format']}`\n"
            f"- Location: {deliverable['location']}\n\n"
            "## Acceptance\n\n"
            + "\n".join(f"- {item}" for item in request.payload["acceptance"])
            + "\n"
        )
