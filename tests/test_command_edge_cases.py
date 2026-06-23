from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from plb.commands.review import (
    _approved_inputs,
    _coerce_review_state,
    _domain_input_requirements_met,
    _health_from_review_state,
    _load_worker_review_result,
    _stage_document_requirements_met,
    _upstream_input_requirements_met,
    packet_review,
    record_review,
    run_review,
)
from plb.commands.stage import list_stages, next_step, set_stage_status
from plb.core.errors import WorkflowStateError
from plb.core.models import ReviewState, StageHealth, StageLifecyclePhase, StageStatus, WorkflowStage
from plb.core.paths import ProjectPaths
from plb.state.store import StateStore


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


class _FakeReviewStore:
    def __init__(self, artifact=None, payload=None):
        self._artifact = artifact
        self._payload = payload

    def read_review_artifact(self, stage, kind):
        return self._artifact or {}

    def load_review(self, stage):
        return SimpleNamespace(payload=self._payload)


def test_packet_review_rejects_domain_without_approved_discovery(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    store.set_stage(WorkflowStage.DOMAIN, StageStatus.ACTIVE, {"goal": "scope domain boundary"})

    with pytest.raises(WorkflowStateError, match="domain requires approved discovery input"):
        packet_review(WorkflowStage.DOMAIN.value, store)


def test_packet_review_rejects_late_stage_without_frozen_upstream_inputs(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    store.set_stage(WorkflowStage.DISCOVERY, StageStatus.COMPLETED, {"goal": "discover launch scope"})
    store.set_review(WorkflowStage.DISCOVERY, ReviewState.PASSED, {"worker_review_state": "passed"})
    store.set_stage(WorkflowStage.STATE, StageStatus.ACTIVE, {"goal": "model state transitions"})

    with pytest.raises(WorkflowStateError, match="requires frozen upstream inputs"):
        packet_review(WorkflowStage.STATE.value, store)


def test_run_review_creates_packet_and_reads_result_from_file_when_artifact_missing(tmp_path, monkeypatch):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    store.set_stage(WorkflowStage.DISCOVERY, StageStatus.ACTIVE, {"goal": "discover launch scope"})

    result_path = tmp_path / "worker-review.json"

    class FakeResult:
        def __init__(self, path):
            self.review_state = ReviewState.PASSED
            self.summary = "isolated review passed for discovery"
            self.result_path = path

    def fake_run(self, packet):
        result_path.write_text(
            json.dumps(
                {
                    "review_state": "passed",
                    "summary": "isolated review passed for discovery",
                    "evidence": ["project_state=initialized"],
                    "counterexamples": ["x"],
                    "rollback_point": "analysis",
                    "violations": [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return FakeResult(result_path)

    monkeypatch.setattr("plb.review.runner.FilesystemReviewRunner.run", fake_run)
    result = run_review(WorkflowStage.DISCOVERY.value, store)
    review_record = store.load_review(WorkflowStage.DISCOVERY)

    assert result.data["worker_review_state"] == "passed"
    assert result.data["violations"] == []
    assert review_record.payload["worker_review_state"] == "passed"


def test_run_review_uses_existing_artifacts_without_fallback_read(tmp_path, monkeypatch):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    store.set_stage(WorkflowStage.DISCOVERY, StageStatus.ACTIVE, {"goal": "discover launch scope"})
    store.write_review_artifact(
        WorkflowStage.DISCOVERY,
        "packet",
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": {"summary": "existing packet"},
            "prompt_bundle": {"prompt": "existing"},
        },
    )
    store.write_review_artifact(
        WorkflowStage.DISCOVERY,
        "review",
        {
            "review_state": ReviewState.PASSED.value,
            "summary": "cached review",
            "violations": ["cached violation"],
            "counterexamples": ["cached counterexample"],
            "evidence": ["cached evidence"],
            "rollback_point": "analysis",
        },
    )

    class FakeResult:
        def __init__(self):
            self.review_state = ReviewState.PASSED
            self.summary = "runner summary"
            self.result_path = tmp_path / "unused-review.json"

    def fake_run(self, packet):
        return FakeResult()

    monkeypatch.setattr("plb.review.runner.FilesystemReviewRunner.run", fake_run)

    result = run_review(WorkflowStage.DISCOVERY.value, store)

    assert result.data["violations"] == ["cached violation"]
    assert result.data["counterexamples"] == ["cached counterexample"]
    assert result.data["evidence"] == ["cached evidence"]
    assert result.data["review_state"] == ReviewState.REVIEW_RUNNING.value


def test_run_review_handles_invalid_json_result_file(tmp_path, monkeypatch):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    store.set_stage(WorkflowStage.DISCOVERY, StageStatus.ACTIVE, {"goal": "discover launch scope"})

    class FakeResult:
        def __init__(self):
            self.review_state = ReviewState.PASSED
            self.summary = "runner summary"
            self.result_path = tmp_path / "broken-review.json"

    def fake_run(self, packet):
        fake_result = FakeResult()
        fake_result.result_path.write_text("{not-json", encoding="utf-8")
        return fake_result

    monkeypatch.setattr("plb.review.runner.FilesystemReviewRunner.run", fake_run)

    result = run_review(WorkflowStage.DISCOVERY.value, store)

    assert result.data["violations"] == []
    assert result.data["counterexamples"] == []
    assert result.data["evidence"] == []


def test_record_review_uses_worker_result_and_keeps_stage_status(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    store.set_stage(WorkflowStage.DISCOVERY, StageStatus.ACTIVE, {"goal": "discover launch scope"})
    store.write_review_artifact(
        WorkflowStage.DISCOVERY,
        "review",
        {
            "review_state": ReviewState.PASSED.value,
            "summary": "isolated review passed",
            "violations": [],
            "rollback_point": "analysis",
            "counterexamples": [],
            "evidence": [],
        },
    )

    result = record_review(WorkflowStage.DISCOVERY.value, store)
    stage_record = store.load_stage(WorkflowStage.DISCOVERY)
    lifecycle = store.load_stage_lifecycle(WorkflowStage.DISCOVERY)

    assert result.data["decision"] == "record"
    assert result.data["recorded_review_state"] == ReviewState.PASSED.value
    assert stage_record.status == StageStatus.ACTIVE
    assert lifecycle.phase == StageLifecyclePhase.REVIEW_RECORDED


def test_review_helper_guards_cover_false_and_fallback_paths(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    assert _approved_inputs(store, WorkflowStage.DISCOVERY) == ["analysis"]

    store.set_stage(WorkflowStage.DISCOVERY, StageStatus.COMPLETED, {"goal": "discover launch scope"})
    assert _approved_inputs(store, WorkflowStage.DOMAIN) == ["discovery"]

    assert _domain_input_requirements_met({"domain_input_inventory": []}, ["analysis", "discovery"]) is False
    assert _domain_input_requirements_met(
        {"domain_input_inventory": [{"role": "secondary"}]},
        ["analysis", "discovery"],
    ) is False
    assert _domain_input_requirements_met(
        {"domain_input_inventory": [{"role": "primary"}]},
        ["analysis"],
    ) is False
    assert _stage_document_requirements_met(
        {
            "stage_document_inventory": [],
            "stage_document_summary": {},
            "stage_document_coverage_template": [{"path": "records/project-launch-blueprint/discovery/method.md"}],
        }
    ) is False
    assert _stage_document_requirements_met(
        {
            "stage_document_inventory": [{"path": "records/project-launch-blueprint/discovery/method.md"}],
            "stage_document_summary": {},
            "stage_document_coverage_template": [],
        }
    ) is False
    assert _stage_document_requirements_met(
        {
            "stage_document_inventory": [{"path": "records/project-launch-blueprint/discovery/method.md"}],
            "stage_document_summary": "not-a-dict",
            "stage_document_coverage_template": [{"path": "records/project-launch-blueprint/discovery/method.md"}],
        }
    ) is False
    assert _upstream_input_requirements_met(
        {
            "upstream_input_inventory": [],
            "upstream_input_summary": {},
            "upstream_input_coverage_template": [{"source_stage": "discovery"}],
        },
        ["analysis", "discovery"],
    ) is False
    assert _upstream_input_requirements_met(
        {
            "upstream_input_inventory": [{"source_stage": "discovery", "role": "primary", "packet_path": "a", "review_path": "b"}],
            "upstream_input_summary": "not-a-dict",
            "upstream_input_coverage_template": [{"source_stage": "discovery"}],
        },
        ["analysis", "discovery"],
    ) is False
    assert _upstream_input_requirements_met(
        {
            "upstream_input_inventory": [{"source_stage": "discovery", "role": "primary", "packet_path": "a", "review_path": "b"}],
            "upstream_input_summary": {},
            "upstream_input_coverage_template": [],
        },
        ["analysis", "discovery"],
    ) is False
    assert _coerce_review_state("not-a-review-state") == ReviewState.FAILED
    assert _health_from_review_state(ReviewState.FAILED) == StageHealth.FAILED
    assert _health_from_review_state(ReviewState.NEEDS_REVISION) == StageHealth.DEGRADED


def test_load_worker_review_result_prefers_artifact_then_record_and_state(tmp_path):
    artifact_store = _FakeReviewStore(
        artifact={
            "review_state": ReviewState.PASSED.value,
            "summary": "artifact result",
            "violations": [],
        },
        payload=None,
    )
    artifact_result = _load_worker_review_result(WorkflowStage.DISCOVERY, artifact_store)
    assert artifact_result["_source"] == "artifact"

    record_store = _FakeReviewStore(
        artifact={},
        payload={
            "result": {
                "review_state": ReviewState.NEEDS_REVISION.value,
                "summary": "record result",
            }
        },
    )
    record_result = _load_worker_review_result(WorkflowStage.DOMAIN, record_store)
    assert record_result["_source"] == "record"

    state_store = _FakeReviewStore(
        artifact={},
        payload={"worker_review_state": ReviewState.FAILED.value},
    )
    state_result = _load_worker_review_result(WorkflowStage.STATE, state_store)
    assert state_result["_source"] == "record_state"

    malformed_store = _FakeReviewStore(artifact={}, payload="not-a-dict")
    assert _load_worker_review_result(WorkflowStage.API, malformed_store) == {}

    empty_store = _FakeReviewStore(artifact={}, payload={})
    assert _load_worker_review_result(WorkflowStage.GATES, empty_store) == {}


def test_packet_review_includes_upstream_inventory_for_late_stage(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    store.set_stage(WorkflowStage.DISCOVERY, StageStatus.COMPLETED, {"goal": "discover launch scope"})
    store.write_review_artifact(
        WorkflowStage.DISCOVERY,
        "packet",
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": {},
        },
    )
    store.write_review_artifact(
        WorkflowStage.DISCOVERY,
        "review",
        {
            "review_state": ReviewState.PASSED.value,
            "summary": "approved discovery",
            "violations": [],
            "rollback_point": "analysis",
            "counterexamples": [],
            "evidence": [],
        },
    )

    result = packet_review(WorkflowStage.STATE.value, store)

    assert result.data["stage"] == WorkflowStage.STATE.value
    assert result.data["prompt_bundle"]["upstream_input_inventory"]
    assert "coverage_rule" in result.data["prompt_bundle"]["user_prompt"]


def test_packet_review_asserts_frozen_upstream_inputs_are_present(tmp_path, monkeypatch):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    store.set_stage(WorkflowStage.DISCOVERY, StageStatus.COMPLETED, {"goal": "discover launch scope"})
    store.set_review(WorkflowStage.DISCOVERY, ReviewState.PASSED, {"worker_review_state": "passed"})
    store.set_stage(WorkflowStage.STATE, StageStatus.ACTIVE, {"goal": "model state transitions"})

    monkeypatch.setattr("plb.commands.review._upstream_input_inventory", lambda *args, **kwargs: ([], []))
    monkeypatch.setattr("plb.commands.review._upstream_input_requirements_met", lambda *args, **kwargs: True)

    with pytest.raises(AssertionError, match="late-stage review packets require frozen upstream inputs"):
        packet_review(WorkflowStage.STATE.value, store)


def test_packet_review_rejects_empty_stage_document_coverage_template(tmp_path, monkeypatch):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    class _FakePromptBundle:
        analysis_inventory = [{"path": "analysis/brief.md"}]
        analysis_scope_summary = {"total_inputs": 1}
        analysis_coverage_template = [{"path": "analysis/brief.md"}]
        stage_document_inventory = [{"path": "records/project-launch-blueprint/discovery/method.md"}]
        stage_document_summary = {"total_documents": 1}
        stage_document_coverage_template = []
        domain_input_inventory = []
        domain_input_summary = {}
        domain_coverage_template = []
        user_prompt = "stage_document_count: 1"

        def as_dict(self):
            return {
                "stage_document_inventory": self.stage_document_inventory,
                "stage_document_summary": self.stage_document_summary,
                "stage_document_coverage_template": self.stage_document_coverage_template,
            }

    monkeypatch.setattr("plb.commands.review.build_stage_prompt_bundle", lambda *args, **kwargs: _FakePromptBundle())

    with pytest.raises(WorkflowStateError, match="requires a frozen stage document inventory"):
        packet_review(WorkflowStage.DISCOVERY.value, store)


@pytest.mark.parametrize(
    "status, expected_phase, expected_health",
    [
        (StageStatus.PENDING, StageLifecyclePhase.SEEDED, "stable"),
        (StageStatus.ACTIVE, StageLifecyclePhase.PLANNED, "stable"),
        (StageStatus.COMPLETED, StageLifecyclePhase.COMPLETED, "stable"),
        (StageStatus.BLOCKED, StageLifecyclePhase.BLOCKED, "blocked"),
        (StageStatus.NEEDS_REVISION, StageLifecyclePhase.REJECTED, "degraded"),
    ],
)
def test_set_stage_status_maps_phase_and_health_for_all_statuses(tmp_path, status, expected_phase, expected_health):
    store = _store(tmp_path)

    result = set_stage_status(WorkflowStage.API.value, status.value, store)
    lifecycle = store.load_stage_lifecycle(WorkflowStage.API)

    assert result.data["status"] == status.value
    assert result.data["lifecycle_phase"] == expected_phase.value
    assert result.data["lifecycle_health"] == expected_health
    assert lifecycle.phase == expected_phase


def test_list_stages_reports_registry(tmp_path):
    _ = _store(tmp_path)

    result = list_stages()

    assert result.data["stage_count"] >= 7
    assert "discovery" in result.data["stages"]
    assert "implementation" in result.data["stages"]


def test_next_step_on_blocked_stage_stays_blocked_when_review_fails(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    store.set_stage(WorkflowStage.DISCOVERY, StageStatus.ACTIVE, {"goal": "discover launch scope"})

    result = next_step(WorkflowStage.DISCOVERY.value, store, dry_run=True)

    assert result.data["allowed"] is False
    assert store.load_stage(WorkflowStage.DISCOVERY).status == StageStatus.BLOCKED
