# Domain Model

> 第二阶段目录：只负责 `discovery capability map + discovery validation report + 辅助证据 -> bounded contexts -> aggregates -> entities/value objects -> context map -> domain-model validation report`。
> 这一层的职责是把已验证能力收敛成业务边界和对象责任，避免能力地图直接滑向实现细节。

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

> 本目录消费的是 `discovery` 已验证输出，不直接把原始 `analysis` 当作主输入；`analysis` 只作为辅助证据。
