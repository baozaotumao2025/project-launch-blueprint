# Output Schema

> `implementation` 阶段只输出可执行的实现计划和实现交付报告。

## 1. Implementation Plan

```json
{
  "goal": "",
  "scope": "",
  "upstream_input_inventory": [],
  "upstream_input_coverage_matrix": [],
  "goal_registry": [
    {
      "goal_id": "",
      "order": 1,
      "goal": "",
      "depends_on": [],
      "status": "",
      "regression_scope": [],
      "rollback_point": "",
      "evidence": []
    }
  ],
  "inputs": {
    "codex_goal": "",
    "quality_gates_validation_report": "",
    "vertical_slice_map": "",
    "api_contract_map": "",
    "design_system_map": "",
    "state_machine_map": "",
    "domain_model_map": "",
    "discovery_capability_map": "",
    "technical_solution": ""
  },
  "implementation_plan": [
    {
      "step": "",
      "intent": "",
      "deliverables": [],
      "rollback_point": "",
      "evidence": []
    }
  ],
  "code_scaffold_map": [
    {
      "artifact": "",
      "code_location": "",
      "purpose": "",
      "owner_layer": "",
      "files": [],
      "directories": [],
      "evidence": []
    }
  ],
  "directory_tree": [],
  "bootstrap_manifest": [
    {
      "kind": "",
      "action": "",
      "path": "",
      "parent": "",
      "source": "",
      "owner_layer": "",
      "purpose": ""
    }
  ],
  "task_batch_list": [
    {
      "batch_name": "",
      "goal": "",
      "tasks": [],
      "dependencies": [],
      "acceptance_criteria": [],
      "rollback_point": "",
      "evidence": []
    }
  ],
  "branch_commit_plan": [
    {
      "branch_name": "",
      "commit_theme": "",
      "scope": "",
      "notes": []
    }
  ],
  "verification_plan": {
    "positive_checks": [],
    "negative_checks": [],
    "test_matrix": [],
    "manual_checks": [],
    "automation_checks": [],
    "regression_checks": [
      {
        "after_goal": "",
        "what_to_rerun": [],
        "why": "",
        "pass_criteria": [],
        "rollback_point": ""
      }
    ]
  },
  "assumptions": [],
  "blocked_items": [],
  "handoff_notes": []
}
```

## 2. Implementation Handoff Report

```json
{
  "decision": "",
  "summary": "",
  "goal_progress": {
    "total_goals": 0,
    "completed_goals": 0,
    "current_goal": "",
    "next_goal": ""
  },
  "upstream_input_inventory": [],
  "upstream_input_coverage_matrix": [],
  "latest_verification": {
    "goal_id": "",
    "regression_passed": false,
    "checked_goals": [],
    "blocked_items": [],
    "rollback_point": "",
    "status": ""
  },
  "passed_checks": [],
  "failed_checks": [],
  "blocked_by": [],
  "rollback_point": "",
  "next_action": "",
  "risks": [],
  "evidence": []
}
```

## 3. Usage Rule

- 先输出 `implementation_plan`
- 再输出 `implementation_handoff_report`
- 不输出 schema 之外的对象
