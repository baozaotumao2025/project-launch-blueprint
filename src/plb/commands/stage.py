from __future__ import annotations

from plb.core.models import CommandResult, StageStatus, WorkflowStage
from plb.implementation.engine import next_implementation, plan_implementation, status_implementation, verify_implementation
from plb.state.store import StateStore
from plb.workflow.registry import STAGE_ORDER, stage_names


def _normalize_stage(stage: str) -> WorkflowStage:
    return WorkflowStage(stage)


def _stage_index(stage: WorkflowStage) -> int:
    return STAGE_ORDER.index(stage)


def _previous_stage(stage: WorkflowStage) -> WorkflowStage | None:
    index = _stage_index(stage)
    if index == 0:
        return None
    return STAGE_ORDER[index - 1]


def _previous_completed(store: StateStore, stage: WorkflowStage) -> bool:
    previous = _previous_stage(stage)
    if previous is None:
        return True
    return store.load_stage(previous).status == StageStatus.COMPLETED


def plan_stage(stage: str, store: StateStore, goal: str | None = None, fresh_reviewer: bool = False, dry_run: bool = False) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    if workflow_stage == WorkflowStage.IMPLEMENTATION:
        return plan_implementation(store, goal, fresh_reviewer=fresh_reviewer, dry_run=dry_run)
    record = store.ensure_stage_seed(workflow_stage)
    return CommandResult(
        status="ok",
        message=f"plan for {workflow_stage.value} is ready",
        data={
            "stage": workflow_stage.value,
            "stage_index": _stage_index(workflow_stage),
            "status": record.status.value,
            "previous_stage": _previous_stage(workflow_stage).value if _previous_stage(workflow_stage) else None,
        },
    )


def stage_status(stage: str, store: StateStore, verbose: bool = False) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    if workflow_stage == WorkflowStage.IMPLEMENTATION:
        return status_implementation(store)
    record = store.load_stage(workflow_stage)
    return CommandResult(
        status="ok",
        message=f"status for {workflow_stage.value} loaded",
        data={
            "stage": workflow_stage.value,
            "stage_index": _stage_index(workflow_stage),
            "status": record.status.value,
            "previous_completed": _previous_completed(store, workflow_stage),
        },
    )


def next_step(stage: str, store: StateStore, goal_id: str | None = None, regress: bool = True, dry_run: bool = False) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    if workflow_stage == WorkflowStage.IMPLEMENTATION:
        return next_implementation(store, goal_id=goal_id, regress=regress, dry_run=dry_run)
    index = _stage_index(workflow_stage)
    next_stage = STAGE_ORDER[index + 1].value if index + 1 < len(STAGE_ORDER) else None
    current = store.load_stage(workflow_stage)
    allowed = current.status == StageStatus.COMPLETED and _previous_completed(store, workflow_stage)
    next_status = None
    if allowed and next_stage is not None:
        next_record = store.set_stage(STAGE_ORDER[index + 1], StageStatus.ACTIVE, {"started_after": workflow_stage.value})
        next_status = next_record.status.value
    return CommandResult(
        status="ok",
        message=f"next step for {workflow_stage.value} resolved",
        data={
            "stage": workflow_stage.value,
            "current_status": current.status.value,
            "next_stage": next_stage,
            "next_status": next_status,
            "allowed": allowed,
        },
    )


def verify_stage(stage: str, store: StateStore, strict: bool = False) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    if workflow_stage == WorkflowStage.IMPLEMENTATION:
        return verify_implementation(store, strict=strict)
    record = store.load_stage(workflow_stage)
    previous_completed = _previous_completed(store, workflow_stage)
    allowed = record.status == StageStatus.COMPLETED and previous_completed
    return CommandResult(
        status="ok",
        message=f"verify for {workflow_stage.value} resolved",
        data={
            "stage": workflow_stage.value,
            "stage_index": _stage_index(workflow_stage),
            "status": record.status.value,
            "previous_completed": previous_completed,
            "allowed": allowed,
        },
    )


def list_stages() -> CommandResult:
    return CommandResult(
        status="ok",
        message="workflow stage registry",
        data={"stage_count": len(STAGE_ORDER), "stages": ", ".join(stage_names())},
    )


def set_stage_status(stage: str, status: str, store: StateStore) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    stage_status = StageStatus(status)
    record = store.set_stage(workflow_stage, stage_status)
    return CommandResult(
        status="ok",
        message=f"stage {workflow_stage.value} marked as {stage_status.value}",
        data={
            "stage": workflow_stage.value,
            "stage_index": _stage_index(workflow_stage),
            "status": record.status.value,
        },
    )
