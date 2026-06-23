from __future__ import annotations

from plb.commands.review import approve_review, packet_review, record_review, reject_review, run_review
from plb.commands.root import get_project_status, init_project, publish_project
from plb.commands.stage import next_step, plan_stage, set_stage_status, stage_status, verify_stage
from plb.core.models import CommandResult, WorkflowStage
from plb.state.store import StateStore


def _normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _find_stage(text: str) -> WorkflowStage | None:
    normalized = _normalize_text(text)
    for stage in WorkflowStage:
        if stage.value in normalized:
            return stage
    return None


def route_text(text: str, store: StateStore) -> CommandResult:
    normalized = _normalize_text(text)
    stage = _find_stage(text)

    if "初始化" in normalized or "init" in normalized:
        return init_project(store)
    if "发布" in normalized or "publish" in normalized:
        return publish_project(store)
    if "状态" in normalized or "status" in normalized:
        if stage is None:
            return get_project_status(store)
        return stage_status(stage.value, store)
    if any(keyword in normalized for keyword in ("计划", "plan", "开始", "启动", "freeze scope", "frozen scope")) and stage is not None:
        return plan_stage(stage.value, store)
    if any(keyword in normalized for keyword in ("审查包", "packet", "packaging", "freeze review")) and stage is not None:
        return packet_review(stage.value, store)
    if any(keyword in normalized for keyword in ("运行审查", "review run", "run review", "审查运行", "review")) and stage is not None:
        return run_review(stage.value, store)
    if any(keyword in normalized for keyword in ("记录审查", "record", "落库")) and stage is not None:
        return record_review(stage.value, store)
    if any(keyword in normalized for keyword in ("批准", "approve")) and stage is not None:
        return approve_review(stage.value, store)
    if any(keyword in normalized for keyword in ("拒绝", "reject")) and stage is not None:
        return reject_review(stage.value, store)
    if any(keyword in normalized for keyword in ("验证", "verify")) and stage is not None:
        return verify_stage(stage.value, store)
    if any(keyword in normalized for keyword in ("推进", "next", "下一步")) and stage is not None:
        return next_step(stage.value, store)
    if any(keyword in normalized for keyword in ("set", "标记")) and stage is not None:
        return set_stage_status(stage.value, "active", store)

    return CommandResult(
        status="blocked",
        message="could not route natural-language request",
        data={"input": text, "hint": "mention init/status/plan/packet/run/record/approve/reject/verify/next and a stage name"},
    )
