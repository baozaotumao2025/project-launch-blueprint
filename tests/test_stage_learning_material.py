from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

STAGE_MATERIAL = [
    (
        "domain",
        "0005-domain-stage-boundary-and-approved-inputs.md",
        "domain-implementation-tutorial.md",
    ),
    (
        "state",
        "0006-state-stage-lifecycle-and-state-machine-boundary.md",
        "state-implementation-tutorial.md",
    ),
    (
        "api",
        "0007-api-stage-contract-synthesis-and-validation.md",
        "api-implementation-tutorial.md",
    ),
    (
        "design",
        "0008-design-stage-system-contract-and-review-fence.md",
        "design-implementation-tutorial.md",
    ),
    (
        "slice",
        "0009-slice-stage-vertical-integration-and-execution-order.md",
        "slice-implementation-tutorial.md",
    ),
    (
        "gates",
        "0010-gates-stage-release-fence-before-implementation.md",
        "gates-implementation-tutorial.md",
    ),
]


def test_stage_learning_material_is_complete_and_linked():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "index.md").read_text(encoding="utf-8")
    tutorials_index = (REPO_ROOT / "docs" / "tutorial" / "index.md").read_text(encoding="utf-8")
    conventions = (REPO_ROOT / "docs" / "tutorial" / "conventions.md").read_text(encoding="utf-8")
    stage_map = (REPO_ROOT / "docs" / "tutorial" / "stage-map.md").read_text(encoding="utf-8")
    adr_index = (REPO_ROOT / "adr" / "README.md").read_text(encoding="utf-8")
    user_manual = (REPO_ROOT / "docs" / "step-04-user-manual.md").read_text(encoding="utf-8")

    assert "docs/tutorial/index.md" in readme
    assert "adr/README.md" in readme
    assert "Each stage must enumerate its stage documents" in readme
    assert "docs/tutorial/index.md" in skill
    assert "adr/README.md" in skill
    assert "stage input inventory" in skill.lower()
    assert "tutorials" in docs_index.lower()
    assert "tutorials" in tutorials_index.lower()
    assert "Shared Structure" in conventions
    assert "Why This Matters" in conventions
    assert "Stage Map" in stage_map
    assert "Key Code" in stage_map
    assert "domain-model/" in stage_map
    assert "quality-gates/" in stage_map
    assert "src/plb/commands/review.py" in stage_map
    assert "src/plb/state/store.py" in stage_map
    assert "0011-discovery-file-inventory-and-coverage-matrix.md" in adr_index
    assert "0012-domain-input-inventory-and-coverage-matrix.md" in adr_index
    assert "0013-freeze-first-inventory-first-verify-second-methodology.md" in adr_index
    assert "freeze-first" in adr_index.lower()
    assert "file inventory" in user_manual.lower()
    assert "coverage matrix" in user_manual.lower()
    assert "analysis_coverage_matrix" in (REPO_ROOT / "discovery" / "output-schema.md").read_text(encoding="utf-8")
    example_output = (REPO_ROOT / "discovery" / "example-output.md").read_text(encoding="utf-8")
    assert "analysis_coverage_matrix" in example_output
    assert '"status": "mapped"' in example_output
    assert '"status": "excluded"' in example_output
    assert '"status": "needs_review"' in example_output
    domain_schema = (REPO_ROOT / "domain-model" / "output-schema.md").read_text(encoding="utf-8")
    domain_example = (REPO_ROOT / "domain-model" / "example-output.md").read_text(encoding="utf-8")
    assert "domain_input_inventory" in domain_schema
    assert "domain_coverage_matrix" in domain_schema
    assert "domain_input_inventory" in domain_example
    assert '"status": "mapped"' in domain_example
    assert '"status": "excluded"' in domain_example
    assert '"status": "needs_review"' in domain_example
    assert "upstream_input_inventory" in (REPO_ROOT / "state-machine" / "output-schema.md").read_text(encoding="utf-8")
    assert "upstream_input_inventory" in (REPO_ROOT / "api-contract" / "output-schema.md").read_text(encoding="utf-8")
    assert "upstream_input_inventory" in (REPO_ROOT / "design-system" / "output-schema.md").read_text(encoding="utf-8")
    assert "upstream_input_inventory" in (REPO_ROOT / "vertical-slice" / "output-schema.md").read_text(encoding="utf-8")
    assert "upstream_input_inventory" in (REPO_ROOT / "quality-gates" / "output-schema.md").read_text(encoding="utf-8")
    assert "upstream input inventory" in (REPO_ROOT / "state-machine" / "validation-rules.md").read_text(encoding="utf-8").lower()
    assert "upstream input inventory" in (REPO_ROOT / "api-contract" / "validation-rules.md").read_text(encoding="utf-8").lower()
    assert "upstream input inventory" in (REPO_ROOT / "design-system" / "validation-rules.md").read_text(encoding="utf-8").lower()
    assert "upstream input inventory" in (REPO_ROOT / "vertical-slice" / "validation-rules.md").read_text(encoding="utf-8").lower()
    assert "upstream input inventory" in (REPO_ROOT / "quality-gates" / "validation-rules.md").read_text(encoding="utf-8").lower()
    assert "upstream_input_inventory" in (REPO_ROOT / "implementation" / "output-schema.md").read_text(encoding="utf-8")
    assert "upstream input inventory" in (REPO_ROOT / "implementation" / "validation-rules.md").read_text(encoding="utf-8").lower()

    for stage, adr_file, tutorial_file in STAGE_MATERIAL:
        assert (REPO_ROOT / "adr" / adr_file).exists()
        assert (REPO_ROOT / "docs" / "tutorial" / tutorial_file).exists()
        assert adr_file in adr_index
        assert tutorial_file in tutorials_index
        assert stage in tutorials_index
        assert tutorial_file in stage_map
