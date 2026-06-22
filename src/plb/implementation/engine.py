from __future__ import annotations

from dataclasses import asdict
import re

from plb.core.models import CommandResult, GoalEntry, GoalProgress, ProjectState, RegressionCheck, StageStatus, WorkflowStage
from plb.state.store import StateStore


def _normalize_goal_text(goal_text: str) -> str:
    cleaned = " ".join(goal_text.strip().split())
    return cleaned or "implement requested goal"


def _derive_goal_clauses(goal_text: str) -> list[str]:
    text = _normalize_goal_text(goal_text)
    parts = re.split(r"\s*(?:,|，|;|；|、|\band then\b|\band\b|\bthen\b|和|以及|并且|并|再)\s*", text, flags=re.IGNORECASE)
    clauses = [part.strip() for part in parts if part and part.strip()]
    unique: list[str] = []
    seen: set[str] = set()
    for clause in clauses:
        normalized = clause.lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(clause)
    return unique


def _build_goal_registry(goal_text: str, scope: str) -> list[GoalEntry]:
    base = _normalize_goal_text(goal_text)
    clauses = _derive_goal_clauses(goal_text)
    if not clauses:
        clauses = ["core behavior"]

    goal_registry: list[GoalEntry] = [
        GoalEntry(
            goal_id="goal-1",
            order=1,
            goal=f"freeze scope for {base}",
            depends_on=[],
            status="active",
            regression_scope=[],
            rollback_point="analysis",
            evidence=[base, scope],
        )
    ]

    prior_goal_ids: list[str] = ["goal-1"]
    for index, clause in enumerate(clauses, start=2):
        goal_id = f"goal-{index}"
        goal_registry.append(
            GoalEntry(
                goal_id=goal_id,
                order=index,
                goal=f"implement {clause} for {base}",
                depends_on=list(prior_goal_ids),
                status="pending",
                regression_scope=list(prior_goal_ids),
                rollback_point="analysis",
                evidence=[base, scope, clause],
            )
        )
        prior_goal_ids.append(goal_id)

    final_order = len(goal_registry) + 1
    goal_registry.append(
        GoalEntry(
            goal_id=f"goal-{final_order}",
            order=final_order,
            goal=f"run regressions and finalize {base}",
            depends_on=list(prior_goal_ids),
            status="pending",
            regression_scope=list(prior_goal_ids),
            rollback_point="analysis",
            evidence=[base, scope],
        )
    )
    return goal_registry


def _build_regression_checks(goal_registry: list[GoalEntry]) -> list[RegressionCheck]:
    checks: list[RegressionCheck] = []
    for goal in goal_registry:
        checks.append(
            RegressionCheck(
                after_goal=goal.goal_id,
                what_to_rerun=list(goal.regression_scope),
                why=f"protect regressions after {goal.goal_id}",
                pass_criteria=[f"{goal.goal_id} scope remains stable"],
                rollback_point=goal.rollback_point or "analysis",
            )
        )
    return checks


def _goal_progress(goal_registry: list[GoalEntry]) -> GoalProgress:
    current_goal = ""
    next_goal = ""
    completed = 0
    for index, goal in enumerate(goal_registry):
        if goal.status == "completed":
            completed += 1
            continue
        if goal.status == "active" and not current_goal:
            current_goal = goal.goal_id
            if index + 1 < len(goal_registry):
                next_goal = goal_registry[index + 1].goal_id
            break
    if not current_goal and goal_registry:
        first_pending = next((goal for goal in goal_registry if goal.status in {"pending", "active"}), None)
        if first_pending is not None:
            current_goal = first_pending.goal_id
            idx = goal_registry.index(first_pending)
            if idx + 1 < len(goal_registry):
                next_goal = goal_registry[idx + 1].goal_id
    return GoalProgress(
        total_goals=len(goal_registry),
        completed_goals=completed,
        current_goal=current_goal,
        next_goal=next_goal,
    )


def _serialize_run(store: StateStore, run: dict[str, object]) -> None:
    goal_registry = [asdict(entry) for entry in run["goal_registry"]]
    regression_checks = [asdict(check) for check in run["regression_checks"]]
    payload = {
        "goal_registry": goal_registry,
        "goal_progress": asdict(run["goal_progress"]),
        "regression_checks": regression_checks,
        "implementation_plan": run.get("implementation_plan", []),
        "code_scaffold_map": run.get("code_scaffold_map", []),
        "directory_tree": run.get("directory_tree", []),
        "bootstrap_manifest": run.get("bootstrap_manifest", []),
        "task_batch_list": run.get("task_batch_list", []),
        "branch_commit_plan": run.get("branch_commit_plan", []),
        "verification_plan": run.get("verification_plan", {}),
        "assumptions": run.get("assumptions", []),
        "inputs": run.get("inputs", {}),
        "latest_verification": run.get("latest_verification", {}),
        "blocked_items": list(run.get("blocked_items", [])),
        "rollback_point": run.get("rollback_point", "analysis"),
        "status": run.get("status", "active"),
    }
    store.save_implementation_run(
        goal=str(run["goal"]),
        scope=str(run["scope"]),
        fresh_reviewer=bool(run.get("fresh_reviewer", False)),
        payload=payload,
        status=str(run.get("status", "active")),
    )


def _load_goals(payload: dict[str, object]) -> list[GoalEntry]:
    goals: list[GoalEntry] = []
    for item in payload.get("goal_registry", []):
        goals.append(
            GoalEntry(
                goal_id=str(item.get("goal_id", "")),
                order=int(item.get("order", 0)),
                goal=str(item.get("goal", "")),
                depends_on=list(item.get("depends_on", [])),
                status=str(item.get("status", "pending")),
                regression_scope=list(item.get("regression_scope", [])),
                rollback_point=str(item.get("rollback_point", "analysis")),
                evidence=list(item.get("evidence", [])),
            )
        )
    return goals


def _load_regressions(payload: dict[str, object]) -> list[RegressionCheck]:
    checks: list[RegressionCheck] = []
    for item in payload.get("regression_checks", []):
        checks.append(
            RegressionCheck(
                after_goal=str(item.get("after_goal", "")),
                what_to_rerun=list(item.get("what_to_rerun", [])),
                why=str(item.get("why", "")),
                pass_criteria=list(item.get("pass_criteria", [])),
                rollback_point=str(item.get("rollback_point", "analysis")),
                status=str(item.get("status", "pending")),
                evidence=list(item.get("evidence", [])),
            )
        )
    return checks


def _goal_by_id(goal_registry: list[GoalEntry], goal_id: str) -> GoalEntry | None:
    return next((goal for goal in goal_registry if goal.goal_id == goal_id), None)


def _goal_index(goal_registry: list[GoalEntry], goal_id: str) -> int:
    for index, goal in enumerate(goal_registry):
        if goal.goal_id == goal_id:
            return index
    return -1


def _prior_goal_ids(goal_registry: list[GoalEntry], goal_id: str) -> list[str]:
    index = _goal_index(goal_registry, goal_id)
    if index <= 0:
        return []
    return [goal.goal_id for goal in goal_registry[:index]]


def _slugify(text: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    if not tokens:
        return "goal"
    return "-".join(tokens[:5])


def _infer_layer(clause: str) -> tuple[str, str, str]:
    normalized = clause.lower()
    slug = _slugify(clause)
    if any(keyword in normalized for keyword in ("review", "reviewer", "audit", "verdict")):
        return "review", "src/plb/review/", f"tests/test_{slug}_review.py"
    if any(keyword in normalized for keyword in ("state", "workflow", "transition")):
        return "state", "src/plb/state/", f"tests/test_{slug}_state.py"
    if any(keyword in normalized for keyword in ("release", "publish", "ship")):
        return "release", "src/plb/commands/root.py", f"tests/test_{slug}_release.py"
    if any(keyword in normalized for keyword in ("api", "contract", "endpoint")):
        return "api", "src/plb/commands/", f"tests/test_{slug}_api.py"
    if any(keyword in normalized for keyword in ("design", "theme", "token", "style")):
        return "design", "records/project-launch-blueprint/design-system/", f"tests/test_{slug}_design.py"
    if any(keyword in normalized for keyword in ("slice", "flow", "journey", "feature")):
        return "vertical slice", "src/plb/implementation/", f"tests/test_{slug}_slice.py"
    if any(keyword in normalized for keyword in ("gate", "quality", "regression", "verify")):
        return "quality gates", "records/project-launch-blueprint/quality-gates/", f"tests/test_{slug}_gates.py"
    if any(keyword in normalized for keyword in ("test", "check", "validation")):
        return "testing", "tests/", f"tests/test_{slug}.py"
    return "feature", f"src/plb/features/{slug}/", f"tests/test_{slug}.py"


def _scaffold_files(layer: str, slug: str, test_location: str) -> list[str]:
    if layer == "review":
        return [f"src/plb/review/{slug}.py", test_location]
    if layer == "state":
        return [f"src/plb/state/{slug}.py", test_location]
    if layer == "release":
        return ["src/plb/commands/root.py", test_location]
    if layer == "api":
        return [f"src/plb/commands/{slug}.py", test_location]
    if layer == "design":
        return [f"records/project-launch-blueprint/design-system/{slug}.md", test_location]
    if layer == "vertical slice":
        return [f"src/plb/features/{slug}/index.py", f"src/plb/features/{slug}/service.py", test_location]
    if layer == "quality gates":
        return [f"records/project-launch-blueprint/quality-gates/{slug}.md", test_location]
    if layer == "testing":
        return [test_location]
    return [f"src/plb/features/{slug}/index.py", f"src/plb/features/{slug}/service.py", test_location]


def _scaffold_directories(files: list[str]) -> list[str]:
    directories: list[str] = []
    seen: set[str] = set()
    for file_path in files:
        parts = file_path.split("/")[:-1]
        while parts:
            directory = "/".join(parts)
            if directory and directory not in seen:
                seen.add(directory)
                directories.append(directory)
            parts = parts[:-1]
    return directories


def _build_code_scaffold_map(goal_registry: list[GoalEntry], clauses: list[str]) -> list[dict[str, object]]:
    scaffold_map: list[dict[str, object]] = [
        {
            "artifact": "implementation runtime foundation",
            "code_location": "src/plb/implementation/",
            "purpose": "hold goal registry, regression checks and execution flow",
            "owner_layer": "implementation bridge",
            "files": [
                "src/plb/implementation/engine.py",
                "src/plb/implementation/__init__.py",
                "tests/test_implementation_progress.py",
            ],
            "directories": ["src/plb/implementation", "tests"],
            "evidence": [goal_registry[0].goal_id if goal_registry else "goal-1"],
        }
    ]
    for index, clause in enumerate(clauses, start=2):
        slug = _slugify(clause)
        layer, code_location, test_location = _infer_layer(clause)
        scaffold_map.append(
            {
                "artifact": f"{slug} module scaffold",
                "code_location": code_location,
                "purpose": f"implement {clause}",
                "owner_layer": layer,
                "files": _scaffold_files(layer, slug, test_location),
                "directories": _scaffold_directories(_scaffold_files(layer, slug, test_location)),
                "evidence": [f"goal-{index}", clause],
            }
        )
        scaffold_map.append(
            {
                "artifact": f"{slug} test scaffold",
                "code_location": test_location,
                "purpose": f"verify {clause}",
                "owner_layer": "testing",
                "files": [test_location],
                "directories": _scaffold_directories([test_location]),
                "evidence": [f"goal-{index}", clause],
            }
        )
    scaffold_map.append(
        {
            "artifact": "regression and handoff scaffold",
            "code_location": "tests/test_implementation_progress.py",
            "purpose": "protect prior goals and capture final handoff",
            "owner_layer": "implementation bridge",
            "files": [
                "tests/test_implementation_progress.py",
                "tests/test_review_finalization.py",
            ],
            "directories": ["tests"],
            "evidence": [goal_registry[-1].goal_id if goal_registry else "goal-1"],
        }
    )
    return scaffold_map


def _build_directory_tree(scaffold_map: list[dict[str, object]]) -> list[str]:
    directories: list[str] = []
    seen: set[str] = set()
    for item in scaffold_map:
        for directory in item.get("directories", []):
            if isinstance(directory, str) and directory and directory not in seen:
                seen.add(directory)
                directories.append(directory)
    return directories


def _build_bootstrap_manifest(scaffold_map: list[dict[str, object]], directory_tree: list[str]) -> list[dict[str, object]]:
    manifest: list[dict[str, object]] = []
    seen_files: set[str] = set()
    for directory in directory_tree:
        manifest.append(
            {
                "kind": "directory",
                "action": "create",
                "path": directory,
                "parent": "/".join(directory.split("/")[:-1]),
                "source": "directory_tree",
            }
        )
    for item in scaffold_map:
        owner_layer = str(item.get("owner_layer", "implementation bridge"))
        purpose = str(item.get("purpose", "bootstrap scaffold"))
        source = str(item.get("artifact", "scaffold"))
        for file_path in item.get("files", []):
            if not isinstance(file_path, str) or not file_path or file_path in seen_files:
                continue
            seen_files.add(file_path)
            manifest.append(
                {
                    "kind": "file",
                    "action": "create",
                    "path": file_path,
                    "parent": "/".join(file_path.split("/")[:-1]),
                    "source": source,
                    "owner_layer": owner_layer,
                    "purpose": purpose,
                }
            )
    return manifest


def _build_bootstrap_steps(bootstrap_manifest: list[dict[str, object]]) -> list[dict[str, object]]:
    steps: list[dict[str, object]] = []
    step_index = 1

    directories = [item for item in bootstrap_manifest if item.get("kind") == "directory"]
    files = [item for item in bootstrap_manifest if item.get("kind") == "file"]

    if directories:
        steps.append(
            {
                "step": f"bootstrap-step-{step_index}",
                "action": "create_directories",
                "items": directories,
                "rollback_point": directories[0].get("parent", "analysis"),
            }
        )
        step_index += 1

    if files:
        steps.append(
            {
                "step": f"bootstrap-step-{step_index}",
                "action": "create_files",
                "items": files,
                "rollback_point": files[0].get("parent", "analysis"),
            }
        )
        step_index += 1

    steps.append(
        {
            "step": f"bootstrap-step-{step_index}",
            "action": "verify_bootstrap",
            "items": [
                "confirm directories exist",
                "confirm scaffold files are present",
                "confirm tests are wired to generated paths",
            ],
            "rollback_point": "analysis",
        }
    )
    return steps


def _build_task_batches(goal_registry: list[GoalEntry], clauses: list[str]) -> list[dict[str, object]]:
    batches: list[dict[str, object]] = [
        {
            "batch_name": "freeze_scope",
            "goal": goal_registry[0].goal if goal_registry else "freeze scope",
            "tasks": [
                "normalize the goal text",
                "freeze the implementation scope",
                "record rollback point",
            ],
            "dependencies": [],
            "acceptance_criteria": [
                "goal can be expressed as a single scope",
                "rollback point is analysis",
            ],
            "rollback_point": "analysis",
            "evidence": [goal_registry[0].goal if goal_registry else "goal-1"],
        }
    ]
    for index, clause in enumerate(clauses, start=2):
        goal = goal_registry[index - 1] if index - 1 < len(goal_registry) else None
        slug = _slugify(clause)
        layer, code_location, test_location = _infer_layer(clause)
        batches.append(
            {
                "batch_name": f"build_{slug}",
                "goal": goal.goal if goal is not None else clause,
                "tasks": [
                    f"create {code_location} scaffold",
                    f"add types and contracts for {clause}",
                    f"add tests at {test_location}",
                    f"wire mock / real toggle for {layer}",
                ],
                "dependencies": list(goal.depends_on) if goal is not None else [f"goal-{index - 1}"],
                "acceptance_criteria": [
                    f"{layer} boundary exists",
                    "mock and real remain structurally aligned",
                    "tests cover a positive and a negative path",
                ],
                "rollback_point": goal.rollback_point if goal is not None else "analysis",
                "evidence": [f"goal-{index}", clause, layer],
            }
        )
    final_goal = goal_registry[-1] if goal_registry else None
    batches.append(
        {
            "batch_name": "regression_and_handoff",
            "goal": final_goal.goal if final_goal is not None else "run regressions and finalize",
            "tasks": [
                "rerun all prior goal regression checks",
                "record latest verification",
                "prepare implementation handoff report",
            ],
            "dependencies": list(final_goal.depends_on) if final_goal is not None else [],
            "acceptance_criteria": [
                "every completed goal is protected by regression",
                "latest verification is persisted",
                "handoff report has an explicit decision",
            ],
            "rollback_point": final_goal.rollback_point if final_goal is not None else "analysis",
            "evidence": [final_goal.goal_id if final_goal is not None else "goal-final"],
        }
    )
    return batches


def _build_branch_commit_plan(goal_registry: list[GoalEntry], clauses: list[str]) -> list[dict[str, object]]:
    branches: list[dict[str, object]] = [
        {
            "branch_name": f"feat/{_slugify(goal_registry[0].goal if goal_registry else 'implementation')}-scope",
            "commit_theme": "scope freeze",
            "scope": "freeze scope and record rollback point",
            "notes": ["one batch, one commit", "do not widen scope mid-flight"],
        }
    ]
    for index, clause in enumerate(clauses, start=2):
        branches.append(
            {
                "branch_name": f"feat/{_slugify(clause)}-{index}",
                "commit_theme": _infer_layer(clause)[0],
                "scope": clause,
                "notes": [f"goal-{index}", "keep regression checks adjacent"],
            }
        )
    branches.append(
        {
            "branch_name": f"feat/{_slugify(goal_registry[-1].goal if goal_registry else 'handoff')}-handoff",
            "commit_theme": "regression and handoff",
            "scope": "final regression sweep and handoff",
            "notes": ["final verification must be persisted", "ready for release review"],
        }
    )
    return branches


def _build_verification_plan(goal_registry: list[GoalEntry], regressions: list[RegressionCheck], clauses: list[str]) -> dict[str, object]:
    positive_checks = [
        "goal registry can be traced to code scaffold map",
        "every batch has a rollback point",
        "latest verification is persisted after each goal",
    ]
    negative_checks = [
        "component does not bypass service or repository layers",
        "no goal introduces a new business concept",
        "no batch skips regression for completed goals",
    ]
    test_matrix = [
        "mock / real parity for each generated slice",
        "positive path and counterexample path for each clause",
    ]
    manual_checks = [
        "review scaffold tree before implementation",
        "confirm regression scope after each goal",
    ]
    automation_checks = [
        "uv run python -m pytest",
        "implementation next auto-updates latest_verification",
    ]
    return {
        "positive_checks": positive_checks,
        "negative_checks": negative_checks,
        "test_matrix": test_matrix,
        "manual_checks": manual_checks,
        "automation_checks": automation_checks,
        "regression_checks": [asdict(check) for check in regressions],
        "clauses": list(clauses),
        "goal_count": len(goal_registry),
    }


def _build_implementation_steps(goal_registry: list[GoalEntry], scaffold_map: list[dict[str, object]], task_batches: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "step": "freeze_scope",
            "intent": "把 goal 冻结成单一实现范围",
            "deliverables": [goal_registry[0].goal if goal_registry else "scope note"],
            "rollback_point": "analysis",
            "evidence": [goal_registry[0].goal_id if goal_registry else "goal-1"],
        },
        {
            "step": "break_down_goals",
            "intent": "按并列语义和依赖关系拆分 goal registry",
            "deliverables": [f"{len(goal_registry)} goals", "dependency chain"],
            "rollback_point": "analysis",
            "evidence": [goal.goal_id for goal in goal_registry],
        },
        {
            "step": "map_artifacts",
            "intent": "把每个 goal 映射到代码目录和测试位置",
            "deliverables": [f"{len(scaffold_map)} scaffold items"],
            "rollback_point": "analysis",
            "evidence": [item["code_location"] for item in scaffold_map[: min(3, len(scaffold_map))]],
        },
        {
            "step": "scaffold",
            "intent": "先创建目录、入口和测试壳",
            "deliverables": [batch["batch_name"] for batch in task_batches],
            "rollback_point": task_batches[0]["rollback_point"] if task_batches else "analysis",
            "evidence": [batch["batch_name"] for batch in task_batches[: min(3, len(task_batches))]],
        },
        {
            "step": "implement",
            "intent": "按批次填充行为和边界",
            "deliverables": ["module implementations", "service hooks", "tests"],
            "rollback_point": task_batches[1]["rollback_point"] if len(task_batches) > 1 else "analysis",
            "evidence": [batch["goal"] for batch in task_batches[1:-1]],
        },
        {
            "step": "wire_validation",
            "intent": "把正向、负向和回归检查接起来",
            "deliverables": ["verification plan", "regression matrix"],
            "rollback_point": task_batches[-1]["rollback_point"] if task_batches else "analysis",
            "evidence": [batch["batch_name"] for batch in task_batches[-1:]],
        },
        {
            "step": "review_counterexamples",
            "intent": "用反例检查是否越界或假完成",
            "deliverables": ["counterexample notes", "review summary"],
            "rollback_point": task_batches[-1]["rollback_point"] if task_batches else "analysis",
            "evidence": [goal.goal_id for goal in goal_registry],
        },
        {
            "step": "decide",
            "intent": "确认是否可以进入真实编码",
            "deliverables": ["implementation handoff report"],
            "rollback_point": task_batches[-1]["rollback_point"] if task_batches else "analysis",
            "evidence": [goal_registry[-1].goal_id if goal_registry else "goal-final"],
        },
    ]


def plan_implementation(store: StateStore, goal_text: str | None, fresh_reviewer: bool = False, dry_run: bool = False) -> CommandResult:
    if not goal_text or not goal_text.strip():
        return CommandResult(status="blocked", message="implementation plan requires --goal", data={"blocked_items": ["missing goal"]})

    scope = _normalize_goal_text(goal_text)
    clauses = _derive_goal_clauses(goal_text)
    goal_registry = _build_goal_registry(goal_text, scope)
    progress = _goal_progress(goal_registry)
    regressions = _build_regression_checks(goal_registry)
    scaffold_map = _build_code_scaffold_map(goal_registry, clauses)
    directory_tree = _build_directory_tree(scaffold_map)
    bootstrap_manifest = _build_bootstrap_manifest(scaffold_map, directory_tree)
    task_batches = _build_task_batches(goal_registry, clauses)
    branch_commit_plan = _build_branch_commit_plan(goal_registry, clauses)
    verification_plan = _build_verification_plan(goal_registry, regressions, clauses)
    implementation_plan = _build_implementation_steps(goal_registry, scaffold_map, task_batches)
    run = {
        "goal": scope,
        "scope": scope,
        "fresh_reviewer": fresh_reviewer,
        "inputs": {
            "codex_goal": scope,
            "quality_gates_validation_report": "",
            "vertical_slice_map": "",
            "api_contract_map": "",
            "design_system_map": "",
            "state_machine_map": "",
            "domain_model_map": "",
            "discovery_capability_map": "",
            "technical_solution": "",
        },
        "goal_registry": goal_registry,
        "goal_progress": progress,
        "regression_checks": regressions,
        "implementation_plan": implementation_plan,
        "code_scaffold_map": scaffold_map,
        "directory_tree": directory_tree,
        "bootstrap_manifest": bootstrap_manifest,
        "task_batch_list": task_batches,
        "branch_commit_plan": branch_commit_plan,
        "verification_plan": verification_plan,
        "assumptions": [
            "quality gates inputs are frozen before implementation",
            "goal registry is derived from goal text clauses",
        ],
        "latest_verification": {
            "goal_id": "",
            "regression_passed": False,
            "checked_goals": [],
            "blocked_items": [],
            "rollback_point": "analysis",
            "status": "pending",
        },
        "blocked_items": [],
        "rollback_point": "analysis",
        "status": "active",
    }

    if not dry_run:
        _serialize_run(store, run)
        store.set_stage(WorkflowStage.IMPLEMENTATION, StageStatus.ACTIVE, {"goal": scope, "phase": "plan"})
        store.set_project_state(ProjectState.READY_FOR_IMPLEMENTATION, {"goal": scope})

    return CommandResult(
        status="ok" if not dry_run else "dry_run",
        message="implementation plan created" if not dry_run else "implementation plan previewed",
        data={
            "goal": scope,
            "scope": scope,
            "goal_progress": asdict(progress),
            "goal_registry": [asdict(goal) for goal in goal_registry],
            "regression_checks": [asdict(check) for check in regressions],
            "implementation_plan": implementation_plan,
            "code_scaffold_map": scaffold_map,
            "directory_tree": directory_tree,
            "bootstrap_manifest": bootstrap_manifest,
            "task_batch_list": task_batches,
            "branch_commit_plan": branch_commit_plan,
            "verification_plan": verification_plan,
            "inputs": run["inputs"],
            "assumptions": run["assumptions"],
            "blocked_items": [],
            "handoff_notes": [
                "scaffold first",
                "run regression after every goal",
            ],
            "latest_verification": run["latest_verification"],
            "rollback_point": "analysis",
            "fresh_reviewer": fresh_reviewer,
        },
    )


def status_implementation(store: StateStore) -> CommandResult:
    run = store.load_implementation_run()
    if run is None:
        return CommandResult(
            status="ok",
            message="implementation run not initialized",
            data={"goal_progress": asdict(GoalProgress()), "goal_registry": [], "regression_checks": [], "rollback_point": "analysis"},
        )

    goal_registry = _load_goals(run)
    regressions = _load_regressions(run)
    progress = run.get("goal_progress")
    if isinstance(progress, dict):
        progress_obj = GoalProgress(
            total_goals=int(progress.get("total_goals", len(goal_registry))),
            completed_goals=int(progress.get("completed_goals", 0)),
            current_goal=str(progress.get("current_goal", "")),
            next_goal=str(progress.get("next_goal", "")),
        )
    else:
        progress_obj = _goal_progress(goal_registry)
    latest_verification = run.get("latest_verification", {})
    if not isinstance(latest_verification, dict):
        latest_verification = {}
    return CommandResult(
        status="ok",
        message="implementation status loaded",
        data={
            "goal": run.get("goal", ""),
            "scope": run.get("scope", ""),
            "goal_progress": asdict(progress_obj),
            "goal_registry": [asdict(goal) for goal in goal_registry],
            "regression_checks": [asdict(check) for check in regressions],
            "implementation_plan": run.get("implementation_plan", []),
            "code_scaffold_map": run.get("code_scaffold_map", []),
            "directory_tree": run.get("directory_tree", []),
            "bootstrap_manifest": run.get("bootstrap_manifest", []),
            "task_batch_list": run.get("task_batch_list", []),
            "branch_commit_plan": run.get("branch_commit_plan", []),
            "verification_plan": run.get("verification_plan", {}),
            "assumptions": run.get("assumptions", []),
            "latest_verification": latest_verification,
            "rollback_point": run.get("rollback_point", "analysis"),
            "status": run.get("status", "active"),
        },
    )


def _mark_goal_status(goal_registry: list[GoalEntry], goal_id: str, status: str) -> None:
    goal = _goal_by_id(goal_registry, goal_id)
    if goal is not None:
        goal.status = status


def _run_regressions(goal: GoalEntry, goal_registry: list[GoalEntry]) -> tuple[bool, list[str]]:
    blocked: list[str] = []
    for dependency_id in goal.regression_scope:
        dependency = _goal_by_id(goal_registry, dependency_id)
        if dependency is None or dependency.status != "completed":
            blocked.append(dependency_id)
    return len(blocked) == 0, blocked


def next_implementation(store: StateStore, goal_id: str | None = None, regress: bool = True, dry_run: bool = False) -> CommandResult:
    run = store.load_implementation_run()
    if run is None:
        return CommandResult(status="blocked", message="implementation plan is missing", data={"blocked_items": ["no implementation run"], "rollback_point": "analysis"})

    goal_registry = _load_goals(run)
    if not goal_registry:
        return CommandResult(status="blocked", message="goal registry is empty", data={"blocked_items": ["empty goal registry"], "rollback_point": str(run.get("rollback_point", "analysis"))})

    explicit_goal = _goal_by_id(goal_registry, goal_id) if goal_id else None
    if goal_id and explicit_goal is None:
        return CommandResult(
            status="blocked",
            message=f"goal {goal_id} not found",
            data={"blocked_items": [goal_id], "rollback_point": str(run.get("rollback_point", "analysis"))},
        )

    current_goal = explicit_goal or _goal_by_id(goal_registry, str(run.get("goal_progress", {}).get("current_goal", "")))
    if current_goal is None:
        current_goal = next((goal for goal in goal_registry if goal.status in {"pending", "active"}), None)
    if current_goal is None:
        return CommandResult(status="ok", message="implementation goals already completed", data={"goal_progress": run.get("goal_progress", {}), "rollback_point": str(run.get("rollback_point", "analysis"))})

    if goal_id and current_goal.status == "completed":
        return CommandResult(
            status="blocked",
            message=f"goal {goal_id} is already completed",
            data={"blocked_items": [goal_id], "rollback_point": current_goal.rollback_point or "analysis"},
        )

    if current_goal.status == "completed":
        next_pending = next((goal for goal in goal_registry if goal.status in {"pending", "active"}), None)
        if next_pending is None:
            return CommandResult(status="ok", message="implementation goals already completed", data={"goal_progress": run.get("goal_progress", {}), "rollback_point": str(run.get("rollback_point", "analysis"))})
        current_goal = next_pending

    if dry_run:
        progress = _goal_progress(goal_registry)
        return CommandResult(
            status="dry_run",
            message=f"would execute {current_goal.goal_id}",
            data={
                "current_goal": current_goal.goal_id,
                "goal_progress": asdict(progress),
                "regression_scope": list(current_goal.regression_scope),
                "rollback_point": current_goal.rollback_point or "analysis",
            },
        )

    _mark_goal_status(goal_registry, current_goal.goal_id, "completed")
    regression_passed = True
    regression_blockers: list[str] = []
    if regress:
        regression_passed, regression_blockers = _run_regressions(current_goal, goal_registry)
    checked_goals = _prior_goal_ids(goal_registry, current_goal.goal_id)

    regression_checks = _load_regressions(run)
    for check in regression_checks:
        if check.after_goal == current_goal.goal_id:
            check.status = "passed" if regression_passed else "failed"
            if regression_passed:
                check.evidence = [f"regression reran: {', '.join(checked_goals) or 'none'}"]
            elif regression_blockers:
                check.evidence = regression_blockers

    current_index = goal_registry.index(current_goal)
    next_goal = goal_registry[current_index + 1].goal_id if current_index + 1 < len(goal_registry) else ""
    if not regression_passed:
        current_goal.status = "blocked"
        run["blocked_items"] = regression_blockers
        run["status"] = "blocked"
        run["goal_progress"] = GoalProgress(
            total_goals=len(goal_registry),
            completed_goals=sum(1 for goal in goal_registry if goal.status == "completed"),
            current_goal=current_goal.goal_id,
            next_goal=next_goal,
        )
        run["latest_verification"] = {
            "goal_id": current_goal.goal_id,
            "regression_passed": False,
            "checked_goals": checked_goals,
            "blocked_items": regression_blockers,
            "rollback_point": current_goal.rollback_point or "analysis",
            "status": "blocked",
        }
        store.set_stage(WorkflowStage.IMPLEMENTATION, StageStatus.BLOCKED, {"goal": current_goal.goal_id, "blocked_items": regression_blockers})
    else:
        if next_goal:
            _mark_goal_status(goal_registry, next_goal, "active")
            store.set_stage(WorkflowStage.IMPLEMENTATION, StageStatus.ACTIVE, {"goal": next_goal, "phase": "next"})
        else:
            store.set_stage(WorkflowStage.IMPLEMENTATION, StageStatus.COMPLETED, {"goal": current_goal.goal_id, "phase": "completed"})
            store.set_project_state(ProjectState.IMPLEMENTED, {"goal": run.get("goal", "")})
            run["status"] = "completed"
        run["latest_verification"] = {
            "goal_id": current_goal.goal_id,
            "regression_passed": True,
            "checked_goals": checked_goals,
            "blocked_items": [],
            "rollback_point": current_goal.rollback_point or "analysis",
            "status": "passed",
        }

    run["goal_registry"] = goal_registry
    run["goal_progress"] = _goal_progress(goal_registry)
    run["regression_checks"] = regression_checks
    run["blocked_items"] = regression_blockers
    if not regression_passed:
        run["rollback_point"] = current_goal.rollback_point or "analysis"
    _serialize_run(store, run)

    return CommandResult(
        status="ok" if regression_passed else "blocked",
        message=f"implementation goal {current_goal.goal_id} processed",
        data={
            "current_goal": current_goal.goal_id,
            "goal_progress": asdict(run["goal_progress"]),
            "regression_passed": regression_passed,
            "blocked_items": regression_blockers,
            "rollback_point": current_goal.rollback_point or "analysis",
            "next_goal": run["goal_progress"].next_goal,
            "latest_verification": run.get("latest_verification", {}),
        },
    )


def verify_implementation(store: StateStore, strict: bool = False) -> CommandResult:
    run = store.load_implementation_run()
    if run is None:
        return CommandResult(status="no_go", message="implementation run is missing", data={"gaps": ["goal registry missing"], "rollback_point": "analysis"})

    goal_registry = _load_goals(run)
    regressions = _load_regressions(run)
    gaps: list[str] = []
    if not goal_registry:
        gaps.append("goal registry missing")
    if not regressions:
        gaps.append("regression checks missing")
    if strict:
        for goal in goal_registry:
            if goal.status != "completed":
                gaps.append(f"{goal.goal_id} is not completed")
        for check in regressions:
            if check.status != "passed":
                gaps.append(f"{check.after_goal} regression not passed")
    else:
        if any(goal.status == "blocked" for goal in goal_registry):
            gaps.append("blocked goal exists")
        if any(check.status == "failed" for check in regressions):
            gaps.append("failed regression exists")

    decision = "go" if not gaps else "no_go"
    latest_verification = run.get("latest_verification", {})
    if not isinstance(latest_verification, dict):
        latest_verification = {}
    return CommandResult(
        status=decision,
        message="implementation verify completed" if not gaps else "implementation verify found gaps",
        data={
            "goal_progress": run.get("goal_progress", asdict(GoalProgress())),
            "goal_registry": [asdict(goal) for goal in goal_registry],
            "regression_checks": [asdict(check) for check in regressions],
            "verification_plan": run.get("verification_plan", {}),
            "directory_tree": run.get("directory_tree", []),
            "bootstrap_manifest": run.get("bootstrap_manifest", []),
            "latest_verification": latest_verification,
            "gaps": gaps,
            "rollback_point": run.get("rollback_point", "analysis"),
        },
    )
