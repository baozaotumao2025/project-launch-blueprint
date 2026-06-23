# Implementation Example Output

> 复制这个样板后，直接替换 `<...>` 占位符。  
> 规则：
> - 不要删字段，只能补值。
> - 先冻结 goal，再做计划。
> - 不适用就保留空数组、空字符串或 `false`。

## 1. Implementation Plan

```json
{
  "goal": "<one_sentence_goal>",
  "scope": "<frozen_scope>",
  "upstream_input_inventory": [
    {
      "input_key": "codex_goal",
      "input_type": "codex goal",
      "role": "primary",
      "path": "<goal_text>",
      "size_bytes": 0
    }
  ],
  "upstream_input_coverage_matrix": [
    {
      "input_key": "codex_goal",
      "input_type": "codex goal",
      "role": "primary",
      "path": "<goal_text>",
      "status": "unmapped",
      "mapped_to": [],
      "reason": "",
      "evidence": []
    }
  ],
  "goal_registry": [
    {
      "goal_id": "goal-1",
      "order": 1,
      "goal": "freeze scope",
      "depends_on": [],
      "status": "done",
      "regression_scope": [
        "baseline slice"
      ],
      "rollback_point": "analysis",
      "evidence": [
        "<goal_text>"
      ]
    }
  ],
  "inputs": {
    "codex_goal": "<goal_text>",
    "quality_gates_validation_report": "<validation_report_ref>",
    "vertical_slice_map": "<vertical_slice_ref>",
    "api_contract_map": "<api_contract_ref>",
    "design_system_map": "<design_system_ref>",
    "state_machine_map": "<state_machine_ref>",
    "domain_model_map": "<domain_model_ref>",
    "discovery_capability_map": "<capability_ref>",
    "technical_solution": "<technical_solution_ref>"
  },
  "implementation_plan": [
    {
      "step": "freeze_scope",
      "intent": "把 goal 转成单一可执行范围",
      "deliverables": [
        "scope note",
        "rollback point"
      ],
      "rollback_point": "analysis",
      "evidence": [
        "<goal_text>"
      ]
    }
  ],
  "code_scaffold_map": [
    {
      "artifact": "slice entry",
      "code_location": "features/invite/",
      "purpose": "承载原型切片骨架",
      "owner_layer": "vertical slice",
      "evidence": [
        "<vertical_slice_ref>"
      ]
    }
  ],
  "task_batch_list": [
    {
      "batch_name": "scaffold_first",
      "goal": "先把目录、文件和类型壳搭好",
      "tasks": [
        "create directory skeleton",
        "add types",
        "add test shells"
      ],
      "dependencies": [],
      "acceptance_criteria": [
        "目录存在",
        "骨架可读"
      ],
      "rollback_point": "code_scaffold_map",
      "evidence": [
        "<technical_solution_ref>"
      ]
    }
  ],
  "branch_commit_plan": [
    {
      "branch_name": "feat/prototype-invite-skeleton",
      "commit_theme": "scaffold",
      "scope": "only directory and type shells",
      "notes": [
        "one batch per commit"
      ]
    }
  ],
  "verification_plan": {
    "positive_checks": [
      "goal can be traced to files"
    ],
    "negative_checks": [
      "component does not fetch directly"
    ],
    "test_matrix": [
      "mock/real parity"
    ],
    "manual_checks": [
      "directory tree review"
    ],
    "automation_checks": [
      "test runner"
    ],
    "regression_checks": [
      {
        "after_goal": "goal-1",
        "what_to_rerun": [
          "baseline slice tests"
        ],
        "why": "protect existing behavior",
        "pass_criteria": [
          "baseline still passes"
        ],
        "rollback_point": "analysis"
      }
    ]
  },
  "assumptions": [
    "goal is already narrow"
  ],
  "blocked_items": [],
  "handoff_notes": [
    "continue with implementation only after scope freeze"
  ]
}
```

## 2. Implementation Handoff Report

```json
{
  "decision": "go",
  "summary": "goal is clear and scaffold-first plan is ready",
  "goal_progress": {
    "total_goals": 1,
    "completed_goals": 1,
    "current_goal": "goal-1",
    "next_goal": ""
  },
  "upstream_input_inventory": [
    {
      "input_key": "codex_goal",
      "input_type": "codex goal",
      "role": "primary",
      "path": "<goal_text>",
      "size_bytes": 0
    }
  ],
  "upstream_input_coverage_matrix": [
    {
      "input_key": "codex_goal",
      "input_type": "codex goal",
      "role": "primary",
      "path": "<goal_text>",
      "status": "unmapped",
      "mapped_to": [],
      "reason": "",
      "evidence": []
    }
  ],
  "passed_checks": [
    "goal clarity",
    "artifact mapping",
    "rollback safety"
  ],
  "failed_checks": [],
  "blocked_by": [],
  "rollback_point": "analysis",
  "next_action": "generate scaffold",
  "risks": [
    "scope creep"
  ],
  "evidence": [
    "<goal_text>",
    "<validation_report_ref>"
  ]
}
```
