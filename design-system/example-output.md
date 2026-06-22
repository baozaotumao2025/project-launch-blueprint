# Design System Example Output

> 复制这个样板后，直接替换 `<...>` 占位符。  
> 规则：
> - 不要删字段，只能补值。
> - token 必须是语义变量，不是页面常量。
> - 组件必须能覆盖状态矩阵、无障碍和响应式要求。

## 1. Design System Map

```json
{
  "design_systems": [
    {
      "name": "<design_system_name>",
      "version": "<v1|v2|...>",
      "goal": "<design_goal>",
      "scope": "<scope>",
      "api_contracts": [
        "<validated_contract_name>"
      ],
      "state_machines": [
        "<validated_state_machine_name>"
      ],
      "domain_objects": [
        "<domain_object_name>"
      ],
      "capabilities": [
        "<validated_capability_name>"
      ],
      "tokens": {
        "semantic_colors": [
          {
            "name": "<color_token_name>",
            "value": "<token_value>",
            "meaning": "<semantic_meaning>"
          }
        ],
        "spacing": [
          {
            "name": "<space_token_name>",
            "value": "<token_value>",
            "meaning": "<spacing_semantics>"
          }
        ],
        "radius": [
          {
            "name": "<radius_token_name>",
            "value": "<token_value>",
            "meaning": "<radius_semantics>"
          }
        ],
        "shadow": [
          {
            "name": "<shadow_token_name>",
            "value": "<token_value>",
            "meaning": "<shadow_semantics>"
          }
        ],
        "z_index": [
          {
            "name": "<z_index_token_name>",
            "value": "<token_value>",
            "meaning": "<layer_semantics>"
          }
        ]
      },
      "color_system": {
        "palette": [
          "<base_color_name>"
        ],
        "semantic_mapping": [
          "<semantic_color_mapping>"
        ],
        "contrast_rules": [
          "<contrast_rule_1>"
        ]
      },
      "typography": {
        "families": [
          "<font_family_name>"
        ],
        "scale": [
          "<font_scale_token>"
        ],
        "weights": [
          "<font_weight_token>"
        ],
        "line_heights": [
          "<line_height_token>"
        ]
      },
      "layout_rules": {
        "grid": [
          "<grid_rule>"
        ],
        "breakpoints": [
          "<breakpoint_token>"
        ],
        "density": [
          "<density_mode>"
        ],
        "composition": [
          "<layout_composition_rule>"
        ]
      },
      "motion_rules": {
        "durations": [
          "<duration_token>"
        ],
        "easing": [
          "<easing_token>"
        ],
        "reduced_motion": [
          "<reduced_motion_rule>"
        ]
      },
      "accessibility_rules": [
        "<accessibility_rule_1>"
      ],
      "responsive_rules": [
        "<responsive_rule_1>"
      ],
      "iconography_rules": [
        "<iconography_rule_1>"
      ],
      "components": [
        {
          "name": "<component_name>",
          "purpose": "<what_it_solves>",
          "anatomy": [
            "<part_1>"
          ],
          "variants": [
            "<variant_1>"
          ],
          "sizes": [
            "<size_1>"
          ],
          "states": [
            "<default|hover|focus|loading|empty|error|disabled|success>"
          ],
          "behaviors": [
            "<behavior_1>"
          ],
          "props": [
            "<prop_1>"
          ],
          "tokens": [
            "<token_reference_1>"
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
              "rollback_point": "<token_or_component>"
            }
          ],
          "rollback_point": "<token_or_component>",
          "evidence": [
            "<contract_or_state_reference>"
          ]
        }
      ],
      "interaction_patterns": [
        "<interaction_pattern_1>"
      ],
      "usage_guidelines": [
        "<usage_guideline_1>"
      ],
      "anti_patterns": [
        "<anti_pattern_1>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<design_system_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<api_contract_map>"
        }
      ],
      "rollback_point": "<api_contract_map>",
      "evidence": [
        "<api_contract_or_state_reference>"
      ],
      "assumptions": [
        "<assumption_1>"
      ]
    }
  ]
}
```

## 2. Design-System Validation Report

```json
{
  "coverage": "<pass|partial|fail>",
  "token_purity": "<pass|partial|fail>",
  "semantic_consistency": "<pass|partial|fail>",
  "component_reusability": "<pass|partial|fail>",
  "state_coverage": "<pass|partial|fail>",
  "accessibility_fit": "<pass|partial|fail>",
  "responsive_fit": "<pass|partial|fail>",
  "motion_clarity": "<pass|partial|fail>",
  "positive_test_results": [
    "<positive_test_result_1>"
  ],
  "negative_test_results": [
    "<negative_test_result_1>"
  ],
  "item_results": [
    {
      "item_name": "<token_or_component_name>",
      "verdict": "<pass|fail>",
      "reason": "<why_it_passed_or_failed>",
      "rollback_point": "<api_contract_map_or_token>",
      "evidence": [
        "<contract_or_state_reference>"
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

1. 先填 `tokens` 和 `components`。
2. 每个组件都补 `positive_tests` 和 `negative_tests`。
3. 再补 `accessibility_rules` / `responsive_rules` / `motion_rules`。
4. 最后汇总 `item_results` 和整体验证报告。

