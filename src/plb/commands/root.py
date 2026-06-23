from __future__ import annotations

from plb.core.models import CommandResult, ProjectState, StageHealth, StageLifecyclePhase, StageStatus
from plb.state.store import StateStore
from plb.workflow.registry import STAGE_ORDER
from plb.workflow.materialize import materialize_project_docs


def init_project(store: StateStore) -> CommandResult:
    snapshot = store.set_project_state(ProjectState.INITIALIZED, data={"phase": "bootstrap"})
    materialized = materialize_project_docs(store.paths)
    for stage in STAGE_ORDER:
        store.set_stage(stage, StageStatus.PENDING, payload={"seeded": True})
        store.record_stage_lifecycle(
            stage,
            "seeded",
            phase=StageLifecyclePhase.SEEDED,
            health=StageHealth.STABLE,
            status=StageStatus.PENDING,
            details={"seeded": True},
        )
    return CommandResult(
        status="ok",
        message="plb scaffold initialized",
        data={
            "project_state": snapshot.project_state.value,
            "state_db": str(store.paths.state_db),
            "projections_dir": str(store.paths.projections_dir),
            "docs_root": str(materialized.docs_root),
            "materialized_files": len(materialized.copied_files),
        },
    )


def get_project_status(store: StateStore) -> CommandResult:
    snapshot = store.load()
    return CommandResult(
        status="ok",
        message="status snapshot loaded",
        data={
            "project_state": snapshot.project_state.value,
            "completed_stages": store.completed_stage_count(),
            "state_db": str(store.paths.state_db),
            "projections_dir": str(store.paths.projections_dir),
        },
    )


def publish_project(store: StateStore) -> CommandResult:
    snapshot = store.set_project_state(ProjectState.PUBLISHED, data={"phase": "published"})
    return CommandResult(
        status="ok",
        message="publish flow is not implemented yet",
        data={
            "project_state": snapshot.project_state.value,
            "state_db": str(store.paths.state_db),
            "projections_dir": str(store.paths.projections_dir),
        },
    )
