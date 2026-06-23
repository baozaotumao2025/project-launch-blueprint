from __future__ import annotations

from plb.core.models import (
    CommandResult,
    ReviewState,
    StageHealth,
    StageLifecyclePhase,
    StageStatus,
    WorkflowStage,
)
from plb.implementation.engine import next_implementation, plan_implementation, status_implementation, verify_implementation
from plb.state.store import StateStore
from plb.workflow.prompting import ensure_stage_inputs_available
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


def _review_passed(store: StateStore, stage: WorkflowStage) -> bool:
    return store.load_review(stage).state == ReviewState.PASSED


def _phase_for_status(status: StageStatus) -> StageLifecyclePhase:
    mapping = {
        StageStatus.PENDING: StageLifecyclePhase.SEEDED,
        StageStatus.ACTIVE: StageLifecyclePhase.PLANNED,
        StageStatus.COMPLETED: StageLifecyclePhase.COMPLETED,
        StageStatus.BLOCKED: StageLifecyclePhase.BLOCKED,
        StageStatus.NEEDS_REVISION: StageLifecyclePhase.REJECTED,
    }
    return mapping[status]


def plan_stage(stage: str, store: StateStore, goal: str | None = None, fresh_reviewer: bool = False, dry_run: bool = False) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    if workflow_stage == WorkflowStage.IMPLEMENTATION:
        return plan_implementation(store, goal, fresh_reviewer=fresh_reviewer, dry_run=dry_run)
    ensure_stage_inputs_available(store.paths.root, workflow_stage)
    record = store.ensure_stage_seed(workflow_stage)
    record = store.set_stage(
        workflow_stage,
        StageStatus.ACTIVE,
        {
            "goal": goal,
            "fresh_reviewer": fresh_reviewer,
            "dry_run": dry_run,
            "previous_stage": _previous_stage(workflow_stage).value if _previous_stage(workflow_stage) else None,
        },
    )
    lifecycle = store.record_stage_lifecycle(
        workflow_stage,
        "planned",
        phase=StageLifecyclePhase.PLANNED,
        health=StageHealth.STABLE,
        status=record.status,
        details={
            "goal": goal,
            "fresh_reviewer": fresh_reviewer,
            "dry_run": dry_run,
            "previous_stage": _previous_stage(workflow_stage).value if _previous_stage(workflow_stage) else None,
        },
    )
    return CommandResult(
        status="ok",
        message=f"plan for {workflow_stage.value} is ready",
        data={
            "stage": workflow_stage.value,
            "stage_index": _stage_index(workflow_stage),
            "status": record.status.value,
            "lifecycle_phase": lifecycle.phase.value,
            "lifecycle_health": lifecycle.health.value,
            "previous_stage": _previous_stage(workflow_stage).value if _previous_stage(workflow_stage) else None,
        },
    )


def stage_status(stage: str, store: StateStore, verbose: bool = False) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    if workflow_stage == WorkflowStage.IMPLEMENTATION:
        return status_implementation(store)
    record = store.load_stage(workflow_stage)
    lifecycle = store.load_stage_lifecycle(workflow_stage)
    return CommandResult(
        status="ok",
        message=f"status for {workflow_stage.value} loaded",
        data={
            "stage": workflow_stage.value,
            "stage_index": _stage_index(workflow_stage),
            "status": record.status.value,
            "lifecycle_phase": lifecycle.phase.value,
            "lifecycle_health": lifecycle.health.value,
            "lifecycle_event": lifecycle.last_event,
            "review_passed": _review_passed(store, workflow_stage),
            "previous_completed": _previous_completed(store, workflow_stage),
        },
    )


def next_step(stage: str, store: StateStore, goal_id: str | None = None, regress: bool = True, dry_run: bool = False) -> CommandResult:
    workflow_stage = _normalize_stage(stage)
    if workflow_stage == WorkflowStage.IMPLEMENTATION:
        return next_implementation(store, goal_id=goal_id, regress=regress, dry_run=dry_run)
    index = _stage_index(workflow_stage)
    next_stage = STAGE_ORDER[index + 1].value if index + 1 < len(STAGE_ORDER) else None
    # IMPLEMENTATION is handled above, so every stage reaching this block must have a follow-up stage.
    assert next_stage is not None, "non-implementation stages must have a follow-up stage"
    current = store.load_stage(workflow_stage)
    review_passed = _review_passed(store, workflow_stage)
    allowed = current.status == StageStatus.COMPLETED and review_passed and _previous_completed(store, workflow_stage)
    next_status = None
    if allowed:
        next_record = store.set_stage(STAGE_ORDER[index + 1], StageStatus.ACTIVE, {"started_after": workflow_stage.value})
        next_status = next_record.status.value
        store.record_stage_lifecycle(
            workflow_stage,
            "advanced",
            phase=StageLifecyclePhase.COMPLETED,
            health=StageHealth.STABLE,
            status=StageStatus.COMPLETED,
            details={"next_stage": next_stage, "goal_id": goal_id, "regress": regress, "dry_run": dry_run},
        )
        store.record_stage_lifecycle(
            STAGE_ORDER[index + 1],
            "activated",
            phase=StageLifecyclePhase.PLANNED,
            health=StageHealth.STABLE,
            status=StageStatus.ACTIVE,
            details={"started_after": workflow_stage.value},
        )
    else:
        store.set_stage(workflow_stage, StageStatus.BLOCKED, {"blocked_reason": "review_not_passed_or_previous_incomplete"})
        store.record_stage_lifecycle(
            workflow_stage,
            "blocked",
            phase=StageLifecyclePhase.BLOCKED,
            health=StageHealth.BLOCKED,
            status=StageStatus.BLOCKED,
            details={
                "next_stage": next_stage,
                "current_status": current.status.value,
                "review_passed": review_passed,
                "previous_completed": _previous_completed(store, workflow_stage),
                "goal_id": goal_id,
                "regress": regress,
                "dry_run": dry_run,
            },
        )
    return CommandResult(
        status="ok",
        message=f"next step for {workflow_stage.value} resolved",
        data={
            "stage": workflow_stage.value,
            "current_status": current.status.value,
            "review_passed": review_passed,
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
    review_passed = _review_passed(store, workflow_stage)
    allowed = record.status == StageStatus.COMPLETED and review_passed and previous_completed
    return CommandResult(
        status="ok",
        message=f"verify for {workflow_stage.value} resolved",
        data={
            "stage": workflow_stage.value,
            "stage_index": _stage_index(workflow_stage),
            "status": record.status.value,
            "review_passed": review_passed,
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
    lifecycle = store.record_stage_lifecycle(
        workflow_stage,
        f"status_set_{stage_status.value}",
        phase=_phase_for_status(stage_status),
        health=StageHealth.STABLE if stage_status == StageStatus.COMPLETED else StageHealth.DEGRADED if stage_status == StageStatus.NEEDS_REVISION else StageHealth.BLOCKED if stage_status == StageStatus.BLOCKED else StageHealth.STABLE,
        status=stage_status,
        details={"manual_override": True},
    )
    return CommandResult(
        status="ok",
        message=f"stage {workflow_stage.value} marked as {stage_status.value}",
        data={
            "stage": workflow_stage.value,
            "stage_index": _stage_index(workflow_stage),
            "status": record.status.value,
            "lifecycle_phase": lifecycle.phase.value,
            "lifecycle_health": lifecycle.health.value,
        },
    )
