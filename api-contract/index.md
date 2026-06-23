# API Contract

> 第四阶段目录：只负责 `discovery capability map + domain model map + state machine map + upstream input inventory + 辅助证据 -> api contracts -> requests -> responses -> status/headers/errors/auth/idempotency/versioning -> api-contract validation report`。
> 这一层的职责是把已验证的能力、边界和状态翻译成稳定的 HTTP 交换语义，避免 UI 或实现细节反向塑形接口。

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

> 本目录消费 `discovery`、`domain-model` 和 `state-machine` 的已验证输出，并冻结上游输入 inventory / coverage matrix，不直接把原始 `analysis` 当作主输入；`analysis` 只作为辅助证据。
