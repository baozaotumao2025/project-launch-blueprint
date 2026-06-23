from __future__ import annotations

from plb.commands.review import packet_review, run_review
from plb.commands.stage import next_step, plan_stage, stage_status
from plb.core.models import ReviewState, StageStatus, WorkflowStage
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


def test_discovery_plan_records_lifecycle_and_status(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)

    result = plan_stage(WorkflowStage.DISCOVERY.value, store, goal="discover launch scope")
    lifecycle = store.load_stage_lifecycle(WorkflowStage.DISCOVERY)
    events = store.stage_lifecycle_events(WorkflowStage.DISCOVERY)

    assert result.data["status"] == StageStatus.ACTIVE.value
    assert result.data["lifecycle_phase"] == "planned"
    assert lifecycle.phase.value == "planned"
    assert lifecycle.health.value == "stable"
    assert lifecycle.status == StageStatus.ACTIVE
    assert lifecycle.last_event == "planned"
    assert events[-1].event == "planned"
    assert events[-1].details["goal"] == "discover launch scope"

    status = stage_status(WorkflowStage.DISCOVERY.value, store)
    assert status.data["lifecycle_phase"] == "planned"
    assert status.data["review_passed"] is False


def test_discovery_review_flow_uses_subagent_and_blocks_unapproved_next(tmp_path):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    plan_stage(WorkflowStage.DISCOVERY.value, store, goal="discover launch scope")

    packet = packet_review(WorkflowStage.DISCOVERY.value, store)
    assert packet.data["packet_path"].endswith("discovery-packet.json")
    assert packet.data["lifecycle_phase"] == "packet_created"

    run = run_review(WorkflowStage.DISCOVERY.value, store)
    assert run.data["execution_policy"] == "isolated_subagent"
    assert run.data["worker_review_state"] in {
        ReviewState.PASSED.value,
        ReviewState.NEEDS_REVISION.value,
        ReviewState.FAILED.value,
    }

    lifecycle = store.load_stage_lifecycle(WorkflowStage.DISCOVERY)
    assert lifecycle.last_event == "review_running"
    next_result = next_step(WorkflowStage.DISCOVERY.value, store)
    assert next_result.data["allowed"] is False
    assert store.load_stage(WorkflowStage.DISCOVERY).status == StageStatus.BLOCKED


def test_review_run_invokes_isolated_worker_process(tmp_path, monkeypatch):
    _prepare_discovery_inputs(tmp_path)
    store = _store(tmp_path)
    plan_stage(WorkflowStage.DISCOVERY.value, store, goal="discover launch scope")
    packet_review(WorkflowStage.DISCOVERY.value, store)

    calls = []

    def fake_run(*args, **kwargs):
        cmd = args[0]
        calls.append(cmd)
        result_path = tmp_path / ".project-launch-blueprint" / "audits" / "discovery-review.json"
        result_path.write_text(
            """
            {
              "packet": {"stage": "discovery"},
              "summary": "isolated review passed for discovery",
              "review_state": "passed",
              "evidence": ["project_state=initialized"],
              "counterexamples": ["x"],
              "rollback_point": "analysis",
              "violations": [],
              "checks": {
                "packet_shape": true,
                "payload_rules": true,
                "target_matches_stage": true,
                "has_evidence": true,
                "has_counterexamples": true,
                "has_rollback_point": true
              }
            }
            """,
            encoding="utf-8",
        )

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr("plb.review.runner.subprocess.run", fake_run)

    result = run_review(WorkflowStage.DISCOVERY.value, store)

    assert calls
    assert calls[0][0].endswith("python") or calls[0][0].endswith("python3")
    assert calls[0][1] == "-m"
    assert calls[0][2] == "plb.review.worker"
    assert result.data["execution_policy"] == "isolated_subagent"
