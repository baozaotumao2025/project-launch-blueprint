# Output Schema

> api-contract 阶段只输出 `api contract map` 和 `api-contract validation report`。

## 1. API Contract Map

```json
{
  "api_contracts": [
    {
      "contract_id": "",
      "name": "",
      "api_family": "http",
      "version": "",
      "bounded_context": "",
      "state_machine": "",
      "goal": "",
      "scope": "",
      "method": "",
      "path": "",
      "purpose": "",
      "success_statuses": [],
      "response_headers": [],
      "request": {
        "content_type": "",
        "headers": [],
        "fields": [],
        "validation": [],
        "examples": []
      },
      "response": {
        "content_type": "",
        "headers": [],
        "fields": [],
        "examples": []
      },
      "errors": [
        {
          "code": "",
          "status": "",
          "meaning": "",
          "recoverability": "",
          "example": ""
        }
      ],
      "auth": {
        "roles": [],
        "scopes": [],
        "rules": []
      },
      "idempotency": {
        "required": false,
        "strategy": "",
        "key_location": ""
      },
      "versioning": {
        "supported": false,
        "compatibility": "",
        "deprecation": ""
      },
      "pagination": {
        "supported": false,
        "cursor_or_offset": "",
        "rules": []
      },
      "filtering": [],
      "sorting": [],
      "state_alignment": [],
      "capabilities": [],
      "domain_objects": [],
      "state_transitions": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": [],
      "assumptions": []
    }
  ]
}
```

## 2. API-Contract Validation Report

```json
{
  "coverage": "",
  "upstream_input_inventory": [],
  "upstream_input_coverage_matrix": [],
  "boundary_purity": "",
  "method_fit": "",
  "status_semantics": "",
  "versioning_fit": "",
  "error_semantics": "",
  "auth_clarity": "",
  "idempotency_fit": "",
  "state_alignment": "",
  "contract_results": [
    {
      "contract_id": "",
      "verdict": "",
      "reason": "",
      "positive_test_results": [],
      "negative_test_results": [],
      "rollback_point": "",
      "evidence": []
    }
  ],
  "negative_test_results": [],
  "gaps": [],
  "rejected_items": [],
  "accepted_items": []
}
```

## 3. Usage Rule

- 先输出 api contract map
- 再输出 api-contract validation report
- 不输出 api-contract 以外的对象
