# Quality Gates

> 第七阶段目录：只负责 `discovery capability map + domain model map + state machine map + api contract map + design system map + vertical slice map + upstream input inventory + 辅助证据 -> quality gates -> release criteria -> rollback plan -> quality-gates validation report`。
> 这一层的职责是把前面所有阶段的成果变成可发布、可回滚、可观测的交付门槛，而不是重新建模业务。

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

> 本目录消费前面所有阶段的已验证输出，并冻结上游输入 inventory / coverage matrix，不直接把原始 `analysis` 当作主输入；`analysis` 只作为辅助证据。
