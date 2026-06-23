from __future__ import annotations

import argparse
import json
from pathlib import Path

from plb.core.models import ReviewState
from plb.workflow.registry import STAGE_ORDER


ALLOWED_PACKET_KEYS = {"stage", "target", "review_state", "payload"}
REQUIRED_PAYLOAD_KEYS = {"project_state", "stage_status", "rollback_point", "counterexample_prompts", "approved_inputs", "prompt_bundle"}
FORBIDDEN_CONTEXT_KEYS = {"generation_context", "private_context", "draft_prompt"}
REQUIRED_PROMPT_BUNDLE_KEYS = {"stage", "purpose", "stage_dir", "template_name", "system_prompt", "user_prompt", "documents", "prompt_sections"}
REQUIRED_PROMPT_DOCUMENT_KEYS = {"name", "path", "text"}
STAGE_DOCUMENT_REQUIRED_KEYS = {"stage_document_inventory", "stage_document_summary", "stage_document_coverage_template"}
STAGE_DOCUMENT_COVERAGE_ROW_KEYS = {"name", "path", "role", "status", "mapped_to", "reason", "evidence"}
UPSTREAM_INPUT_REQUIRED_KEYS = {"upstream_input_inventory", "upstream_input_summary", "upstream_input_coverage_template"}
UPSTREAM_INPUT_COVERAGE_ROW_KEYS = {"source_stage", "role", "packet_path", "review_path", "status", "mapped_to", "reason", "evidence"}
DISCOVERY_REQUIRED_PAYLOAD_KEYS = {"analysis_inventory", "analysis_scope_summary", "analysis_coverage_template"}
DISCOVERY_COVERAGE_ROW_KEYS = {"path", "analysis_path", "status", "covered_by", "reason", "evidence"}
DOMAIN_REQUIRED_PAYLOAD_KEYS = {"domain_input_inventory", "domain_input_summary", "domain_coverage_template"}
DOMAIN_COVERAGE_ROW_KEYS = {"path", "input_type", "role", "status", "mapped_to", "reason", "evidence"}


def _stage_names() -> set[str]:
    return {stage.value for stage in STAGE_ORDER}


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(_is_nonempty_string(item) for item in value)


def _is_dict_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, dict) for item in value)


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

    prompt_bundle = payload.get("prompt_bundle")
    if not isinstance(prompt_bundle, dict):
        violations.append("prompt_bundle must be an object")
    else:
        missing_prompt_bundle = REQUIRED_PROMPT_BUNDLE_KEYS.difference(prompt_bundle.keys())
        if missing_prompt_bundle:
            violations.append(f"missing prompt_bundle keys: {', '.join(sorted(missing_prompt_bundle))}")
        if not _is_nonempty_string(prompt_bundle.get("stage")):
            violations.append("prompt_bundle.stage must be a non-empty string")
        if not _is_nonempty_string(prompt_bundle.get("purpose")):
            violations.append("prompt_bundle.purpose must be a non-empty string")
        if not _is_nonempty_string(prompt_bundle.get("stage_dir")):
            violations.append("prompt_bundle.stage_dir must be a non-empty string")
        if not _is_nonempty_string(prompt_bundle.get("template_name")):
            violations.append("prompt_bundle.template_name must be a non-empty string")
        if not _is_nonempty_string(prompt_bundle.get("system_prompt")):
            violations.append("prompt_bundle.system_prompt must be a non-empty string")
        if not _is_nonempty_string(prompt_bundle.get("user_prompt")):
            violations.append("prompt_bundle.user_prompt must be a non-empty string")
        documents = prompt_bundle.get("documents")
        if not isinstance(documents, list) or not documents:
            violations.append("prompt_bundle.documents must be a non-empty list")
        else:
            for index, document in enumerate(documents):
                if not isinstance(document, dict):
                    violations.append(f"prompt_bundle.documents[{index}] must be an object")
                    continue
                missing_document = REQUIRED_PROMPT_DOCUMENT_KEYS.difference(document.keys())
                if missing_document:
                    violations.append(
                        f"prompt_bundle.documents[{index}] missing keys: {', '.join(sorted(missing_document))}"
                    )
                if not _is_nonempty_string(document.get("name")):
                    violations.append(f"prompt_bundle.documents[{index}].name must be a non-empty string")
                if not _is_nonempty_string(document.get("path")):
                    violations.append(f"prompt_bundle.documents[{index}].path must be a non-empty string")
                if not _is_nonempty_string(document.get("text")):
                    violations.append(f"prompt_bundle.documents[{index}].text must be a non-empty string")
        prompt_sections = prompt_bundle.get("prompt_sections")
        if not isinstance(prompt_sections, dict):
            violations.append("prompt_bundle.prompt_sections must be an object")
        elif not _is_nonempty_string(prompt_sections.get("source")):
            violations.append("prompt_bundle.prompt_sections.source must be a non-empty string")
        if prompt_bundle.get("stage") != packet.get("stage"):
            violations.append("prompt_bundle.stage must match packet stage")

    stage_document_inventory = payload.get("stage_document_inventory")
    stage_document_summary = payload.get("stage_document_summary")
    stage_document_coverage_template = payload.get("stage_document_coverage_template")
    stage_document_missing = STAGE_DOCUMENT_REQUIRED_KEYS.difference(payload.keys())
    if stage_document_missing:
        violations.append(f"missing stage document payload keys: {', '.join(sorted(stage_document_missing))}")
    if not _is_dict_list(stage_document_inventory) or not stage_document_inventory:
        violations.append("stage_document_inventory must be a non-empty list of objects")
    if not isinstance(stage_document_summary, dict):
        violations.append("stage_document_summary must be an object")
    if not _is_dict_list(stage_document_coverage_template) or not stage_document_coverage_template:
        violations.append("stage_document_coverage_template must be a non-empty list of objects")

    if isinstance(stage_document_inventory, list) and isinstance(stage_document_coverage_template, list):
        inventory_paths = []
        coverage_paths = []
        for index, item in enumerate(stage_document_inventory):
            if not isinstance(item, dict):
                continue
            missing_inventory = {"name", "path", "role", "size_bytes"}.difference(item.keys())
            if missing_inventory:
                violations.append(
                    f"stage_document_inventory[{index}] missing keys: {', '.join(sorted(missing_inventory))}"
                )
            if not _is_nonempty_string(item.get("name")):
                violations.append(f"stage_document_inventory[{index}].name must be a non-empty string")
            if not _is_nonempty_string(item.get("path")):
                violations.append(f"stage_document_inventory[{index}].path must be a non-empty string")
            if not _is_nonempty_string(item.get("role")):
                violations.append(f"stage_document_inventory[{index}].role must be a non-empty string")
            inventory_paths.append(str(item.get("path", "")))

        for index, item in enumerate(stage_document_coverage_template):
            if not isinstance(item, dict):
                continue
            missing_coverage = STAGE_DOCUMENT_COVERAGE_ROW_KEYS.difference(item.keys())
            if missing_coverage:
                violations.append(
                    f"stage_document_coverage_template[{index}] missing keys: {', '.join(sorted(missing_coverage))}"
                )
            if not _is_nonempty_string(item.get("name")):
                violations.append(f"stage_document_coverage_template[{index}].name must be a non-empty string")
            if not _is_nonempty_string(item.get("path")):
                violations.append(f"stage_document_coverage_template[{index}].path must be a non-empty string")
            if not _is_nonempty_string(item.get("role")):
                violations.append(f"stage_document_coverage_template[{index}].role must be a non-empty string")
            if item.get("status") != "unmapped":
                violations.append(f"stage_document_coverage_template[{index}].status must start as unmapped")
            if not isinstance(item.get("mapped_to"), list):
                violations.append(f"stage_document_coverage_template[{index}].mapped_to must be a list")
            if not isinstance(item.get("evidence"), list):
                violations.append(f"stage_document_coverage_template[{index}].evidence must be a list")
            coverage_paths.append(str(item.get("path", "")))

        if inventory_paths and coverage_paths and inventory_paths != coverage_paths:
            violations.append("stage_document_coverage_template must mirror stage_document_inventory order and paths")
        if isinstance(stage_document_summary, dict):
            total_documents = stage_document_summary.get("total_documents")
            if total_documents != len(inventory_paths):
                violations.append("stage_document_summary.total_documents must equal stage_document_inventory length")

    upstream_input_inventory = payload.get("upstream_input_inventory")
    upstream_input_summary = payload.get("upstream_input_summary")
    upstream_input_coverage_template = payload.get("upstream_input_coverage_template")
    if packet.get("stage") in {"state", "api", "design", "slice", "gates"}:
        upstream_missing = UPSTREAM_INPUT_REQUIRED_KEYS.difference(payload.keys())
        if upstream_missing:
            violations.append(f"missing upstream input payload keys: {', '.join(sorted(upstream_missing))}")
        if not _is_dict_list(upstream_input_inventory) or not upstream_input_inventory:
            violations.append("upstream_input_inventory must be a non-empty list of objects")
        if not isinstance(upstream_input_summary, dict):
            violations.append("upstream_input_summary must be an object")
        if not _is_dict_list(upstream_input_coverage_template) or not upstream_input_coverage_template:
            violations.append("upstream_input_coverage_template must be a non-empty list of objects")

        if isinstance(upstream_input_inventory, list) and isinstance(upstream_input_coverage_template, list):
            inventory_sources = []
            coverage_sources = []
            primary_count = 0
            for index, item in enumerate(upstream_input_inventory):
                if not isinstance(item, dict):
                    continue
                missing_inventory = {"source_stage", "role", "packet_path", "review_path", "size_bytes"}.difference(item.keys())
                if missing_inventory:
                    violations.append(
                        f"upstream_input_inventory[{index}] missing keys: {', '.join(sorted(missing_inventory))}"
                    )
                if not _is_nonempty_string(item.get("source_stage")):
                    violations.append(f"upstream_input_inventory[{index}].source_stage must be a non-empty string")
                if not _is_nonempty_string(item.get("role")):
                    violations.append(f"upstream_input_inventory[{index}].role must be a non-empty string")
                if not _is_nonempty_string(item.get("packet_path")):
                    violations.append(f"upstream_input_inventory[{index}].packet_path must be a non-empty string")
                if not _is_nonempty_string(item.get("review_path")):
                    violations.append(f"upstream_input_inventory[{index}].review_path must be a non-empty string")
                if item.get("role") == "primary":
                    primary_count += 1
                inventory_sources.append(str(item.get("source_stage", "")))

            for index, item in enumerate(upstream_input_coverage_template):
                if not isinstance(item, dict):
                    continue
                missing_coverage = UPSTREAM_INPUT_COVERAGE_ROW_KEYS.difference(item.keys())
                if missing_coverage:
                    violations.append(
                        f"upstream_input_coverage_template[{index}] missing keys: {', '.join(sorted(missing_coverage))}"
                    )
                if not _is_nonempty_string(item.get("source_stage")):
                    violations.append(f"upstream_input_coverage_template[{index}].source_stage must be a non-empty string")
                if not _is_nonempty_string(item.get("role")):
                    violations.append(f"upstream_input_coverage_template[{index}].role must be a non-empty string")
                if not _is_nonempty_string(item.get("packet_path")):
                    violations.append(f"upstream_input_coverage_template[{index}].packet_path must be a non-empty string")
                if not _is_nonempty_string(item.get("review_path")):
                    violations.append(f"upstream_input_coverage_template[{index}].review_path must be a non-empty string")
                if item.get("status") != "unmapped":
                    violations.append(f"upstream_input_coverage_template[{index}].status must start as unmapped")
                if not isinstance(item.get("mapped_to"), list):
                    violations.append(f"upstream_input_coverage_template[{index}].mapped_to must be a list")
                if not isinstance(item.get("evidence"), list):
                    violations.append(f"upstream_input_coverage_template[{index}].evidence must be a list")
                coverage_sources.append(str(item.get("source_stage", "")))

            if inventory_sources and coverage_sources and inventory_sources != coverage_sources:
                violations.append("upstream_input_coverage_template must mirror upstream_input_inventory order and source stages")
            if isinstance(upstream_input_summary, dict):
                total_inputs = upstream_input_summary.get("total_inputs")
                if total_inputs != len(inventory_sources):
                    violations.append("upstream_input_summary.total_inputs must equal upstream_input_inventory length")
            if primary_count == 0:
                violations.append("upstream_input_inventory must include at least one primary upstream input")

    if packet.get("stage") == "discovery":
        discovery_missing = DISCOVERY_REQUIRED_PAYLOAD_KEYS.difference(payload.keys())
        if discovery_missing:
            violations.append(f"missing discovery payload keys: {', '.join(sorted(discovery_missing))}")

        analysis_inventory = payload.get("analysis_inventory")
        analysis_coverage_template = payload.get("analysis_coverage_template")
        analysis_scope_summary = payload.get("analysis_scope_summary")

        if not _is_dict_list(analysis_inventory) or not analysis_inventory:
            violations.append("analysis_inventory must be a non-empty list of objects")
        if not _is_dict_list(analysis_coverage_template) or not analysis_coverage_template:
            violations.append("analysis_coverage_template must be a non-empty list of objects")
        if not isinstance(analysis_scope_summary, dict):
            violations.append("analysis_scope_summary must be an object")

        if isinstance(analysis_inventory, list) and isinstance(analysis_coverage_template, list):
            inventory_paths = []
            coverage_paths = []
            for index, item in enumerate(analysis_inventory):
                if not isinstance(item, dict):
                    continue
                missing_inventory = {"path", "analysis_path", "top_level", "suffix", "size_bytes"}.difference(item.keys())
                if missing_inventory:
                    violations.append(
                        f"analysis_inventory[{index}] missing keys: {', '.join(sorted(missing_inventory))}"
                    )
                if not _is_nonempty_string(item.get("path")):
                    violations.append(f"analysis_inventory[{index}].path must be a non-empty string")
                if not _is_nonempty_string(item.get("analysis_path")):
                    violations.append(f"analysis_inventory[{index}].analysis_path must be a non-empty string")
                inventory_paths.append(str(item.get("path", "")))

            for index, item in enumerate(analysis_coverage_template):
                if not isinstance(item, dict):
                    continue
                missing_coverage = DISCOVERY_COVERAGE_ROW_KEYS.difference(item.keys())
                if missing_coverage:
                    violations.append(
                        f"analysis_coverage_template[{index}] missing keys: {', '.join(sorted(missing_coverage))}"
                    )
                if not _is_nonempty_string(item.get("path")):
                    violations.append(f"analysis_coverage_template[{index}].path must be a non-empty string")
                if not _is_nonempty_string(item.get("analysis_path")):
                    violations.append(
                        f"analysis_coverage_template[{index}].analysis_path must be a non-empty string"
                    )
                if item.get("status") != "unmapped":
                    violations.append(f"analysis_coverage_template[{index}].status must start as unmapped")
                if not isinstance(item.get("covered_by"), list):
                    violations.append(f"analysis_coverage_template[{index}].covered_by must be a list")
                if not isinstance(item.get("evidence"), list):
                    violations.append(f"analysis_coverage_template[{index}].evidence must be a list")
                coverage_paths.append(str(item.get("path", "")))

            if inventory_paths and coverage_paths and inventory_paths != coverage_paths:
                violations.append("analysis_coverage_template must mirror analysis_inventory order and paths")
            if isinstance(analysis_scope_summary, dict):
                total_files = analysis_scope_summary.get("total_files")
                if total_files != len(inventory_paths):
                    violations.append("analysis_scope_summary.total_files must equal analysis_inventory length")

    if packet.get("stage") == "domain":
        domain_missing = DOMAIN_REQUIRED_PAYLOAD_KEYS.difference(payload.keys())
        if domain_missing:
            violations.append(f"missing domain payload keys: {', '.join(sorted(domain_missing))}")

        domain_input_inventory = payload.get("domain_input_inventory")
        domain_coverage_template = payload.get("domain_coverage_template")
        domain_input_summary = payload.get("domain_input_summary")

        if not _is_dict_list(domain_input_inventory) or not domain_input_inventory:
            violations.append("domain_input_inventory must be a non-empty list of objects")
        if not _is_dict_list(domain_coverage_template) or not domain_coverage_template:
            violations.append("domain_coverage_template must be a non-empty list of objects")
        if not isinstance(domain_input_summary, dict):
            violations.append("domain_input_summary must be an object")

        if isinstance(domain_input_inventory, list) and isinstance(domain_coverage_template, list):
            inventory_paths = []
            coverage_paths = []
            primary_count = 0
            for index, item in enumerate(domain_input_inventory):
                if not isinstance(item, dict):
                    continue
                missing_inventory = {"path", "input_type", "role", "size_bytes"}.difference(item.keys())
                if missing_inventory:
                    violations.append(
                        f"domain_input_inventory[{index}] missing keys: {', '.join(sorted(missing_inventory))}"
                    )
                if not _is_nonempty_string(item.get("path")):
                    violations.append(f"domain_input_inventory[{index}].path must be a non-empty string")
                if not _is_nonempty_string(item.get("input_type")):
                    violations.append(f"domain_input_inventory[{index}].input_type must be a non-empty string")
                if not _is_nonempty_string(item.get("role")):
                    violations.append(f"domain_input_inventory[{index}].role must be a non-empty string")
                if item.get("role") == "primary":
                    primary_count += 1
                inventory_paths.append(str(item.get("path", "")))

            for index, item in enumerate(domain_coverage_template):
                if not isinstance(item, dict):
                    continue
                missing_coverage = DOMAIN_COVERAGE_ROW_KEYS.difference(item.keys())
                if missing_coverage:
                    violations.append(
                        f"domain_coverage_template[{index}] missing keys: {', '.join(sorted(missing_coverage))}"
                    )
                if not _is_nonempty_string(item.get("path")):
                    violations.append(f"domain_coverage_template[{index}].path must be a non-empty string")
                if not _is_nonempty_string(item.get("input_type")):
                    violations.append(f"domain_coverage_template[{index}].input_type must be a non-empty string")
                if not _is_nonempty_string(item.get("role")):
                    violations.append(f"domain_coverage_template[{index}].role must be a non-empty string")
                if item.get("status") != "unmapped":
                    violations.append(f"domain_coverage_template[{index}].status must start as unmapped")
                if not isinstance(item.get("mapped_to"), list):
                    violations.append(f"domain_coverage_template[{index}].mapped_to must be a list")
                if not isinstance(item.get("evidence"), list):
                    violations.append(f"domain_coverage_template[{index}].evidence must be a list")
                coverage_paths.append(str(item.get("path", "")))

            if inventory_paths and coverage_paths and inventory_paths != coverage_paths:
                violations.append("domain_coverage_template must mirror domain_input_inventory order and paths")
            if isinstance(domain_input_summary, dict):
                total_inputs = domain_input_summary.get("total_inputs")
                if total_inputs != len(inventory_paths):
                    violations.append("domain_input_summary.total_inputs must equal domain_input_inventory length")
            if primary_count == 0:
                violations.append("domain_input_inventory must include at least one primary approved discovery input")

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
