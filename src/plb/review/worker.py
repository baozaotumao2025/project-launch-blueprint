from __future__ import annotations

import argparse
import json
from pathlib import Path

from plb.core.models import ReviewState
from plb.workflow.registry import STAGE_ORDER


ALLOWED_PACKET_KEYS = {"stage", "target", "review_state", "payload"}
REQUIRED_PAYLOAD_KEYS = {"project_state", "stage_status", "rollback_point", "counterexample_prompts", "approved_inputs"}
FORBIDDEN_CONTEXT_KEYS = {"generation_context", "private_context", "draft_prompt"}


def _stage_names() -> set[str]:
    return {stage.value for stage in STAGE_ORDER}


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(_is_nonempty_string(item) for item in value)


def _check_packet_shape(packet: dict[str, object]) -> list[str]:
    violations: list[str] = []
    missing = ALLOWED_PACKET_KEYS.difference(packet.keys())
    if missing:
        violations.append(f"missing packet keys: {', '.join(sorted(missing))}")
    extra = set(packet.keys()).difference(ALLOWED_PACKET_KEYS)
    if extra:
        violations.append(f"unexpected packet keys: {', '.join(sorted(extra))}")
    if not _is_nonempty_string(packet.get("stage")):
        violations.append("stage must be a non-empty string")
    elif str(packet["stage"]) not in _stage_names():
        violations.append(f"unknown stage: {packet['stage']}")
    if not _is_nonempty_string(packet.get("target")):
        violations.append("target must be a non-empty string")
    elif packet.get("stage") != packet.get("target"):
        violations.append("target must match stage")
    if packet.get("review_state") != ReviewState.PACKET_CREATED.value:
        violations.append("packet review_state must be packet_created")
    if not isinstance(packet.get("payload"), dict):
        violations.append("payload must be an object")
    return violations


def _check_payload_rules(packet: dict[str, object]) -> tuple[list[str], list[str], list[str]]:
    payload = packet.get("payload", {})
    if not isinstance(payload, dict):
        return ["payload is not an object"], [], []

    violations: list[str] = []
    evidence: list[str] = []
    counterexamples: list[str] = []

    missing = REQUIRED_PAYLOAD_KEYS.difference(payload.keys())
    if missing:
        violations.append(f"missing payload keys: {', '.join(sorted(missing))}")

    for key in FORBIDDEN_CONTEXT_KEYS:
        if key in payload:
            violations.append(f"forbidden context key present: {key}")

    if not _is_nonempty_string(payload.get("project_state")):
        violations.append("project_state must be a non-empty string")
    else:
        evidence.append(f"project_state={payload['project_state']}")

    if not _is_nonempty_string(payload.get("stage_status")):
        violations.append("stage_status must be a non-empty string")
    else:
        evidence.append(f"stage_status={payload['stage_status']}")

    if not _is_nonempty_string(payload.get("rollback_point")):
        violations.append("rollback_point must be a non-empty string")
    else:
        evidence.append(f"rollback_point={payload['rollback_point']}")

    prompts = payload.get("counterexample_prompts")
    if not _is_string_list(prompts):
        violations.append("counterexample_prompts must be a non-empty list of strings")
    else:
        evidence.append("counterexample prompts present")
        counterexamples.extend(prompts)

    approved_inputs = payload.get("approved_inputs")
    if not _is_string_list(approved_inputs):
        violations.append("approved_inputs must be a non-empty list of strings")
    else:
        evidence.extend(f"approved_input={item}" for item in approved_inputs)

    if payload.get("stage_status") in {"draft", "pending"}:
        violations.append("stage_status is not yet reviewable")

    return violations, evidence, counterexamples


def _evaluate_packet(packet: dict[str, object]) -> dict[str, object]:
    structural_violations = _check_packet_shape(packet)
    payload_violations, evidence, counterexamples = _check_payload_rules(packet)
    violations = structural_violations + payload_violations
    stage = str(packet.get("stage", ""))
    payload = packet.get("payload", {})
    rollback_point = "analysis"
    if isinstance(payload, dict) and _is_nonempty_string(payload.get("rollback_point")):
        rollback_point = str(payload["rollback_point"])

    if structural_violations:
        summary = f"packet malformed for {stage or 'unknown stage'}"
        review_state = ReviewState.FAILED.value
    elif violations:
        summary = f"revision needed for {stage}"
        review_state = ReviewState.NEEDS_REVISION.value
    else:
        summary = f"isolated review passed for {stage}"
        review_state = ReviewState.PASSED.value

    return {
        "packet": packet,
        "summary": summary,
        "review_state": review_state,
        "evidence": evidence,
        "counterexamples": counterexamples,
        "rollback_point": rollback_point,
        "violations": violations,
        "checks": {
            "packet_shape": not structural_violations,
            "payload_rules": not payload_violations,
            "target_matches_stage": packet.get("stage") == packet.get("target"),
            "has_evidence": bool(evidence),
            "has_counterexamples": bool(counterexamples),
            "has_rollback_point": bool(rollback_point),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="plb review worker")
    parser.add_argument("--packet", required=True)
    parser.add_argument("--result", required=True)
    args = parser.parse_args()

    packet_path = Path(args.packet)
    result_path = Path(args.result)
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    result = _evaluate_packet(packet)
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
