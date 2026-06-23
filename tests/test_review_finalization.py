from __future__ import annotations

from plb.commands.review import approve_review, reject_review
from plb.core.models import ReviewState, WorkflowStage
from plb.core.paths import ProjectPaths
from plb.state.store import StateStore


def _store(tmp_path):
    store = StateStore(ProjectPaths(root=tmp_path))
    store.ensure_layout()
    return store


def test_approve_review_keeps_worker_needs_revision(tmp_path):
    store = _store(tmp_path)
    store.write_review_artifact(
        WorkflowStage.DISCOVERY,
        "review",
        {
            "review_state": ReviewState.NEEDS_REVISION.value,
            "summary": "revision needed",
            "violations": ["missing evidence"],
        },
    )

    result = approve_review(WorkflowStage.DISCOVERY.value, store)
    record = store.load_review(WorkflowStage.DISCOVERY)

    assert result.data["recorded_review_state"] == ReviewState.NEEDS_REVISION.value
    assert result.data["worker_review_state"] == ReviewState.NEEDS_REVISION.value
    assert record.state == ReviewState.NEEDS_REVISION


def test_reject_review_keeps_worker_failed(tmp_path):
    store = _store(tmp_path)
    store.write_review_artifact(
        WorkflowStage.DOMAIN,
        "review",
        {
            "review_state": ReviewState.FAILED.value,
            "summary": "packet malformed",
            "violations": ["payload missing"],
        },
    )

    result = reject_review(WorkflowStage.DOMAIN.value, store)
    record = store.load_review(WorkflowStage.DOMAIN)

    assert result.data["recorded_review_state"] == ReviewState.FAILED.value
    assert result.data["worker_review_state"] == ReviewState.FAILED.value
    assert record.state == ReviewState.FAILED


def test_approve_review_completes_stage_when_worker_passes(tmp_path):
    store = _store(tmp_path)
    store.write_review_artifact(
        WorkflowStage.DISCOVERY,
        "review",
        {
            "review_state": ReviewState.PASSED.value,
            "summary": "isolated review passed",
            "violations": [],
        },
    )

    result = approve_review(WorkflowStage.DISCOVERY.value, store)
    stage_record = store.load_stage(WorkflowStage.DISCOVERY)
    lifecycle = store.load_stage_lifecycle(WorkflowStage.DISCOVERY)

    assert result.data["recorded_review_state"] == ReviewState.PASSED.value
    assert stage_record.status.value == "completed"
    assert lifecycle.phase.value == "approved"
    assert lifecycle.health.value == "stable"
