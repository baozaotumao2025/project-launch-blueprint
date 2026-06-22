from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


RUNTIME_DIR_NAME = ".project-launch-blueprint"
DOCS_DIR_NAME = "records/project-launch-blueprint"
ROOT_ENV_VAR = "PLB_ROOT_DIR"


@dataclass(frozen=True, slots=True)
class ProjectPaths:
    """Resolved paths for a plb workspace."""

    root: Path

    @property
    def runtime_dir(self) -> Path:
        return self.root / RUNTIME_DIR_NAME

    @property
    def state_db(self) -> Path:
        return self.runtime_dir / "state.db"

    @property
    def logs_dir(self) -> Path:
        return self.runtime_dir / "logs"

    @property
    def audits_dir(self) -> Path:
        return self.runtime_dir / "audits"

    @property
    def exports_dir(self) -> Path:
        return self.runtime_dir / "exports"

    @property
    def backups_dir(self) -> Path:
        return self.runtime_dir / "backups"

    @property
    def projections_dir(self) -> Path:
        return self.runtime_dir / "projections"

    @property
    def docs_root(self) -> Path:
        return self.root / DOCS_DIR_NAME


def resolve_project_root(value: str | None = None) -> Path:
    env_value = os.environ.get(ROOT_ENV_VAR)
    candidate = value or env_value
    return Path(candidate).expanduser().resolve() if candidate else Path.cwd().resolve()
