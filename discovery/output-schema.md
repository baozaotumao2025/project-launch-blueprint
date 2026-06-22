# Output Schema

> discovery 阶段只输出两样东西：`discovery capability map` 和 `discovery validation report`。

## 1. Discovery Capability Map

```json
{
  "capabilities": [
    {
      "name": "",
      "actor": "",
      "trigger": "",
      "input": [],
      "outcome": "",
      "lifecycle_stage": "",
      "related_pages": [],
      "related_features": [],
      "related_story_steps": [],
      "gwt_examples": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": [],
      "assumptions": []
    }
  ]
}
```

## 2. Discovery Validation Report

```json
{
  "coverage": "",
  "purity": "",
  "traceability": "",
  "testability": "",
  "boundary_purity": "",
  "language_consistency": "",
  "positive_test_results": [],
  "negative_test_results": [],
  "item_results": [],
  "gaps": [],
  "rejected_items": [],
  "accepted_items": []
}
```

## 3. Usage Rule

- 先输出 discovery capability map
- 再输出 discovery validation report
- 不输出 discovery 以外的对象
