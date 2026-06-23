from __future__ import annotations

from plb.core.models import ProjectState, ReviewState, StageHealth, StageLifecyclePhase, StageStatus, WorkflowStage
from plb.core.paths import ProjectPaths
from plb.state.store import StateStore


def _store(tmp_path):
    return StateStore(ProjectPaths(root=tmp_path))


def test_state_store_defaults_without_database(tmp_path):
    store = _store(tmp_path)

    snapshot = store.load()
    stage_record = store.load_stage(WorkflowStage.DISCOVERY)
    lifecycle_record = store.load_stage_lifecycle(WorkflowStage.DISCOVERY)
    review_record = store.load_review(WorkflowStage.DISCOVERY)
    lifecycle_events = store.stage_lifecycle_events(WorkflowStage.DISCOVERY)

    assert snapshot.project_state == ProjectState.UNINITIALIZED
    assert snapshot.data == {}
    assert stage_record.status == StageStatus.PENDING
    assert lifecycle_record.phase == StageLifecyclePhase.SEEDED
    assert lifecycle_record.health == StageHealth.STABLE
    assert review_record.state == ReviewState.PACKET_CREATED
    assert lifecycle_events == []
    assert store.load_implementation_run() is None
    assert store.completed_stage_count() == 0
    assert store._stage_exists(WorkflowStage.DISCOVERY) is False
    assert store.read_review_artifact(WorkflowStage.DISCOVERY, "packet") == {}


def test_state_store_round_trip_and_path_helpers(tmp_path):
    store = _store(tmp_path)
    store.ensure_layout()

    snapshot = store.set_project_state(ProjectState.INITIALIZED, {"mode": "test"})
    stage_record = store.set_stage(WorkflowStage.DISCOVERY, StageStatus.ACTIVE, {"goal": "discover"})
    review_record = store.set_review(WorkflowStage.DISCOVERY, ReviewState.PASSED, {"worker_review_state": "passed"})
    packet_path = store.write_review_artifact(WorkflowStage.DISCOVERY, "packet", {"packet": True})

    assert snapshot.project_state == ProjectState.INITIALIZED
    assert store.load().data == {"mode": "test"}
    assert stage_record.status == StageStatus.ACTIVE
    assert review_record.state == ReviewState.PASSED
    assert store.review_packet_path(WorkflowStage.DISCOVERY).name == "discovery-packet.json"
    assert store.review_result_path(WorkflowStage.DISCOVERY).name == "discovery-review.json"
    assert store.read_review_artifact(WorkflowStage.DISCOVERY, "packet") == {"packet": True}
    assert packet_path.exists()
    assert store.completed_stage_count() == 0


def test_state_store_lifecycle_events_merge_details_and_update_counts(tmp_path):
    store = _store(tmp_path)
    store.ensure_layout()

    first = store.record_stage_lifecycle(
        WorkflowStage.API,
        "seeded",
        phase=StageLifecyclePhase.SEEDED,
        health=StageHealth.STABLE,
        status=StageStatus.PENDING,
        details=None,
    )
    second = store.record_stage_lifecycle(
        WorkflowStage.API,
        "planned",
        phase=StageLifecyclePhase.PLANNED,
        health=StageHealth.DEGRADED,
        status=StageStatus.ACTIVE,
        details={"goal": "ship api"},
    )
    events = store.stage_lifecycle_events(WorkflowStage.API)

    assert first.last_event == "seeded"
    assert second.phase == StageLifecyclePhase.PLANNED
    assert second.health == StageHealth.DEGRADED
    assert second.details["goal"] == "ship api"
    assert len(events) == 2
    assert events[0].event == "seeded"
    assert events[1].event == "planned"
    assert store.load_stage_lifecycle(WorkflowStage.API).details["goal"] == "ship api"


def test_state_store_implementation_run_round_trip_and_missing_update(tmp_path):
    store = _store(tmp_path)
    store.ensure_layout()

    assert store.update_implementation_run({"latest_verification": {}}) is None

    saved = store.save_implementation_run(
        goal="ship the slice",
        scope="scope",
        fresh_reviewer=True,
        payload={"goal_registry": [], "regression_checks": []},
        status="active",
    )
    updated = store.update_implementation_run({"latest_verification": {"status": "passed"}}, status="completed")

    assert saved["goal"] == "ship the slice"
    assert updated is not None
    assert updated["status"] == "completed"
    assert updated["latest_verification"] == {"status": "passed"}
    assert store.load_implementation_run()["status"] == "completed"


def test_state_store_ensure_stage_seed_covers_both_paths(tmp_path):
    fresh_store = _store(tmp_path / "fresh")
    seeded_without_layout = fresh_store.ensure_stage_seed(WorkflowStage.DISCOVERY)
    assert seeded_without_layout.status == StageStatus.PENDING
    assert fresh_store._stage_exists(WorkflowStage.DISCOVERY) is True

    laid_out_store = _store(tmp_path / "laid-out")
    laid_out_store.ensure_layout()
    seeded_with_layout = laid_out_store.ensure_stage_seed(WorkflowStage.DOMAIN)
    laid_out_store.set_stage(WorkflowStage.API, StageStatus.ACTIVE, {"goal": "already seeded"})
    reused_seed = laid_out_store.ensure_stage_seed(WorkflowStage.API)

    assert seeded_with_layout.status == StageStatus.PENDING
    assert laid_out_store._stage_exists(WorkflowStage.DOMAIN) is True
    assert reused_seed.status == StageStatus.ACTIVE
