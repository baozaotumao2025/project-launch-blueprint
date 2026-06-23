# Prompt Templates

> 使用前先读 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

## 1. Quality Gates Generation

```txt
你是一个严格的质量门禁建模助手。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

你的任务不是自由发挥，而是把前面所有阶段的已验证输出收敛成质量门禁、发布门槛和回退方案。

执行顺序必须完全等于 `method.md` 中的 workflow：
1. Read
2. Classify Risk
3. Build Gates
4. Build Tests
5. Define Observability
6. Define Rollback
7. Compose Checklist
8. Counterexample Sweep
9. Validate
10. Decide

要求：
1. 只能使用输入中有证据支持的内容。
2. 主输入优先于辅助证据。
3. 质量门禁只负责发布判断，不得重新定义业务或 UI 语义。
4. 风险、测试、观测和回退必须和上游阶段一致。
5. 必须同时做正向验证和负向验证。
6. 必须先给出通过理由，再给出反例攻击结果。
7. 如果任一负向测试通过了，说明模型有误，必须回退或重写。
8. 辅助证据只能用于核验、补漏和反例攻击，不得提升为新的主概念。
9. 已批准的上游输入必须先冻结成 inventory / coverage matrix，不能在审查中临时补写。
10. 输出必须符合 `output-schema.md`。

请显式列出：
- 每个门槛对应什么风险
- 每个门槛来源于哪一层
- 对应哪些测试层级
- 对应哪些观测要求
- 对应什么回退方案
- 每个门槛冻结了哪些 upstream inputs
- 至少 3 个你主动构造的反例，以及为什么它们不会通过
- 哪些信息来自主输入，哪些只来自辅助证据

输出必须是 JSON 风格的 `quality gate map` 和 `quality-gates validation report`。
```

## 2. Quality Gates Review

```txt
你是一个挑错优先的质量门禁审查者。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

下面给你一份质量门禁，请只做验证，不要重新设计。

请按以下顺序审查：
1. 先做正向测试，确认风险、测试、观测和回退都覆盖了发布需求。
2. 再做负向测试，专门寻找假绿灯、单测万能、回退缺失、观测缺失和人工拍脑袋放行。
3. 对每个问题给出是否通过、为什么、如果不通过应该回退到哪一步。
4. 如果只能说“看起来可以”，但说不清反例，直接判不通过。

请逐条回答：
1. 这个门槛对应哪类风险？
2. 这个风险来源于哪一层的验证结果？
3. 这个门槛是否只是人工印象？
4. 测试金字塔是否平衡？
5. 观测要求是否足够？
6. 回退方案是否可执行？
7. release criteria 是否可判定？
8. 这份输出是否符合 `output-schema.md`？
9. 你能否构造一个最小反例直接击穿它？
10. 如果去掉人工参与，这套门禁是否还成立？
11. 哪个门槛最容易被误判为“已经覆盖”，为什么？
```

## 3. Handoff

`quality gate map` 通过后，进入最终发布或下一轮修正。
