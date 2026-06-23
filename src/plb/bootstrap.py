from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .commands.review import approve_review, packet_review, record_review, reject_review, run_review
from .commands.root import get_project_status, init_project, publish_project
from .commands.routing import route_text
from .commands.stage import list_stages, next_step, plan_stage, set_stage_status, stage_status, verify_stage
from .core.errors import PLBError
from .core.paths import ProjectPaths, ROOT_ENV_VAR
from .state.store import StateStore
from .workflow.registry import STAGE_ORDER


def _normalize_root(value: str | None) -> Path:
    if value is None or not str(value).strip():
        return Path.cwd().resolve()
    return Path(value).expanduser().resolve()


def _validate_root(root: Path) -> None:
    if not root.exists():
        raise PLBError(
            f"Project root '{root}' does not exist. Create it first or pass a valid --root / "
            f"set {ROOT_ENV_VAR}."
        )
    if not root.is_dir():
        raise PLBError(f"Project root '{root}' is not a directory.")


def _paths(root: Path) -> ProjectPaths:
    return ProjectPaths(root=root)


def _store(root: Path) -> StateStore:
    _validate_root(root)
    store = StateStore(_paths(root))
    store.ensure_layout()
    return store


def _emit(result) -> None:
    lines = [f"status: {result.status}"]
    if result.message:
        lines.append(f"message: {result.message}")
    for key, value in result.data.items():
        lines.append(f"{key}: {value}")
    sys.stdout.write("\n".join(lines) + "\n")


def _run(command) -> int:
    try:
        _emit(command())
        return 0
    except PLBError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    except ValueError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="plb", description="Project Launch Blueprint CLI")
    parser.add_argument(
        "--root",
        "-C",
        default=None,
        help=f"Project root directory. Defaults to ${{{ROOT_ENV_VAR}}} or the current working directory.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize the project space")
    init_parser.add_argument("--project", "-p", default=None, help="Project label used by callers.")

    status_parser = subparsers.add_parser("status", help="Show the current project status")
    status_parser.add_argument("--project", "-p", default=None, help="Project label used by callers.")

    publish_parser = subparsers.add_parser("publish", help="Publish the project bundle")
    publish_parser.add_argument("--project", "-p", default=None, help="Project label used by callers.")

    route_parser = subparsers.add_parser("route", help="Route a natural-language request")
    route_parser.add_argument("text")
    route_parser.add_argument("--project", "-p", default=None, help="Project label used by callers.")

    stage_parser = subparsers.add_parser("stage", help="Stage operations")
    stage_subparsers = stage_parser.add_subparsers(dest="stage_command", required=True)
    stage_names = [stage.value for stage in STAGE_ORDER]

    for stage_name in stage_names:
        namespace = stage_subparsers.add_parser(stage_name, help=f"{stage_name} stage operations")
        namespace_subparsers = namespace.add_subparsers(dest="action", required=True)

        plan_parser = namespace_subparsers.add_parser("plan", help=f"Plan {stage_name}")
        plan_parser.add_argument("--goal", default=None)
        plan_parser.add_argument("--fresh-reviewer", action="store_true", default=False)
        plan_parser.add_argument("--dry-run", action="store_true", default=False)
        plan_parser.add_argument("--project", "-p", default=None)

        status_parser = namespace_subparsers.add_parser("status", help=f"Status for {stage_name}")
        status_parser.add_argument("--verbose", action="store_true", default=False)
        status_parser.add_argument("--project", "-p", default=None)

        next_parser = namespace_subparsers.add_parser("next", help=f"Advance {stage_name}")
        next_parser.add_argument("--goal-id", default=None)
        next_parser.add_argument("--regress", action=argparse.BooleanOptionalAction, default=True)
        next_parser.add_argument("--dry-run", action="store_true", default=False)
        next_parser.add_argument("--project", "-p", default=None)

        verify_parser = namespace_subparsers.add_parser("verify", help=f"Verify {stage_name}")
        verify_parser.add_argument("--strict", action="store_true", default=False)
        verify_parser.add_argument("--project", "-p", default=None)

        set_parser = namespace_subparsers.add_parser("set", help=f"Set {stage_name} status")
        set_parser.add_argument("status")
        set_parser.add_argument("--project", "-p", default=None)

    stage_subparsers.add_parser("list", help="List workflow stages")

    review_parser = subparsers.add_parser("review", help="Reviewer operations")
    review_subparsers = review_parser.add_subparsers(dest="review_action", required=True)

    for action in ("packet", "run", "record", "approve", "reject"):
        action_parser = review_subparsers.add_parser(action, help=f"{action} a review")
        action_parser.add_argument("stage")
        action_parser.add_argument("--project", "-p", default=None)

    return parser


def _dispatch(args: argparse.Namespace) -> int:
    root = _normalize_root(getattr(args, "root", None))

    if args.command == "init":
        return _run(lambda: init_project(_store(root)))
    if args.command == "status":
        return _run(lambda: get_project_status(_store(root)))
    if args.command == "publish":
        return _run(lambda: publish_project(_store(root)))
    if args.command == "route":
        return _run(lambda: route_text(args.text, _store(root)))

    if args.command == "stage":
        if args.stage_command == "list":
            _emit(list_stages())
            return 0

        stage_name = args.stage_command
        project_root = root

        if args.action == "plan":
            return _run(
                lambda: plan_stage(
                    stage_name,
                    _store(project_root),
                    goal=args.goal,
                    fresh_reviewer=args.fresh_reviewer,
                    dry_run=args.dry_run,
                )
            )
        if args.action == "status":
            return _run(lambda: stage_status(stage_name, _store(project_root), verbose=args.verbose))
        if args.action == "next":
            return _run(
                lambda: next_step(
                    stage_name,
                    _store(project_root),
                    goal_id=args.goal_id,
                    regress=args.regress,
                    dry_run=args.dry_run,
                )
            )
        if args.action == "verify":
            return _run(lambda: verify_stage(stage_name, _store(project_root), strict=args.strict))
        if args.action == "set":
            return _run(lambda: set_stage_status(stage_name, args.status, _store(project_root)))

    if args.command == "review":
        project_root = root
        if args.review_action == "packet":
            return _run(lambda: packet_review(args.stage, _store(project_root)))
        if args.review_action == "run":
            return _run(lambda: run_review(args.stage, _store(project_root)))
        if args.review_action == "record":
            return _run(lambda: record_review(args.stage, _store(project_root)))
        if args.review_action == "approve":
            return _run(lambda: approve_review(args.stage, _store(project_root)))
        if args.review_action == "reject":
            return _run(lambda: reject_review(args.stage, _store(project_root)))

    raise PLBError("Unsupported command path.")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return _dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())
