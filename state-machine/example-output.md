# State Machine Example Output

> 复制这个样板后，直接替换 `<...>` 占位符。  
> 规则：
> - 不要删字段，只能补值。
> - 状态必须是业务阶段，事件必须是业务事实。
> - 不适用就保留空数组、空字符串或 `false`。

## 1. State Machine Map

```json
{
  "state_machines": [
    {
      "name": "<state_machine_name>",
      "bounded_context": "<bounded_context_name>",
      "goal": "<business_goal>",
      "scope": "<flow_scope>",
      "states": [
        "<state_name>"
      ],
      "events": [
        "<business_event_name>"
      ],
      "guards": [
        "<guard_name>"
      ],
      "transitions": [
        "<from_state> -> <to_state> on <event>"
      ],
      "terminal_states": [
        "<terminal_state_name>"
      ],
      "entry_conditions": [
        "<entry_condition_1>"
      ],
      "exit_conditions": [
        "<exit_condition_1>"
      ],
      "capabilities": [
        "<validated_capability_name>"
      ],
      "domain_objects": [
        "<domain_object_name>"
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
          "evidence": "<state_machine_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<bounded_context_or_capability>"
        }
      ],
      "rollback_point": "<bounded_context_or_capability>",
      "evidence": [
        "<capability_or_domain_reference>"
      ],
      "assumptions": [
        "<assumption_1>"
      ]
    }
  ]
}
```

## 2. State-Machine Validation Report

```json
{
  "coverage": "<pass|partial|fail>",
  "state_purity": "<pass|partial|fail>",
  "event_purity": "<pass|partial|fail>",
  "guard_clarity": "<pass|partial|fail>",
  "terminal_validity": "<pass|partial|fail>",
  "flow_cohesion": "<pass|partial|fail>",
  "positive_test_results": [
    "<positive_test_result_1>"
  ],
  "negative_test_results": [
    "<negative_test_result_1>"
  ],
  "item_results": [
    {
      "item_name": "<state_machine_name_or_state_name>",
      "verdict": "<pass|fail>",
      "reason": "<why_it_passed_or_failed>",
      "rollback_point": "<bounded_context_name>",
      "evidence": [
        "<capability_or_domain_reference>"
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

1. 先填 `state_machines`。
2. 每个状态机都补 `positive_tests` 和 `negative_tests`。
3. 再汇总 `item_results` 和整体验证报告。
4. 如果不通过，回退到 `bounded_context` 或更前面的 capability。

