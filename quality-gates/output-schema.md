# Output Schema

> quality-gates 阶段只输出 `quality gate map` 和 `quality-gates validation report`。

## 1. Quality Gate Map

```json
{
  "quality_gates": [
    {
      "name": "",
      "goal": "",
      "scope": "",
      "risk_category": "",
      "source_stage": "",
      "entry_criteria": [],
      "exit_criteria": [],
      "required_tests": [],
      "required_observability": [],
      "rollback_conditions": [],
      "release_action": "",
      "owner": "",
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": [],
      "assumptions": []
    }
  ],
  "release_readiness_report": {
    "overall_status": "",
    "blocked_by": [],
    "approved_by": [],
    "notes": []
  }
}
```

## 2. Quality-Gates Validation Report

```json
{
  "coverage": "",
  "upstream_input_inventory": [],
  "upstream_input_coverage_matrix": [],
  "risk_coverage": "",
  "test_pyramid_balance": "",
  "observability_fit": "",
  "rollback_fit": "",
  "release_criteria_clarity": "",
  "positive_test_results": [],
  "negative_test_results": [],
  "item_results": [],
  "gaps": [],
  "rejected_items": [],
  "accepted_items": []
}
```

## 3. Usage Rule

- 先输出 quality gate map
- 再输出 quality-gates validation report
- 不输出 quality-gates 以外的对象
