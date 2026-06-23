from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from plb.core.errors import WorkflowStateError
from plb.core.models import WorkflowStage
from plb.core.paths import ProjectPaths


STAGE_DOC_DIRS: dict[WorkflowStage, str] = {
    WorkflowStage.DISCOVERY: "discovery",
    WorkflowStage.DOMAIN: "domain-model",
    WorkflowStage.STATE: "state-machine",
    WorkflowStage.API: "api-contract",
    WorkflowStage.DESIGN: "design-system",
    WorkflowStage.SLICE: "vertical-slice",
    WorkflowStage.GATES: "quality-gates",
    WorkflowStage.IMPLEMENTATION: "implementation",
}


@dataclass(slots=True)
class StagePromptDocument:
    name: str
    path: str
    text: str


@dataclass(slots=True)
class StagePromptBundle:
    stage: WorkflowStage
    purpose: str
    stage_dir: str
    template_name: str
    system_prompt: str
    user_prompt: str
    documents: list[StagePromptDocument] = field(default_factory=list)
    prompt_sections: dict[str, str] = field(default_factory=dict)
    stage_document_inventory: list[dict[str, Any]] = field(default_factory=list)
    stage_document_summary: dict[str, Any] = field(default_factory=dict)
    stage_document_coverage_template: list[dict[str, Any]] = field(default_factory=list)
    upstream_input_inventory: list[dict[str, Any]] = field(default_factory=list)
    upstream_input_summary: dict[str, Any] = field(default_factory=dict)
    upstream_input_coverage_template: list[dict[str, Any]] = field(default_factory=list)
    analysis_inventory: list[dict[str, Any]] = field(default_factory=list)
    analysis_scope_summary: dict[str, Any] = field(default_factory=dict)
    analysis_coverage_template: list[dict[str, Any]] = field(default_factory=list)
    domain_input_inventory: list[dict[str, Any]] = field(default_factory=list)
    domain_input_summary: dict[str, Any] = field(default_factory=dict)
    domain_coverage_template: list[dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "purpose": self.purpose,
            "stage_dir": self.stage_dir,
            "template_name": self.template_name,
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "documents": [
                {"name": document.name, "path": document.path, "text": document.text}
                for document in self.documents
            ],
            "prompt_sections": dict(self.prompt_sections),
            "stage_document_inventory": list(self.stage_document_inventory),
            "stage_document_summary": dict(self.stage_document_summary),
            "stage_document_coverage_template": list(self.stage_document_coverage_template),
            "upstream_input_inventory": list(self.upstream_input_inventory),
            "upstream_input_summary": dict(self.upstream_input_summary),
            "upstream_input_coverage_template": list(self.upstream_input_coverage_template),
            "analysis_inventory": list(self.analysis_inventory),
            "analysis_scope_summary": dict(self.analysis_scope_summary),
            "analysis_coverage_template": list(self.analysis_coverage_template),
            "domain_input_inventory": list(self.domain_input_inventory),
            "domain_input_summary": dict(self.domain_input_summary),
            "domain_coverage_template": list(self.domain_coverage_template),
        }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _stage_dir(stage: WorkflowStage, project_root: Path | None = None) -> Path:
    if project_root is not None:
        candidate = project_root / STAGE_DOC_DIRS[stage]
        if candidate.exists():
            return candidate
    return _repo_root() / STAGE_DOC_DIRS[stage]


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _display_root_for(path: Path, project_root: Path | None = None) -> Path:
    if project_root is not None:
        try:
            path.relative_to(project_root)
            return project_root
        except ValueError:
            pass
    return _repo_root()


def _analysis_inventory(root: Path | None) -> list[dict[str, Any]]:
    if root is None:
        return []
    analysis_dir = root / "analysis"
    if not analysis_dir.exists():
        return []

    records: list[dict[str, Any]] = []
    files = sorted(
        (candidate for candidate in analysis_dir.rglob("*") if candidate.is_file()),
        key=lambda item: item.relative_to(analysis_dir).as_posix(),
    )
    for path in files:
        analysis_path = path.relative_to(analysis_dir).as_posix()
        top_level = analysis_path.split("/", 1)[0] if analysis_path else ""
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "analysis_path": f"analysis/{analysis_path}",
                "top_level": top_level,
                "suffix": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
            }
        )
    return records


def _analysis_scope_summary(inventory: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for item in inventory:
        top_level = str(item.get("top_level", ""))
        counts[top_level] = counts.get(top_level, 0) + 1
    return {"total_files": len(inventory), "top_level_counts": dict(sorted(counts.items()))}


def _analysis_coverage_template(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    template: list[dict[str, Any]] = []
    for item in inventory:
        template.append(
            {
                "path": item["path"],
                "analysis_path": item["analysis_path"],
                "status": "unmapped",
                "covered_by": [],
                "reason": "",
                "evidence": [],
            }
        )
    return template


def _domain_inventory(root: Path | None) -> list[dict[str, Any]]:
    if root is None:
        return []

    records: list[dict[str, Any]] = []

    def add_path(path: Path, *, input_type: str, role: str) -> None:
        if not path.exists():
            return
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "input_type": input_type,
                "role": role,
                "size_bytes": path.stat().st_size,
            }
        )

    audits_dir = root / ".project-launch-blueprint" / "audits"
    add_path(audits_dir / "discovery-packet.json", input_type="approved discovery output", role="primary")
    add_path(audits_dir / "discovery-review.json", input_type="approved discovery output", role="primary")

    analysis_dir = root / "analysis"
    if analysis_dir.exists():
        for path in sorted(
            (candidate for candidate in analysis_dir.rglob("*") if candidate.is_file()),
            key=lambda item: item.relative_to(analysis_dir).as_posix(),
        ):
            analysis_path = path.relative_to(analysis_dir).as_posix()
            if analysis_path == "gwt" or analysis_path.startswith("gwt/"):
                continue
            records.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "input_type": "auxiliary evidence",
                    "role": "secondary",
                    "size_bytes": path.stat().st_size,
                }
            )

    return records


def _domain_input_summary(inventory: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for item in inventory:
        role = str(item.get("role", ""))
        counts[role] = counts.get(role, 0) + 1
    return {"total_inputs": len(inventory), "role_counts": dict(sorted(counts.items()))}


def _domain_coverage_template(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    template: list[dict[str, Any]] = []
    for item in inventory:
        template.append(
            {
                "path": item["path"],
                "input_type": item["input_type"],
                "role": item["role"],
                "status": "unmapped",
                "mapped_to": [],
                "reason": "",
                "evidence": [],
            }
        )
    return template


def _load_documents(stage: WorkflowStage, project_root: Path | None = None) -> list[StagePromptDocument]:
    stage_dir = _stage_dir(stage, project_root=project_root)
    display_root = _display_root_for(stage_dir, project_root=project_root)
    doc_names = ["method.md", "validation-rules.md", "output-schema.md", "prompt-templates.md", "example-output.md", "checklist.md"]
    documents: list[StagePromptDocument] = []
    for name in doc_names:
        path = stage_dir / name
        documents.append(
            StagePromptDocument(
                name=name,
                path=str(path.relative_to(display_root)),
                text=_read_text(path),
            )
        )
    return documents


def _stage_document_inventory(documents: list[StagePromptDocument]) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for document in documents:
        inventory.append(
            {
                "name": document.name,
                "path": document.path,
                "role": "stage_document",
                "size_bytes": len(document.text.encode("utf-8")),
            }
        )
    return inventory


def _stage_document_summary(inventory: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total_documents": len(inventory),
        "document_names": [str(item.get("name", "")) for item in inventory],
    }


def _stage_document_coverage_template(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    template: list[dict[str, Any]] = []
    for item in inventory:
        template.append(
            {
                "name": item["name"],
                "path": item["path"],
                "role": item["role"],
                "status": "unmapped",
                "mapped_to": [],
                "reason": "",
                "evidence": [],
            }
        )
    return template


def _approved_stage_input_roles(stage: WorkflowStage) -> dict[str, str]:
    if stage == WorkflowStage.STATE:
        return {
            WorkflowStage.DISCOVERY.value: "primary",
            WorkflowStage.DOMAIN.value: "primary",
        }
    if stage == WorkflowStage.API:
        return {
            WorkflowStage.DISCOVERY.value: "primary",
            WorkflowStage.DOMAIN.value: "primary",
            WorkflowStage.STATE.value: "primary",
        }
    if stage == WorkflowStage.DESIGN:
        return {
            WorkflowStage.DISCOVERY.value: "secondary",
            WorkflowStage.DOMAIN.value: "secondary",
            WorkflowStage.STATE.value: "secondary",
            WorkflowStage.API.value: "primary",
        }
    if stage == WorkflowStage.SLICE:
        return {
            WorkflowStage.DISCOVERY.value: "secondary",
            WorkflowStage.DOMAIN.value: "secondary",
            WorkflowStage.STATE.value: "secondary",
            WorkflowStage.API.value: "primary",
            WorkflowStage.DESIGN.value: "primary",
        }
    if stage == WorkflowStage.GATES:
        return {
            WorkflowStage.DISCOVERY.value: "primary",
            WorkflowStage.DOMAIN.value: "primary",
            WorkflowStage.STATE.value: "primary",
            WorkflowStage.API.value: "primary",
            WorkflowStage.DESIGN.value: "primary",
            WorkflowStage.SLICE.value: "primary",
        }
    return {}


def _upstream_input_inventory(
    root: Path | None,
    stage: WorkflowStage,
    approved_inputs: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    if root is None:
        return [], []
    audits_dir = root / ".project-launch-blueprint" / "audits"
    role_map = _approved_stage_input_roles(stage)
    inventory: list[dict[str, Any]] = []
    missing: list[str] = []
    for upstream in approved_inputs:
        if upstream == "analysis":
            continue
        if upstream not in role_map:
            continue
        packet_path = audits_dir / f"{upstream}-packet.json"
        review_path = audits_dir / f"{upstream}-review.json"
        if not packet_path.exists() or not review_path.exists():
            missing.append(upstream)
            continue
        inventory.append(
            {
                "source_stage": upstream,
                "role": role_map[upstream],
                "packet_path": packet_path.relative_to(root).as_posix(),
                "review_path": review_path.relative_to(root).as_posix(),
                "size_bytes": packet_path.stat().st_size + review_path.stat().st_size,
            }
        )
    return inventory, sorted(set(missing), key=lambda item: approved_inputs.index(item) if item in approved_inputs else 0)


def _upstream_input_summary(inventory: list[dict[str, Any]]) -> dict[str, Any]:
    role_counts: dict[str, int] = {}
    stage_counts: dict[str, int] = {}
    for item in inventory:
        role = str(item.get("role", ""))
        source_stage = str(item.get("source_stage", ""))
        role_counts[role] = role_counts.get(role, 0) + 1
        stage_counts[source_stage] = stage_counts.get(source_stage, 0) + 1
    return {
        "total_inputs": len(inventory),
        "role_counts": dict(sorted(role_counts.items())),
        "source_stage_counts": dict(sorted(stage_counts.items())),
    }


def _upstream_input_coverage_template(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    template: list[dict[str, Any]] = []
    for item in inventory:
        template.append(
            {
                "source_stage": item["source_stage"],
                "role": item["role"],
                "packet_path": item["packet_path"],
                "review_path": item["review_path"],
                "status": "unmapped",
                "mapped_to": [],
                "reason": "",
                "evidence": [],
            }
        )
    return template


def _has_files(path: Path, pattern: str) -> bool:
    return any(path.glob(pattern))


def _has_file(path: Path, relative: str) -> bool:
    return (path / relative).exists()


def validate_stage_inputs(root: Path, stage: WorkflowStage) -> list[str]:
    if stage != WorkflowStage.DISCOVERY:
        return []

    analysis_dir = root / "analysis"
    missing: list[str] = []
    if not _has_file(analysis_dir, "brief.md"):
        missing.append("analysis/brief.md")
    if not _has_files(analysis_dir / "story-maps", "*.md"):
        missing.append("analysis/story-maps/*.md")
    if not _has_files(analysis_dir / "pages", "*.md"):
        missing.append("analysis/pages/*.md")
    if not _has_file(analysis_dir, "features/index.md"):
        missing.append("analysis/features/index.md")
    if not _has_files(analysis_dir / "gwt", "*.feature"):
        missing.append("analysis/gwt/*.feature")
    if not _has_files(analysis_dir / "relations", "*.md"):
        missing.append("analysis/relations/*.md")
    return missing


def ensure_stage_inputs_available(root: Path, stage: WorkflowStage) -> None:
    missing = validate_stage_inputs(root, stage)
    if missing:
        raise WorkflowStateError(
            f"{stage.value} requires user-prepared analysis inputs. Missing: {', '.join(missing)}"
        )


def _extract_section(text: str, heading: str) -> str:
    if not text.strip():
        return ""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if heading.lower() in line.lower():
            start = index + 1
            break
    if start is None:
        return text.strip()
    collected: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def _template_name_for(stage: WorkflowStage, purpose: str) -> str:
    if stage == WorkflowStage.DISCOVERY:
        return "Capability Map Generation" if purpose == "generate" else "Discovery Capability Map Review"
    if purpose == "generate":
        return "Generation"
    return "Review"


def build_stage_prompt_bundle(stage: WorkflowStage, purpose: str, project_paths: ProjectPaths | None = None) -> StagePromptBundle:
    project_root = project_paths.docs_root if project_paths is not None else None
    analysis_root = project_paths.root if project_paths is not None else None
    stage_dir = _stage_dir(stage, project_root=project_root)
    display_root = _display_root_for(stage_dir, project_root=project_root)
    documents = _load_documents(stage, project_root=project_root)
    stage_document_inventory = _stage_document_inventory(documents)
    stage_document_summary = _stage_document_summary(stage_document_inventory)
    stage_document_coverage_template = _stage_document_coverage_template(stage_document_inventory)
    prompt_templates = next((document for document in documents if document.name == "prompt-templates.md"), None)
    template_name = _template_name_for(stage, purpose)
    template_text = ""
    prompt_sections: dict[str, str] = {}
    analysis_inventory: list[dict[str, Any]] = []
    analysis_scope_summary: dict[str, Any] = {}
    analysis_coverage_template: list[dict[str, Any]] = []
    domain_input_inventory: list[dict[str, Any]] = []
    domain_input_summary: dict[str, Any] = {}
    domain_coverage_template: list[dict[str, Any]] = []
    upstream_input_inventory: list[dict[str, Any]] = []
    upstream_input_summary: dict[str, Any] = {}
    upstream_input_coverage_template: list[dict[str, Any]] = []
    if stage == WorkflowStage.DISCOVERY:
        analysis_inventory = _analysis_inventory(analysis_root)
        analysis_scope_summary = _analysis_scope_summary(analysis_inventory)
        analysis_coverage_template = _analysis_coverage_template(analysis_inventory)
    if stage == WorkflowStage.DOMAIN:
        domain_input_inventory = _domain_inventory(analysis_root)
        domain_input_summary = _domain_input_summary(domain_input_inventory)
        domain_coverage_template = _domain_coverage_template(domain_input_inventory)
    if prompt_templates is not None:
        prompt_sections = {
            "source": prompt_templates.text,
            "selected": _extract_section(prompt_templates.text, f"## {template_name}"),
        }
        template_text = prompt_sections["selected"] or prompt_templates.text

    system_prompt = (
        f"You are the isolated {purpose} subagent for {stage.value}. "
        f"Follow the stage documents exactly and do not inherit generation context."
    )
    doc_digest = "\n\n".join(
        f"[{document.name}]\n{document.text.strip()}" for document in documents if document.text.strip()
    )
    user_prompt = "\n\n".join(
        [
            f"stage: {stage.value}",
            f"purpose: {purpose}",
            f"stage_dir: {stage_dir.relative_to(display_root)}",
            f"template_name: {template_name}",
            f"stage_document_count: {len(stage_document_inventory)}",
            f"upstream_input_count: {len(upstream_input_inventory)}",
            f"analysis_inventory_count: {len(analysis_inventory)}",
            template_text.strip(),
            doc_digest,
        ]
    ).strip()
    if stage_document_inventory:
        inventory_lines = "\n".join(
            f"- {item['path']} [{item['role']}]" for item in stage_document_inventory
        )
        user_prompt = "\n\n".join(
            [
                user_prompt,
                "stage_document_inventory:",
                inventory_lines,
                "coverage_rule:",
                "Every stage_document_inventory item must appear exactly once in the coverage matrix, with either a direct use or an explicit exclusion reason.",
            ]
        ).strip()
    if analysis_inventory:
        inventory_lines = "\n".join(f"- {item['analysis_path']}" for item in analysis_inventory)
        user_prompt = "\n\n".join(
            [
                user_prompt,
                "analysis_inventory:",
                inventory_lines,
                "coverage_rule:",
                "Every analysis_inventory item must appear exactly once in the coverage matrix, with either a capability mapping or an explicit exclusion reason.",
            ]
        ).strip()
    if domain_input_inventory:
        inventory_lines = "\n".join(f"- {item['path']} [{item['role']}/{item['input_type']}]" for item in domain_input_inventory)
        user_prompt = "\n\n".join(
            [
                user_prompt,
                "domain_input_inventory:",
                inventory_lines,
                "coverage_rule:",
                "Every domain_input_inventory item must appear exactly once in the coverage matrix, with either a model mapping or an explicit exclusion reason.",
            ]
        ).strip()
    if project_paths is not None and stage_dir.is_relative_to(project_paths.root):
        display_root = project_paths.root
    else:
        display_root = _repo_root()

    return StagePromptBundle(
        stage=stage,
        purpose=purpose,
        stage_dir=str(stage_dir.relative_to(display_root)),
        template_name=template_name,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        documents=documents,
        prompt_sections=prompt_sections,
        stage_document_inventory=stage_document_inventory,
        stage_document_summary=stage_document_summary,
        stage_document_coverage_template=stage_document_coverage_template,
        upstream_input_inventory=upstream_input_inventory,
        upstream_input_summary=upstream_input_summary,
        upstream_input_coverage_template=upstream_input_coverage_template,
        analysis_inventory=analysis_inventory,
        analysis_scope_summary=analysis_scope_summary,
        analysis_coverage_template=analysis_coverage_template,
        domain_input_inventory=domain_input_inventory,
        domain_input_summary=domain_input_summary,
        domain_coverage_template=domain_coverage_template,
    )
