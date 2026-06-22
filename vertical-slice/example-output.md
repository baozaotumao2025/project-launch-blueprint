# Vertical Slice Example Output

> 复制这个样板后，直接替换 `<...>` 占位符。  
> 规则：
> - 不要删字段，只能补值。
> - 切片必须是单一业务能力的完整闭环。
> - 不适用就保留空数组、空字符串或 `false`。

## 1. Vertical Slice Map

```json
{
  "vertical_slices": [
    {
      "name": "<slice_name>",
      "goal": "<business_goal>",
      "scope": "<slice_scope>",
      "capabilities": [
        "<validated_capability_name>"
      ],
      "api_contracts": [
        "<api_contract_name>"
      ],
      "design_system_components": [
        "<component_name>"
      ],
      "state_machine": "<state_machine_name>",
      "route": "<route_path>",
      "pages": [
        {
          "name": "<page_name>",
          "path": "<page_path>",
          "purpose": "<why_this_page_exists>",
          "components": [
            "<component_name>"
          ],
          "states": [
            "loading",
            "empty",
            "success",
            "error"
          ],
          "positive_tests": [
            {
              "name": "<positive_test_name>",
              "given": "<precondition>",
              "when": "<action>",
              "then": "<expected_result>",
              "evidence": "<contract_or_state_reference>"
            }
          ],
          "negative_tests": [
            {
              "name": "<negative_test_name>",
              "bad_case": "<what_should_fail>",
              "why_fail": "<failure_reason>",
              "rollback_point": "<slice_name>"
            }
          ],
          "rollback_point": "<slice_name>",
          "evidence": [
            "<contract_or_state_reference>"
          ]
        }
      ],
      "feature_modules": [
        {
          "name": "<module_name>",
          "responsibility": "<what_it_owns>",
          "hooks": [
            "<hook_name>"
          ],
          "services": [
            "<service_name>"
          ],
          "repositories": [
            "<repository_name>"
          ],
          "mocks": [
            "<mock_name>"
          ],
          "positive_tests": [
            {
              "name": "<positive_test_name>",
              "given": "<precondition>",
              "when": "<action>",
              "then": "<expected_result>",
              "evidence": "<module_reference>"
            }
          ],
          "negative_tests": [
            {
              "name": "<negative_test_name>",
              "bad_case": "<what_should_fail>",
              "why_fail": "<failure_reason>",
              "rollback_point": "<slice_name>"
            }
          ],
          "rollback_point": "<slice_name>",
          "evidence": [
            "<contract_or_component_reference>"
          ]
        }
      ],
      "hooks": [
        "<hook_name>"
      ],
      "services": [
        "<service_name>"
      ],
      "repositories": [
        "<repository_name>"
      ],
      "mocks": [
        "<mock_name>"
      ],
      "data_adapter_rules": [
        "<adapter_rule_1>"
      ],
      "state_wiring_rules": [
        "<state_wiring_rule_1>"
      ],
      "error_handling_rules": [
        "<error_rule_1>"
      ],
      "loading_empty_success_error_flow_rules": [
        "<flow_rule_1>"
      ],
      "integration_boundaries": [
        "<integration_boundary_1>"
      ],
      "acceptance_criteria": [
        "<acceptance_criteria_1>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<slice_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<api_contract_or_design_system>"
        }
      ],
      "rollback_point": "<api_contract_or_design_system>",
      "evidence": [
        "<contract_or_component_reference>"
      ],
      "assumptions": [
        "<assumption_1>"
      ]
    }
  ]
}
```

## 2. Validation Report

```json
{
  "coverage": "<pass|partial|fail>",
  "slice_cohesion": "<pass|partial|fail>",
  "route_cohesion": "<pass|partial|fail>",
  "state_alignment": "<pass|partial|fail>",
  "contract_alignment": "<pass|partial|fail>",
  "design_system_alignment": "<pass|partial|fail>",
  "mock_real_parity": "<pass|partial|fail>",
  "testability": "<pass|partial|fail>",
  "positive_test_results": [
    "<positive_test_result_1>"
  ],
  "negative_test_results": [
    "<negative_test_result_1>"
  ],
  "item_results": [
    {
      "item_name": "<slice_or_page_name>",
      "verdict": "<pass|fail>",
      "reason": "<why_it_passed_or_failed>",
      "rollback_point": "<api_contract_map_or_design_system_map>",
      "evidence": [
        "<contract_or_component_reference>"
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

1. 先填 `vertical_slices`。
2. 每个 slice 都补 `positive_tests` 和 `negative_tests`。
3. 明确 page、hook、service、repository、mock 的职责。
4. 最后汇总 `item_results` 和整体验证报告。

