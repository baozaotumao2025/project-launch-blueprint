from __future__ import annotations

import pytest

from plb.commands.routing import route_text
from plb.commands.review import approve_review, packet_review, run_review
from plb.commands.stage import next_step, plan_stage
from plb.core.models import StageStatus, WorkflowStage
from plb.core.paths import ProjectPaths
from plb.state.store import StateStore
from plb.workflow.registry import STAGE_ORDER
from plb.workflow.prompting import build_stage_prompt_bundle


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
    (analysis / "notes.txt").write_text("Notes", encoding="utf-8")


def _complete_discovery_and_domain(store):
    plan_stage(WorkflowStage.DISCOVERY.value, store, goal="discover launch scope")
    packet_review(WorkflowStage.DISCOVERY.value, store)
    run_review(WorkflowStage.DISCOVERY.value, store)
    approve_review(WorkflowStage.DISCOVERY.value, store)

    plan_stage(WorkflowStage.DOMAIN.value, store, goal="scope domain boundary")
    packet_review(WorkflowStage.DOMAIN.value, store)
    run_review(WorkflowStage.DOMAIN.value, store)
    approve_review(WorkflowStage.DOMAIN.value, store)


def _goal_for_stage(stage: WorkflowStage) -> str:
    return {
        WorkflowStage.DISCOVERY: "discover launch scope",
        WorkflowStage.DOMAIN: "scope domain boundary",
        WorkflowStage.STATE: "model state transitions",
        WorkflowStage.API: "shape api contract",
        WorkflowStage.DESIGN: "define design system rules",
        WorkflowStage.SLICE: "assemble a vertical slice",
        WorkflowStage.GATES: "validate implementation gates",
    }[stage]


def _prepare_through_stage(store, target_stage: WorkflowStage) -> None:
    for stage in STAGE_ORDER:
        if stage == target_stage:
            break
        plan_stage(stage.value, store, goal=_goal_for_stage(stage))
        packet_review(stage.value, store)
        run_review(stage.value, store)
        approve_review(stage.value, store)


def _packet_payload(store, stage: WorkflowStage) -> dict[str, object]:
    packet = store.read_review_artifact(stage, "packet")
    assert packet is not None
    payload = packet["payload"]
    assert isinstance(payload, dict)
    return payload


def test_discovery_prompt_bundle_loads_method_templates_and_schema():
    bundle = build_stage_prompt_bundle(WorkflowStage.DISCOVERY, "review")

    assert bundle.stage == WorkflowStage.DISCOVERY
    assert bundle.purpose == "review"
    assert bundle.template_name == "Discovery Capability Map Review"
    assert bundle.system_prompt
    assert bundle.user_prompt
    assert len(bundle.documents) == 6
    assert bundle.documents[0].name == "method.md"
    assert "analysis" in bundle.documents[0].text
    assert "validation-rules" not in bundle.system_prompt.lower()
    assert "Capability Map Generation" in bundle.prompt_sections["source"]


def test_discovery_prompt_bundle_builds_analysis_inventory_and_coverage_template(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    bundle = build_stage_prompt_bundle(WorkflowStage.DISCOVERY, "review", store.paths)

    inventory_paths = [item["path"] for item in bundle.analysis_inventory]

    assert bundle.analysis_scope_summary["total_files"] == len(bundle.analysis_inventory)
    assert "analysis/notes.txt" in inventory_paths
    assert len(bundle.analysis_coverage_template) == len(bundle.analysis_inventory)
    assert [item["path"] for item in bundle.analysis_coverage_template] == inventory_paths
    assert all(item["status"] == "unmapped" for item in bundle.analysis_coverage_template)


def test_review_packet_embeds_prompt_bundle_and_route_text_uses_same_flow(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    packet_result = packet_review(WorkflowStage.DISCOVERY.value, store)
    packet_payload = store.read_review_artifact(WorkflowStage.DISCOVERY, "packet")

    assert packet_result.data["prompt_bundle"]["stage"] == WorkflowStage.DISCOVERY.value
    assert packet_payload["payload"]["prompt_bundle"]["stage"] == WorkflowStage.DISCOVERY.value
    assert packet_payload["payload"]["prompt_bundle"]["documents"][0]["name"] == "method.md"
    assert packet_payload["payload"]["analysis_inventory"]
    assert packet_payload["payload"]["analysis_scope_summary"]["total_files"] == len(
        packet_payload["payload"]["analysis_inventory"]
    )
    assert len(packet_payload["payload"]["analysis_coverage_template"]) == len(
        packet_payload["payload"]["analysis_inventory"]
    )
    assert packet_payload["payload"]["stage_document_inventory"]
    assert packet_payload["payload"]["stage_document_summary"]["total_documents"] == len(
        packet_payload["payload"]["stage_document_inventory"]
    )
    assert len(packet_payload["payload"]["stage_document_coverage_template"]) == len(
        packet_payload["payload"]["stage_document_inventory"]
    )

    route_result = route_text("开始 discovery", store)
    assert route_result.data["stage"] == WorkflowStage.DISCOVERY.value
    assert route_result.data["status"] == "active"


def test_discovery_review_run_rejects_inventory_coverage_mismatch(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    packet_review(WorkflowStage.DISCOVERY.value, store)
    packet = store.read_review_artifact(WorkflowStage.DISCOVERY, "packet")
    packet["payload"]["analysis_coverage_template"] = packet["payload"]["analysis_coverage_template"][:-1]
    store.write_review_artifact(WorkflowStage.DISCOVERY, "packet", packet)

    result = run_review(WorkflowStage.DISCOVERY.value, store)
    worker_result = store.read_review_artifact(WorkflowStage.DISCOVERY, "review")

    assert result.data["worker_review_state"] == "needs_revision"
    assert worker_result["review_state"] == "needs_revision"
    assert any("analysis_coverage_template" in violation or "analysis_scope_summary" in violation for violation in worker_result["violations"])


def test_domain_review_packet_and_run_use_input_inventory(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    plan_stage(WorkflowStage.DISCOVERY.value, store, goal="discover launch scope")
    packet_review(WorkflowStage.DISCOVERY.value, store)
    run_review(WorkflowStage.DISCOVERY.value, store)
    approve_review(WorkflowStage.DISCOVERY.value, store)

    packet_result = packet_review(WorkflowStage.DOMAIN.value, store)
    packet_payload = store.read_review_artifact(WorkflowStage.DOMAIN, "packet")

    assert packet_result.data["prompt_bundle"]["stage"] == WorkflowStage.DOMAIN.value
    assert packet_payload["payload"]["domain_input_inventory"]
    assert packet_payload["payload"]["domain_input_summary"]["total_inputs"] == len(
        packet_payload["payload"]["domain_input_inventory"]
    )
    assert len(packet_payload["payload"]["domain_coverage_template"]) == len(
        packet_payload["payload"]["domain_input_inventory"]
    )
    assert any(item["role"] == "primary" for item in packet_payload["payload"]["domain_input_inventory"])

    result = run_review(WorkflowStage.DOMAIN.value, store)
    worker_result = store.read_review_artifact(WorkflowStage.DOMAIN, "review")

    assert result.data["worker_review_state"] in {"passed", "needs_revision"}
    assert worker_result["review_state"] == result.data["worker_review_state"]


def test_domain_review_run_rejects_input_coverage_mismatch(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    plan_stage(WorkflowStage.DISCOVERY.value, store, goal="discover launch scope")
    packet_review(WorkflowStage.DISCOVERY.value, store)
    run_review(WorkflowStage.DISCOVERY.value, store)
    approve_review(WorkflowStage.DISCOVERY.value, store)

    packet_review(WorkflowStage.DOMAIN.value, store)
    packet = store.read_review_artifact(WorkflowStage.DOMAIN, "packet")
    packet["payload"]["domain_coverage_template"] = packet["payload"]["domain_coverage_template"][:-1]
    store.write_review_artifact(WorkflowStage.DOMAIN, "packet", packet)

    result = run_review(WorkflowStage.DOMAIN.value, store)
    worker_result = store.read_review_artifact(WorkflowStage.DOMAIN, "review")

    assert result.data["worker_review_state"] == "needs_revision"
    assert worker_result["review_state"] == "needs_revision"
    assert any("domain_coverage_template" in violation or "domain_input_summary" in violation for violation in worker_result["violations"])


def test_state_review_packet_and_run_use_stage_document_inventory(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    _complete_discovery_and_domain(store)

    plan_stage(WorkflowStage.STATE.value, store, goal="model state transitions")
    bundle = build_stage_prompt_bundle(WorkflowStage.STATE, "review", store.paths)
    assert bundle.stage_document_inventory
    assert bundle.stage_document_summary["total_documents"] == len(bundle.stage_document_inventory)
    assert len(bundle.stage_document_coverage_template) == len(bundle.stage_document_inventory)

    packet_result = packet_review(WorkflowStage.STATE.value, store)
    packet_payload = store.read_review_artifact(WorkflowStage.STATE, "packet")

    assert packet_result.data["prompt_bundle"]["stage"] == WorkflowStage.STATE.value
    assert packet_payload["payload"]["upstream_input_inventory"]
    assert packet_payload["payload"]["upstream_input_summary"]["total_inputs"] == len(
        packet_payload["payload"]["upstream_input_inventory"]
    )
    assert len(packet_payload["payload"]["upstream_input_coverage_template"]) == len(
        packet_payload["payload"]["upstream_input_inventory"]
    )
    assert [item["source_stage"] for item in packet_payload["payload"]["upstream_input_inventory"]] == [
        WorkflowStage.DISCOVERY.value,
        WorkflowStage.DOMAIN.value,
    ]
    assert packet_payload["payload"]["stage_document_inventory"]
    assert packet_payload["payload"]["stage_document_summary"]["total_documents"] == len(
        packet_payload["payload"]["stage_document_inventory"]
    )
    assert len(packet_payload["payload"]["stage_document_coverage_template"]) == len(
        packet_payload["payload"]["stage_document_inventory"]
    )

    result = run_review(WorkflowStage.STATE.value, store)
    worker_result = store.read_review_artifact(WorkflowStage.STATE, "review")

    assert result.data["worker_review_state"] in {"passed", "needs_revision"}
    assert worker_result["review_state"] == result.data["worker_review_state"]


def test_state_review_run_rejects_stage_document_coverage_mismatch(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    _complete_discovery_and_domain(store)

    plan_stage(WorkflowStage.STATE.value, store, goal="model state transitions")
    packet_review(WorkflowStage.STATE.value, store)
    packet = store.read_review_artifact(WorkflowStage.STATE, "packet")
    packet["payload"]["stage_document_coverage_template"] = packet["payload"]["stage_document_coverage_template"][:-1]
    store.write_review_artifact(WorkflowStage.STATE, "packet", packet)

    result = run_review(WorkflowStage.STATE.value, store)
    worker_result = store.read_review_artifact(WorkflowStage.STATE, "review")

    assert result.data["worker_review_state"] == "needs_revision"
    assert worker_result["review_state"] == "needs_revision"
    assert any(
        "stage_document_coverage_template" in violation or "stage_document_summary" in violation
        for violation in worker_result["violations"]
    )


def test_state_review_run_rejects_upstream_input_coverage_mismatch(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    _complete_discovery_and_domain(store)

    plan_stage(WorkflowStage.STATE.value, store, goal="model state transitions")
    packet_review(WorkflowStage.STATE.value, store)
    packet = store.read_review_artifact(WorkflowStage.STATE, "packet")
    packet["payload"]["upstream_input_coverage_template"] = packet["payload"]["upstream_input_coverage_template"][:-1]
    store.write_review_artifact(WorkflowStage.STATE, "packet", packet)

    result = run_review(WorkflowStage.STATE.value, store)
    worker_result = store.read_review_artifact(WorkflowStage.STATE, "review")

    assert result.data["worker_review_state"] == "needs_revision"
    assert worker_result["review_state"] == "needs_revision"
    assert any(
        "upstream_input_coverage_template" in violation or "upstream_input_summary" in violation
        for violation in worker_result["violations"]
    )


@pytest.mark.parametrize(
    "stage, expected_upstream_count",
    [
        (WorkflowStage.API, 3),
        (WorkflowStage.DESIGN, 4),
        (WorkflowStage.SLICE, 5),
        (WorkflowStage.GATES, 6),
    ],
)
def test_late_stage_packets_and_runs_pass_with_expected_inventories(tmp_path, stage, expected_upstream_count):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    _prepare_through_stage(store, stage)

    plan_stage(stage.value, store, goal=_goal_for_stage(stage))
    packet_review(stage.value, store)
    payload = _packet_payload(store, stage)

    assert payload["stage_document_inventory"]
    assert payload["stage_document_summary"]["total_documents"] == len(payload["stage_document_inventory"])
    assert len(payload["stage_document_coverage_template"]) == len(payload["stage_document_inventory"])
    assert payload["upstream_input_inventory"]
    assert payload["upstream_input_summary"]["total_inputs"] == len(payload["upstream_input_inventory"])
    assert len(payload["upstream_input_coverage_template"]) == len(payload["upstream_input_inventory"])
    assert len(payload["upstream_input_inventory"]) == expected_upstream_count

    result = run_review(stage.value, store)
    worker_result = store.read_review_artifact(stage, "review")

    assert result.data["worker_review_state"] == "passed"
    assert worker_result["review_state"] == "passed"
    assert worker_result["violations"] == []

    approve_review(stage.value, store)
    next_result = next_step(stage.value, store)
    assert next_result.data["allowed"] is True


def test_gates_next_step_allowed_with_no_follow_up_stage(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    _prepare_through_stage(store, WorkflowStage.GATES)

    plan_stage(WorkflowStage.GATES.value, store, goal=_goal_for_stage(WorkflowStage.GATES))
    packet_review(WorkflowStage.GATES.value, store)
    run_review(WorkflowStage.GATES.value, store)
    approve_review(WorkflowStage.GATES.value, store)

    next_result = next_step(WorkflowStage.GATES.value, store)

    assert next_result.data["allowed"] is True
    assert next_result.data["next_stage"] == WorkflowStage.IMPLEMENTATION.value
    assert next_result.data["next_status"] == StageStatus.ACTIVE.value


@pytest.mark.parametrize(
    "stage, tamper_mode, expected_violation_fragment",
    [
        (
            WorkflowStage.API,
            "drop_upstream_coverage",
            "upstream_input_coverage_template must mirror upstream_input_inventory order and source stages",
        ),
        (
            WorkflowStage.DESIGN,
            "reverse_upstream_inventory",
            "upstream_input_coverage_template must mirror upstream_input_inventory order and source stages",
        ),
        (
            WorkflowStage.SLICE,
            "mark_stage_document_mapped",
            "stage_document_coverage_template[0].status must start as unmapped",
        ),
        (
            WorkflowStage.GATES,
            "inflate_stage_document_summary",
            "stage_document_summary.total_documents must equal stage_document_inventory length",
        ),
    ],
)
def test_late_stage_packets_reject_distinct_tampering_and_block_next(
    tmp_path,
    stage,
    tamper_mode,
    expected_violation_fragment,
):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    _prepare_through_stage(store, stage)

    plan_stage(stage.value, store, goal=_goal_for_stage(stage))
    packet_review(stage.value, store)
    payload = _packet_payload(store, stage)

    if tamper_mode == "drop_upstream_coverage":
        payload["upstream_input_coverage_template"] = payload["upstream_input_coverage_template"][:-1]
    elif tamper_mode == "reverse_upstream_inventory":
        payload["upstream_input_inventory"] = list(reversed(payload["upstream_input_inventory"]))
    elif tamper_mode == "mark_stage_document_mapped":
        payload["stage_document_coverage_template"][0]["status"] = "mapped"
    elif tamper_mode == "inflate_stage_document_summary":
        payload["stage_document_summary"]["total_documents"] += 1
    else:
        raise AssertionError(f"unknown tamper mode: {tamper_mode}")

    store.write_review_artifact(stage, "packet", {**store.read_review_artifact(stage, "packet"), "payload": payload})

    result = run_review(stage.value, store)
    worker_result = store.read_review_artifact(stage, "review")

    assert result.data["worker_review_state"] == "needs_revision"
    assert worker_result["review_state"] == "needs_revision"
    assert any(expected_violation_fragment in violation for violation in worker_result["violations"])

    next_result = next_step(stage.value, store)
    assert next_result.data["allowed"] is False
    assert store.load_stage(stage).status.value == "blocked"
