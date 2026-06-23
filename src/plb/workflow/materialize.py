from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from plb.core.paths import ProjectPaths


@dataclass(slots=True)
class MaterializationResult:
    docs_root: Path
    copied_files: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)


TOP_LEVEL_FILES = (
    "README.md",
    "index.md",
    "template-spec.md",
    "cli-architecture.md",
    "workflow-state.md",
    "command-reference.md",
)

STAGE_DIRS = (
    "discovery",
    "domain-model",
    "state-machine",
    "api-contract",
    "design-system",
    "vertical-slice",
    "quality-gates",
    "implementation",
)

ADDITIONAL_DIRS = (
    "adr",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _copy_file(source: Path, target: Path) -> bool:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return False
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return True


def _copy_tree(source_dir: Path, target_dir: Path) -> tuple[list[str], list[str]]:
    copied: list[str] = []
    skipped: list[str] = []
    if not source_dir.exists():
        return copied, skipped
    for path in source_dir.rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(source_dir)
        target = target_dir / relative
        if _copy_file(path, target):
            copied.append(str(target))
        else:
            skipped.append(str(target))
    return copied, skipped


def materialize_project_docs(paths: ProjectPaths) -> MaterializationResult:
    repo_root = _repo_root()
    docs_root = paths.docs_root
    copied: list[str] = []
    skipped: list[str] = []
    docs_root.mkdir(parents=True, exist_ok=True)

    for filename in TOP_LEVEL_FILES:
        source = repo_root / filename
        target = docs_root / filename
        if source.exists():
            if _copy_file(source, target):
                copied.append(str(target))
            else:
                skipped.append(str(target))

    for dirname in STAGE_DIRS:
        source_dir = repo_root / dirname
        target_dir = docs_root / dirname
        stage_copied, stage_skipped = _copy_tree(source_dir, target_dir)
        copied.extend(stage_copied)
        skipped.extend(stage_skipped)

    for dirname in ADDITIONAL_DIRS:
        source_dir = repo_root / dirname
        target_dir = docs_root / dirname
        extra_copied, extra_skipped = _copy_tree(source_dir, target_dir)
        copied.extend(extra_copied)
        skipped.extend(extra_skipped)

    return MaterializationResult(docs_root=docs_root, copied_files=copied, skipped_files=skipped)
