# API Contract Example Output

> 复制这个样板后，直接替换 `<...>` 占位符。  
> 规则：
> - 不要删字段，只能补值。
> - 不适用就保留空数组、空字符串或 `false`。
> - `api_contracts` 里每个对象都必须能回指 capability / domain object / state machine。

## 1. API Contract Map

```json
{
  "api_contracts": [
    {
      "contract_id": "<unique_contract_id>",
      "name": "<human_readable_contract_name>",
      "api_family": "http",
      "version": "<v1|v2|...>",
      "bounded_context": "<bounded_context_name>",
      "state_machine": "<state_machine_name_or_empty>",
      "goal": "<what_this_contract_achieves>",
      "scope": "<contract_scope>",
      "method": "<GET|POST|PUT|PATCH|DELETE>",
      "path": "</resource/{id}/action>",
      "purpose": "<why_this_endpoint_exists>",
      "success_statuses": ["<200>", "<201>", "<204>"],
      "response_headers": ["<header_name_if_needed>"],
      "request": {
        "content_type": "application/json",
        "headers": [
          "<header_name_if_needed>"
        ],
        "fields": [
          {
            "name": "<field_name>",
            "type": "<string|number|boolean|object|array>",
            "required": true,
            "source": "<discovery|domain_model|state_machine>",
            "description": "<why_this_field_is_needed>"
          }
        ],
        "validation": [
          "<validation_rule_1>",
          "<validation_rule_2>"
        ],
        "examples": [
          {
            "name": "<request_example_name>",
            "value": "<example_request_payload>",
            "notes": "<why_this_example_passes>"
          }
        ]
      },
      "response": {
        "content_type": "application/json",
        "headers": [
          "<header_name_if_needed>"
        ],
        "fields": [
          {
            "name": "<field_name>",
            "type": "<string|number|boolean|object|array>",
            "source": "<domain_object|state_alignment|capability>",
            "description": "<why_this_field_is_returned>"
          }
        ],
        "examples": [
          {
            "name": "<success_example_name>",
            "status": "<200|201|204>",
            "value": "<example_response_payload>",
            "notes": "<why_this_example_passes>"
          }
        ]
      },
      "errors": [
        {
          "code": "<error_code>",
          "status": "<400|401|403|404|409|422|500>",
          "meaning": "<what_failed>",
          "recoverability": "<retry|fix_input|refresh_state|no_recovery>",
          "example": "<example_error_payload>"
        }
      ],
      "auth": {
        "roles": [
          "<role_name>"
        ],
        "scopes": [
          "<scope_name>"
        ],
        "rules": [
          "<access_rule_1>",
          "<access_rule_2>"
        ]
      },
      "idempotency": {
        "required": false,
        "strategy": "<key_based|resource_based|state_based|none>",
        "key_location": "<header|body|path|none>"
      },
      "versioning": {
        "supported": true,
        "compatibility": "<backward_compatible|breaking|mixed>",
        "deprecation": "<if_and_when_this_contract_is_deprecated>"
      },
      "pagination": {
        "supported": false,
        "cursor_or_offset": "<cursor|offset|none>",
        "rules": [
          "<pagination_rule_if_needed>"
        ]
      },
      "filtering": [
        "<filter_field_1>"
      ],
      "sorting": [
        "<sort_field_1>"
      ],
      "state_alignment": [
        "<state_machine_state_or_transition>"
      ],
      "capabilities": [
        "<validated_capability_1>"
      ],
      "domain_objects": [
        "<domain_object_1>"
      ],
      "state_transitions": [
        "<state_transition_1>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<why_this_is_supported>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<where_to_go_back>"
        }
      ],
      "rollback_point": "<state_machine_or_model_step_to_return_to_if_wrong>",
      "evidence": [
        "<source_reference_1>"
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
  "boundary_purity": "<pass|partial|fail>",
  "method_fit": "<pass|partial|fail>",
  "status_semantics": "<pass|partial|fail>",
  "versioning_fit": "<pass|partial|fail>",
  "error_semantics": "<pass|partial|fail>",
  "auth_clarity": "<pass|partial|fail>",
  "idempotency_fit": "<pass|partial|fail>",
  "state_alignment": "<pass|partial|fail>",
  "contract_results": [
    {
      "contract_id": "<unique_contract_id>",
      "verdict": "<pass|fail>",
      "reason": "<why_it_passed_or_failed>",
      "positive_test_results": [
        "<positive_test_pass_1>"
      ],
      "negative_test_results": [
        "<negative_test_fail_1>"
      ],
      "rollback_point": "<where_to_return_if_failed>",
      "evidence": [
        "<evidence_reference_1>"
      ]
    }
  ],
  "negative_test_results": [
    "<global_negative_test_result_1>"
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

1. 先填 `api_contracts`。
2. 每个 contract 都补 `positive_tests` 和 `negative_tests`。
3. 先写 `contract_results`，再汇总 `coverage` 和其他总体结论。
4. 如果某项不通过，直接填对应的 `rollback_point`，不要模糊描述。

