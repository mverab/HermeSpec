from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .config import load_config
from .errors import OpenSpecMCPError
from .service import OpenSpecContractService


def _serialize_error(error: OpenSpecMCPError) -> dict:
    return {"error": error.to_dict()}


def build_server() -> FastMCP:
    server = FastMCP("openspec-mcp")
    config = load_config()
    service = OpenSpecContractService(config.workspace, config=config)

    @server.tool(name="openspec.propose")
    def propose(payload: dict) -> dict:
        try:
            return service.propose_dict(payload)
        except OpenSpecMCPError as error:
            return _serialize_error(error)

    @server.tool(name="openspec.get_change")
    def get_change(change_id: str) -> dict:
        try:
            return service.get_change_dict(change_id)
        except OpenSpecMCPError as error:
            return _serialize_error(error)

    @server.tool(name="openspec.list_changes")
    def list_changes() -> dict:
        try:
            return service.list_changes_dict()
        except OpenSpecMCPError as error:
            return _serialize_error(error)

    @server.tool(name="openspec.approve")
    def approve(payload: dict) -> dict:
        try:
            return service.approve_dict(payload)
        except OpenSpecMCPError as error:
            return _serialize_error(error)

    @server.tool(name="openspec.reject")
    def reject(payload: dict) -> dict:
        try:
            return service.reject_dict(payload)
        except OpenSpecMCPError as error:
            return _serialize_error(error)

    @server.tool(name="openspec.archive")
    def archive(payload: dict) -> dict:
        try:
            return service.archive_dict(payload)
        except OpenSpecMCPError as error:
            return _serialize_error(error)

    return server


def main() -> None:
    build_server().run()
