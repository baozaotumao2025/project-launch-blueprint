from __future__ import annotations

from plb import bootstrap


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


def test_bootstrap_rejects_missing_root(tmp_path, capsys):
    missing_root = tmp_path / "does-not-exist"

    exit_code = bootstrap.main(["--root", str(missing_root), "status"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "does not exist" in captured.err
