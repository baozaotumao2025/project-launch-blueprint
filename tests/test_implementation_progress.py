from __future__ import annotations

import pytest

from plb.implementation.engine import (
    _build_bootstrap_steps,
    _build_goal_registry,
    _derive_goal_clauses,
    _goal_index,
    _goal_progress,
    _mark_goal_status,
    _slugify,
    _run_regressions,
    next_implementation,
    plan_implementation,
    status_implementation,
    verify_implementation,
)
from plb.core.models import GoalEntry, WorkflowStage
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


def test_implementation_dry_run_does_not_persist_and_missing_run_has_safe_defaults(tmp_path):
    store = _store(tmp_path)

    plan_result = plan_implementation(store, "Preview the implementation plan only", dry_run=True)

    assert plan_result.status == "dry_run"
    assert store.load_implementation_run() is None

    status_result = status_implementation(store)
    assert status_result.data["goal_progress"]["total_goals"] == 0
    assert status_result.data["goal_registry"] == []
    assert "latest_verification" not in status_result.data

    verify_result = verify_implementation(store)
    assert verify_result.status == "no_go"
    assert verify_result.data["gaps"] == ["goal registry missing"]


def test_implementation_plan_rejects_blank_goal(tmp_path):
    store = _store(tmp_path)

    result = plan_implementation(store, "   ")

    assert result.status == "blocked"
    assert result.data["blocked_items"] == ["missing goal"]


def test_implementation_status_falls_back_when_progress_is_not_dict(tmp_path):
    store = _store(tmp_path)
    plan_implementation(store, "Stabilize progress fallback")
    store.update_implementation_run({"goal_progress": "broken"})

    status_result = status_implementation(store)

    assert status_result.data["goal_progress"]["total_goals"] == 3
    assert status_result.data["goal_progress"]["current_goal"] == "goal-1"


def test_goal_progress_prefers_pending_goals_when_no_active_goal():
    progress = _goal_progress(
        [
            GoalEntry(
                goal_id="goal-1",
                order=1,
                goal="freeze scope",
                depends_on=[],
                status="completed",
                regression_scope=[],
                rollback_point="analysis",
                evidence=[],
            ),
            GoalEntry(
                goal_id="goal-2",
                order=2,
                goal="implement slice",
                depends_on=["goal-1"],
                status="pending",
                regression_scope=["goal-1"],
                rollback_point="analysis",
                evidence=[],
            ),
            GoalEntry(
                goal_id="goal-3",
                order=3,
                goal="final regression",
                depends_on=["goal-1", "goal-2"],
                status="pending",
                regression_scope=["goal-1", "goal-2"],
                rollback_point="analysis",
                evidence=[],
            ),
        ]
    )

    assert progress.total_goals == 3
    assert progress.completed_goals == 1
    assert progress.current_goal == "goal-2"
    assert progress.next_goal == "goal-3"


def test_goal_progress_handles_fully_completed_registry():
    progress = _goal_progress(
        [
            GoalEntry(
                goal_id="goal-1",
                order=1,
                goal="freeze scope",
                depends_on=[],
                status="completed",
                regression_scope=[],
                rollback_point="analysis",
                evidence=[],
            )
        ]
    )

    assert progress.total_goals == 1
    assert progress.completed_goals == 1
    assert progress.current_goal == ""
    assert progress.next_goal == ""


def test_implementation_internal_helpers_cover_edge_branches():
    assert _derive_goal_clauses(",,,") == []
    assert _derive_goal_clauses("alpha and alpha") == ["alpha"]
    assert _slugify("!!!") == "goal"
    assert _goal_index([], "goal-9") == -1

    registry = _build_goal_registry(",,,", "")
    assert registry[0].goal == "freeze scope for ,,,"
    assert registry[-1].goal == "run regressions and finalize ,,,"

    progress = _goal_progress(
        [
            GoalEntry(
                goal_id="goal-1",
                order=1,
                goal="freeze scope",
                depends_on=[],
                status="completed",
                regression_scope=[],
                rollback_point="analysis",
                evidence=[],
            ),
            GoalEntry(
                goal_id="goal-2",
                order=2,
                goal="final regression",
                depends_on=["goal-1"],
                status="pending",
                regression_scope=["goal-1"],
                rollback_point="analysis",
                evidence=[],
            ),
        ]
    )
    assert progress.current_goal == "goal-2"
    assert progress.next_goal == ""

    goals = [
        GoalEntry(
            goal_id="goal-1",
            order=1,
            goal="freeze scope",
            depends_on=[],
            status="pending",
            regression_scope=[],
            rollback_point="analysis",
            evidence=[],
        )
    ]
    _mark_goal_status(goals, "goal-1", "completed")
    _mark_goal_status(goals, "goal-9", "blocked")
    assert goals[0].status == "completed"


def test_implementation_next_rejects_invalid_goal_and_completed_goal(tmp_path):
    store = _store(tmp_path)
    plan_implementation(store, "Ship the first slice")

    missing_goal = next_implementation(store, goal_id="goal-999")
    assert missing_goal.status == "blocked"
    assert missing_goal.data["blocked_items"] == ["goal-999"]

    first_step = next_implementation(store)
    assert first_step.status == "ok"
    assert first_step.data["current_goal"] == "goal-1"

    completed_goal = next_implementation(store, goal_id="goal-1")
    assert completed_goal.status == "blocked"
    assert completed_goal.data["blocked_items"] == ["goal-1"]


def test_implementation_next_handles_missing_run_empty_registry_and_completed_current_goal(tmp_path):
    store = _store(tmp_path)

    missing = next_implementation(store)
    assert missing.status == "blocked"
    assert missing.data["blocked_items"] == ["no implementation run"]

    store.save_implementation_run(
        goal="manual",
        scope="manual",
        fresh_reviewer=False,
        payload={
            "goal_registry": [],
            "regression_checks": [],
            "goal_progress": {"total_goals": 0, "completed_goals": 0, "current_goal": "", "next_goal": ""},
        },
        status="active",
    )
    empty = next_implementation(store)
    assert empty.status == "blocked"
    assert empty.data["blocked_items"] == ["empty goal registry"]

    store.save_implementation_run(
        goal="manual",
        scope="manual",
        fresh_reviewer=False,
        payload={
            "goal_registry": [
                {
                    "goal_id": "goal-1",
                    "order": 1,
                    "goal": "freeze scope",
                    "depends_on": [],
                    "status": "completed",
                    "regression_scope": [],
                    "rollback_point": "analysis",
                    "evidence": [],
                }
            ],
            "regression_checks": [],
            "goal_progress": {"total_goals": 1, "completed_goals": 1, "current_goal": "goal-1", "next_goal": ""},
        },
        status="active",
    )
    completed = next_implementation(store)
    assert completed.status == "ok"
    assert completed.message == "implementation goals already completed"


def test_implementation_next_advances_completed_current_goal_to_next_pending(tmp_path):
    store = _store(tmp_path)
    store.save_implementation_run(
        goal="manual",
        scope="manual",
        fresh_reviewer=False,
        payload={
            "goal_registry": [
                {
                    "goal_id": "goal-1",
                    "order": 1,
                    "goal": "freeze scope",
                    "depends_on": [],
                    "status": "completed",
                    "regression_scope": [],
                    "rollback_point": "analysis",
                    "evidence": [],
                },
                {
                    "goal_id": "goal-2",
                    "order": 2,
                    "goal": "implement slice",
                    "depends_on": ["goal-1"],
                    "status": "pending",
                    "regression_scope": ["goal-1"],
                    "rollback_point": "analysis",
                    "evidence": [],
                },
            ],
            "regression_checks": [],
            "goal_progress": {"total_goals": 2, "completed_goals": 1, "current_goal": "goal-1", "next_goal": "goal-2"},
        },
        status="active",
    )

    result = next_implementation(store)

    assert result.status == "ok"
    assert result.data["current_goal"] == "goal-2"
    assert result.data["next_goal"] == ""


def test_implementation_next_blocks_when_regressions_fail(tmp_path):
    store = _store(tmp_path)
    plan_implementation(store, "Ship a multi-step workflow")

    blocked = next_implementation(store, goal_id="goal-2")

    assert blocked.status == "blocked"
    assert blocked.data["current_goal"] == "goal-2"
    assert blocked.data["blocked_items"] == ["goal-1"]
    assert blocked.data["latest_verification"]["status"] == "blocked"
    assert store.load_stage(WorkflowStage.IMPLEMENTATION).status.value == "blocked"


def test_implementation_regression_failure_always_carries_blockers(tmp_path):
    store = _store(tmp_path)
    plan_implementation(store, "Ship a multi-step workflow")

    run = store.load_implementation_run()
    assert run is not None
    goal_registry = [GoalEntry(**item) for item in run["goal_registry"]]
    current_goal = next(goal for goal in goal_registry if goal.goal_id == "goal-2")

    passed, blockers = _run_regressions(current_goal, goal_registry)

    assert passed is False
    assert blockers == ["goal-1"]


def test_implementation_next_asserts_failed_regressions_carry_blockers(tmp_path, monkeypatch):
    store = _store(tmp_path)
    plan_implementation(store, "Ship a multi-step workflow")

    monkeypatch.setattr("plb.implementation.engine._run_regressions", lambda goal, goal_registry: (False, []))

    with pytest.raises(AssertionError, match="failed regressions must report blockers"):
        next_implementation(store)


def test_implementation_next_covers_regress_false_and_empty_registry(tmp_path):
    store = _store(tmp_path)
    plan_implementation(store, "Ship a no-regress path")

    first = next_implementation(store, regress=False)
    assert first.status == "ok"
    assert first.data["regression_passed"] is True

    store.save_implementation_run(
        goal="manual",
        scope="manual",
        fresh_reviewer=False,
        payload={
            "goal_registry": [],
            "regression_checks": [],
            "goal_progress": {"total_goals": 0, "completed_goals": 0, "current_goal": "", "next_goal": ""},
        },
        status="active",
    )

    empty = next_implementation(store)
    assert empty.status == "blocked"
    assert empty.message == "goal registry is empty"


def test_implementation_next_covers_dry_run_and_completed_paths(tmp_path):
    store = _store(tmp_path)
    plan_implementation(store, "Ship a dry-run path")

    dry_run = next_implementation(store, dry_run=True)
    assert dry_run.status == "dry_run"
    assert dry_run.data["current_goal"] == "goal-1"

    first = next_implementation(store)
    second = next_implementation(store)
    third = next_implementation(store)
    completed = next_implementation(store)

    assert first.data["current_goal"] == "goal-1"
    assert second.data["current_goal"] == "goal-2"
    assert third.data["current_goal"] == "goal-3"
    assert completed.status == "ok"
    assert completed.message == "implementation goals already completed"


def test_implementation_status_and_verify_handle_bad_latest_verification(tmp_path):
    store = _store(tmp_path)
    plan_implementation(store, "Stabilize the runtime")

    updated = store.update_implementation_run({"latest_verification": []})
    assert updated is not None

    status_result = status_implementation(store)
    assert status_result.data["latest_verification"] == {}

    current = store.load_implementation_run()
    assert current is not None
    goal_registry = current["goal_registry"]
    goal_registry[0]["status"] = "blocked"
    store.update_implementation_run({"goal_registry": goal_registry})

    verify_result = verify_implementation(store, strict=False)
    assert "blocked goal exists" in verify_result.data["gaps"]
    assert verify_result.data["latest_verification"] == {}


def test_implementation_verify_reports_missing_registry_and_regression_checks(tmp_path):
    store = _store(tmp_path)

    store.save_implementation_run(
        goal="manual",
        scope="manual",
        fresh_reviewer=False,
        payload={
            "goal_registry": [],
            "regression_checks": [
                {
                    "after_goal": "goal-1",
                    "what_to_rerun": [],
                    "why": "protect",
                    "pass_criteria": [],
                    "rollback_point": "analysis",
                    "status": "passed",
                    "evidence": [],
                }
            ],
            "goal_progress": {"total_goals": 0, "completed_goals": 0, "current_goal": "", "next_goal": ""},
        },
        status="active",
    )

    missing_registry = verify_implementation(store, strict=True)
    assert "goal registry missing" in missing_registry.data["gaps"]

    store.save_implementation_run(
        goal="manual",
        scope="manual",
        fresh_reviewer=False,
        payload={
            "goal_registry": [
                {
                    "goal_id": "goal-1",
                    "order": 1,
                    "goal": "freeze scope",
                    "depends_on": [],
                    "status": "completed",
                    "regression_scope": [],
                    "rollback_point": "analysis",
                    "evidence": [],
                }
            ],
            "regression_checks": [],
            "goal_progress": {"total_goals": 1, "completed_goals": 1, "current_goal": "", "next_goal": ""},
        },
        status="active",
    )
    missing_checks = verify_implementation(store, strict=True)
    assert "regression checks missing" in missing_checks.data["gaps"]


def test_implementation_bootstrap_steps_cover_empty_and_single_item_manifests():
    empty_steps = _build_bootstrap_steps([])
    dir_only_steps = _build_bootstrap_steps([
        {"kind": "directory", "path": "src/plb/features", "parent": "src/plb"},
    ])
    file_only_steps = _build_bootstrap_steps([
        {"kind": "file", "path": "src/plb/features/index.py", "parent": "src/plb/features"},
    ])

    assert empty_steps == [
        {
            "step": "bootstrap-step-1",
            "action": "verify_bootstrap",
            "items": [
                "confirm directories exist",
                "confirm scaffold files are present",
                "confirm tests are wired to generated paths",
            ],
            "rollback_point": "analysis",
        }
    ]
    assert dir_only_steps[0]["action"] == "create_directories"
    assert dir_only_steps[-1]["action"] == "verify_bootstrap"
    assert file_only_steps[0]["action"] == "create_files"
    assert file_only_steps[-1]["action"] == "verify_bootstrap"


def test_implementation_verify_strict_reports_pending_goals_and_regressions(tmp_path):
    store = _store(tmp_path)
    plan_implementation(store, "Harden the verification path")

    strict = verify_implementation(store, strict=True)

    assert strict.status == "no_go"
    assert "goal-1 is not completed" in strict.data["gaps"]
    assert "goal-2 is not completed" in strict.data["gaps"]
    assert "goal-3 is not completed" in strict.data["gaps"]
    assert "goal-1 regression not passed" in strict.data["gaps"]
    assert "goal-2 regression not passed" in strict.data["gaps"]
    assert "goal-3 regression not passed" in strict.data["gaps"]


def test_implementation_verify_strict_and_non_strict_failed_regressions(tmp_path):
    store = _store(tmp_path)
    store.save_implementation_run(
        goal="manual",
        scope="manual",
        fresh_reviewer=False,
        payload={
            "goal_registry": [
                {
                    "goal_id": "goal-1",
                    "order": 1,
                    "goal": "freeze scope",
                    "depends_on": [],
                    "status": "completed",
                    "regression_scope": [],
                    "rollback_point": "analysis",
                    "evidence": [],
                }
            ],
            "regression_checks": [
                {
                    "after_goal": "goal-1",
                    "what_to_rerun": [],
                    "why": "protect",
                    "pass_criteria": [],
                    "rollback_point": "analysis",
                    "status": "failed",
                    "evidence": [],
                }
            ],
            "goal_progress": {"total_goals": 1, "completed_goals": 1, "current_goal": "", "next_goal": ""},
        },
        status="active",
    )

    strict = verify_implementation(store, strict=True)
    assert "goal-1 regression not passed" in strict.data["gaps"]

    non_strict = verify_implementation(store, strict=False)
    assert "failed regression exists" in non_strict.data["gaps"]


def test_implementation_verify_reports_missing_regression_checks_and_failed_regressions(tmp_path):
    store = _store(tmp_path)
    plan_implementation(store, "Detect regression gaps")

    store.save_implementation_run(
        goal="manual",
        scope="manual",
        fresh_reviewer=False,
        payload={
            "goal_registry": [
                {
                    "goal_id": "goal-1",
                    "order": 1,
                    "goal": "freeze scope",
                    "depends_on": [],
                    "status": "completed",
                    "regression_scope": [],
                    "rollback_point": "analysis",
                    "evidence": [],
                }
            ],
            "regression_checks": [],
            "goal_progress": {"total_goals": 1, "completed_goals": 1, "current_goal": "", "next_goal": ""},
        },
        status="active",
    )

    missing_checks = verify_implementation(store, strict=True)
    assert "regression checks missing" in missing_checks.data["gaps"]

    store.save_implementation_run(
        goal="manual",
        scope="manual",
        fresh_reviewer=False,
        payload={
            "goal_registry": [
                {
                    "goal_id": "goal-1",
                    "order": 1,
                    "goal": "freeze scope",
                    "depends_on": [],
                    "status": "completed",
                    "regression_scope": [],
                    "rollback_point": "analysis",
                    "evidence": [],
                }
            ],
            "regression_checks": [
                {
                    "after_goal": "goal-1",
                    "what_to_rerun": [],
                    "why": "protect",
                    "pass_criteria": [],
                    "rollback_point": "analysis",
                    "status": "failed",
                    "evidence": [],
                }
            ],
            "goal_progress": {"total_goals": 1, "completed_goals": 1, "current_goal": "", "next_goal": ""},
        },
        status="active",
    )

    failed = verify_implementation(store, strict=False)
    assert "failed regression exists" in failed.data["gaps"]


def test_implementation_plan_covers_all_layer_inference_paths(tmp_path):
    store = _store(tmp_path)

    plan_result = plan_implementation(
        store,
        "review audit, state workflow, release publish, api contract, design token, slice journey, gate regression, test validation, custom capability",
        fresh_reviewer=False,
    )

    owner_layers = {item["owner_layer"] for item in plan_result.data["code_scaffold_map"]}
    assert {"review", "state", "release", "api", "design", "vertical slice", "quality gates", "testing", "feature"} <= owner_layers
    assert any(item["code_location"] == "src/plb/review/" for item in plan_result.data["code_scaffold_map"])
    assert any(item["code_location"] == "src/plb/state/" for item in plan_result.data["code_scaffold_map"])
    assert any(item["code_location"] == "src/plb/commands/root.py" for item in plan_result.data["code_scaffold_map"])
    assert any(item["code_location"].startswith("src/plb/commands/") and item["code_location"] != "src/plb/commands/root.py" for item in plan_result.data["code_scaffold_map"])
    assert any(item["code_location"].startswith("records/project-launch-blueprint/design-system/") for item in plan_result.data["code_scaffold_map"])
    assert any(item["code_location"].startswith("records/project-launch-blueprint/quality-gates/") for item in plan_result.data["code_scaffold_map"])
    assert any(
        item["code_location"].startswith("src/plb/features/") and item["owner_layer"] == "feature"
        for item in plan_result.data["code_scaffold_map"]
    )


def test_implementation_bootstrap_steps_are_built_from_manifest(tmp_path):
    store = _store(tmp_path)

    plan_result = plan_implementation(store, "Launch the final bootstrapped slice")
    steps = _build_bootstrap_steps(plan_result.data["bootstrap_manifest"])

    assert len(steps) == 3
    assert steps[0]["action"] == "create_directories"
    assert steps[1]["action"] == "create_files"
    assert steps[2]["action"] == "verify_bootstrap"
    assert steps[2]["items"] == [
        "confirm directories exist",
        "confirm scaffold files are present",
        "confirm tests are wired to generated paths",
    ]
