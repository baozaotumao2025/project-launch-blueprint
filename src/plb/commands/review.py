from __future__ import annotations

import json

from plb.core.models import CommandResult, ReviewState, WorkflowStage
from plb.review.runner import FilesystemReviewRunner, build_review_packet
from plb.state.store import StateStore
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


def _coerce_review_state(result_state: object) -> ReviewState:
    mapping = {
        ReviewState.PASSED.value: ReviewState.PASSED,
        ReviewState.NEEDS_REVISION.value: ReviewState.NEEDS_REVISION,
        ReviewState.FAILED.value: ReviewState.FAILED,
    }
    if isinstance(result_state, str) and result_state in mapping:
        return mapping[result_state]
    return ReviewState.FAILED


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
    stage_record = store.load_stage(workflow_stage)
    rollback_point = stage_record.payload.get("rollback_point", "analysis")
    packet = build_review_packet(
        workflow_stage,
        target=workflow_stage.value,
        payload={
            "project_state": store.load().project_state.value,
            "stage_status": store.load_stage(workflow_stage).status.value,
            "rollback_point": rollback_point,
            "counterexample_prompts": _counterexample_prompts(workflow_stage),
            "approved_inputs": _approved_inputs(store, workflow_stage),
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
            "packet_path": str(packet_path),
        },
    )


def run_review(stage: str, store: StateStore) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    packet_payload = store.read_review_artifact(workflow_stage, "packet")
    if not packet_payload:
        packet_review(stage, store)
        packet_payload = store.read_review_artifact(workflow_stage, "packet")
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
