from __future__ import annotations

from plb import bootstrap
from plb.commands.review import packet_review
from plb.commands.stage import plan_stage
from plb.core.errors import WorkflowStateError
from plb.core.models import WorkflowStage
from plb.core.paths import ProjectPaths
from plb.state.store import StateStore


def _store(tmp_path):
    store = StateStore(ProjectPaths(root=tmp_path))
    store.ensure_layout()
    return store


def test_discovery_plan_requires_user_prepared_analysis_inputs(tmp_path):
    store = _store(tmp_path)

    try:
        plan_stage(WorkflowStage.DISCOVERY.value, store, goal="discover launch scope")
    except WorkflowStateError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected discovery planning to fail without analysis inputs")

    assert "analysis/brief.md" in message
    assert "analysis/story-maps/*.md" in message
    assert "analysis/pages/*.md" in message
    assert "analysis/features/index.md" in message
    assert "analysis/gwt/*.feature" in message
    assert "analysis/relations/*.md" in message


def test_discovery_packet_requires_user_prepared_analysis_inputs(tmp_path):
    store = _store(tmp_path)

    try:
        packet_review(WorkflowStage.DISCOVERY.value, store)
    except WorkflowStateError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected discovery packet creation to fail without analysis inputs")

    assert "analysis/brief.md" in message


def test_bootstrap_route_blocks_missing_discovery_inputs(tmp_path, capsys):
    exit_code = bootstrap.main(["--root", str(tmp_path), "route", "开始 discovery"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "requires user-prepared analysis inputs" in captured.err
    assert "analysis/brief.md" in captured.err
