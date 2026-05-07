from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from .errors import OpenSpecMCPError


@dataclass(frozen=True)
class OpenSpecCLI:
    bin_name: str
    workspace: Path

    def ensure_available(self) -> str:
        resolved = shutil.which(self.bin_name)
        if resolved is None:
            raise OpenSpecMCPError(
                "OPENSPEC_CLI_UNAVAILABLE",
                f"OpenSpec CLI is unavailable: {self.bin_name}",
                {"bin": self.bin_name, "workspace": str(self.workspace)},
            )
        return resolved
