# Vertical Slice

> 第六阶段目录：只负责 `api contract map + design system map + state machine map + upstream input inventory + 辅助证据 -> vertical slices -> routes -> pages -> feature modules -> hooks -> services -> repositories -> mocks -> vertical-slice validation report`。
> 这一层的职责是把前面已经稳定下来的语义真正拼成可运行的功能切片，而不是重新发明业务、状态或 UI 规则。

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

> 本目录消费 `api-contract`、`design-system` 和 `state-machine` 的已验证输出，并冻结上游输入 inventory / coverage matrix，不直接把原始 `analysis` 当作主输入；`analysis` 只作为辅助证据。
