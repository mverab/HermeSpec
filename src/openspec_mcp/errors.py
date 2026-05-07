from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OpenSpecMCPError(Exception):
    code: str
    message: str
    detail: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "detail": self.detail}


def invalid_input(message: str, **detail: Any) -> OpenSpecMCPError:
    return OpenSpecMCPError("INVALID_INPUT", message, detail)
