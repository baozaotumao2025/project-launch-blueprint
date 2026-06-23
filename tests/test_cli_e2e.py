from __future__ import annotations

import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from plb import bootstrap
from plb.core.paths import ProjectPaths
from plb.core.models import WorkflowStage
from plb.state.store import StateStore


def _run_cli(root: Path, *args: str) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = bootstrap.main(["--root", str(root), *args])
    return exit_code, stdout.getvalue(), stderr.getvalue()


def _store(root: Path) -> StateStore:
    store = StateStore(ProjectPaths(root=root))
    store.ensure_layout()
    return store


def _write_discovery_inputs(root: Path) -> None:
    analysis = root / "analysis"
    (analysis / "story-maps").mkdir(parents=True, exist_ok=True)
    (analysis / "pages").mkdir(parents=True, exist_ok=True)
    (analysis / "features").mkdir(parents=True, exist_ok=True)
    (analysis / "gwt").mkdir(parents=True, exist_ok=True)
    (analysis / "relations").mkdir(parents=True, exist_ok=True)
    (analysis / "notes").mkdir(parents=True, exist_ok=True)
    (analysis / "brief.md").write_text("Brief", encoding="utf-8")
    (analysis / "story-maps" / "story.md").write_text("Story", encoding="utf-8")
    (analysis / "pages" / "page.md").write_text("Page", encoding="utf-8")
    (analysis / "features" / "index.md").write_text("Feature", encoding="utf-8")
    (analysis / "gwt" / "case.feature").write_text("Feature: Case", encoding="utf-8")
    (analysis / "relations" / "relations.md").write_text("Relations", encoding="utf-8")
    (analysis / "notes" / "extra.md").write_text("Notes", encoding="utf-8")


def _write_incomplete_discovery_inputs(root: Path) -> None:
    analysis = root / "analysis"
    (analysis / "story-maps").mkdir(parents=True, exist_ok=True)
    (analysis / "pages").mkdir(parents=True, exist_ok=True)
    (analysis / "brief.md").write_text("Brief", encoding="utf-8")
    (analysis / "story-maps" / "story.md").write_text("Story", encoding="utf-8")
    (analysis / "pages" / "page.md").write_text("Page", encoding="utf-8")


def _complete_review_cycle(root: Path, stage: str, goal: str | None = None) -> tuple[int, str, str]:
    plan_args = ["stage", stage, "plan"]
    if goal is not None:
        plan_args.extend(["--goal", goal])
    plan_exit, plan_out, plan_err = _run_cli(root, *plan_args)
    assert plan_exit == 0, plan_out + plan_err

    packet_exit, packet_out, packet_err = _run_cli(root, "review", "packet", stage)
    assert packet_exit == 0, packet_out + packet_err

    run_exit, run_out, run_err = _run_cli(root, "review", "run", stage)
    assert run_exit == 0, run_out + run_err

    record_exit, record_out, record_err = _run_cli(root, "review", "record", stage)
    assert record_exit == 0, record_out + record_err

    approve_exit, approve_out, approve_err = _run_cli(root, "review", "approve", stage)
    assert approve_exit == 0, approve_out + approve_err

    next_exit, next_out, next_err = _run_cli(root, "stage", stage, "next")
    assert next_exit == 0, next_out + next_err
    return next_exit, next_out, next_err


def test_cli_e2e_runs_full_pipeline_and_cleans_temp_root() -> None:
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="plb-e2e-") as tmp_root:
        root = Path(tmp_root)

        init_exit, init_out, init_err = _run_cli(root, "init")
        assert init_exit == 0, init_out + init_err
        assert "project_state: initialized" in init_out

        missing_discovery_exit, missing_discovery_out, missing_discovery_err = _run_cli(
            root,
            "stage",
            "discovery",
            "plan",
            "--goal",
            "discover launch scope",
        )
        assert missing_discovery_exit == 1
        assert "requires user-prepared analysis inputs" in missing_discovery_err

        _write_discovery_inputs(root)

        status_exit, status_out, status_err = _run_cli(root, "status")
        assert status_exit == 0, status_out + status_err
        assert "completed_stages: 0" in status_out

        ambiguous_exit, ambiguous_out, ambiguous_err = _run_cli(root, "route", "随便说点别的")
        assert ambiguous_exit == 0, ambiguous_out + ambiguous_err
        assert "status: blocked" in ambiguous_out
        assert "could not route natural-language request" in ambiguous_out

        plan_exit, plan_out, plan_err = _run_cli(root, "stage", "discovery", "plan", "--goal", "discover launch scope")
        assert plan_exit == 0, plan_out + plan_err
        assert "status: ok" in plan_out

        packet_exit, packet_out, packet_err = _run_cli(root, "review", "packet", "discovery")
        assert packet_exit == 0, packet_out + packet_err

        store = _store(root)
        packet = store.read_review_artifact(WorkflowStage.DISCOVERY, "packet")
        discovery_inventory = packet["payload"]["analysis_inventory"]
        discovery_coverage = packet["payload"]["analysis_coverage_template"]
        discovery_inventory_paths = [item["path"] for item in discovery_inventory]
        assert "analysis/notes/extra.md" in discovery_inventory_paths
        assert packet["payload"]["analysis_scope_summary"]["total_files"] == len(discovery_inventory)
        assert len(discovery_inventory) == len(discovery_coverage)
        assert [item["path"] for item in discovery_coverage] == discovery_inventory_paths

        packet["payload"]["analysis_coverage_template"] = discovery_coverage[:-1]
        store.write_review_artifact(WorkflowStage.DISCOVERY, "packet", packet)

        tampered_run_exit, tampered_run_out, tampered_run_err = _run_cli(root, "review", "run", "discovery")
        assert tampered_run_exit == 0, tampered_run_out + tampered_run_err
        assert "worker_review_state: needs_revision" in tampered_run_out

        packet_exit, packet_out, packet_err = _run_cli(root, "review", "packet", "discovery")
        assert packet_exit == 0, packet_out + packet_err
        run_exit, run_out, run_err = _run_cli(root, "review", "run", "discovery")
        assert run_exit == 0, run_out + run_err
        assert "worker_review_state: passed" in run_out
        record_exit, record_out, record_err = _run_cli(root, "review", "record", "discovery")
        assert record_exit == 0, record_out + record_err
        approve_exit, approve_out, approve_err = _run_cli(root, "review", "approve", "discovery")
        assert approve_exit == 0, approve_out + approve_err
        assert "recorded_review_state: passed" in approve_out
        next_exit, next_out, next_err = _run_cli(root, "stage", "discovery", "next")
        assert next_exit == 0, next_out + next_err
        assert "allowed: True" in next_out
        assert "next_stage: domain" in next_out

        domain_plan_exit, domain_plan_out, domain_plan_err = _run_cli(root, "stage", "domain", "plan", "--goal", "scope domain boundary")
        assert domain_plan_exit == 0, domain_plan_out + domain_plan_err

        domain_packet_exit, domain_packet_out, domain_packet_err = _run_cli(root, "review", "packet", "domain")
        assert domain_packet_exit == 0, domain_packet_out + domain_packet_err

        domain_packet = store.read_review_artifact(WorkflowStage.DOMAIN, "packet")
        domain_inventory = domain_packet["payload"]["domain_input_inventory"]
        domain_coverage = domain_packet["payload"]["domain_coverage_template"]
        domain_inventory_paths = [item["path"] for item in domain_inventory]
        assert "analysis/notes/extra.md" in domain_inventory_paths
        assert any(item["role"] == "primary" for item in domain_inventory)
        assert len(domain_inventory) == len(domain_coverage)
        assert [item["path"] for item in domain_coverage] == domain_inventory_paths

        domain_packet["payload"]["domain_coverage_template"] = domain_coverage[:-1]
        store.write_review_artifact(WorkflowStage.DOMAIN, "packet", domain_packet)

        domain_tampered_run_exit, domain_tampered_run_out, domain_tampered_run_err = _run_cli(
            root,
            "review",
            "run",
            "domain",
        )
        assert domain_tampered_run_exit == 0, domain_tampered_run_out + domain_tampered_run_err
        assert "worker_review_state: needs_revision" in domain_tampered_run_out

        domain_packet_exit, domain_packet_out, domain_packet_err = _run_cli(root, "review", "packet", "domain")
        assert domain_packet_exit == 0, domain_packet_out + domain_packet_err
        domain_run_exit, domain_run_out, domain_run_err = _run_cli(root, "review", "run", "domain")
        assert domain_run_exit == 0, domain_run_out + domain_run_err
        domain_record_exit, domain_record_out, domain_record_err = _run_cli(root, "review", "record", "domain")
        assert domain_record_exit == 0, domain_record_out + domain_record_err
        domain_approve_exit, domain_approve_out, domain_approve_err = _run_cli(root, "review", "approve", "domain")
        assert domain_approve_exit == 0, domain_approve_out + domain_approve_err
        assert "recorded_review_state: passed" in domain_approve_out

        for stage, goal in [
            ("state", "model state transitions"),
            ("api", "shape api contract"),
            ("design", "define design system rules"),
            ("slice", "assemble a vertical slice"),
            ("gates", "validate implementation gates"),
        ]:
            stage_plan_exit, stage_plan_out, stage_plan_err = _run_cli(root, "stage", stage, "plan", "--goal", goal)
            assert stage_plan_exit == 0, stage_plan_out + stage_plan_err
            assert "status: ok" in stage_plan_out
            stage_packet_exit, stage_packet_out, stage_packet_err = _run_cli(root, "review", "packet", stage)
            assert stage_packet_exit == 0, stage_packet_out + stage_packet_err
            stage_run_exit, stage_run_out, stage_run_err = _run_cli(root, "review", "run", stage)
            assert stage_run_exit == 0, stage_run_out + stage_run_err
            assert "worker_review_state: passed" in stage_run_out
            stage_record_exit, stage_record_out, stage_record_err = _run_cli(root, "review", "record", stage)
            assert stage_record_exit == 0, stage_record_out + stage_record_err
            stage_approve_exit, stage_approve_out, stage_approve_err = _run_cli(root, "review", "approve", stage)
            assert stage_approve_exit == 0, stage_approve_out + stage_approve_err
            assert "recorded_review_state: passed" in stage_approve_out
            stage_next_exit, stage_next_out, stage_next_err = _run_cli(root, "stage", stage, "next")
            assert stage_next_exit == 0, stage_next_out + stage_next_err
            assert "allowed: True" in stage_next_out

        implementation_missing_goal_exit, implementation_missing_goal_out, implementation_missing_goal_err = _run_cli(
            root,
            "stage",
            "implementation",
            "plan",
        )
        assert implementation_missing_goal_exit == 0, implementation_missing_goal_out + implementation_missing_goal_err
        assert "status: blocked" in implementation_missing_goal_out
        assert "implementation plan requires --goal" in implementation_missing_goal_out

        implementation_plan_exit, implementation_plan_out, implementation_plan_err = _run_cli(
            root,
            "stage",
            "implementation",
            "plan",
            "--goal",
            "Build a small customer invite prototype",
        )
        assert implementation_plan_exit == 0, implementation_plan_out + implementation_plan_err
        assert "status: ok" in implementation_plan_out

        implementation_store = _store(root)
        implementation_run = implementation_store.load_implementation_run()
        assert implementation_run is not None
        total_goals = int(implementation_run["goal_progress"]["total_goals"])
        assert total_goals >= 3

        for _ in range(total_goals):
            next_exit, next_out, next_err = _run_cli(root, "stage", "implementation", "next")
            assert next_exit == 0, next_out + next_err
            assert "regression_passed: True" in next_out

        verify_exit, verify_out, verify_err = _run_cli(root, "stage", "implementation", "verify", "--strict")
        assert verify_exit == 0, verify_out + verify_err
        assert "status: go" in verify_out
        assert "gaps: []" in verify_out

        final_store = _store(root)
        assert final_store.load().project_state.value == "implemented"

    assert not root.exists()


def test_cli_e2e_rejects_incomplete_analysis_before_discovery() -> None:
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="plb-e2e-negative-") as tmp_root:
        root = Path(tmp_root)

        init_exit, init_out, init_err = _run_cli(root, "init")
        assert init_exit == 0, init_out + init_err

        _write_incomplete_discovery_inputs(root)
        plan_exit, plan_out, plan_err = _run_cli(root, "stage", "discovery", "plan", "--goal", "discover launch scope")
        assert plan_exit == 1
        assert "analysis/features/index.md" in plan_err or "analysis/gwt/*.feature" in plan_err

        route_exit, route_out, route_err = _run_cli(root, "route", "完全看不懂这句")
        assert route_exit == 0, route_out + route_err
        assert "status: blocked" in route_out
        assert "hint" in route_out

    assert not root.exists()
