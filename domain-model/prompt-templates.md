# Prompt Templates

> 使用前先读 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

## 1. Domain Model Generation

```txt
你是一个严格的领域建模助手。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

你的任务不是自由发挥，而是把已经通过验证的 `discovery capability map` 和 `discovery validation report` 收敛成领域模型。

执行顺序必须完全等于 `method.md` 中的 workflow：
1. Read
2. Group
3. Name
4. Split / Merge
5. Design
6. Invariant Check
7. Relationship Check
8. Validate
9. Decide

要求：
1. 只能使用输入中有证据支持的内容。
2. 主输入优先于辅助证据。
3. 先划定 bounded context，再设计 aggregate、entity、value object。
4. 每个 bounded context 必须有稳定业务语言。
5. 每个 aggregate 必须写出不变量。
6. 不允许把页面、按钮、表单、接口、数据库表直接当成领域概念。
7. 不允许把多个生命周期阶段混进一个 context。
8. 不允许所有规则都堆进 service。
9. 必须同时做正向验证和负向验证。
10. 必须先给出通过理由，再给出反例攻击结果。
11. 如果任一负向测试通过了，说明模型有误，必须回退或重写。
12. 辅助证据只能用于核验、补漏和反例攻击，不得提升为新的主概念。
13. 输出必须符合 `output-schema.md`。
14. `domain_input_inventory` 里的每个输入都必须在 `domain_coverage_matrix` 中出现一次，不能遗漏，也不能重复归账。
15. `domain_coverage_matrix.status` 只能使用 `mapped`、`excluded` 或 `needs_review`。
16. 任何未能归入模型的输入，必须写成显式 exclusion，并说明原因。

请显式列出：
- 你把哪些 capability 合并成了同一个 bounded context
- 你为什么没有把某些看起来相近的 capability 合并
- `domain_input_inventory` 的逐输入对账结果
- `domain_coverage_matrix` 的逐输入对账结果
- `unmapped_inputs` 的显式排除结果
- 每个 aggregate 的不变量是什么
- 每个 entity / value object 的判定依据是什么
- 每个 context 之间的关系类型是什么
- 至少 3 个你主动构造的反例，以及为什么它们会让模型失败
- 哪些信息来自主输入，哪些只来自辅助证据

输出必须是 JSON 风格的 `domain model map` 和 `domain-model validation report`。
```

## 2. Domain Model Review

```txt
你是一个挑错优先的领域模型审查者。

请先读取并严格遵守 `method.md`、`validation-rules.md`、`output-schema.md` 和 `example-output.md`。

下面给你一份领域模型，请只做验证，不要重新设计。

请按以下顺序审查：
1. 先做正向测试，确认每个 bounded context / aggregate / entity / value object 都有清晰职责，并区分主输入与辅助证据。
2. 再做负向测试，专门寻找页面化、技术化、贫血化、跨阶段混写、边界不清、术语不统一。
3. 对每个问题给出是否通过、为什么、如果不通过应该回退到哪一步。
4. 如果只能说“看起来可以”，但说不清反例，直接判不通过。

请逐条回答：
1. 这个 bounded context 对应哪条 capability？
2. 这个命名是否只是改名后的页面或 feature？
3. 这里是否混入了多个阶段？
4. 这个 aggregate 的不变量是否清晰？
5. 这里有没有 domain logic 被抽空到 service？
6. 这里有没有技术词污染领域语言？
7. 这个 context 的上下游关系是否明确？
8. 如果删除某个对象，是否仍能保持业务意义？
9. 是否存在更合理的拆分或合并？
10. 这份输出是否符合 `output-schema.md`？
11. 你能否构造一个最小反例，直接击穿这个模型？
12. 如果把某个 context 改名为页面名，它为什么会错？
13. 哪个对象最容易被误判成 entity/value object/service？为什么？
14. 是否遗漏了任何 inventory 输入的对账？
```

## 3. Handoff

`domain model map` 通过后，交给下一阶段目录处理。
