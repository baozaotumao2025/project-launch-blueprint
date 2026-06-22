from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from plb.core.errors import PLBError
from plb.commands.review import (
    approve_review,
    packet_review,
    record_review,
    reject_review,
    run_review,
)
from plb.commands.root import get_project_status, init_project, publish_project
from plb.commands.stage import list_stages, next_step, plan_stage, set_stage_status, stage_status, verify_stage
from plb.core.paths import ProjectPaths, resolve_project_root
from plb.state.store import StateStore
from plb.workflow.registry import STAGE_ORDER

console = Console()
app = typer.Typer(add_completion=False, help="Project Launch Blueprint CLI")
stage_app = typer.Typer(help="Stage operations")
review_app = typer.Typer(help="Reviewer operations")

app.add_typer(stage_app, name="stage")
app.add_typer(review_app, name="review")


def _register_stage_namespace(stage_name: str) -> None:
    namespace = typer.Typer(help=f"{stage_name} stage")
    stage_app.add_typer(namespace, name=stage_name)

    @namespace.command("plan")
    def _plan(
        project: Annotated[str | None, typer.Option("--project", "-p")] = None,
        goal: Annotated[str | None, typer.Option("--goal")] = None,
        fresh_reviewer: Annotated[bool, typer.Option("--fresh-reviewer/--no-fresh-reviewer")] = False,
        dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    ) -> None:
        store = _store(project)
        _render_result(plan_stage(stage_name, store, goal=goal, fresh_reviewer=fresh_reviewer, dry_run=dry_run))

    @namespace.command("status")
    def _status(
        project: Annotated[str | None, typer.Option("--project", "-p")] = None,
        verbose: Annotated[bool, typer.Option("--verbose")] = False,
    ) -> None:
        store = _store(project)
        _render_result(stage_status(stage_name, store, verbose=verbose))

    @namespace.command("next")
    def _next(
        project: Annotated[str | None, typer.Option("--project", "-p")] = None,
        goal_id: Annotated[str | None, typer.Option("--goal-id")] = None,
        regress: Annotated[bool, typer.Option("--regress/--no-regress")] = True,
        dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    ) -> None:
        store = _store(project)
        _render_result(next_step(stage_name, store, goal_id=goal_id, regress=regress, dry_run=dry_run))

    @namespace.command("verify")
    def _verify(
        project: Annotated[str | None, typer.Option("--project", "-p")] = None,
        strict: Annotated[bool, typer.Option("--strict")] = False,
    ) -> None:
        store = _store(project)
        _render_result(verify_stage(stage_name, store, strict=strict))

    @namespace.command("set")
    def _set(
        status: str,
        project: Annotated[str | None, typer.Option("--project", "-p")] = None,
    ) -> None:
        store = _store(project)
        _render_result(set_stage_status(stage_name, status, store))


for _stage in STAGE_ORDER:
    _register_stage_namespace(_stage.value)


def _paths(project: str | None) -> ProjectPaths:
    return ProjectPaths(root=resolve_project_root(project))


def _render_result(result) -> None:
    table = Table(show_header=False, box=None)
    table.add_row("status", result.status)
    if result.message:
        table.add_row("message", result.message)
    for key, value in result.data.items():
        table.add_row(key, str(value))
    console.print(table)


def _store(project: str | None) -> StateStore:
    paths = _paths(project)
    store = StateStore(paths)
    store.ensure_layout()
    return store


def _run(command):
    try:
        _render_result(command())
    except PLBError as exc:
        raise typer.Exit(code=1) from exc


def main() -> None:
    app()


@app.command()
def init(project: Annotated[str | None, typer.Option("--project", "-p")] = None) -> None:
    store = _store(project)
    _run(lambda: init_project(store))


@app.command()
def status(project: Annotated[str | None, typer.Option("--project", "-p")] = None) -> None:
    store = _store(project)
    _run(lambda: get_project_status(store))


@app.command()
def publish(project: Annotated[str | None, typer.Option("--project", "-p")] = None) -> None:
    store = _store(project)
    _run(lambda: publish_project(store))


@stage_app.command("plan")
def stage_plan(
    stage: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
    goal: Annotated[str | None, typer.Option("--goal")] = None,
    fresh_reviewer: Annotated[bool, typer.Option("--fresh-reviewer/--no-fresh-reviewer")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    store = _store(project)
    _render_result(plan_stage(stage, store, goal=goal, fresh_reviewer=fresh_reviewer, dry_run=dry_run))


@stage_app.command("status")
def stage_status_cmd(
    stage: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
    verbose: Annotated[bool, typer.Option("--verbose")] = False,
) -> None:
    store = _store(project)
    _render_result(stage_status(stage, store, verbose=verbose))


@stage_app.command("next")
def stage_next(
    stage: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
    goal_id: Annotated[str | None, typer.Option("--goal-id")] = None,
    regress: Annotated[bool, typer.Option("--regress/--no-regress")] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    store = _store(project)
    _render_result(next_step(stage, store, goal_id=goal_id, regress=regress, dry_run=dry_run))


@stage_app.command("verify")
def stage_verify(
    stage: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
    strict: Annotated[bool, typer.Option("--strict")] = False,
) -> None:
    store = _store(project)
    _render_result(verify_stage(stage, store, strict=strict))


@stage_app.command("list")
def stage_list() -> None:
    _render_result(list_stages())


@stage_app.command("set")
def stage_set(
    stage: str,
    status: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
) -> None:
    store = _store(project)
    _render_result(set_stage_status(stage, status, store))


@review_app.command("packet")
def review_packet(
    stage: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
) -> None:
    store = _store(project)
    _render_result(packet_review(stage, store))


@review_app.command("run")
def review_run(
    stage: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
) -> None:
    store = _store(project)
    _render_result(run_review(stage, store))


@review_app.command("record")
def review_record(
    stage: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
) -> None:
    store = _store(project)
    _render_result(record_review(stage, store))


@review_app.command("approve")
def review_approve(
    stage: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
) -> None:
    store = _store(project)
    _render_result(approve_review(stage, store))


@review_app.command("reject")
def review_reject(
    stage: str,
    project: Annotated[str | None, typer.Option("--project", "-p")] = None,
) -> None:
    store = _store(project)
    _render_result(reject_review(stage, store))
