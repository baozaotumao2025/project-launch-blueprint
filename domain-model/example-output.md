# Domain Model Example Output

> 复制这个样板后，直接替换 `<...>` 占位符。  
> 规则：
> - 不要删字段，只能补值。
> - 每个 context / aggregate / entity / value object 都要能回指已验证 capability。
> - 不适用就保留空数组、空字符串或 `false`。

## 1. Domain Model Map

```json
{
  "bounded_contexts": [
    {
      "name": "<bounded_context_name>",
      "goal": "<business_goal>",
      "scope": "<scope>",
      "capabilities": [
        "<validated_capability_name>"
      ],
      "language": [
        "<domain_term_1>"
      ],
      "owner_personas": [
        "<persona_name>"
      ],
      "upstream_contexts": [
        "<upstream_context_name>"
      ],
      "downstream_contexts": [
        "<downstream_context_name>"
      ],
      "relationships": [
        "<upstream|downstream|acl|shared_kernel|published_language>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<capability_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "discovery capability map"
        }
      ],
      "rollback_point": "discovery capability map",
      "notes": [
        "<note_1>"
      ]
    }
  ],
  "aggregates": [
    {
      "name": "<aggregate_name>",
      "bounded_context": "<bounded_context_name>",
      "root_entity": "<root_entity_name>",
      "responsibility": "<what_it_protects>",
      "invariants": [
        "<invariant_1>"
      ],
      "commands": [
        "<command_name>"
      ],
      "events": [
        "<domain_event_name>"
      ],
      "related_entities": [
        "<entity_name>"
      ],
      "related_value_objects": [
        "<value_object_name>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<aggregate_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<bounded_context_name>"
        }
      ],
      "rollback_point": "<bounded_context_name>",
      "evidence": [
        "<capability_reference>"
      ],
      "assumptions": [
        "<assumption_1>"
      ]
    }
  ],
  "entities": [
    {
      "name": "<entity_name>",
      "bounded_context": "<bounded_context_name>",
      "identity": "<identity_rule>",
      "responsibility": "<responsibility>",
      "attributes": [
        "<attribute_name>"
      ],
      "behaviors": [
        "<behavior_name>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<entity_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<aggregate_name>"
        }
      ],
      "rollback_point": "<aggregate_name>",
      "evidence": [
        "<capability_reference>"
      ]
    }
  ],
  "value_objects": [
    {
      "name": "<value_object_name>",
      "bounded_context": "<bounded_context_name>",
      "value_semantics": "<what_makes_it_a_value>",
      "attributes": [
        "<attribute_name>"
      ],
      "validation_rules": [
        "<rule_1>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<vo_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<entity_or_aggregate_name>"
        }
      ],
      "rollback_point": "<entity_or_aggregate_name>",
      "evidence": [
        "<capability_reference>"
      ]
    }
  ],
  "domain_services": [
    {
      "name": "<domain_service_name>",
      "bounded_context": "<bounded_context_name>",
      "responsibility": "<orchestration_or_rule>",
      "rules": [
        "<rule_1>"
      ],
      "inputs": [
        "<input_1>"
      ],
      "outputs": [
        "<output_1>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<service_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<bounded_context_name>"
        }
      ],
      "rollback_point": "<bounded_context_name>",
      "evidence": [
        "<capability_reference>"
      ]
    }
  ],
  "domain_events": [
    {
      "name": "<domain_event_name>",
      "bounded_context": "<bounded_context_name>",
      "fact": "<what_happened>",
      "trigger": "<what_caused_it>",
      "producers": [
        "<producer_name>"
      ],
      "consumers": [
        "<consumer_name>"
      ],
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<event_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<bounded_context_name>"
        }
      ],
      "rollback_point": "<bounded_context_name>",
      "evidence": [
        "<capability_reference>"
      ]
    }
  ],
  "context_map": [
    {
      "from": "<upstream_context>",
      "to": "<downstream_context>",
      "relationship": "<upstream|downstream|acl|shared_kernel|published_language>",
      "translation": "<how_terms_are_translated>",
      "reason": "<why_this_relationship_exists>",
      "positive_tests": [
        {
          "name": "<positive_test_name>",
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected_result>",
          "evidence": "<relationship_reference>"
        }
      ],
      "negative_tests": [
        {
          "name": "<negative_test_name>",
          "bad_case": "<what_should_fail>",
          "why_fail": "<failure_reason>",
          "rollback_point": "<bounded_context_name>"
        }
      ],
      "rollback_point": "<bounded_context_name>",
      "evidence": [
        "<capability_reference>"
      ]
    }
  ]
}
```

## 2. Domain-Model Validation Report

```json
{
  "coverage": "<pass|partial|fail>",
  "boundary_purity": "<pass|partial|fail>",
  "language_consistency": "<pass|partial|fail>",
  "aggregate_integrity": "<pass|partial|fail>",
  "behavior_richness": "<pass|partial|fail>",
  "domain_input_inventory": [
    {
      "path": "discovery/discovery-capability-map.json",
      "input_type": "discovery capability map",
      "role": "primary",
      "size_bytes": 5120
    },
    {
      "path": "analysis/features/index.md",
      "input_type": "auxiliary evidence",
      "role": "secondary",
      "size_bytes": 2048
    }
  ],
  "domain_coverage_matrix": [
    {
      "path": "discovery/discovery-capability-map.json",
      "input_type": "discovery capability map",
      "status": "mapped",
      "mapped_to": [
        "bounded_context: customer_intake"
      ],
      "reason": "Validated capabilities were grouped into a single intake boundary",
      "evidence": [
        "discovery capability map"
      ]
    },
    {
      "path": "analysis/features/index.md",
      "input_type": "auxiliary evidence",
      "status": "excluded",
      "mapped_to": [],
      "reason": "Feature index only confirms terminology and does not become a primary domain source",
      "evidence": [
        "analysis/features/index.md"
      ]
    },
    {
      "path": "analysis/pages/ambiguous-page.md",
      "input_type": "auxiliary evidence",
      "status": "needs_review",
      "mapped_to": [],
      "reason": "Page semantics are unclear and need human clarification before final context mapping",
      "evidence": [
        "analysis/pages/ambiguous-page.md"
      ]
    }
  ],
  "unmapped_inputs": [
    {
      "path": "analysis/pages/ambiguous-page.md",
      "input_type": "auxiliary evidence",
      "reason": "Needs clarification before it can influence the model",
      "rollback_point": "discovery capability map"
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
      "item_name": "<bounded_context_or_aggregate_name>",
      "verdict": "<pass|fail>",
      "reason": "<why_it_passed_or_failed>",
      "rollback_point": "<discovery capability map|bounded_context_name>",
      "evidence": [
        "<capability_reference>"
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

1. 先填 `bounded_contexts`。
2. 再补 `aggregates`、`entities`、`value_objects`、`domain_services`、`domain_events`。
3. 每个对象都补 `positive_tests` 和 `negative_tests`。
4. 再汇总 `item_results` 和整体验证报告。
