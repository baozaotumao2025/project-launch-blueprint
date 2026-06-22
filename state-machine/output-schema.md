# Output Schema

> state machine 阶段只输出状态机结构和 `state-machine validation report`。

## 1. State Machine Map

```json
{
  "state_machines": [
    {
      "name": "",
      "bounded_context": "",
      "goal": "",
      "scope": "",
      "states": [],
      "events": [],
      "guards": [],
      "transitions": [],
      "terminal_states": [],
      "entry_conditions": [],
      "exit_conditions": [],
      "capabilities": [],
      "domain_objects": [],
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

## 2. State-Machine Validation Report

```json
{
  "coverage": "",
  "state_purity": "",
  "event_purity": "",
  "guard_clarity": "",
  "terminal_validity": "",
  "flow_cohesion": "",
  "positive_test_results": [],
  "negative_test_results": [],
  "item_results": [],
  "gaps": [],
  "rejected_items": [],
  "accepted_items": []
}
```

## 3. Usage Rule

- 先输出 state machine map
- 再输出 state-machine validation report
- 不输出 state machine 以外的对象
