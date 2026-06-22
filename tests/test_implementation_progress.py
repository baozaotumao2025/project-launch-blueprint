from __future__ import annotations

from plb.implementation.engine import next_implementation, plan_implementation, status_implementation
from plb.core.models import WorkflowStage
from plb.core.paths import ProjectPaths
from plb.state.store import StateStore


def _store(tmp_path):
    store = StateStore(ProjectPaths(root=tmp_path))
    store.ensure_layout()
    return store


def test_implementation_progress_tracks_latest_verification(tmp_path):
    store = _store(tmp_path)

    plan_result = plan_implementation(store, "Ship a customer invite prototype", fresh_reviewer=True)
    assert plan_result.data["goal_progress"]["total_goals"] == 3
    assert plan_result.data["latest_verification"]["status"] == "pending"
    assert len(plan_result.data["implementation_plan"]) == 8
    assert len(plan_result.data["code_scaffold_map"]) >= 3
    assert "src/plb/implementation" in plan_result.data["directory_tree"]
    assert plan_result.data["bootstrap_manifest"][0]["kind"] == "directory"
    assert len(plan_result.data["task_batch_list"]) == 3
    assert "src/plb/implementation/engine.py" in plan_result.data["code_scaffold_map"][0]["files"]

    first = next_implementation(store)
    assert first.data["current_goal"] == "goal-1"
    assert first.data["regression_passed"] is True
    assert first.data["latest_verification"]["checked_goals"] == []

    second = next_implementation(store)
    assert second.data["current_goal"] == "goal-2"
    assert second.data["regression_passed"] is True
    assert second.data["latest_verification"]["checked_goals"] == ["goal-1"]

    third = next_implementation(store)
    assert third.data["current_goal"] == "goal-3"
    assert third.data["regression_passed"] is True
    assert third.data["latest_verification"]["checked_goals"] == ["goal-1", "goal-2"]

    final_status = status_implementation(store)
    assert final_status.data["goal_progress"]["completed_goals"] == 3
    assert final_status.data["latest_verification"]["status"] == "passed"
    assert final_status.data["latest_verification"]["goal_id"] == "goal-3"
    assert final_status.data["status"] == "completed"


def test_implementation_plan_expands_goal_registry_from_compound_goal(tmp_path):
    store = _store(tmp_path)

    plan_result = plan_implementation(
        store,
        "Build review flow, state management, and release checks",
        fresh_reviewer=False,
    )

    goal_registry = plan_result.data["goal_registry"]
    assert len(goal_registry) == 5
    assert len(plan_result.data["code_scaffold_map"]) == 8
    assert "src/plb/review" in plan_result.data["directory_tree"]
    assert any(item["kind"] == "file" and item["path"] == "src/plb/review/build-review-flow.py" for item in plan_result.data["bootstrap_manifest"])
    assert len(plan_result.data["task_batch_list"]) == 5
    assert plan_result.data["code_scaffold_map"][1]["files"][0] == "src/plb/review/build-review-flow.py"
    assert goal_registry[1]["goal"] == "implement Build review flow for Build review flow, state management, and release checks"
    assert goal_registry[2]["goal"] == "implement state management for Build review flow, state management, and release checks"
    assert goal_registry[3]["goal"] == "implement release checks for Build review flow, state management, and release checks"
    assert goal_registry[4]["goal"] == "run regressions and finalize Build review flow, state management, and release checks"
    assert goal_registry[4]["depends_on"] == ["goal-1", "goal-2", "goal-3", "goal-4"]
