from __future__ import annotations

import runpy
import sys
from argparse import Namespace

import pytest

from plb import bootstrap
from plb.core.errors import PLBError
from plb.core.models import CommandResult


class _NoMessageResult:
    status = "ok"
    message = ""
    data = {"value": 1}


def test_bootstrap_init_and_status_use_explicit_root(tmp_path, capsys):
    init_exit = bootstrap.main(["--root", str(tmp_path), "init"])
    init_output = capsys.readouterr()

    assert init_exit == 0
    assert "plb scaffold initialized" in init_output.out
    assert "initialized" in init_output.out

    status_exit = bootstrap.main(["--root", str(tmp_path), "status"])
    status_output = capsys.readouterr()

    assert status_exit == 0
    assert "status snapshot loaded" in status_output.out
    assert "project_state: initialized" in status_output.out
    assert "completed_stages: 0" in status_output.out
    assert (tmp_path / ".project-launch-blueprint" / "state.db").exists()
    assert (tmp_path / "records" / "project-launch-blueprint" / "README.md").exists()
    assert (tmp_path / "records" / "project-launch-blueprint" / "discovery" / "method.md").exists()
    assert (tmp_path / "records" / "project-launch-blueprint" / "adr" / "README.md").exists()
    assert (tmp_path / "records" / "project-launch-blueprint" / "adr" / "0010-gates-stage-release-fence-before-implementation.md").exists()
    assert "docs_root" in init_output.out


def test_bootstrap_rejects_missing_root(tmp_path, capsys):
    missing_root = tmp_path / "does-not-exist"

    exit_code = bootstrap.main(["--root", str(missing_root), "status"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "does not exist" in captured.err


def test_bootstrap_route_can_drive_natural_language_intent(tmp_path, capsys):
    init_exit = bootstrap.main(["--root", str(tmp_path), "init"])
    capsys.readouterr()

    assert init_exit == 0

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

    route_exit = bootstrap.main(["--root", str(tmp_path), "route", "开始 discovery"])
    route_output = capsys.readouterr()

    assert route_exit == 0
    assert "discovery" in route_output.out
    assert "planned" in route_output.out or "active" in route_output.out


def test_bootstrap_init_preserves_existing_materialized_docs(tmp_path, capsys):
    docs_root = tmp_path / "records" / "project-launch-blueprint"
    docs_root.mkdir(parents=True, exist_ok=True)
    readme = docs_root / "README.md"
    readme.write_text("custom readme", encoding="utf-8")

    init_exit = bootstrap.main(["--root", str(tmp_path), "init"])
    capsys.readouterr()

    assert init_exit == 0
    assert readme.read_text(encoding="utf-8") == "custom readme"
    assert (docs_root / "discovery" / "method.md").exists()
    assert (docs_root / "adr" / "README.md").exists()
    assert (docs_root / "adr" / "0010-gates-stage-release-fence-before-implementation.md").exists()


def test_bootstrap_helpers_cover_default_root_and_value_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    assert bootstrap._normalize_root(None) == tmp_path.resolve()
    assert bootstrap._normalize_root("   ") == tmp_path.resolve()

    bootstrap._emit(_NoMessageResult())
    emitted = capsys.readouterr().out
    assert "status: ok" in emitted
    assert "message:" not in emitted
    assert "value: 1" in emitted

    not_a_directory = tmp_path / "payload.txt"
    not_a_directory.write_text("payload", encoding="utf-8")
    with pytest.raises(PLBError, match="not a directory"):
        bootstrap._validate_root(not_a_directory)

    exit_code = bootstrap._run(lambda: (_ for _ in ()).throw(ValueError("bad input")))
    stderr = capsys.readouterr().err

    assert exit_code == 1
    assert "bad input" in stderr


def test_bootstrap_routes_publish_stage_review_and_script_entrypoint(tmp_path, capsys, monkeypatch):
    init_exit = bootstrap.main(["--root", str(tmp_path), "init"])
    capsys.readouterr()
    assert init_exit == 0

    publish_exit = bootstrap.main(["--root", str(tmp_path), "publish"])
    publish_output = capsys.readouterr()
    assert publish_exit == 0
    assert "status: ok" in publish_output.out

    stage_list_exit = bootstrap.main(["--root", str(tmp_path), "stage", "list"])
    stage_list_output = capsys.readouterr()
    assert stage_list_exit == 0
    assert "discovery" in stage_list_output.out
    assert "implementation" in stage_list_output.out

    stage_status_exit = bootstrap.main(["--root", str(tmp_path), "stage", "discovery", "status"])
    stage_status_output = capsys.readouterr()
    assert stage_status_exit == 0
    assert "status:" in stage_status_output.out

    stage_set_exit = bootstrap.main(["--root", str(tmp_path), "stage", "discovery", "set", "completed"])
    stage_set_output = capsys.readouterr()
    assert stage_set_exit == 0
    assert "completed" in stage_set_output.out

    review_reject_exit = bootstrap.main(["--root", str(tmp_path), "review", "reject", "discovery"])
    review_reject_output = capsys.readouterr()
    assert review_reject_exit == 0
    assert "review reject" in review_reject_output.out

    monkeypatch.setattr(sys, "argv", ["plb", "--root", str(tmp_path), "stage", "list"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("plb.bootstrap", run_name="__main__")

    assert excinfo.value.code == 0


def test_bootstrap_dispatch_covers_stage_and_review_actions(monkeypatch):
    store = object()
    monkeypatch.setattr(bootstrap, "_store", lambda root: store)
    monkeypatch.setattr(bootstrap, "init_project", lambda s: CommandResult(status="ok", message="init", data={}))
    monkeypatch.setattr(bootstrap, "get_project_status", lambda s: CommandResult(status="ok", message="status", data={}))
    monkeypatch.setattr(bootstrap, "publish_project", lambda s: CommandResult(status="ok", message="publish", data={}))
    monkeypatch.setattr(bootstrap, "route_text", lambda text, s: CommandResult(status="ok", message="route", data={"text": text}))
    monkeypatch.setattr(bootstrap, "list_stages", lambda: CommandResult(status="ok", message="list", data={}))
    monkeypatch.setattr(bootstrap, "plan_stage", lambda *args, **kwargs: CommandResult(status="ok", message="plan", data={}))
    monkeypatch.setattr(bootstrap, "stage_status", lambda *args, **kwargs: CommandResult(status="ok", message="status", data={}))
    monkeypatch.setattr(bootstrap, "next_step", lambda *args, **kwargs: CommandResult(status="ok", message="next", data={}))
    monkeypatch.setattr(bootstrap, "verify_stage", lambda *args, **kwargs: CommandResult(status="ok", message="verify", data={}))
    monkeypatch.setattr(bootstrap, "set_stage_status", lambda *args, **kwargs: CommandResult(status="ok", message="set", data={}))
    monkeypatch.setattr(bootstrap, "packet_review", lambda *args, **kwargs: CommandResult(status="ok", message="packet", data={}))
    monkeypatch.setattr(bootstrap, "run_review", lambda *args, **kwargs: CommandResult(status="ok", message="run", data={}))
    monkeypatch.setattr(bootstrap, "record_review", lambda *args, **kwargs: CommandResult(status="ok", message="record", data={}))
    monkeypatch.setattr(bootstrap, "approve_review", lambda *args, **kwargs: CommandResult(status="ok", message="approve", data={}))
    monkeypatch.setattr(bootstrap, "reject_review", lambda *args, **kwargs: CommandResult(status="ok", message="reject", data={}))

    assert bootstrap._dispatch(Namespace(command="init", root=None)) == 0
    assert bootstrap._dispatch(Namespace(command="status", root=None)) == 0
    assert bootstrap._dispatch(Namespace(command="publish", root=None)) == 0
    assert bootstrap._dispatch(Namespace(command="route", root=None, text="hello")) == 0
    assert bootstrap._dispatch(Namespace(command="stage", root=None, stage_command="list")) == 0
    assert bootstrap._dispatch(
        Namespace(
            command="stage",
            root=None,
            stage_command="discovery",
            action="plan",
            goal="goal",
            fresh_reviewer=False,
            dry_run=False,
        )
    ) == 0
    assert bootstrap._dispatch(
        Namespace(command="stage", root=None, stage_command="discovery", action="status", verbose=True)
    ) == 0
    assert bootstrap._dispatch(
        Namespace(command="stage", root=None, stage_command="discovery", action="next", goal_id=None, regress=True, dry_run=False)
    ) == 0
    assert bootstrap._dispatch(
        Namespace(command="stage", root=None, stage_command="discovery", action="verify", strict=False)
    ) == 0
    assert bootstrap._dispatch(
        Namespace(command="stage", root=None, stage_command="discovery", action="set", status="completed")
    ) == 0
    assert bootstrap._dispatch(Namespace(command="review", root=None, review_action="packet", stage="discovery")) == 0
    assert bootstrap._dispatch(Namespace(command="review", root=None, review_action="run", stage="discovery")) == 0
    assert bootstrap._dispatch(Namespace(command="review", root=None, review_action="record", stage="discovery")) == 0
    assert bootstrap._dispatch(Namespace(command="review", root=None, review_action="approve", stage="discovery")) == 0
    assert bootstrap._dispatch(Namespace(command="review", root=None, review_action="reject", stage="discovery")) == 0

    with pytest.raises(PLBError, match="Unsupported command path"):
        bootstrap._dispatch(Namespace(command="stage", root=None, stage_command="discovery", action="bogus"))

    with pytest.raises(PLBError, match="Unsupported command path"):
        bootstrap._dispatch(Namespace(command="review", root=None, review_action="bogus", stage="discovery"))

    with pytest.raises(PLBError, match="Unsupported command path"):
        bootstrap._dispatch(Namespace(command="unsupported", root=None))
