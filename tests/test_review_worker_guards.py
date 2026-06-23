from __future__ import annotations

import json
import runpy
import sys

import pytest

from plb.core.models import ReviewState, WorkflowStage
from plb.review.worker import _check_packet_shape, _check_payload_rules, _evaluate_packet, main as review_worker_main


def _base_payload(stage: WorkflowStage) -> dict[str, object]:
    return {
        "project_state": "initialized",
        "stage_status": "active",
        "rollback_point": "analysis",
        "counterexample_prompts": ["what could fail?"],
        "approved_inputs": ["analysis"],
        "prompt_bundle": {
            "stage": stage.value,
            "purpose": "review",
            "stage_dir": "records/project-launch-blueprint/" + stage.value,
            "template_name": "Review",
            "system_prompt": "system",
            "user_prompt": "user",
            "documents": [{"name": "method.md", "path": "stage/method.md", "text": "method"}],
            "prompt_sections": {"source": "source", "selected": "selected"},
        },
        "stage_document_inventory": [
            {"name": "method.md", "path": "stage/method.md", "role": "stage_document", "size_bytes": 1}
        ],
        "stage_document_summary": {"total_documents": 1, "document_names": ["method.md"]},
        "stage_document_coverage_template": [
            {
                "name": "method.md",
                "path": "stage/method.md",
                "role": "stage_document",
                "status": "unmapped",
                "mapped_to": [],
                "reason": "",
                "evidence": [],
            }
        ],
    }


def test_worker_rejects_malformed_packet_shape_and_prompt_bundle_fields():
    packet = {
        "stage": "bogus",
        "target": "domain",
        "review_state": ReviewState.REVIEW_RUNNING.value,
        "payload": "not-a-payload",
        "unexpected": True,
    }

    result = _evaluate_packet(packet)

    assert result["review_state"] == ReviewState.FAILED.value
    assert result["summary"] == "packet malformed for bogus"
    assert result["checks"]["packet_shape"] is False
    assert "unexpected packet keys: unexpected" in result["violations"]
    assert "unknown stage: bogus" in result["violations"]
    assert "target must match stage" in result["violations"]
    assert "packet review_state must be packet_created" in result["violations"]
    assert "payload must be an object" in result["violations"]


def test_worker_rejects_prompt_bundle_and_stage_document_structure_errors():
    payload = _base_payload(WorkflowStage.API)
    payload["prompt_bundle"]["documents"] = [{"name": "method.md", "path": "stage/method.md"}]
    payload["prompt_bundle"]["prompt_sections"] = "broken"
    payload["prompt_bundle"]["stage"] = WorkflowStage.DISCOVERY.value
    payload["stage_document_inventory"] = [{"name": "method.md"}]
    payload["stage_document_summary"] = {"total_documents": 2}
    payload["stage_document_coverage_template"] = [
        {
            "name": "method.md",
            "path": "stage/method.md",
            "role": "stage_document",
            "status": "mapped",
            "mapped_to": [],
            "reason": "",
            "evidence": "bad",
        }
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "forbidden context key present: draft_prompt" not in result["violations"]
    assert "prompt_bundle.stage must match packet stage" in result["violations"]
    assert "prompt_bundle.documents[0] missing keys: text" in result["violations"]
    assert "prompt_bundle.prompt_sections must be an object" in result["violations"]
    assert "stage_document_inventory[0] missing keys: path, role, size_bytes" in result["violations"]
    assert "stage_document_summary.total_documents must equal stage_document_inventory length" in result["violations"]
    assert "stage_document_coverage_template[0].status must start as unmapped" in result["violations"]
    assert "stage_document_coverage_template[0].evidence must be a list" in result["violations"]


def test_worker_rejects_prompt_bundle_stage_and_missing_upstream_payload_keys():
    payload = {
        "project_state": "initialized",
        "stage_status": "active",
        "rollback_point": "analysis",
        "counterexample_prompts": ["what could fail?"],
        "approved_inputs": ["analysis"],
        "prompt_bundle": {
            "stage": "",
            "purpose": "review",
            "stage_dir": "records/project-launch-blueprint/api",
            "template_name": "Review",
            "system_prompt": "system",
            "user_prompt": "user",
            "documents": [{"name": "method.md", "path": "stage/method.md", "text": "method"}],
            "prompt_sections": {"source": "source"},
        },
        "stage_document_inventory": [{"name": "method.md", "path": "stage/method.md", "role": "stage_document", "size_bytes": 1}],
        "stage_document_summary": {"total_documents": 1},
        "stage_document_coverage_template": [{"name": "method.md", "path": "stage/method.md", "role": "stage_document", "status": "unmapped", "mapped_to": [], "reason": "", "evidence": []}],
    }

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "prompt_bundle.stage must be a non-empty string" in result["violations"]
    assert "missing upstream input payload keys: upstream_input_coverage_template, upstream_input_inventory, upstream_input_summary" in result["violations"]


def test_worker_rejects_prompt_bundle_missing_keys_and_empty_documents():
    payload = {
        "project_state": "initialized",
        "stage_status": "active",
        "rollback_point": "analysis",
        "counterexample_prompts": ["what could fail?"],
        "approved_inputs": ["analysis"],
        "prompt_bundle": {
            "stage": WorkflowStage.API.value,
            "purpose": "review",
            "stage_dir": "records/project-launch-blueprint/api",
            "system_prompt": "system",
            "user_prompt": "user",
            "documents": [],
            "prompt_sections": {"source": "source"},
        },
        "stage_document_inventory": [{"name": "method.md", "path": "stage/method.md", "role": "stage_document", "size_bytes": 1}],
        "stage_document_summary": [],
        "stage_document_coverage_template": [{"name": "method.md", "path": "stage/method.md", "role": "stage_document", "status": "unmapped", "mapped_to": [], "reason": "", "evidence": []}],
        "upstream_input_inventory": [
            {
                "source_stage": "design",
                "role": "primary",
                "packet_path": "design-packet.json",
                "review_path": "design-review.json",
                "size_bytes": 1,
            }
        ],
        "upstream_input_summary": {"total_inputs": 1},
        "upstream_input_coverage_template": [
            {
                "source_stage": "design",
                "role": "primary",
                "packet_path": "design-packet.json",
                "review_path": "design-review.json",
                "status": "unmapped",
                "mapped_to": [],
                "reason": "",
                "evidence": [],
            }
        ],
    }

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "missing prompt_bundle keys: template_name" in result["violations"]
    assert "prompt_bundle.documents must be a non-empty list" in result["violations"]
    assert "stage_document_summary must be an object" in result["violations"]


def test_worker_rejects_stage_document_coverage_missing_keys():
    payload = _base_payload(WorkflowStage.API)
    payload["stage_document_inventory"] = [{"name": "method.md", "path": "stage/method.md", "role": "stage_document", "size_bytes": 1}]
    payload["stage_document_summary"] = {"total_documents": 1}
    payload["stage_document_coverage_template"] = [{"status": "unmapped", "mapped_to": [], "reason": "", "evidence": []}]
    payload["upstream_input_inventory"] = [
        {
            "source_stage": "design",
            "role": "primary",
            "packet_path": "design-packet.json",
            "review_path": "design-review.json",
            "size_bytes": 1,
        }
    ]
    payload["upstream_input_summary"] = {"total_inputs": 1}
    payload["upstream_input_coverage_template"] = [
        {
            "source_stage": "design",
            "role": "primary",
            "packet_path": "design-packet.json",
            "review_path": "design-review.json",
            "status": "unmapped",
            "mapped_to": [],
            "reason": "",
            "evidence": [],
        }
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "stage_document_coverage_template[0] missing keys: name, path, role" in result["violations"]


def test_worker_rejects_missing_packet_and_payload_keys():
    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": "",
            "payload": {},
            "unexpected": True,
        }
    )

    assert result["review_state"] == ReviewState.FAILED.value
    assert any(entry.startswith("missing packet keys: ") for entry in result["violations"])
    assert "unexpected packet keys: unexpected" in result["violations"]
    assert "target must be a non-empty string" in result["violations"]
    assert "packet review_state must be packet_created" in result["violations"]
    assert any(entry.startswith("missing payload keys:") for entry in result["violations"])


def test_worker_rejects_discovery_inventory_and_summary_errors():
    payload = _base_payload(WorkflowStage.DISCOVERY)
    payload["analysis_inventory"] = [
        {
            "path": "analysis/brief.md",
            "analysis_path": "analysis/brief.md",
            "top_level": "analysis",
            "suffix": ".md",
            "size_bytes": 8,
        },
        {
            "path": "",
            "analysis_path": "",
            "top_level": "analysis",
            "suffix": ".md",
            "size_bytes": 8,
        },
    ]
    payload["analysis_scope_summary"] = {"total_files": 3}
    payload["analysis_coverage_template"] = [
        {
            "path": "analysis/brief.md",
            "analysis_path": "analysis/brief.md",
            "status": "mapped",
            "covered_by": "bad",
            "reason": "",
            "evidence": [],
        },
        {
            "path": "analysis/extra.md",
            "analysis_path": "analysis/extra.md",
            "status": "unmapped",
            "covered_by": [],
            "reason": "",
            "evidence": [],
        },
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "analysis_inventory[1].path must be a non-empty string" in result["violations"]
    assert "analysis_inventory[1].analysis_path must be a non-empty string" in result["violations"]
    assert "analysis_coverage_template[0].status must start as unmapped" in result["violations"]
    assert "analysis_coverage_template[0].covered_by must be a list" in result["violations"]
    assert "analysis_coverage_template must mirror analysis_inventory order and paths" in result["violations"]
    assert "analysis_scope_summary.total_files must equal analysis_inventory length" in result["violations"]


def test_worker_rejects_missing_discovery_payload_keys():
    payload = _base_payload(WorkflowStage.DISCOVERY)
    payload["analysis_inventory"] = [
        {
            "path": "analysis/brief.md",
            "analysis_path": "analysis/brief.md",
            "top_level": "analysis",
            "suffix": ".md",
            "size_bytes": 8,
        }
    ]
    payload["analysis_scope_summary"] = {"total_files": 1}
    payload.pop("analysis_coverage_template", None)

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "missing discovery payload keys: analysis_coverage_template" in result["violations"]
    assert "analysis_inventory must be a non-empty list of objects" not in result["violations"]


def test_worker_rejects_discovery_summary_non_object():
    payload = _base_payload(WorkflowStage.DISCOVERY)
    payload["analysis_inventory"] = [
        {
            "path": "analysis/brief.md",
            "analysis_path": "analysis/brief.md",
            "top_level": "analysis",
            "suffix": ".md",
            "size_bytes": 8,
        }
    ]
    payload["analysis_scope_summary"] = []
    payload["analysis_coverage_template"] = [
        {
            "path": "analysis/brief.md",
            "analysis_path": "analysis/brief.md",
            "status": "unmapped",
            "covered_by": [],
            "reason": "",
            "evidence": [],
        }
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "analysis_scope_summary must be an object" in result["violations"]


def test_worker_accepts_discovery_summary_when_counts_match():
    payload = _base_payload(WorkflowStage.DISCOVERY)
    payload["analysis_inventory"] = [
        {
            "path": "analysis/brief.md",
            "analysis_path": "analysis/brief.md",
            "top_level": "analysis",
            "suffix": ".md",
            "size_bytes": 8,
        }
    ]
    payload["analysis_scope_summary"] = {"total_files": 1}
    payload["analysis_coverage_template"] = [
        {
            "path": "analysis/brief.md",
            "analysis_path": "analysis/brief.md",
            "status": "unmapped",
            "covered_by": [],
            "reason": "",
            "evidence": [],
        }
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.PASSED.value
    assert result["summary"] == "isolated review passed for discovery"


def test_worker_rejects_discovery_missing_keys_and_row_shapes():
    payload = {
        "project_state": "initialized",
        "stage_status": "active",
        "rollback_point": "analysis",
        "counterexample_prompts": ["what could fail?"],
        "approved_inputs": ["analysis"],
        "prompt_bundle": {
            "stage": WorkflowStage.DISCOVERY.value,
            "purpose": "review",
            "stage_dir": "records/project-launch-blueprint/discovery",
            "template_name": "Review",
            "system_prompt": "system",
            "user_prompt": "user",
            "documents": [{"name": "method.md", "path": "stage/method.md", "text": "method"}],
            "prompt_sections": {"source": "source"},
        },
        "stage_document_inventory": [
            {"name": "method.md", "path": "stage/method.md", "role": "stage_document", "size_bytes": 1}
        ],
        "stage_document_summary": {"total_documents": 1},
        "stage_document_coverage_template": [
            {"name": "method.md", "path": "stage/method.md", "role": "stage_document", "status": "unmapped", "mapped_to": [], "reason": "", "evidence": []}
        ],
        "analysis_inventory": [
            {"analysis_path": "analysis/brief.md", "top_level": "analysis", "suffix": ".md", "size_bytes": 8},
            {"path": "", "analysis_path": "", "top_level": "analysis", "suffix": ".md", "size_bytes": 8},
        ],
        "analysis_scope_summary": {"total_files": 1},
        "analysis_coverage_template": [
            {"path": "analysis/brief.md", "analysis_path": "analysis/brief.md", "status": "unmapped", "covered_by": [], "reason": "", "evidence": []},
            {"status": "mapped", "covered_by": "bad", "reason": "", "evidence": "bad"},
        ],
    }

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "analysis_inventory[0] missing keys: path" in result["violations"]
    assert "analysis_inventory[0].path must be a non-empty string" in result["violations"]
    assert "analysis_inventory[1].path must be a non-empty string" in result["violations"]
    assert "analysis_inventory[1].analysis_path must be a non-empty string" in result["violations"]
    assert any(
        entry.startswith("analysis_coverage_template[1] missing keys:")
        for entry in result["violations"]
    )
    assert "analysis_coverage_template[1].covered_by must be a list" in result["violations"]
    assert "analysis_coverage_template[1].status must start as unmapped" in result["violations"]


def test_worker_rejects_domain_and_upstream_inventory_errors():
    payload = _base_payload(WorkflowStage.DOMAIN)
    payload["domain_input_inventory"] = [
        {
            "path": "analysis/discovery-review.json",
            "input_type": "approved discovery output",
            "role": "primary",
            "size_bytes": 1,
        },
        {
            "path": "analysis/notes.txt",
            "input_type": "auxiliary evidence",
            "role": "secondary",
            "size_bytes": 1,
        },
    ]
    payload["domain_input_summary"] = {"total_inputs": 3}
    payload["domain_coverage_template"] = [
        {
            "path": "analysis/discovery-review.json",
            "input_type": "approved discovery output",
            "role": "primary",
            "status": "mapped",
            "mapped_to": [],
            "reason": "",
            "evidence": [],
        }
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DOMAIN.value,
            "target": WorkflowStage.DOMAIN.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "domain_input_summary.total_inputs must equal domain_input_inventory length" in result["violations"]
    assert "domain_coverage_template must mirror domain_input_inventory order and paths" in result["violations"]


def test_worker_rejects_domain_missing_keys_and_row_shapes():
    payload = _base_payload(WorkflowStage.DOMAIN)
    payload["domain_input_inventory"] = [
        {"role": "primary", "size_bytes": 1},
        {"path": "", "input_type": "", "role": "", "size_bytes": 1},
    ]
    payload["domain_input_summary"] = {"total_inputs": 1}
    payload["domain_coverage_template"] = [
        {"path": "analysis/discovery-review.json", "input_type": "approved discovery output", "role": "primary", "status": "unmapped", "mapped_to": [], "reason": "", "evidence": []},
        {"status": "mapped", "mapped_to": "bad", "reason": "", "evidence": "bad"},
    ]
    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DOMAIN.value,
            "target": WorkflowStage.DOMAIN.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "domain_input_inventory[0] missing keys: input_type, path" in result["violations"]
    assert "domain_input_inventory[1].path must be a non-empty string" in result["violations"]
    assert "domain_input_inventory[1].input_type must be a non-empty string" in result["violations"]
    assert "domain_input_inventory[1].role must be a non-empty string" in result["violations"]
    assert "domain_coverage_template[1] missing keys: input_type, path, role" in result["violations"]
    assert "domain_input_summary.total_inputs must equal domain_input_inventory length" in result["violations"]
    assert "domain_coverage_template[1].status must start as unmapped" in result["violations"]


def test_worker_rejects_domain_summary_non_object():
    payload = _base_payload(WorkflowStage.DOMAIN)
    payload["domain_input_inventory"] = [
        {
            "path": "analysis/discovery-review.json",
            "input_type": "approved discovery output",
            "role": "primary",
            "size_bytes": 1,
        }
    ]
    payload["domain_input_summary"] = []
    payload["domain_coverage_template"] = [
        {
            "path": "analysis/discovery-review.json",
            "input_type": "approved discovery output",
            "role": "primary",
            "status": "unmapped",
            "mapped_to": [],
            "reason": "",
            "evidence": [],
        }
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DOMAIN.value,
            "target": WorkflowStage.DOMAIN.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "domain_input_summary must be an object" in result["violations"]


def test_worker_accepts_domain_summary_when_counts_match():
    payload = _base_payload(WorkflowStage.DOMAIN)
    payload["domain_input_inventory"] = [
        {
            "path": "analysis/discovery-review.json",
            "input_type": "approved discovery output",
            "role": "primary",
            "size_bytes": 1,
        }
    ]
    payload["domain_input_summary"] = {"total_inputs": 1}
    payload["domain_coverage_template"] = [
        {
            "path": "analysis/discovery-review.json",
            "input_type": "approved discovery output",
            "role": "primary",
            "status": "unmapped",
            "mapped_to": [],
            "reason": "",
            "evidence": [],
        }
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DOMAIN.value,
            "target": WorkflowStage.DOMAIN.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.PASSED.value
    assert result["summary"] == "isolated review passed for domain"


def test_worker_rejects_upstream_inventory_errors():
    payload = _base_payload(WorkflowStage.API)
    payload["upstream_input_inventory"] = [
        {
            "input_key": "api_contract_map",
            "input_type": "api contract map",
            "role": "secondary",
            "path": "api-contract/index.md",
            "size_bytes": 1,
        },
        {
            "input_key": "design_system_map",
            "input_type": "design system map",
            "role": "secondary",
            "path": "design-system/index.md",
            "size_bytes": 1,
        },
    ]
    payload["upstream_input_summary"] = {"total_inputs": 3}
    payload["upstream_input_coverage_template"] = [
        {
            "source_stage": "design",
            "role": "secondary",
            "packet_path": "design-packet.json",
            "review_path": "design-review.json",
            "status": "mapped",
            "mapped_to": [],
            "reason": "",
            "evidence": [],
        },
        {"role": "secondary", "status": "unmapped", "mapped_to": [], "reason": "", "evidence": []},
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "upstream_input_coverage_template[0].status must start as unmapped" in result["violations"]
    assert "upstream_input_coverage_template must mirror upstream_input_inventory order and source stages" in result["violations"]
    assert "upstream_input_summary.total_inputs must equal upstream_input_inventory length" in result["violations"]
    assert "upstream_input_inventory must include at least one primary upstream input" in result["violations"]


def test_worker_rejects_upstream_missing_keys_and_row_shapes():
    payload = _base_payload(WorkflowStage.API)
    payload["upstream_input_inventory"] = [
        {"role": "primary", "packet_path": "design-packet.json", "review_path": "design-review.json", "size_bytes": 1},
        {"source_stage": "", "role": "", "packet_path": "", "review_path": "", "size_bytes": 1},
    ]
    payload["upstream_input_summary"] = {"total_inputs": 1}
    payload["upstream_input_coverage_template"] = [
        {"source_stage": "design", "role": "primary", "packet_path": "design-packet.json", "review_path": "design-review.json", "status": "unmapped", "mapped_to": [], "reason": "", "evidence": []},
        {"status": "mapped", "mapped_to": "bad", "reason": "", "evidence": "bad"},
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "upstream_input_inventory[0] missing keys: source_stage" in result["violations"]
    assert "upstream_input_inventory[1].source_stage must be a non-empty string" in result["violations"]
    assert "upstream_input_inventory[1].packet_path must be a non-empty string" in result["violations"]
    assert "upstream_input_inventory[1].review_path must be a non-empty string" in result["violations"]
    assert any(
        entry.startswith("upstream_input_coverage_template[1] missing keys:")
        for entry in result["violations"]
    )
    assert "upstream_input_summary.total_inputs must equal upstream_input_inventory length" in result["violations"]
    assert "upstream_input_coverage_template[1].status must start as unmapped" in result["violations"]


def test_worker_rejects_reviewable_state_and_forbidden_context_keys():
    payload = _base_payload(WorkflowStage.STATE)
    payload["stage_status"] = "draft"
    payload["generation_context"] = {"foo": "bar"}
    payload["private_context"] = {"secret": True}
    payload["draft_prompt"] = "hidden"

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.STATE.value,
            "target": WorkflowStage.STATE.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "forbidden context key present: draft_prompt" in result["violations"]
    assert "forbidden context key present: generation_context" in result["violations"]
    assert "forbidden context key present: private_context" in result["violations"]
    assert "stage_status is not yet reviewable" in result["violations"]


def test_worker_rejects_packet_shape_and_payload_non_object_branches():
    packet = {
        "stage": "",
        "target": "api",
        "review_state": ReviewState.REVIEW_RUNNING.value,
        "payload": [],
        "unexpected": True,
    }

    shape_violations = _check_packet_shape(packet)
    payload_violations, evidence, counterexamples = _check_payload_rules({"payload": []})

    assert "stage must be a non-empty string" in shape_violations
    assert "target must match stage" in shape_violations
    assert "packet review_state must be packet_created" in shape_violations
    assert "payload must be an object" in shape_violations
    assert payload_violations == ["payload is not an object"]
    assert evidence == []
    assert counterexamples == []


def test_worker_rejects_prompt_bundle_document_and_stage_document_shape_edges():
    payload = _base_payload(WorkflowStage.API)
    payload["project_state"] = ""
    payload["stage_status"] = ""
    payload["rollback_point"] = ""
    payload["counterexample_prompts"] = []
    payload["approved_inputs"] = []
    payload["prompt_bundle"] = {
        "stage": WorkflowStage.DISCOVERY.value,
        "purpose": "",
        "stage_dir": "",
        "template_name": "",
        "system_prompt": "",
        "user_prompt": "",
        "documents": [
            None,
            {"name": "", "path": "", "text": ""},
        ],
        "prompt_sections": {"source": ""},
    }
    payload["stage_document_inventory"] = [
        None,
        {"name": "", "path": "", "role": "", "size_bytes": 1},
    ]
    payload["stage_document_summary"] = {"total_documents": 0}
    payload["stage_document_coverage_template"] = [
        None,
        {"name": "", "path": "", "role": "", "status": "mapped", "mapped_to": "bad", "reason": "", "evidence": "bad"},
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "project_state must be a non-empty string" in result["violations"]
    assert "stage_status must be a non-empty string" in result["violations"]
    assert "rollback_point must be a non-empty string" in result["violations"]
    assert "counterexample_prompts must be a non-empty list of strings" in result["violations"]
    assert "approved_inputs must be a non-empty list of strings" in result["violations"]
    assert "prompt_bundle.stage must match packet stage" in result["violations"]
    assert "prompt_bundle.purpose must be a non-empty string" in result["violations"]
    assert "prompt_bundle.documents[0] must be an object" in result["violations"]
    assert "prompt_bundle.documents[1].name must be a non-empty string" in result["violations"]
    assert "prompt_bundle.prompt_sections.source must be a non-empty string" in result["violations"]
    assert "stage_document_inventory[1].name must be a non-empty string" in result["violations"]
    assert "stage_document_coverage_template[1].name must be a non-empty string" in result["violations"]
    assert "stage_document_coverage_template[1].status must start as unmapped" in result["violations"]
    assert "stage_document_coverage_template[1].mapped_to must be a list" in result["violations"]
    assert "stage_document_coverage_template[1].evidence must be a list" in result["violations"]


def test_worker_rejects_discovery_domain_and_upstream_shape_edges():
    payload = _base_payload(WorkflowStage.DISCOVERY)
    payload["analysis_inventory"] = [
        None,
        {"path": "", "analysis_path": "", "top_level": "analysis", "suffix": ".md", "size_bytes": 8},
    ]
    payload["analysis_scope_summary"] = "broken"
    payload["analysis_coverage_template"] = [
        None,
        {"path": "", "analysis_path": "", "status": "mapped", "covered_by": "bad", "reason": "", "evidence": "bad"},
    ]
    payload["domain_input_inventory"] = [
        None,
        {"path": "", "input_type": "", "role": "", "size_bytes": 1},
    ]
    payload["domain_input_summary"] = "broken"
    payload["domain_coverage_template"] = [
        None,
        {"path": "", "input_type": "", "role": "", "status": "mapped", "mapped_to": "bad", "reason": "", "evidence": "bad"},
    ]
    payload["upstream_input_inventory"] = [
        None,
        {"source_stage": "", "role": "", "packet_path": "", "review_path": "", "size_bytes": 1},
    ]
    payload["upstream_input_summary"] = "broken"
    payload["upstream_input_coverage_template"] = [
        None,
        {"source_stage": "", "role": "", "packet_path": "", "review_path": "", "status": "mapped", "mapped_to": "bad", "reason": "", "evidence": "bad"},
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "analysis_inventory[1].path must be a non-empty string" in result["violations"]
    assert "analysis_inventory[1].analysis_path must be a non-empty string" in result["violations"]
    assert "analysis_scope_summary must be an object" in result["violations"]
    assert "analysis_coverage_template[1].path must be a non-empty string" in result["violations"]
    assert "analysis_coverage_template[1].analysis_path must be a non-empty string" in result["violations"]
    assert "analysis_coverage_template[1].covered_by must be a list" in result["violations"]
    assert "analysis_coverage_template[1].evidence must be a list" in result["violations"]


def test_worker_rejects_discovery_summary_total_mismatch():
    payload = _base_payload(WorkflowStage.DISCOVERY)
    payload["analysis_inventory"] = [
        {
            "path": "analysis/brief.md",
            "analysis_path": "analysis/brief.md",
            "top_level": "analysis",
            "suffix": ".md",
            "size_bytes": 8,
        }
    ]
    payload["analysis_scope_summary"] = {"total_files": 2}
    payload["analysis_coverage_template"] = [
        {
            "path": "analysis/brief.md",
            "analysis_path": "analysis/brief.md",
            "status": "unmapped",
            "covered_by": [],
            "reason": "",
            "evidence": [],
        }
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "analysis_scope_summary.total_files must equal analysis_inventory length" in result["violations"]


def test_worker_rejects_domain_shape_edges():
    payload = _base_payload(WorkflowStage.DOMAIN)
    payload["domain_input_inventory"] = [
        None,
        {"path": "", "input_type": "", "role": "", "size_bytes": 1},
    ]
    payload["domain_input_summary"] = "broken"
    payload["domain_coverage_template"] = [
        None,
        {"path": "", "input_type": "", "role": "", "status": "mapped", "mapped_to": "bad", "reason": "", "evidence": "bad"},
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DOMAIN.value,
            "target": WorkflowStage.DOMAIN.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "domain_input_inventory[1].path must be a non-empty string" in result["violations"]
    assert "domain_input_inventory[1].input_type must be a non-empty string" in result["violations"]
    assert "domain_input_inventory[1].role must be a non-empty string" in result["violations"]
    assert "domain_input_summary must be an object" in result["violations"]
    assert "domain_coverage_template[1].path must be a non-empty string" in result["violations"]
    assert "domain_coverage_template[1].status must start as unmapped" in result["violations"]
    assert "domain_coverage_template[1].mapped_to must be a list" in result["violations"]
    assert "domain_coverage_template[1].evidence must be a list" in result["violations"]


def test_worker_rejects_upstream_shape_edges():
    payload = _base_payload(WorkflowStage.API)
    payload["upstream_input_inventory"] = [
        None,
        {"source_stage": "", "role": "", "packet_path": "", "review_path": "", "size_bytes": 1},
    ]
    payload["upstream_input_summary"] = "broken"
    payload["upstream_input_coverage_template"] = [
        None,
        {"source_stage": "", "role": "", "packet_path": "", "review_path": "", "status": "mapped", "mapped_to": "bad", "reason": "", "evidence": "bad"},
    ]

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "upstream_input_inventory[1].source_stage must be a non-empty string" in result["violations"]
    assert "upstream_input_inventory[1].role must be a non-empty string" in result["violations"]
    assert "upstream_input_inventory[1].packet_path must be a non-empty string" in result["violations"]
    assert "upstream_input_inventory[1].review_path must be a non-empty string" in result["violations"]
    assert "upstream_input_summary must be an object" in result["violations"]
    assert "upstream_input_coverage_template[1].source_stage must be a non-empty string" in result["violations"]
    assert "upstream_input_coverage_template[1].status must start as unmapped" in result["violations"]
    assert "upstream_input_coverage_template[1].mapped_to must be a list" in result["violations"]
    assert "upstream_input_coverage_template[1].evidence must be a list" in result["violations"]


def test_worker_rejects_prompt_bundle_non_object_and_stage_container_shapes():
    payload = _base_payload(WorkflowStage.DOMAIN)
    payload["prompt_bundle"] = []
    payload["stage_document_inventory"] = "broken"
    payload["stage_document_summary"] = []
    payload["stage_document_coverage_template"] = []

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DOMAIN.value,
            "target": WorkflowStage.DOMAIN.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "prompt_bundle must be an object" in result["violations"]
    assert "stage_document_inventory must be a non-empty list of objects" in result["violations"]
    assert "stage_document_summary must be an object" in result["violations"]
    assert "stage_document_coverage_template must be a non-empty list of objects" in result["violations"]
    assert "missing domain payload keys: domain_coverage_template, domain_input_inventory, domain_input_summary" in result["violations"]
    assert "domain_input_inventory must be a non-empty list of objects" in result["violations"]
    assert "domain_input_summary must be an object" in result["violations"]
    assert "domain_coverage_template must be a non-empty list of objects" in result["violations"]


def test_worker_rejects_discovery_container_shapes_and_missing_payload_keys():
    payload = _base_payload(WorkflowStage.DISCOVERY)
    payload["analysis_inventory"] = "broken"
    payload["analysis_scope_summary"] = []
    payload["analysis_coverage_template"] = []

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.DISCOVERY.value,
            "target": WorkflowStage.DISCOVERY.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "analysis_inventory must be a non-empty list of objects" in result["violations"]
    assert "analysis_coverage_template must be a non-empty list of objects" in result["violations"]
    assert "analysis_scope_summary must be an object" in result["violations"]


def test_worker_rejects_upstream_container_shapes_and_missing_payload_keys():
    payload = _base_payload(WorkflowStage.API)
    payload["upstream_input_inventory"] = []
    payload["upstream_input_summary"] = []
    payload["upstream_input_coverage_template"] = []

    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.NEEDS_REVISION.value
    assert "upstream_input_inventory must be a non-empty list of objects" in result["violations"]
    assert "upstream_input_summary must be an object" in result["violations"]
    assert "upstream_input_coverage_template must be a non-empty list of objects" in result["violations"]


def test_worker_reports_passed_summary_for_valid_packet():
    payload = _base_payload(WorkflowStage.API)
    payload["upstream_input_inventory"] = [
        {
            "source_stage": "design",
            "role": "primary",
            "packet_path": "design-packet.json",
            "review_path": "design-review.json",
            "size_bytes": 1,
        }
    ]
    payload["upstream_input_summary"] = {"total_inputs": 1}
    payload["upstream_input_coverage_template"] = [
        {
            "source_stage": "design",
            "role": "primary",
            "packet_path": "design-packet.json",
            "review_path": "design-review.json",
            "status": "unmapped",
            "mapped_to": [],
            "reason": "",
            "evidence": [],
        }
    ]
    result = _evaluate_packet(
        {
            "stage": WorkflowStage.API.value,
            "target": WorkflowStage.API.value,
            "review_state": ReviewState.PACKET_CREATED.value,
            "payload": payload,
        }
    )

    assert result["review_state"] == ReviewState.PASSED.value
    assert result["summary"] == "isolated review passed for api"
    assert result["checks"]["packet_shape"] is True
    assert result["checks"]["payload_rules"] is True
    assert result["checks"]["has_evidence"] is True
    assert result["checks"]["has_counterexamples"] is True


def test_worker_main_round_trip_writes_json(tmp_path, monkeypatch):
    packet_path = tmp_path / "packet.json"
    result_path = tmp_path / "result.json"
    payload = _base_payload(WorkflowStage.API)
    payload["upstream_input_inventory"] = [
        {
            "source_stage": "design",
            "role": "primary",
            "packet_path": "design-packet.json",
            "review_path": "design-review.json",
            "size_bytes": 1,
        }
    ]
    payload["upstream_input_summary"] = {"total_inputs": 1}
    payload["upstream_input_coverage_template"] = [
        {
            "source_stage": "design",
            "role": "primary",
            "packet_path": "design-packet.json",
            "review_path": "design-review.json",
            "status": "unmapped",
            "mapped_to": [],
            "reason": "",
            "evidence": [],
        }
    ]
    packet_path.write_text(
        json.dumps(
            {
                "stage": WorkflowStage.API.value,
                "target": WorkflowStage.API.value,
                "review_state": ReviewState.PACKET_CREATED.value,
                "payload": payload,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("sys.argv", ["worker", "--packet", str(packet_path), "--result", str(result_path)])

    review_worker_main()

    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["review_state"] == ReviewState.PASSED.value
    assert result["summary"] == "isolated review passed for api"


def test_worker_main_entrypoint_works_under_runpy(tmp_path, monkeypatch):
    packet_path = tmp_path / "packet.json"
    result_path = tmp_path / "result.json"
    payload = _base_payload(WorkflowStage.API)
    payload["upstream_input_inventory"] = [
        {
            "source_stage": "design",
            "role": "primary",
            "packet_path": "design-packet.json",
            "review_path": "design-review.json",
            "size_bytes": 1,
        }
    ]
    payload["upstream_input_summary"] = {"total_inputs": 1}
    payload["upstream_input_coverage_template"] = [
        {
            "source_stage": "design",
            "role": "primary",
            "packet_path": "design-packet.json",
            "review_path": "design-review.json",
            "status": "unmapped",
            "mapped_to": [],
            "reason": "",
            "evidence": [],
        }
    ]
    packet_path.write_text(
        json.dumps(
            {
                "stage": WorkflowStage.API.value,
                "target": WorkflowStage.API.value,
                "review_state": ReviewState.PACKET_CREATED.value,
                "payload": payload,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(sys, "argv", ["worker", "--packet", str(packet_path), "--result", str(result_path)])

    runpy.run_module("plb.review.worker", run_name="__main__")
    assert result_path.exists()
