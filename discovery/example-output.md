# Discovery Example Output

> 复制这个样板后，直接替换 `<...>` 占位符。  
> 规则：
> - 不要删字段，只能补值。
> - 每条 capability 必须能回指 `analysis` 里的证据。
> - 不适用就保留空数组、空字符串或 `false`。

## 1. Discovery Capability Map

```json
{
  "capabilities": [
    {
      "name": "<business_capability_name>",
      "actor": "<persona_or_role>",
      "trigger": "<what_starts_it>",
      "input": [
        "<required_input_1>"
      ],
      "outcome": "<business_result>",
      "lifecycle_stage": "<stage_name>",
      "related_pages": [
        "<page_name>"
      ],
      "related_features": [
        "<feature_name>"
      ],
      "related_story_steps": [
        "<story_step_reference>"
      ],
      "gwt_examples": [
        "<given_when_then_example>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<analysis_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "analysis"
        }
      ],
      "rollback_point": "analysis",
      "evidence": [
        "<analysis/feature_or_page_or_gwt_reference>"
      ],
      "assumptions": [
        "<assumption_if_any>"
      ]
    }
  ]
}
```

## 2. Discovery Validation Report

```json
{
  "coverage": "<pass|partial|fail>",
  "purity": "<pass|partial|fail>",
  "traceability": "<pass|partial|fail>",
  "testability": "<pass|partial|fail>",
  "boundary_purity": "<pass|partial|fail>",
  "language_consistency": "<pass|partial|fail>",
  "analysis_inventory": [
    {
      "path": "analysis/brief.md",
      "analysis_path": "analysis/brief.md",
      "top_level": "brief.md",
      "suffix": ".md",
      "size_bytes": 120
    }
  ],
  "analysis_coverage_matrix": [
    {
      "path": "analysis/brief.md",
      "analysis_path": "analysis/brief.md",
      "status": "mapped",
      "covered_by": [
        "capability: customer_onboarding_scope"
      ],
      "reason": "Scope statement mapped into onboarding capability",
      "evidence": [
        "analysis/brief.md"
      ]
    },
    {
      "path": "analysis/relations/experimental-note.md",
      "analysis_path": "analysis/relations/experimental-note.md",
      "status": "excluded",
      "covered_by": [],
      "reason": "Experimental note is not a source of truth for discovery synthesis",
      "evidence": [
        "analysis/relations/experimental-note.md"
      ]
    },
    {
      "path": "analysis/pages/ambiguous-page.md",
      "analysis_path": "analysis/pages/ambiguous-page.md",
      "status": "needs_review",
      "covered_by": [],
      "reason": "Page intent is unclear and needs human clarification before mapping",
      "evidence": [
        "analysis/pages/ambiguous-page.md"
      ]
    }
  ],
  "unmapped_files": [
    {
      "path": "analysis/notes.txt",
      "analysis_path": "analysis/notes.txt",
      "reason": "Non-authoritative note, excluded from capability synthesis",
      "rollback_point": "analysis"
    },
    {
      "path": "analysis/pages/ambiguous-page.md",
      "analysis_path": "analysis/pages/ambiguous-page.md",
      "reason": "Needs human review before capability mapping",
      "rollback_point": "analysis"
    }
  ],
  "positive_test_results": [
    "<positive_test_result_1>"
  ],
  "negative_test_results": [
    "<negative_test_result_1>"
  ],
  "item_results": [
    {
      "capability_name": "<name>",
      "verdict": "<pass|fail>",
      "reason": "<why_it_passed_or_failed>",
      "rollback_point": "analysis",
      "evidence": [
        "<analysis_reference>"
      ]
    }
  ],
  "gaps": [
    "<missing_item_1>"
  ],
  "rejected_items": [
    "<rejected_item_1>"
  ],
  "accepted_items": [
    "<accepted_item_1>"
  ]
}
```

## 3. How To Use

1. 先填 `capabilities`。
2. 每条 capability 都补 `positive_tests` 和 `negative_tests`。
3. `rollback_point` 默认回到 `analysis`。
4. 再汇总 `item_results` 和整体验证报告。
