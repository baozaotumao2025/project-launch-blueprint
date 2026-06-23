from __future__ import annotations

from typer.testing import CliRunner

from plb.cli import app


runner = CliRunner()


def test_init_creates_runtime_layout_without_business_source_tree(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0, result.output
    assert "status" in result.output
    assert "ok" in result.output
    assert "initialized" in result.output

    runtime_dir = tmp_path / ".project-launch-blueprint"
    assert runtime_dir.is_dir()
    assert (runtime_dir / "state.db").exists()
    assert (runtime_dir / "logs").is_dir()
    assert (runtime_dir / "audits").is_dir()
    assert (runtime_dir / "exports").is_dir()
    assert (runtime_dir / "backups").is_dir()
    assert (runtime_dir / "projections").is_dir()
    assert (tmp_path / "records" / "project-launch-blueprint" / "README.md").exists()
    assert (tmp_path / "records" / "project-launch-blueprint" / "discovery" / "method.md").exists()
    assert (tmp_path / "records" / "project-launch-blueprint" / "adr" / "README.md").exists()

    assert not (tmp_path / "src").exists()
    assert not (tmp_path / "tests").exists()


def test_status_before_init_reports_uninitialized_and_does_not_create_business_source_tree(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0, result.output
    assert "status" in result.output
    assert "uninitialized" in result.output
    assert "completed_stages" in result.output

    runtime_dir = tmp_path / ".project-launch-blueprint"
    assert runtime_dir.is_dir()
    assert (runtime_dir / "state.db").exists()

    assert not (tmp_path / "src").exists()
    assert not (tmp_path / "tests").exists()


def test_route_command_drives_the_same_stage_flow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

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

    result = runner.invoke(app, ["route", "开始 discovery"])

    assert result.exit_code == 0, result.output
    assert "discovery" in result.output
    assert "planned" in result.output or "active" in result.output
