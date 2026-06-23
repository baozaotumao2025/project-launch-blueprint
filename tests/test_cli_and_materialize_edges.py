from __future__ import annotations

from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from plb.cli import _paths, _render_result, _run, _store, app
from plb.core.errors import PLBError
from plb.core.paths import ProjectPaths
from plb.workflow.materialize import (
    MaterializationResult,
    _copy_file,
    _copy_tree,
    _repo_root,
    materialize_project_docs,
)


def test_cli_routes_root_stage_and_review_commands(tmp_path, monkeypatch):
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

    runner = CliRunner()

    result = runner.invoke(app, ["init", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "plb scaffold initialized" in result.output

    result = runner.invoke(app, ["status", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "initialized" in result.output

    result = runner.invoke(app, ["route", "开始 discovery", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "discovery" in result.output

    result = runner.invoke(app, ["stage", "list"])
    assert result.exit_code == 0
    assert "discovery" in result.output

    result = runner.invoke(app, ["publish", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "status" in result.output

    result = runner.invoke(app, ["stage", "plan", "discovery", "--project", str(tmp_path), "--goal", "discover scope"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["stage", "status", "discovery", "--project", str(tmp_path), "--verbose"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["stage", "next", "discovery", "--project", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["stage", "verify", "discovery", "--project", str(tmp_path)])
    assert result.exit_code == 0

    result = runner.invoke(app, ["stage", "set", "discovery", "completed", "--project", str(tmp_path)])
    assert result.exit_code == 0

    result = runner.invoke(app, ["stage", "discovery", "plan", "--project", str(tmp_path), "--goal", "discover scope"])
    assert result.exit_code == 0
    assert "planned" in result.output or "active" in result.output

    result = runner.invoke(app, ["stage", "discovery", "status", "--project", str(tmp_path), "--verbose"])
    assert result.exit_code == 0
    assert "status" in result.output

    result = runner.invoke(app, ["stage", "discovery", "next", "--project", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "status" in result.output

    result = runner.invoke(app, ["stage", "discovery", "verify", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "status" in result.output

    result = runner.invoke(app, ["stage", "discovery", "set", "completed", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "completed" in result.output

    result = runner.invoke(app, ["review", "packet", "discovery", "--project", str(tmp_path)])
    assert result.exit_code == 0
    assert "packet_created" in result.output or "status" in result.output

    result = runner.invoke(app, ["review", "run", "discovery", "--project", str(tmp_path)])
    assert result.exit_code == 0

    result = runner.invoke(app, ["review", "record", "discovery", "--project", str(tmp_path)])
    assert result.exit_code == 0

    result = runner.invoke(app, ["review", "approve", "discovery", "--project", str(tmp_path)])
    assert result.exit_code == 0

    result = runner.invoke(app, ["review", "reject", "discovery", "--project", str(tmp_path)])
    assert result.exit_code == 0

    assert _paths(str(tmp_path)).root == tmp_path.resolve()
    assert _store(str(tmp_path)).paths.root == tmp_path.resolve()
    _render_result(type("Result", (), {"status": "ok", "message": "", "data": {"value": 1}})())


def test_cli_main_and_run_error_path(monkeypatch):
    monkeypatch.setattr("plb.cli.app", lambda: None)
    from plb.cli import main

    assert main() is None

    with pytest.raises(typer.Exit) as exc_info:
        _run(lambda: (_ for _ in ()).throw(PLBError("boom")))

    assert exc_info.value.exit_code == 1


def test_materialize_copies_skips_and_handles_missing_sources(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    docs_root = tmp_path / "records" / "project-launch-blueprint"
    repo_root.mkdir()

    top_level = repo_root / "README.md"
    top_level.write_text("readme", encoding="utf-8")

    discovery_dir = repo_root / "discovery"
    discovery_dir.mkdir()
    (discovery_dir / "method.md").write_text("method", encoding="utf-8")
    (discovery_dir / "existing.md").write_text("existing", encoding="utf-8")

    adr_dir = repo_root / "adr"
    adr_dir.mkdir()
    (adr_dir / "0001-note.md").write_text("note", encoding="utf-8")

    monkeypatch.setattr("plb.workflow.materialize._repo_root", lambda: repo_root)

    paths = ProjectPaths(root=tmp_path)
    result = materialize_project_docs(paths)

    assert result.docs_root == docs_root
    assert isinstance(result, MaterializationResult)
    assert (docs_root / "README.md").read_text(encoding="utf-8") == "readme"
    assert (docs_root / "discovery" / "method.md").read_text(encoding="utf-8") == "method"
    assert (docs_root / "adr" / "0001-note.md").read_text(encoding="utf-8") == "note"
    assert result.copied_files
    assert result.skipped_files == []

    second = materialize_project_docs(paths)
    assert second.skipped_files
    assert any(path.endswith("README.md") for path in second.skipped_files)


def test_materialize_helpers_cover_copy_tree_and_copy_file_edges(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")
    (source / "nested").mkdir()
    (source / "nested" / "b.txt").write_text("b", encoding="utf-8")

    copied, skipped = _copy_tree(source, target)
    assert len(copied) == 2
    assert skipped == []
    assert (target / "a.txt").read_text(encoding="utf-8") == "a"
    assert (target / "nested" / "b.txt").read_text(encoding="utf-8") == "b"

    copied_again, skipped_again = _copy_tree(source, target)
    assert copied_again == []
    assert len(skipped_again) == 2

    missing_copied, missing_skipped = _copy_tree(tmp_path / "missing", tmp_path / "unused")
    assert missing_copied == []
    assert missing_skipped == []

    file_source = tmp_path / "file.txt"
    file_source.write_text("payload", encoding="utf-8")
    file_target = tmp_path / "file-target.txt"
    assert _copy_file(file_source, file_target) is True
    assert _copy_file(file_source, file_target) is False
    assert _repo_root().name == "project-launch-blueprint"
