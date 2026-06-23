from __future__ import annotations

import pytest

from plb.commands.routing import route_text
from plb.commands.root import get_project_status
from plb.commands.stage import next_step, set_stage_status, stage_status, verify_stage
from plb.core.models import StageStatus, WorkflowStage
from plb.core.paths import ProjectPaths
from plb.state.store import StateStore
from plb.workflow.prompting import (
    StagePromptDocument,
    _approved_stage_input_roles,
    _analysis_inventory,
    _analysis_scope_summary,
    _display_root_for,
    _domain_inventory,
    _domain_coverage_template,
    _domain_input_summary,
    _extract_section,
    _repo_root,
    _read_text,
    _stage_dir,
    _stage_document_coverage_template,
    _stage_document_inventory,
    _stage_document_summary,
    _template_name_for,
    _upstream_input_inventory,
    _upstream_input_coverage_template,
    _upstream_input_summary,
    build_stage_prompt_bundle,
    ensure_stage_inputs_available,
    validate_stage_inputs,
)


def _store(tmp_path):
    store = StateStore(ProjectPaths(root=tmp_path))
    store.ensure_layout()
    return store


def _prepare_discovery_inputs(tmp_path):
    analysis = tmp_path / "analysis"
    (analysis / "story-maps").mkdir(parents=True, exist_ok=True)
    (analysis / "pages").mkdir(parents=True, exist_ok=True)
    (analysis / "features").mkdir(parents=True, exist_ok=True)
    (analysis / "gwt").mkdir(parents=True, exist_ok=True)
    (analysis / "relations").mkdir(parents=True, exist_ok=True)
    (analysis / "brief.md").write_text("Brief", encoding="utf-8")
    (analysis / "story-maps" / "story.md").write_text("Story", encoding="utf-8")
    (analysis / "pages" / "page.md").write_text("Page", encoding="utf-8")
    (analysis / "features" / "index.md").write_text("Feature", encoding="utf-8")
    (analysis / "gwt" / "case.feature").write_text("Feature: Case", encoding="utf-8")
    (analysis / "relations" / "relations.md").write_text("Relations", encoding="utf-8")


def test_route_text_drives_init_status_and_fallbacks(tmp_path):
    store = _store(tmp_path)

    init_result = route_text("请帮我 init", store)
    status_result = route_text("状态", store)
    stage_status_result = route_text("状态 discovery", store)
    fallback_result = route_text("something unrelated", store)

    assert init_result.message == "plb scaffold initialized"
    assert status_result.message == "status snapshot loaded"
    assert status_result.data["project_state"] == "initialized"
    assert stage_status_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert fallback_result.status == "blocked"
    assert "init/status/plan" in fallback_result.data["hint"]


def test_route_text_drives_publish_plan_review_and_stage_commands(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    route_text("init", store)

    publish_result = route_text("publish", store)
    plan_result = route_text("开始 discovery", store)
    packet_result = route_text("packet discovery", store)
    run_result = route_text("run review discovery", store)
    record_result = route_text("record discovery", store)
    approve_result = route_text("approve discovery", store)
    reject_result = route_text("reject discovery", store)
    verify_result = route_text("verify discovery", store)
    next_result = route_text("next discovery", store)
    set_result = route_text("set api", store)

    assert publish_result.data["project_state"] == "published"
    assert plan_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert packet_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert run_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert record_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert approve_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert reject_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert verify_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert next_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert set_result.data["stage"] == WorkflowStage.API.value
    assert set_result.data["status"] == StageStatus.ACTIVE.value


def test_stage_prompt_helpers_cover_empty_and_existing_paths(tmp_path):
    stage_root = tmp_path / "records" / "project-launch-blueprint"
    discovery_dir = stage_root / "discovery"
    discovery_dir.mkdir(parents=True, exist_ok=True)
    (discovery_dir / "method.md").write_text("method", encoding="utf-8")
    missing_dir = _stage_dir(WorkflowStage.DISCOVERY)
    existing_dir = _stage_dir(WorkflowStage.DISCOVERY, stage_root)
    fallback_dir = _stage_dir(WorkflowStage.DISCOVERY, tmp_path)

    assert missing_dir.name == "discovery"
    assert existing_dir == discovery_dir
    assert fallback_dir == _repo_root() / "discovery"
    assert _read_text(discovery_dir / "missing.md") == ""
    assert _analysis_inventory(None) == []
    assert _domain_inventory(None) == []
    assert _upstream_input_inventory(None, WorkflowStage.STATE, ["analysis"]) == ([], [])


def test_prompt_helpers_cover_section_extraction_and_template_selection(tmp_path):
    docs_root = tmp_path / "records" / "project-launch-blueprint"
    stage_dir = docs_root / "discovery"
    stage_dir.mkdir(parents=True, exist_ok=True)

    assert _display_root_for(stage_dir, docs_root) == docs_root
    assert _display_root_for(tmp_path / "elsewhere", docs_root) == _repo_root()
    assert _extract_section("", "## Capability Map Generation") == ""
    assert _extract_section("plain body", "## Capability Map Generation") == "plain body"
    assert (
        _extract_section(
            "## Capability Map Generation\nalpha\nbeta\n## Next\nomega",
            "## Capability Map Generation",
        )
        == "alpha\nbeta"
    )
    assert _extract_section("## Capability Map Generation\nalpha\nbeta", "## Capability Map Generation") == "alpha\nbeta"
    assert _template_name_for(WorkflowStage.DISCOVERY, "generate") == "Capability Map Generation"
    assert _template_name_for(WorkflowStage.DISCOVERY, "review") == "Discovery Capability Map Review"
    assert _template_name_for(WorkflowStage.STATE, "generate") == "Generation"
    assert _template_name_for(WorkflowStage.STATE, "review") == "Review"


def test_prompt_helpers_cover_approval_roles_and_upstream_edge_cases(tmp_path):
    root = tmp_path
    audits = root / ".project-launch-blueprint" / "audits"
    audits.mkdir(parents=True, exist_ok=True)
    (audits / "discovery-packet.json").write_text("abcd", encoding="utf-8")
    (audits / "discovery-review.json").write_text("efgh", encoding="utf-8")

    inventory, missing = _upstream_input_inventory(
        root,
        WorkflowStage.STATE,
        ["analysis", "implementation", "discovery", "state", "domain"],
    )

    assert _approved_stage_input_roles(WorkflowStage.DISCOVERY) == {}
    assert _approved_stage_input_roles(WorkflowStage.IMPLEMENTATION) == {}
    assert _approved_stage_input_roles(WorkflowStage.STATE) == {
        WorkflowStage.DISCOVERY.value: "primary",
        WorkflowStage.DOMAIN.value: "primary",
    }
    assert _approved_stage_input_roles(WorkflowStage.API) == {
        WorkflowStage.DISCOVERY.value: "primary",
        WorkflowStage.DOMAIN.value: "primary",
        WorkflowStage.STATE.value: "primary",
    }
    assert _approved_stage_input_roles(WorkflowStage.DESIGN) == {
        WorkflowStage.DISCOVERY.value: "secondary",
        WorkflowStage.DOMAIN.value: "secondary",
        WorkflowStage.STATE.value: "secondary",
        WorkflowStage.API.value: "primary",
    }
    assert _approved_stage_input_roles(WorkflowStage.SLICE) == {
        WorkflowStage.DISCOVERY.value: "secondary",
        WorkflowStage.DOMAIN.value: "secondary",
        WorkflowStage.STATE.value: "secondary",
        WorkflowStage.API.value: "primary",
        WorkflowStage.DESIGN.value: "primary",
    }
    assert _approved_stage_input_roles(WorkflowStage.GATES) == {
        WorkflowStage.DISCOVERY.value: "primary",
        WorkflowStage.DOMAIN.value: "primary",
        WorkflowStage.STATE.value: "primary",
        WorkflowStage.API.value: "primary",
        WorkflowStage.DESIGN.value: "primary",
        WorkflowStage.SLICE.value: "primary",
    }
    assert inventory == [
        {
            "source_stage": WorkflowStage.DISCOVERY.value,
            "role": "primary",
            "packet_path": ".project-launch-blueprint/audits/discovery-packet.json",
            "review_path": ".project-launch-blueprint/audits/discovery-review.json",
            "size_bytes": 8,
        }
    ]
    assert missing == ["domain"]
    assert _upstream_input_summary(inventory) == {
        "total_inputs": 1,
        "role_counts": {"primary": 1},
        "source_stage_counts": {WorkflowStage.DISCOVERY.value: 1},
    }
    assert _upstream_input_coverage_template(inventory) == [
        {
            "source_stage": WorkflowStage.DISCOVERY.value,
            "role": "primary",
            "packet_path": ".project-launch-blueprint/audits/discovery-packet.json",
            "review_path": ".project-launch-blueprint/audits/discovery-review.json",
            "status": "unmapped",
            "mapped_to": [],
            "reason": "",
            "evidence": [],
        }
    ]
    assert _analysis_scope_summary([]) == {"total_files": 0, "top_level_counts": {}}
    assert _stage_document_inventory([]) == []
    assert _stage_document_summary([]) == {"total_documents": 0, "document_names": []}
    assert _stage_document_coverage_template([]) == []
    assert _domain_input_summary([]) == {"total_inputs": 0, "role_counts": {}}
    assert _domain_coverage_template([]) == []


def test_analysis_and_domain_inventory_return_empty_when_analysis_root_missing(tmp_path):
    assert _analysis_inventory(tmp_path) == []
    assert _domain_inventory(tmp_path) == []


def test_ensure_stage_inputs_available_raises_when_discovery_inputs_are_missing(tmp_path):
    with pytest.raises(Exception) as exc_info:
        ensure_stage_inputs_available(tmp_path, WorkflowStage.DISCOVERY)

    assert "discovery requires user-prepared analysis inputs" in str(exc_info.value)


def test_stage_prompt_bundle_handles_missing_prompt_templates_and_empty_documents(monkeypatch):
    monkeypatch.setattr("plb.workflow.prompting._load_documents", lambda *args, **kwargs: [])

    bundle = build_stage_prompt_bundle(WorkflowStage.STATE, "review")

    assert bundle.documents == []
    assert bundle.prompt_sections == {}
    assert bundle.stage_document_inventory == []
    assert bundle.stage_document_summary == {"total_documents": 0, "document_names": []}
    assert bundle.stage_document_coverage_template == []
    assert bundle.upstream_input_inventory == []
    assert bundle.upstream_input_summary == {}
    assert bundle.upstream_input_coverage_template == []
    assert "stage_document_count: 0" in bundle.user_prompt
    assert "analysis_inventory_count: 0" in bundle.user_prompt


def test_stage_prompt_bundle_handles_no_project_paths_and_missing_inputs(tmp_path):
    bundle = build_stage_prompt_bundle(WorkflowStage.DISCOVERY, "review")

    assert bundle.analysis_inventory == []
    assert bundle.analysis_scope_summary["total_files"] == 0
    assert bundle.analysis_scope_summary["top_level_counts"] == {}
    assert bundle.analysis_coverage_template == []
    assert bundle.domain_input_inventory == []
    assert bundle.upstream_input_inventory == []
    assert "analysis_inventory_count: 0" in bundle.user_prompt

    missing = validate_stage_inputs(tmp_path, WorkflowStage.DISCOVERY)
    assert "analysis/brief.md" in missing

    ensure_stage_inputs_available(tmp_path, WorkflowStage.STATE)


def test_stage_prompt_bundle_builds_domain_inventory_and_stage_documents(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    route_text("init", store)
    route_text("开始 discovery", store)
    route_text("packet discovery", store)
    route_text("run review discovery", store)
    route_text("approve discovery", store)

    bundle = build_stage_prompt_bundle(WorkflowStage.DOMAIN, "review", store.paths)

    assert bundle.domain_input_inventory
    assert bundle.domain_input_summary["total_inputs"] == len(bundle.domain_input_inventory)
    assert len(bundle.domain_coverage_template) == len(bundle.domain_input_inventory)
    assert any(item["role"] == "primary" for item in bundle.domain_input_inventory)
    assert bundle.stage_document_inventory
    assert bundle.stage_document_summary["total_documents"] == len(bundle.stage_document_inventory)
    assert len(bundle.stage_document_coverage_template) == len(bundle.stage_document_inventory)


def test_stage_wrappers_cover_implementation_paths(tmp_path):
    store = _store(tmp_path)
    _prepare_discovery_inputs(tmp_path)

    route_text("init", store)
    route_text("开始 discovery", store)
    route_text("packet discovery", store)
    route_text("run review discovery", store)
    route_text("approve discovery", store)

    from plb.commands.stage import plan_stage

    plan_stage(WorkflowStage.IMPLEMENTATION.value, store, goal="ship the prototype")

    status_result = stage_status(WorkflowStage.IMPLEMENTATION.value, store)
    next_result = next_step(WorkflowStage.IMPLEMENTATION.value, store)
    verify_result = verify_stage(WorkflowStage.IMPLEMENTATION.value, store)

    assert status_result.data["goal_progress"]["total_goals"] >= 1
    assert next_result.data["current_goal"] == "goal-1"
    assert verify_result.status == "go"
