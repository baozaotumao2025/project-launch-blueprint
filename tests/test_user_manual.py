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
