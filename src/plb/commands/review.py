from __future__ import annotations

import json

from plb.core.models import CommandResult, ReviewState, StageHealth, StageLifecyclePhase, StageStatus, WorkflowStage
from plb.core.errors import WorkflowStateError
from plb.review.runner import FilesystemReviewRunner, build_review_packet
from plb.state.store import StateStore
from plb.workflow.prompting import (
    _upstream_input_coverage_template,
    _upstream_input_inventory,
    _upstream_input_summary,
    build_stage_prompt_bundle,
    ensure_stage_inputs_available,
)
from plb.workflow.registry import STAGE_ORDER


def _normalize_stage(stage: str) -> WorkflowStage:
    return WorkflowStage(stage)


def _approved_inputs(store: StateStore, workflow_stage: WorkflowStage) -> list[str]:
    index = STAGE_ORDER.index(workflow_stage)
    approved: list[str] = []
    if index == 0:
        approved.append("analysis")
        return approved
    for upstream in STAGE_ORDER[:index]:
        if store.load_stage(upstream).status.value == "completed":
            approved.append(upstream.value)
    return approved or ["analysis"]


def _counterexample_prompts(workflow_stage: WorkflowStage) -> list[str]:
    stage = workflow_stage.value
    return [
        f"What would make the {stage} packet invalid?",
        f"Which upstream assumption could break {stage}?",
        f"What rollback point should be used if {stage} fails?",
    ]


def _domain_input_requirements_met(prompt_bundle: dict[str, object], approved_inputs: list[str]) -> bool:
    if "discovery" not in approved_inputs:
        return False
    inventory = prompt_bundle.get("domain_input_inventory")
    if not isinstance(inventory, list) or not inventory:
        return False
    return any(
        isinstance(item, dict) and str(item.get("role", "")) == "primary"
        for item in inventory
    )


def _stage_document_requirements_met(prompt_bundle: dict[str, object]) -> bool:
    inventory = prompt_bundle.get("stage_document_inventory")
    summary = prompt_bundle.get("stage_document_summary")
    coverage = prompt_bundle.get("stage_document_coverage_template")
    if not isinstance(inventory, list) or not inventory:
        return False
    if not isinstance(summary, dict):
        return False
    if not isinstance(coverage, list) or not coverage:
        return False
    return len(inventory) == len(coverage)


def _upstream_input_requirements_met(prompt_bundle: dict[str, object], approved_inputs: list[str]) -> bool:
    inventory = prompt_bundle.get("upstream_input_inventory")
    summary = prompt_bundle.get("upstream_input_summary")
    coverage = prompt_bundle.get("upstream_input_coverage_template")
    if not isinstance(inventory, list) or not inventory:
        return False
    if not isinstance(summary, dict):
        return False
    if not isinstance(coverage, list) or not coverage:
        return False
    ordered_sources = [item.get("source_stage") for item in inventory if isinstance(item, dict)]
    approved_sources = [stage for stage in approved_inputs if stage != "analysis"]
    return ordered_sources == approved_sources and len(inventory) == len(coverage)


def _coerce_review_state(result_state: object) -> ReviewState:
    mapping = {
        ReviewState.PASSED.value: ReviewState.PASSED,
        ReviewState.NEEDS_REVISION.value: ReviewState.NEEDS_REVISION,
        ReviewState.FAILED.value: ReviewState.FAILED,
    }
    if isinstance(result_state, str) and result_state in mapping:
        return mapping[result_state]
    return ReviewState.FAILED


def _health_from_review_state(review_state: ReviewState) -> StageHealth:
    if review_state == ReviewState.PASSED:
        return StageHealth.STABLE
    if review_state == ReviewState.NEEDS_REVISION:
        return StageHealth.DEGRADED
    return StageHealth.FAILED


def _load_worker_review_result(workflow_stage: WorkflowStage, store: StateStore) -> dict[str, object]:
    review_result = store.read_review_artifact(workflow_stage, "review")
    if review_result:
        copied = dict(review_result)
        copied["_source"] = "artifact"
        return copied
    review_record = store.load_review(workflow_stage)
    payload = review_record.payload
    if not isinstance(payload, dict):
        return {}
    result = payload.get("result")
    if isinstance(result, dict):
        copied = dict(result)
        copied["_source"] = "record"
        return copied
    worker_review_state = payload.get("worker_review_state")
    if isinstance(worker_review_state, str):
        return {"review_state": worker_review_state, "_source": "record_state"}
    return {}


def _store_worker_review_outcome(stage: str, store: StateStore, action: str) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    worker_result = _load_worker_review_result(workflow_stage, store)
    result_state = worker_result.get("review_state", ReviewState.FAILED.value)
    final_state = _coerce_review_state(result_state)
    finalized = action in {"approve", "reject"}
    stage_status = (
        StageStatus.COMPLETED
        if finalized and final_state == ReviewState.PASSED
        else StageStatus.NEEDS_REVISION
        if finalized
        else store.load_stage(workflow_stage).status
    )
    lifecycle_phase = (
        StageLifecyclePhase.APPROVED
        if action == "approve" and final_state == ReviewState.PASSED
        else StageLifecyclePhase.REJECTED
        if finalized
        else StageLifecyclePhase.REVIEW_RECORDED
    )
    lifecycle_health = _health_from_review_state(final_state)
    record = store.set_review(
        workflow_stage,
        final_state,
        {
            "decision": action,
            "recorded": action == "record",
            "result": worker_result,
            "result_state": result_state,
            "worker_review_state": result_state,
            "recorded_review_state": final_state.value,
            "source": "worker_verdict",
            "result_source": worker_result.get("_source", "fallback"),
        },
    )
    store.set_stage(
        workflow_stage,
        stage_status,
        {
            "review_state": final_state.value,
            "review_action": action,
            "review_result_source": worker_result.get("_source", "fallback"),
            "rollback_point": worker_result.get("rollback_point", "analysis"),
        },
    )
    store.record_stage_lifecycle(
        workflow_stage,
        f"review_{action}",
        phase=lifecycle_phase,
        health=lifecycle_health,
        status=stage_status,
        details={
            "worker_review_state": final_state.value,
            "review_action": action,
            "result_source": worker_result.get("_source", "fallback"),
            "rollback_point": worker_result.get("rollback_point", "analysis"),
        },
    )
    return CommandResult(
        status="ok",
        message=f"review {action} for {workflow_stage.value} stored from worker verdict",
        data={
            "stage": workflow_stage.value,
            "review_state": record.state.value,
            "result_state": result_state,
            "recorded_review_state": final_state.value,
            "worker_review_state": result_state,
            "decision": action,
            "result_source": worker_result.get("_source", "fallback"),
        },
    )


def packet_review(stage: str, store: StateStore) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    ensure_stage_inputs_available(store.paths.root, workflow_stage)
    stage_record = store.load_stage(workflow_stage)
    rollback_point = stage_record.payload.get("rollback_point", "analysis")
    prompt_bundle = build_stage_prompt_bundle(workflow_stage, "review", store.paths)
    analysis_inventory = prompt_bundle.analysis_inventory
    analysis_scope_summary = prompt_bundle.analysis_scope_summary
    analysis_coverage_template = prompt_bundle.analysis_coverage_template
    stage_document_inventory = prompt_bundle.stage_document_inventory
    stage_document_summary = prompt_bundle.stage_document_summary
    stage_document_coverage_template = prompt_bundle.stage_document_coverage_template
    domain_input_inventory = prompt_bundle.domain_input_inventory
    domain_input_summary = prompt_bundle.domain_input_summary
    domain_coverage_template = prompt_bundle.domain_coverage_template
    approved_inputs = _approved_inputs(store, workflow_stage)
    upstream_input_inventory = []
    upstream_input_summary = {}
    upstream_input_coverage_template = []
    if workflow_stage in {
        WorkflowStage.STATE,
        WorkflowStage.API,
        WorkflowStage.DESIGN,
        WorkflowStage.SLICE,
        WorkflowStage.GATES,
    }:
        upstream_input_inventory, upstream_missing = _upstream_input_inventory(
            store.paths.root, workflow_stage, approved_inputs
        )
        if upstream_missing or not _upstream_input_requirements_met(
            {
                "upstream_input_inventory": upstream_input_inventory,
                "upstream_input_summary": _upstream_input_summary(upstream_input_inventory),
                "upstream_input_coverage_template": _upstream_input_coverage_template(upstream_input_inventory),
            },
            approved_inputs,
        ):
            raise WorkflowStateError(
                f"{workflow_stage.value} requires frozen upstream inputs for all approved upstream stages"
            )
        upstream_input_summary = _upstream_input_summary(upstream_input_inventory)
        upstream_input_coverage_template = _upstream_input_coverage_template(upstream_input_inventory)
        prompt_bundle.upstream_input_inventory = upstream_input_inventory
        prompt_bundle.upstream_input_summary = upstream_input_summary
        prompt_bundle.upstream_input_coverage_template = upstream_input_coverage_template
        # Late-stage review packets only reach this block after upstream inputs were frozen.
        # If the inventory is empty here, an earlier guard has regressed.
        assert upstream_input_inventory, "late-stage review packets require frozen upstream inputs"
        prompt_bundle.user_prompt = prompt_bundle.user_prompt.replace(
            "upstream_input_count: 0",
            f"upstream_input_count: {len(upstream_input_inventory)}",
        )
        inventory_lines = "\n".join(
            f"- {item['source_stage']} [{item['role']}] -> {item['packet_path']} + {item['review_path']}"
            for item in upstream_input_inventory
        )
        prompt_bundle.user_prompt = "\n\n".join(
            [
                prompt_bundle.user_prompt,
                "upstream_input_inventory:",
                inventory_lines,
                "coverage_rule:",
                "Every upstream_input_inventory item must appear exactly once in the coverage matrix, with either a direct use or an explicit exclusion reason.",
            ]
        ).strip()
    if workflow_stage == WorkflowStage.DOMAIN and not _domain_input_requirements_met(prompt_bundle.as_dict(), approved_inputs):
        raise WorkflowStateError(
            "domain requires approved discovery input and a non-empty domain input inventory"
        )
    if not _stage_document_requirements_met(prompt_bundle.as_dict()):
        raise WorkflowStateError(
            f"{workflow_stage.value} requires a frozen stage document inventory and coverage template"
        )
    lifecycle = store.record_stage_lifecycle(
        workflow_stage,
        "packet_created",
        phase=StageLifecyclePhase.PACKET_CREATED,
        health=StageHealth.STABLE,
        status=stage_record.status,
        details={
            "rollback_point": rollback_point,
            "execution_policy": "isolated_subagent",
            "prompt_bundle": prompt_bundle.as_dict(),
        },
    )
    packet = build_review_packet(
        workflow_stage,
        target=workflow_stage.value,
        payload={
            "project_state": store.load().project_state.value,
            "stage_status": store.load_stage(workflow_stage).status.value,
            "rollback_point": rollback_point,
            "counterexample_prompts": _counterexample_prompts(workflow_stage),
            "approved_inputs": approved_inputs,
            "analysis_inventory": analysis_inventory,
            "analysis_scope_summary": analysis_scope_summary,
            "analysis_coverage_template": analysis_coverage_template,
            "stage_document_inventory": stage_document_inventory,
            "stage_document_summary": stage_document_summary,
            "stage_document_coverage_template": stage_document_coverage_template,
            "upstream_input_inventory": upstream_input_inventory,
            "upstream_input_summary": upstream_input_summary,
            "upstream_input_coverage_template": upstream_input_coverage_template,
            "domain_input_inventory": domain_input_inventory,
            "domain_input_summary": domain_input_summary,
            "domain_coverage_template": domain_coverage_template,
            "execution_policy": "isolated_subagent",
            "prompt_bundle": prompt_bundle.as_dict(),
        },
    )
    packet_path = store.write_review_artifact(
        workflow_stage,
        "packet",
        {
            "stage": packet.stage.value,
            "target": packet.target,
            "review_state": packet.review_state.value,
            "payload": packet.payload,
            "rollback_point": rollback_point,
            "prompt_bundle": prompt_bundle.as_dict(),
        },
    )
    record = store.set_review(
        workflow_stage,
        ReviewState.PACKET_CREATED,
        {"packet_path": str(packet_path), "packet_target": packet.target},
    )
    return CommandResult(
        status="ok",
        message=f"review packet for {workflow_stage.value} created",
        data={
            "stage": workflow_stage.value,
            "review_state": record.state.value,
            "lifecycle_phase": lifecycle.phase.value,
            "lifecycle_health": lifecycle.health.value,
            "packet_path": str(packet_path),
            "prompt_bundle": prompt_bundle.as_dict(),
        },
    )


def run_review(stage: str, store: StateStore) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    ensure_stage_inputs_available(store.paths.root, workflow_stage)
    packet_payload = store.read_review_artifact(workflow_stage, "packet")
    if not packet_payload:
        packet_review(stage, store)
        packet_payload = store.read_review_artifact(workflow_stage, "packet")
    prompt_bundle = packet_payload.get("prompt_bundle", {})
    store.record_stage_lifecycle(
        workflow_stage,
        "review_running",
        phase=StageLifecyclePhase.REVIEW_RUNNING,
        health=StageHealth.STABLE,
        details={"execution_policy": "isolated_subagent", "prompt_bundle": prompt_bundle},
    )
    runner = FilesystemReviewRunner(store.paths.audits_dir)
    packet = build_review_packet(
        workflow_stage,
        target=packet_payload.get("target", workflow_stage.value),
        payload=packet_payload.get("payload", {}),
    )
    result = runner.run(packet)
    worker_result = store.read_review_artifact(workflow_stage, "review")
    if not worker_result and result.result_path is not None:
        try:
            worker_result = json.loads(result.result_path.read_text(encoding="utf-8"))
        except Exception:
            worker_result = {}
    record = store.set_review(
        workflow_stage,
        ReviewState.REVIEW_RUNNING,
        {
            "fork_context": False,
            "execution_policy": "isolated_subagent",
            "prompt_bundle": prompt_bundle,
            "result_path": str(result.result_path) if result.result_path else None,
            "worker_review_state": result.review_state.value,
            "summary": result.summary,
            "violations": worker_result.get("violations", []),
            "counterexamples": worker_result.get("counterexamples", []),
            "evidence": worker_result.get("evidence", []),
            "rollback_point": worker_result.get("rollback_point", "analysis"),
        },
    )
    return CommandResult(
        status="ok",
        message=f"review run for {workflow_stage.value} started",
        data={
            "stage": workflow_stage.value,
            "review_state": record.state.value,
            "worker_review_state": result.review_state.value,
            "execution_policy": "isolated_subagent",
            "prompt_bundle": prompt_bundle,
            "summary": result.summary,
            "violations": worker_result.get("violations", []),
            "counterexamples": worker_result.get("counterexamples", []),
            "evidence": worker_result.get("evidence", []),
            "rollback_point": worker_result.get("rollback_point", "analysis"),
            "result_path": str(result.result_path) if result.result_path else None,
        },
    )


def record_review(stage: str, store: StateStore) -> CommandResult:
    return _store_worker_review_outcome(stage, store, "record")


def approve_review(stage: str, store: StateStore) -> CommandResult:
    return _store_worker_review_outcome(stage, store, "approve")


def reject_review(stage: str, store: StateStore) -> CommandResult:
    return _store_worker_review_outcome(stage, store, "reject")
