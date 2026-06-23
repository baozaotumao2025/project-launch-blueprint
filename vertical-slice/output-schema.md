# Output Schema

> vertical-slice 阶段只输出 `vertical slice map` 和 `vertical-slice validation report`。

## 1. Vertical Slice Map

```json
{
  "vertical_slices": [
    {
      "name": "",
      "goal": "",
      "scope": "",
      "capabilities": [],
      "api_contracts": [],
      "design_system_components": [],
      "state_machine": "",
      "route": "",
      "pages": [
        {
          "name": "",
          "path": "",
          "purpose": "",
          "components": [],
          "states": [],
          "positive_tests": [],
          "negative_tests": [],
          "rollback_point": "",
          "evidence": []
        }
      ],
      "feature_modules": [
        {
          "name": "",
          "responsibility": "",
          "hooks": [],
          "services": [],
          "repositories": [],
          "mocks": [],
          "positive_tests": [],
          "negative_tests": [],
          "rollback_point": "",
          "evidence": []
        }
      ],
      "hooks": [],
      "services": [],
      "repositories": [],
      "mocks": [],
      "data_adapter_rules": [],
      "state_wiring_rules": [],
      "error_handling_rules": [],
      "loading_empty_success_error_flow_rules": [],
      "integration_boundaries": [],
      "acceptance_criteria": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": [],
      "assumptions": []
    }
  ]
}
```

## 2. Vertical-Slice Validation Report

```json
{
  "coverage": "",
  "upstream_input_inventory": [],
  "upstream_input_coverage_matrix": [],
  "slice_cohesion": "",
  "route_cohesion": "",
  "state_alignment": "",
  "contract_alignment": "",
  "design_system_alignment": "",
  "mock_real_parity": "",
  "testability": "",
  "positive_test_results": [],
  "negative_test_results": [],
  "item_results": [],
  "gaps": [],
  "rejected_items": [],
  "accepted_items": []
}
```

## 3. Usage Rule

- 先输出 vertical slice map
- 再输出 vertical-slice validation report
- 不输出 vertical-slice 以外的对象
