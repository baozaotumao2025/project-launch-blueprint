# Quality Gates Example Output

> 复制这个样板后，直接替换 `<...>` 占位符。  
> 规则：
> - 不要删字段，只能补值。
> - 每个门槛都必须能追溯到上游阶段的风险。
> - 不适用就保留空数组、空字符串或 `false`。

## 1. Quality Gate Map

```json
{
  "quality_gates": [
    {
      "name": "<gate_name>",
      "goal": "<what_this_gate_protects>",
      "scope": "<scope>",
      "risk_category": "<business|technical|experience|rollback|observability>",
      "source_stage": "<discovery|domain-model|state-machine|api-contract|design-system|vertical-slice>",
      "entry_criteria": [
        "<entry_criteria_1>"
      ],
      "exit_criteria": [
        "<exit_criteria_1>"
      ],
      "required_tests": [
        "<unit|integration|contract|e2e|regression>"
      ],
      "required_observability": [
        "<logs|metrics|traces|alerts|health_checks>"
      ],
      "rollback_conditions": [
        "<rollback_condition_1>"
      ],
      "release_action": "<block|allow|allow_with_monitoring|allow_with_flag>",
      "owner": "<owner_role>",
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<upstream_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<source_stage>"
        }
      ],
      "rollback_point": "<source_stage>",
      "evidence": [
        "<upstream_reference>"
      ],
      "assumptions": [
        "<assumption_1>"
      ]
    }
  ],
  "release_readiness_report": {
    "overall_status": "<ready|blocked|ready_with_monitoring>",
    "blocked_by": [
      "<gate_name>"
    ],
    "approved_by": [
      "<gate_name>"
    ],
    "notes": [
      "<note_1>"
    ]
  }
}
```

## 2. Validation Report

```json
{
  "coverage": "<pass|partial|fail>",
  "risk_coverage": "<pass|partial|fail>",
  "test_pyramid_balance": "<pass|partial|fail>",
  "observability_fit": "<pass|partial|fail>",
  "rollback_fit": "<pass|partial|fail>",
  "release_criteria_clarity": "<pass|partial|fail>",
  "positive_test_results": [
    "<positive_test_result_1>"
  ],
  "negative_test_results": [
    "<negative_test_result_1>"
  ],
  "item_results": [
    {
      "item_name": "<gate_name>",
      "verdict": "<pass|fail>",
      "reason": "<why_it_passed_or_failed>",
      "rollback_point": "<source_stage>",
      "evidence": [
        "<upstream_reference>"
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

1. 先填 `quality_gates`。
2. 每个 gate 都补 `positive_tests` 和 `negative_tests`。
3. 明确 release_action 和 rollback_conditions。
4. 最后汇总 `release_readiness_report` 和整体验证报告。

