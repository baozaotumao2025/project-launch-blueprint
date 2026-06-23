# Output Schema

> domain model 阶段只输出领域边界、领域对象、关系和 `domain-model validation report`。

## 1. Domain Model Map

```json
{
  "bounded_contexts": [
    {
      "name": "",
      "goal": "",
      "scope": "",
      "capabilities": [],
      "language": [],
      "owner_personas": [],
      "upstream_contexts": [],
      "downstream_contexts": [],
      "relationships": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "notes": []
    }
  ],
  "aggregates": [
    {
      "name": "",
      "bounded_context": "",
      "root_entity": "",
      "responsibility": "",
      "invariants": [],
      "commands": [],
      "events": [],
      "related_entities": [],
      "related_value_objects": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": [],
      "assumptions": []
    }
  ],
  "entities": [
    {
      "name": "",
      "bounded_context": "",
      "identity": "",
      "responsibility": "",
      "attributes": [],
      "behaviors": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": []
    }
  ],
  "value_objects": [
    {
      "name": "",
      "bounded_context": "",
      "value_semantics": "",
      "attributes": [],
      "validation_rules": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": []
    }
  ],
  "domain_services": [
    {
      "name": "",
      "bounded_context": "",
      "responsibility": "",
      "rules": [],
      "inputs": [],
      "outputs": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": []
    }
  ],
  "domain_events": [
    {
      "name": "",
      "bounded_context": "",
      "fact": "",
      "trigger": "",
      "producers": [],
      "consumers": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": []
    }
  ],
  "context_map": [
    {
      "from": "",
      "to": "",
      "relationship": "",
      "translation": "",
      "reason": "",
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": []
    }
  ]
}
```

## 2. Domain-Model Validation Report

```json
{
  "coverage": "",
  "boundary_purity": "",
  "language_consistency": "",
  "aggregate_integrity": "",
  "behavior_richness": "",
  "domain_input_inventory": [],
  "domain_coverage_matrix": [],
  "unmapped_inputs": [],
  "positive_test_results": [],
  "negative_test_results": [],
  "item_results": [],
  "gaps": [],
  "rejected_items": [],
  "accepted_items": []
}
```

### 2.1 Field Notes

- `domain_input_inventory`: every approved upstream input and auxiliary evidence item considered by domain, in stable order.
- `domain_coverage_matrix`: one row per inventory item, with the mapping decision and evidence.
- `unmapped_inputs`: inputs that are intentionally excluded or still need human clarification.
- `item_results`: model-level verdicts; the coverage matrix stays file/input-level, so both layers remain visible.

## 3. Usage Rule

- 先输出 domain model map
- 再输出 domain-model validation report
- 不输出 domain model 以外的对象
