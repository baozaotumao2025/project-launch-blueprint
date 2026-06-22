# Output Schema

> design-system 阶段只输出 `design system map` 和 `design-system validation report`。

## 1. Design System Map

```json
{
  "design_systems": [
    {
      "name": "",
      "version": "",
      "goal": "",
      "scope": "",
      "api_contracts": [],
      "state_machines": [],
      "domain_objects": [],
      "capabilities": [],
      "tokens": {
        "semantic_colors": [],
        "spacing": [],
        "radius": [],
        "shadow": [],
        "z_index": []
      },
      "color_system": {
        "palette": [],
        "semantic_mapping": [],
        "contrast_rules": []
      },
      "typography": {
        "families": [],
        "scale": [],
        "weights": [],
        "line_heights": []
      },
      "layout_rules": {
        "grid": [],
        "breakpoints": [],
        "density": [],
        "composition": []
      },
      "motion_rules": {
        "durations": [],
        "easing": [],
        "reduced_motion": []
      },
      "accessibility_rules": [],
      "responsive_rules": [],
      "iconography_rules": [],
      "components": [
        {
          "name": "",
          "purpose": "",
          "anatomy": [],
          "variants": [],
          "sizes": [],
          "states": [],
          "behaviors": [],
          "props": [],
          "tokens": [],
          "positive_tests": [],
          "negative_tests": [],
          "rollback_point": "",
          "evidence": []
        }
      ],
      "interaction_patterns": [],
      "usage_guidelines": [],
      "anti_patterns": [],
      "positive_tests": [],
      "negative_tests": [],
      "rollback_point": "",
      "evidence": [],
      "assumptions": []
    }
  ]
}
```

## 2. Design-System Validation Report

```json
{
  "coverage": "",
  "token_purity": "",
  "semantic_consistency": "",
  "component_reusability": "",
  "state_coverage": "",
  "accessibility_fit": "",
  "responsive_fit": "",
  "motion_clarity": "",
  "positive_test_results": [],
  "negative_test_results": [],
  "item_results": [],
  "gaps": [],
  "rejected_items": [],
  "accepted_items": []
}
```

## 3. Usage Rule

- 先输出 design system map
- 再输出 design-system validation report
- 不输出 design-system 以外的对象

