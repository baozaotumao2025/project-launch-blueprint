# State Machine

> 第三阶段目录：只负责 `discovery capability map + domain model map + 辅助证据 -> states -> events -> guards -> transitions -> terminal states -> state-machine validation report`。
> 这一层的职责是把关键业务流程显式化，防止接口和页面提前代替业务做状态决策。

## Files

- `method.md`
- `validation-rules.md`
- `prompt-templates.md`
- `output-schema.md`
- `example-output.md`
- `checklist.md`

## Start Here

1. `../index.md`
2. `method.md`

> 本目录消费 `discovery` 与 `domain-model` 的已验证输出，不直接把原始 `analysis` 当作主输入；`analysis` 只作为辅助证据。
