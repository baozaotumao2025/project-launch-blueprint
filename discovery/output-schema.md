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
  "analysis_inventory": [],
  "analysis_coverage_matrix": [],
  "unmapped_files": [],
  "positive_test_results": [],
  "negative_test_results": [],
  "item_results": [],
  "gaps": [],
  "rejected_items": [],
  "accepted_items": []
}
```

### 2.1 Field Notes

- `analysis_inventory`: every file discovered under `analysis/`, in stable path order.
- `analysis_coverage_matrix`: one row per inventory item, with the mapping decision and evidence.
- `unmapped_files`: inventory items that were intentionally excluded or still need human review.
- `item_results`: capability-level verdicts; the coverage matrix is file-level, so both layers stay visible.

## 3. Usage Rule

- 先输出 discovery capability map
- 再输出 discovery validation report
- 不输出 discovery 以外的对象
